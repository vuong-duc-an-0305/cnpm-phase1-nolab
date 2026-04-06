from django.contrib.auth.models import Group, User
from django.contrib.auth import password_validation
from django.core import exceptions
from rest_framework import serializers
from .models import EmployeeDetail


class EmployeeDetailSerializer(serializers.ModelSerializer):
    """Serializer cho thông tin chi tiết nhân viên"""
    
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = EmployeeDetail
        fields = [
            'full_name',
            'avatar',
            'phone_number',
            'citizen_id',
            'gender',
            'date_of_birth',
            'address',
            'emergency_contact_name',
            'emergency_contact_phone',
            'emergency_contact_relationship',
            'hire_date',
            'salary',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['full_name', 'hire_date', 'created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    employee_detail = EmployeeDetailSerializer(required=False, allow_null=True)

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'role',
            'full_name',
            'is_active',
            'is_staff',
            'is_superuser',
            'date_joined',
            'employee_detail',
        )
        read_only_fields = ['id', 'date_joined', 'full_name', 'role']

    def get_role(self, obj: User) -> str:
        # Map group name sang role cho frontend
        if obj.is_superuser:
            return 'admin'
        
        groups = list(obj.groups.values_list('name', flat=True))
        
        if 'admin' in groups:
            return 'admin'
        elif 'manager' in groups:
            return 'manager'
        elif 'cashier' in groups:
            return 'cashier'
        elif 'waiter' in groups:
            return 'waiter'
        else:
            return 'staff'

    def get_full_name(self, obj: User) -> str:
        full_name = obj.get_full_name()
        return full_name or obj.username
    
    def create(self, validated_data):
        """Tạo user mới với employee detail"""
        employee_detail_data = validated_data.pop('employee_detail', None)
        
        # Tạo User
        user = User.objects.create(**validated_data)
        
        # Tạo EmployeeDetail nếu có data
        if employee_detail_data:
            EmployeeDetail.objects.create(user=user, **employee_detail_data)
        
        return user
    
    def update(self, instance, validated_data):
        """Cập nhật user và employee detail"""
        employee_detail_data = validated_data.pop('employee_detail', None)
        
        # Cập nhật User
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Cập nhật hoặc tạo mới EmployeeDetail
        if employee_detail_data is not None:
            if hasattr(instance, 'employee_detail'):
                # Cập nhật
                detail = instance.employee_detail
                for attr, value in employee_detail_data.items():
                    setattr(detail, attr, value)
                detail.save()
            else:
                # Tạo mới
                EmployeeDetail.objects.create(user=instance, **employee_detail_data)
        
        return instance


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, trim_whitespace=False)
    role = serializers.ChoiceField(choices=(
        ('admin', 'admin'),
        ('manager', 'manager'),
        ('cashier', 'cashier'),
        ('waiter', 'waiter')
    ))

    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'first_name', 'last_name', 'role')

    def validate_password(self, value: str) -> str:
        # Tạo user tạm để validate password (chỉ lấy các field của User model)
        user = User(
            username=self.initial_data.get('username', ''),
            email=self.initial_data.get('email', ''),
            first_name=self.initial_data.get('first_name', ''),
            last_name=self.initial_data.get('last_name', '')
        )
        try:
            password_validation.validate_password(value, user)
        except exceptions.ValidationError as exc:
            raise serializers.ValidationError(exc.messages)
        return value

    def create(self, validated_data):
        role = validated_data.pop('role')
        password = validated_data.pop('password')

        # Dùng create_user để tạo user với password đã hash
        user = User.objects.create_user(
            username=validated_data['username'],
            password=password,
            email=validated_data.get('email', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        
        # Set is_staff cho admin và manager
        if role in ['admin', 'manager']:
            user.is_staff = True
            user.save()

        # Thêm user vào group tương ứng
        group, _ = Group.objects.get_or_create(name=role)
        user.groups.add(group)
        
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)
