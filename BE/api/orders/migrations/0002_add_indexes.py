# Generated migration for adding database indexes
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('orders', '0001_initial'),
    ]
    
    operations = [
        # HoaDon already has indexes defined in Meta (OrderDate, Status, CustomerID, EmployeeID)
        # ChiTietDonHang already has indexes defined in Meta (OrderID, ProductID)
        # This is a placeholder migration to maintain consistency
    ]
