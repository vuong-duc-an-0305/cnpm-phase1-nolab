from django.contrib.auth import authenticate
from django.contrib.auth.models import User, Group
from django.db.models import Q
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.core.permissions import IsAdminRole
from .models import EmployeeDetail
from .serializers import LoginSerializer, RegisterSerializer, UserSerializer, EmployeeDetailSerializer


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        data = {
            'token': token.key,
            'user': UserSerializer(user).data,
        }
        return Response(data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response({'detail': 'Tên đăng nhập hoặc mật khẩu không đúng.'}, status=status.HTTP_400_BAD_REQUEST)

        token, _ = Token.objects.get_or_create(user=user)
        data = {
            'token': token.key,
            'user': UserSerializer(user).data,
        }
        return Response(data)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        data = UserSerializer(user).data
        return Response(data)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        token = getattr(request, 'auth', None)
        if isinstance(token, Token):
            token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ===== USER MANAGEMENT API (Thay thế Employees) =====

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, IsAdminRole])
def users_list(request):
    """
    Danh sách users (thay thế cho employees)
    GET: Lấy danh sách users trong nhóm 'Nhân viên'
    POST: Tạo user mới
    """
    if request.method == 'GET':
        # Chỉ hiển thị users thuộc nhóm: cashier, waiter (không bao gồm admin, manager và superuser)
        # OPTIMIZED: Thêm select_related và prefetch_related để tránh N+1 queries
        users = User.objects.filter(
            Q(groups__name='cashier') |
            Q(groups__name='waiter')
        ).filter(is_superuser=False).select_related(
            'employee_detail'
        ).prefetch_related(
            'groups'
        ).distinct().order_by('-date_joined')
        
        # Search
        search = request.query_params.get('search', '')
        if search:
            users = users.filter(
                Q(username__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )
        
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        # Validate role - chỉ cho phép tạo cashier hoặc waiter
        role = request.data.get('role', 'waiter')
        if role not in ['cashier', 'waiter']:
            return Response(
                {'error': 'Chỉ được tạo nhân viên với role cashier hoặc waiter'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                # Trả về user data với UserSerializer
                return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response(
                    {'error': f'Lỗi khi tạo user: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated, IsAdminRole])
def user_detail(request, pk):
    """
    Chi tiết user
    GET: Lấy thông tin
    PUT/PATCH: Cập nhật
    DELETE: Xóa
    """
    try:
        # Superuser có thể truy cập bất kỳ user nào
        # OPTIMIZED: Thêm select_related và prefetch_related
        if request.user.is_superuser:
            user = User.objects.select_related('employee_detail').prefetch_related('groups').get(pk=pk)
        else:
            user = User.objects.filter(
                pk=pk,
                groups__name__in=['admin', 'manager', 'cashier', 'waiter']
            ).select_related('employee_detail').prefetch_related('groups').distinct().get()
    except User.DoesNotExist:
        return Response(
            {'error': 'User không tồn tại'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data)
    
    elif request.method in ['PUT', 'PATCH']:
        # Xử lý role (group) riêng nếu có trong request
        role = request.data.get('role')
        
        # Loại bỏ 'role' khỏi data trước khi pass vào serializer (vì role là read-only)
        data = dict(request.data)
        if 'role' in data:
            data.pop('role')
        
        serializer = UserSerializer(user, data=data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            serializer.save()
            
            # Cập nhật group sau khi save user
            if role and role in ['admin', 'manager', 'cashier', 'waiter']:
                user.groups.clear()
                group, _ = Group.objects.get_or_create(name=role)
                user.groups.add(group)
            
            # Trả về data mới với role đã cập nhật
            response_serializer = UserSerializer(user)
            return Response(response_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ===== EMPLOYEE DETAIL API =====

@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated, IsAdminRole])
def employee_detail(request, user_id):
    """
    Chi tiết thông tin nhân viên
    GET: Lấy thông tin chi tiết
    PUT/PATCH: Cập nhật thông tin chi tiết
    """
    try:
        # Superuser có thể truy cập bất kỳ user nào
        # OPTIMIZED: Thêm select_related
        if request.user.is_superuser:
            user = User.objects.select_related('employee_detail').get(pk=user_id)
        else:
            user = User.objects.filter(
                pk=user_id,
                groups__name__in=['admin', 'manager', 'cashier', 'waiter']
            ).select_related('employee_detail').distinct().get()
    except User.DoesNotExist:
        return Response(
            {'error': 'User không tồn tại'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'GET':
        # Lấy hoặc tạo mới EmployeeDetail
        detail, created = EmployeeDetail.objects.get_or_create(user=user)
        serializer = EmployeeDetailSerializer(detail)
        return Response(serializer.data)
    
    elif request.method in ['PUT', 'PATCH']:
        # Lấy hoặc tạo mới EmployeeDetail
        detail, created = EmployeeDetail.objects.get_or_create(user=user)
        serializer = EmployeeDetailSerializer(detail, data=request.data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
