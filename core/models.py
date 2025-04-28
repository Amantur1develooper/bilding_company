from django.db import models

# Create your models here.
# models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class Role(models.Model):
    """
    Модель для ролей пользователей (админ, бухгалтер и т.д.)
    """
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    """
    Кастомная модель пользователя с добавлением ролей
    """
    roles = models.ManyToManyField(Role, blank=True, null=True)
    
    def has_role(self, role_name):
        """
        Проверяет, есть ли у пользователя указанная роль
        """
        return self.roles.filter(name=role_name).exists()
    def is_administrator(self):
        """Проверяет, является ли пользователь администратором"""
        return self.roles.filter(name='администратор').exists()
    
    def is_accountant(self):
        """Проверяет, является ли пользователь бухгалтером"""
        return self.roles.filter(name='бухгалтер').exists()
    
    def get_role_names(self):
        """Возвращает список названий всех ролей пользователя"""
        return list(self.roles.values_list('name', flat=True))
    def is_admin(self):
        """
        Проверяет, является ли пользователь админом
        """
        return self.has_role('admin')
    
    def is_accountant(self):
        """
        Проверяет, является ли пользователь бухгалтером
        """
        return self.has_role('accountant')
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        
        
        

# models.py
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone

class Warehouse(models.Model):
    """Модель склада"""
    name = models.CharField("Название склада", max_length=100)
    address = models.TextField("Адрес склада")
    is_active = models.BooleanField("Активен", default=True)
    
    def __str__(self):
        return self.name
from django.db import models


class ConstructionObjectOfWarehouse(models.Model):
    """Строительный объект склада"""
    name = models.CharField("Название объекта", max_length=100)
    address = models.TextField("Адрес")
   
    
    def __str__(self):
        return f"{self.name}"
    class Meta:
        verbose_name = "Строительный объект склада"
        verbose_name_plural = "Строительный объекты склада"


class StorageLocation(models.Model):
    """
    Модель для хранения местоположений/объектов на складе
    """
    PAYMENT_TYPES = [
        ('cash', 'Наличные'),
        ('card', 'Безналичные'),
      
    ]
    warehouse = models.ForeignKey(
        Warehouse, 
        on_delete=models.CASCADE,
        verbose_name="Склад",
         null=True,
        blank=True,
        related_name='storage_locations'
    )
    name = models.CharField("Название места", blank=True,null=True, max_length=100)
    construction_object = models.ForeignKey("ConstructionObjectOfWarehouse", null=True, blank=True, on_delete=models.SET_NULL, 
                                          verbose_name="Объект")
    payment_type = models.CharField("Способ оплаты", max_length=20, choices=PAYMENT_TYPES)
    material = models.CharField(max_length=200, verbose_name="Материал")
    unit = models.ForeignKey("Unit", on_delete=models.PROTECT, verbose_name="Ед. изм.")
    barcode = models.CharField("Штрих-код", max_length=50, blank=True, null=True)
    description = models.TextField("Описание", blank=True)
    quantity = models.DecimalField("Количество", max_digits=12, decimal_places=3,
                                 validators=[MinValueValidator(0)])
    price = models.DecimalField("Цена", max_digits=12, decimal_places=2,
                              validators=[MinValueValidator(0)])
    total = models.DecimalField("Сумма", max_digits=12, decimal_places=2)
    is_active = models.BooleanField("Активно", default=True)
    comment = models.TextField("Комментарий", blank=True)
    from_Warehouse = models.BooleanField(default=False, blank=True, null=True, verbose_name='это поле из склада?')
    datetime = models.DateTimeField("Дата/время", default=timezone.now)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)

    class Meta:
        verbose_name = "Место хранения"
        verbose_name_plural = "Места хранения"
      

    def __str__(self):
        return f"{self.material} (Склад: {self.warehouse})"
    
class ConstructionObject(models.Model):
    """Строительный объект"""
    name = models.CharField("Название объекта", max_length=100)
    address = models.TextField("Адрес")
   
    
    def __str__(self):
        return f"{self.name}"
    class Meta:
        verbose_name = "Строительный объект"
        verbose_name_plural = "Строительный объекты"

class Unit(models.Model):
    """Единицы измерения"""
    name = models.CharField("Единица измерения", max_length=20, unique=True)
    short_name = models.CharField("Сокращение", max_length=10)
    
    def __str__(self):
        return self.short_name
    
    class Meta:
        verbose_name = "Единица измерений"
        verbose_name_plural = "Единици измерений"


class MaterialRecord(models.Model):
    """Запись о материале с привязкой к объекту"""
    PAYMENT_TYPES = [
        ('cash', 'Наличные'),
        ('card', 'Безналичные'),
      
    ]
    OPERATION_TYPES = [
        ('income', 'Приход'),
        ('outcome', 'Расход'),
        ('transfer', 'Перемещение')
    ]
    
    operation_type = models.CharField("Тип операции", max_length=20, choices=OPERATION_TYPES, default='income')
    datetime = models.DateTimeField("Дата/время", default=timezone.now)
    construction_object = models.ForeignKey(ConstructionObject, null=True, blank=True, on_delete=models.SET_NULL, 
                                          verbose_name="Объект")
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.SET_NULL,
        verbose_name="Склад",
        null=True,
        blank=True
    )
    payment_type = models.CharField("Способ оплаты", max_length=20, choices=PAYMENT_TYPES)
    material = models.CharField(max_length=200, verbose_name="Материал")
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT, verbose_name="Ед. изм.")
    barcode = models.CharField("Штрих-код", max_length=50, blank=True)
    quantity = models.DecimalField("Количество", max_digits=12, decimal_places=3,
                                 validators=[MinValueValidator(0)])
    price = models.DecimalField("Цена", max_digits=12, decimal_places=2,
                              validators=[MinValueValidator(0)])
    total = models.DecimalField("Сумма", max_digits=12, decimal_places=2)
    comment = models.TextField("Комментарий", blank=True)
    from_Warehouse = models.BooleanField(default=False, blank=True, null=True, verbose_name='это поле из склада?')
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)
    is_operations = models.BooleanField(verbose_name='эта операция?', default=False, blank=True, null=True)
    object_is_operations = models.CharField(verbose_name='имя операции',max_length=40, blank=True,null=True)
    class Meta:
        verbose_name = "Запись материала"
        verbose_name_plural = "Записи материалов"
        ordering = ['-datetime']
        
    def save(self, *args, **kwargs):
        """Автоматический расчет суммы при сохранении"""
        self.total = self.quantity * self.price
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.material} - {self.quantity}{self.unit.short_name} на {self.construction_object}"
    

class HistoryOdWarehouse(models.Model):
    """Запись о материале с привязкой к объекту"""
    PAYMENT_TYPES = [
        ('cash', 'Наличные'),
        ('card', 'Безналичные'),
       
    ]
    OPERATION_TYPES = [
        ('income', 'Приход'),
        ('outcome', 'Расход'),
        ('transfer', 'Перемещение')
    ]
    
    operation_type = models.CharField("Тип операции", max_length=20, choices=OPERATION_TYPES, default='income')
    datetime = models.DateTimeField("Дата/время", default=timezone.now)
    construction_object = models.ForeignKey(ConstructionObject, null=True, blank=True, on_delete=models.SET_NULL, 
                                          verbose_name="Объект")
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.SET_NULL,
        verbose_name="Склад",
        null=True,
        blank=True
    )
    payment_type = models.CharField("Способ оплаты", max_length=20, choices=PAYMENT_TYPES)
    material = models.CharField(max_length=200, verbose_name="Материал")
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT, verbose_name="Ед. изм.")
    barcode = models.CharField("Штрих-код", max_length=50, blank=True)
    quantity = models.DecimalField("Количество", max_digits=12, decimal_places=3,
                                 validators=[MinValueValidator(0)])
    price = models.DecimalField("Цена", max_digits=12, decimal_places=2,
                              validators=[MinValueValidator(0)])
    total = models.DecimalField("Сумма", max_digits=12, decimal_places=2)
    comment = models.TextField("Комментарий", blank=True)
    
    
    class Meta:
        verbose_name = "История склада"
        verbose_name_plural = "История склада"
        ordering = ['-datetime']
        
    def save(self, *args, **kwargs):
        """Автоматический расчет суммы при сохранении"""
        self.total = self.quantity * self.price
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.material} - {self.quantity}{self.unit.short_name} на {self.construction_object}"
    
