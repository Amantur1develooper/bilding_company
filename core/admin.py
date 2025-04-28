from django.contrib import admin
admin.site.site_header = "Админ-панель"
# Register your models here.
# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import ConstructionObjectOfWarehouse, CustomUser, HistoryOdWarehouse, Role
from .forms import CustomUserCreationForm, CustomUserChangeForm
# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    # Указываем, какие поля показывать при добавлении пользователя
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )
    
    # Указываем, какие поля показывать при изменении пользователя
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    list_display = ('username', 'email', 'is_staff')
    search_fields = ('username', 'email')
    ordering = ('username',)

admin.site.register(CustomUser, CustomUserAdmin)
# admin.site.register(Role)
from django.contrib import admin
from .models import StorageLocation

@admin.register(StorageLocation)
class StorageLocationAdmin(admin.ModelAdmin):
    list_display = ('material', 'warehouse', 'barcode', 'is_active')
    list_filter = ('warehouse', 'is_active')
    search_fields = ('material', 'barcode', 'description')
# admin.py
from django.contrib import admin
from .models import ConstructionObject, Unit, MaterialRecord
# admin.py
from django.contrib import admin
from .models import ConstructionObject, Unit, MaterialRecord

@admin.register(ConstructionObject)
class ConstructionObjectAdmin(admin.ModelAdmin):
    list_display = ('name', )
    search_fields = ('name',)


admin.site.register(ConstructionObjectOfWarehouse)
@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name')
    
    
admin.site.register(HistoryOdWarehouse)
# admin.py
from django.contrib import admin
from .models import Warehouse, ConstructionObject, Unit,  MaterialRecord

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'address')
# admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import MaterialRecord

@admin.register(MaterialRecord)
class MaterialRecordAdmin(admin.ModelAdmin):
    list_display = ('get_operation_type', 'datetime', 'material', 'quantity_unit', 
                   'price_total', 'location', 'payment_type', 'barcode_short')
    list_filter = ('operation_type', 'payment_type', 'unit', 'construction_object', 'warehouse')
    search_fields = ('material', 'barcode', 'construction_object__name', 'warehouse__name')
    list_select_related = ('unit', 'construction_object', 'warehouse')
    date_hierarchy = 'datetime'
    readonly_fields = ('total',)
    list_per_page = 50
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('operation_type', 'datetime', 'payment_type')
        }),
        ('Локация', {
            'fields': ('construction_object', 'warehouse'),
            'description': 'Укажите либо объект, либо склад'
        }),
        ('Материал', {
            'fields': ('material', 'unit', 'barcode', 'quantity', 'price', 'total')
        }),
        ('Дополнительно', {
            'fields': ('comment',),
            'classes': ('collapse',)
        }),
    )
    
    def get_operation_type(self, obj):
        colors = {
            'income': 'green',
            'outcome': 'red',
            'transfer': 'orange'
        }
        return format_html(
            '<span style="color: {};">{}</span>',
            colors.get(obj.operation_type, 'black'),
            obj.get_operation_type_display()
        )
    get_operation_type.short_description = 'Тип операции'
    get_operation_type.admin_order_field = 'operation_type'
    
    def quantity_unit(self, obj):
        return f"{obj.quantity} {obj.unit.short_name}"
    quantity_unit.short_description = 'Количество'
    quantity_unit.admin_order_field = 'quantity'
    
    def price_total(self, obj):
        return f"{obj.price} / {obj.total}"
    price_total.short_description = 'Цена / Сумма'
    
    def location(self, obj):
        if obj.construction_object:
            return f"Объект: {obj.construction_object.name}"
        elif obj.warehouse:
            return f"Склад: {obj.warehouse.name}"
        return "-"
    location.short_description = 'Локация'
    
    def barcode_short(self, obj):
        if obj.barcode:
            return obj.barcode[:10] + '...' if len(obj.barcode) > 10 else obj.barcode
        return "-"
    barcode_short.short_description = 'Штрих-код'
    
    def save_model(self, request, obj, form, change):
        """Автоматический расчет суммы перед сохранением"""
        obj.total = obj.quantity * obj.price
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('unit', 'construction_object', 'warehouse')