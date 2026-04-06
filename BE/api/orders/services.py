"""
Service Layer - Business Logic cho Hóa đơn và Chi tiết đơn hàng
"""
from django.db import transaction
from django.db.models import Q, Count, Sum, Avg, F
from django.db.models.functions import TruncDate, TruncDay, TruncWeek, TruncMonth, TruncYear, Coalesce
from django.db.models import Value, DecimalField
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from .models import HoaDon, ChiTietDonHang
from api.products.models import SanPham
from api.customers.services import CustomerService
from api.ingredients.services import IngredientService
from api.ingredients.models import NguyenLieu
from api.recipes.models import CongThuc


class OrderService:
    """Service xử lý business logic cho đơn hàng"""
    
    @staticmethod
    def get_all_orders(customer_id=None, employee_id=None, status=None, 
                       from_date=None, to_date=None, search=None):
        """
        Lấy danh sách đơn hàng với filter
        Tối ưu: select_related cho ForeignKey, prefetch cho chi tiết
        """
        queryset = HoaDon.objects.select_related(
            'CustomerID',
            'EmployeeID'
        ).prefetch_related(
            'chitietdonhang_set',
            'chitietdonhang_set__ProductID'
        ).annotate(
            items_count=Count('chitietdonhang')
        )
        
        if customer_id:
            queryset = queryset.filter(CustomerID=customer_id)
        
        if employee_id:
            queryset = queryset.filter(EmployeeID=employee_id)
        
        if status:
            queryset = queryset.filter(Status=status)
        
        if from_date:
            queryset = queryset.filter(OrderDate__gte=from_date)
        
        if to_date:
            # Thêm 1 ngày để bao gồm cả ngày to_date
            queryset = queryset.filter(OrderDate__lt=to_date + timedelta(days=1))
        
        if search:
            queryset = queryset.filter(
                Q(OrderID__icontains=search) |
                Q(CustomerID__FullName__icontains=search) |
                Q(CustomerID__PhoneNumber__icontains=search)
            )
        
        return queryset.order_by('-OrderDate')
    
    @staticmethod
    def get_order_by_id(order_id):
        """Lấy đơn hàng theo ID"""
        try:
            return HoaDon.objects.select_related(
                'CustomerID',
                'EmployeeID'
            ).prefetch_related(
                'chitietdonhang_set__ProductID'
            ).get(OrderID=order_id)
        except HoaDon.DoesNotExist:
            return None
    
    @staticmethod
    @transaction.atomic
    def create_order(order_data, items_data):
        """
        Tạo đơn hàng mới với chi tiết
        
        Args:
            order_data: Dict chứa thông tin đơn hàng
            items_data: List of dict chứa thông tin sản phẩm
        
        Returns:
            (success, message/order, errors)
        """
        # Kiểm tra nhân viên
        from django.contrib.auth.models import User
        try:
            employee = User.objects.get(pk=order_data['EmployeeID'], is_staff=True)
        except User.DoesNotExist:
            return False, "Nhân viên không tồn tại", []
        
        # Kiểm tra khách hàng (nếu có)
        customer = None
        if order_data.get('CustomerID'):
            customer = CustomerService.get_customer_by_id(order_data['CustomerID'])
            if not customer:
                return False, "Khách hàng không tồn tại", []
        
        # Kiểm tra sản phẩm và tính toán (chưa trừ nguyên liệu)
        order_details = []
        total_amount = Decimal('0')
        errors = []

        for item in items_data:
            try:
                product = SanPham.objects.get(ProductID=item['ProductID'])

                # Kiểm tra sản phẩm còn hàng không
                if product.Status != 1:
                    errors.append(f"Sản phẩm '{product.ProductName}' hiện không có sẵn")
                    continue

                # Tính toán
                unit_price = product.Price
                quantity = item['Quantity']
                subtotal = unit_price * quantity
                total_amount += subtotal

                order_details.append({
                    'product': product,
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'subtotal': subtotal,
                    'topping_note': item.get('ToppingNote', '')
                })

            except SanPham.DoesNotExist:
                errors.append(f"Sản phẩm ID {item['ProductID']} không tồn tại")
        
        if errors:
            return False, "Có lỗi khi tạo đơn hàng", errors
        
        if not order_details:
            return False, "Không có sản phẩm hợp lệ trong đơn hàng", []
        
        # Kiểm tra nguyên liệu đủ cho toàn bộ đơn hàng
        is_available, missing = OrderService._check_ingredients_for_items(order_details)
        if not is_available:
            return False, "Không đủ nguyên liệu cho đơn hàng", [missing]

        # Tính giảm giá và thành tiền
        # Đảm bảo discount là Decimal
        discount = order_data.get('Discount', Decimal('0'))
        if not isinstance(discount, Decimal):
            discount = Decimal(str(discount))
        if discount > total_amount:
            discount = total_amount
        
        final_amount = total_amount - discount
        
        # Tạo hóa đơn
        order = HoaDon.objects.create(
            CustomerID=customer,
            EmployeeID=employee,
            TotalAmount=total_amount,
            Discount=discount,
            FinalAmount=final_amount,
            PaymentMethod=order_data.get('PaymentMethod', 'CASH'),
            Status='PENDING'
        )
        
        # Tạo chi tiết đơn hàng
        for detail in order_details:
            ChiTietDonHang.objects.create(
                OrderID=order,
                ProductID=detail['product'],
                Quantity=detail['quantity'],
                UnitPrice=detail['unit_price'],
                Subtotal=detail['subtotal'],
                ToppingNote=detail['topping_note']
            )
        
        # Trừ nguyên liệu
        OrderService._reduce_ingredients_for_order(order.OrderID)
        
        # Cộng điểm cho khách hàng (nếu có)
        if customer:
            CustomerService.add_points_from_order(customer.CustomerID, final_amount)
        
        return True, order, []
    
    @staticmethod
    def _check_ingredients_for_items(order_details):
        """Kiểm tra nguyên liệu đủ cho toàn bộ đơn hàng theo tổng nhu cầu.

        order_details: list dict đã chuẩn hóa gồm keys: product, quantity
        """
        # Tổng hợp nhu cầu theo nguyên liệu
        ingredient_required = {}
        product_ids = [d['product'].ProductID for d in order_details]
        recipes = CongThuc.objects.filter(ProductID__in=product_ids).select_related('IngredientID')
        product_to_qty = {d['product'].ProductID: d['quantity'] for d in order_details}

        for recipe in recipes:
            requested_qty = product_to_qty.get(recipe.ProductID_id, 0)
            if not requested_qty:
                continue
            need = recipe.Quantity * requested_qty
            ing_id = recipe.IngredientID_id
            ingredient_required[ing_id] = ingredient_required.get(ing_id, Decimal('0')) + need

        # Đối chiếu tồn kho
        if not ingredient_required:
            return True, ''

        ingredients = NguyenLieu.objects.filter(pk__in=ingredient_required.keys())
        missing_msgs = []
        for ing in ingredients:
            required = ingredient_required.get(ing.pk, Decimal('0'))
            if ing.QuantityInStock < required:
                missing_msgs.append(f"{ing.IngredientName} (cần {required}, có {ing.QuantityInStock})")

        return len(missing_msgs) == 0, ', '.join(missing_msgs) if missing_msgs else ''
    
    @staticmethod
    @transaction.atomic
    def _reduce_ingredients_for_order(order_id):
        """Trừ nguyên liệu khi tạo đơn hàng (gộp theo nguyên liệu, có khóa hàng)"""
        order = OrderService.get_order_by_id(order_id)
        if not order:
            return

        # Tính tổng nhu cầu theo nguyên liệu
        ingredient_required = {}
        for detail in order.chitietdonhang_set.all():
            recipes = CongThuc.objects.filter(ProductID=detail.ProductID).select_related('IngredientID')
            for recipe in recipes:
                need = recipe.Quantity * detail.Quantity
                ing_id = recipe.IngredientID_id
                ingredient_required[ing_id] = ingredient_required.get(ing_id, Decimal('0')) + need

        if not ingredient_required:
            return

        # Khóa các bản ghi nguyên liệu để trừ an toàn
        ingredients = NguyenLieu.objects.select_for_update().filter(pk__in=ingredient_required.keys())
        for ing in ingredients:
            ing.QuantityInStock -= ingredient_required.get(ing.pk, Decimal('0'))
            ing.save()
    
    @staticmethod
    @transaction.atomic
    def _restore_ingredients_for_order(order_id):
        """Hoàn nguyên liệu khi hủy đơn hàng (gộp theo nguyên liệu, có khóa hàng)"""
        order = OrderService.get_order_by_id(order_id)
        if not order:
            return

        ingredient_restore = {}
        for detail in order.chitietdonhang_set.all():
            recipes = CongThuc.objects.filter(ProductID=detail.ProductID).select_related('IngredientID')
            for recipe in recipes:
                qty = recipe.Quantity * detail.Quantity
                ing_id = recipe.IngredientID_id
                ingredient_restore[ing_id] = ingredient_restore.get(ing_id, Decimal('0')) + qty

        if not ingredient_restore:
            return

        ingredients = NguyenLieu.objects.select_for_update().filter(pk__in=ingredient_restore.keys())
        for ing in ingredients:
            ing.QuantityInStock += ingredient_restore.get(ing.pk, Decimal('0'))
            ing.save()
    
    @staticmethod
    def update_order_status(order_id, new_status):
        """
        Cập nhật trạng thái đơn hàng
        
        Returns:
            (success, message, order)
        """
        order = OrderService.get_order_by_id(order_id)
        if not order:
            return False, "Không tìm thấy đơn hàng", None
        
        old_status = order.Status
        
        # Nếu hủy đơn, hoàn nguyên liệu
        if new_status == 'CANCELLED' and old_status != 'CANCELLED':
            OrderService._restore_ingredients_for_order(order_id)
        
        order.Status = new_status
        order.save()
        
        return True, "Cập nhật trạng thái thành công", order
    
    @staticmethod
    def delete_order(order_id):
        """Xóa đơn hàng (chỉ cho phép nếu đang ở trạng thái PENDING hoặc CANCELLED)"""
        order = OrderService.get_order_by_id(order_id)
        if not order:
            return False, "Không tìm thấy đơn hàng"
        
        if order.Status not in ['PENDING', 'CANCELLED']:
            return False, "Chỉ có thể xóa đơn hàng ở trạng thái Chờ xác nhận hoặc Đã hủy"
        
        # Hoàn nguyên liệu nếu chưa hủy
        if order.Status != 'CANCELLED':
            OrderService._restore_ingredients_for_order(order_id)
        
        order.delete()
        return True, "Xóa đơn hàng thành công"
    
    @staticmethod
    def get_revenue_statistics(from_date=None, to_date=None, include_all_status=False):
        """
        Thống kê doanh thu với cache
        Cache key: revenue_stats_{from_date}_{to_date}_{include_all_status}
        Cache timeout: 5 phút cho dashboard, 30 phút cho báo cáo
        """
        from django.core.cache import cache
        
        # Tạo cache key
        cache_key = f"revenue_stats_{from_date}_{to_date}_{include_all_status}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
        
        if include_all_status:
            # Cho dashboard: lấy tất cả đơn hàng hôm nay
            queryset = HoaDon.objects.all()
        else:
            # Cho báo cáo: chỉ lấy đơn hàng đã hoàn thành
            queryset = HoaDon.objects.filter(Status='COMPLETED')
        
        if from_date:
            queryset = queryset.filter(OrderDate__gte=from_date)
        
        if to_date:
            queryset = queryset.filter(OrderDate__lt=to_date + timedelta(days=1))
        
        stats = queryset.aggregate(
            total_orders=Count('OrderID'),
            total_revenue=Coalesce(Sum('FinalAmount'), Value(0, output_field=DecimalField(max_digits=12, decimal_places=2))),
            total_discount=Coalesce(Sum('Discount'), Value(0, output_field=DecimalField(max_digits=12, decimal_places=2))),
            average_order_value=Coalesce(Avg('FinalAmount'), Value(0, output_field=DecimalField(max_digits=12, decimal_places=2)))
        )
        
        # Thống kê theo ngày
        daily_stats = queryset.annotate(
            date=TruncDate('OrderDate')
        ).values('date').annotate(
            orders=Count('OrderID'),
            revenue=Sum('FinalAmount')
        ).order_by('date')
        
        result = {
            'summary': stats,
            'daily': list(daily_stats)
        }
        
        # Cache result: 5 phút cho dashboard, 30 phút cho báo cáo
        cache_timeout = 300 if include_all_status else 1800
        cache.set(cache_key, result, cache_timeout)
        
        return result
    
    @staticmethod
    def get_best_selling_products(from_date=None, to_date=None, limit=10):
        """
        Lấy sản phẩm bán chạy nhất với cache
        Cache timeout: 10 phút
        """
        from django.core.cache import cache
        
        cache_key = f"best_selling_{from_date}_{to_date}_{limit}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
        
        queryset = ChiTietDonHang.objects.filter(
            OrderID__Status='COMPLETED'
        ).select_related('ProductID')  # Tối ưu query
        
        if from_date:
            queryset = queryset.filter(OrderID__OrderDate__gte=from_date)
        
        if to_date:
            queryset = queryset.filter(OrderID__OrderDate__lt=to_date + timedelta(days=1))
        
        best_selling = queryset.values(
            'ProductID',
            'ProductID__ProductName'
        ).annotate(
            total_quantity=Sum('Quantity'),
            total_revenue=Sum('Subtotal'),
            order_count=Count('OrderID', distinct=True)
        ).order_by('-total_quantity')[:limit]
        
        result = list(best_selling)
        cache.set(cache_key, result, 600)  # Cache 10 phút
        return result

    @staticmethod
    def get_revenue_trend(from_date=None, to_date=None, interval: str = 'day'):
        """
        Lấy dữ liệu doanh thu theo thời gian với cache
        Cache timeout: 15 phút
        """
        from django.core.cache import cache
        
        cache_key = f"revenue_trend_{from_date}_{to_date}_{interval}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
        
        queryset = HoaDon.objects.filter(Status='COMPLETED')
        if from_date:
            queryset = queryset.filter(OrderDate__gte=from_date)
        if to_date:
            queryset = queryset.filter(OrderDate__lt=to_date + timedelta(days=1))

        interval = (interval or 'day').lower()
        if interval == 'year':
            trunc_fn = TruncYear
            fmt = '%Y'
        elif interval == 'month':
            trunc_fn = TruncMonth
            fmt = '%Y-%m'
        elif interval == 'week':
            trunc_fn = TruncWeek
            fmt = '%Y-W%W'
        else:
            trunc_fn = TruncDay
            fmt = '%Y-%m-%d'

        series = queryset.annotate(period=trunc_fn('OrderDate')).values('period').annotate(
            revenue=Coalesce(Sum('FinalAmount'), Value(0, output_field=DecimalField(max_digits=12, decimal_places=2)))
        ).order_by('period')

        labels = [item['period'].strftime(fmt) for item in series]
        data = [item['revenue'] for item in series]

        result = {
            'labels': labels,
            'datasets': [
                {
                    'label': 'Revenue',
                    'data': data,
                }
            ],
            'interval': interval,
        }
        
        # Cache 15 phút
        cache.set(cache_key, result, 900)
        return result

    @staticmethod
    def get_revenue_by_category(from_date=None, to_date=None):
        """Tổng doanh thu theo danh mục sản phẩm trong khoảng thời gian"""
        queryset = ChiTietDonHang.objects.filter(
            OrderID__Status='COMPLETED'
        )
        if from_date:
            queryset = queryset.filter(OrderID__OrderDate__gte=from_date)
        if to_date:
            queryset = queryset.filter(OrderID__OrderDate__lt=to_date + timedelta(days=1))

        by_cat = queryset.values(
            'ProductID__CategoryID__CategoryName'
        ).annotate(
            revenue=Coalesce(Sum('Subtotal'), Value(0, output_field=DecimalField(max_digits=12, decimal_places=2)))
        ).order_by('-revenue')

        labels = [item['ProductID__CategoryID__CategoryName'] or 'Khác' for item in by_cat]
        data = [item['revenue'] for item in by_cat]

        return {
            'labels': labels,
            'datasets': [
                {
                    'label': 'Revenue by Category',
                    'data': data,
                }
            ]
        }
