from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import ConstructionObject, CustomUser, Role, StorageLocation, Unit

class CustomUserCreationForm(UserCreationForm):
    roles = forms.ModelMultipleChoiceField(
        queryset=Role.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    class Meta:
        model = CustomUser
        fields = (
            'username',
            'email',
            'password1',
            'password2',
            'roles'
        )
        # Если нужны дополнительные поля, добавьте их явно

class CustomUserChangeForm(UserChangeForm):
    roles = forms.ModelMultipleChoiceField(
        queryset=Role.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    class Meta:
        model = CustomUser
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'is_active',
            'is_staff',
            'is_superuser',
            'roles'
        )
        # Добавьте другие поля, которые вам нужны
        
        
# forms.py
from django import forms
from .models import MaterialRecord

class MaterialRecordForm(forms.ModelForm):
    class Meta:
        model = MaterialRecord
        fields = '__all__'
        widgets = {
            'datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['unit'].queryset = Unit.objects.all()
# forms.py
from django import forms
from .models import MaterialRecord


from django import forms
from .models import MaterialRecord, Unit, Warehouse
from django.utils import timezone

class WarehouseMaterialForm(forms.ModelForm):
    class Meta:
        model = MaterialRecord
        fields = ['material', 'unit', 'payment_type', 'quantity', 'price', 'barcode']
        widgets = {
            'material': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название материала',
                'required': True
            }),
            'unit': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'quantity': forms.NumberInput(attrs={
                'step': '0.001',
                'class': 'form-control',
                'placeholder': '0.000',
                'required': True
            }),
            'price': forms.NumberInput(attrs={
                'step': '0.01',
                'class': 'form-control',
                'placeholder': '0.00',
                'required': True
            }),
            'payment_type': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'barcode': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Необязательно'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        warehouse = kwargs.pop('warehouse', None)
        super().__init__(*args, **kwargs)
        self.fields['unit'].queryset = Unit.objects.all()
        
        if warehouse:
            self.instance.warehouse = warehouse
            self.instance.operation_type = 'income'
            self.instance.datetime = timezone.now()
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.total = instance.quantity * instance.price
        if commit:
            instance.save()
        return instance
    
class ObjectMaterialForm(forms.ModelForm):
    class Meta:
        model = MaterialRecord
        fields = ['material', 'unit', 'quantity', 'price', 'payment_type', 'barcode']
        widgets = {
            'material': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название материала'
            }),
            'unit': forms.Select(attrs={
                'class': 'form-select'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'placeholder': '0.000'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'payment_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'barcode': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Необязательно'
            }),
            
        }
    
    def __init__(self, *args, **kwargs):
        construction_object = kwargs.pop('construction_object', None)
        super().__init__(*args, **kwargs)
        self.fields['unit'].queryset = Unit.objects.all()
        
        if construction_object:
            self.instance.construction_object = construction_object
            self.instance.datetime = timezone.now()
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.total = instance.quantity * instance.price
        if commit:
            instance.save()
        return instance
    
class ObjectMaterialFormSklad(forms.ModelForm):
    class Meta:
        model = StorageLocation
        fields = ['material', 'unit', 'quantity', 'price', 'payment_type', 'barcode']
        widgets = {
            'material': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название материала'
            }),
            'unit': forms.Select(attrs={
                'class': 'form-select'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'placeholder': '0.000'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'payment_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'barcode': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Необязательно'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        construction_object = kwargs.pop('construction_object', None)
        super().__init__(*args, **kwargs)
        self.fields['unit'].queryset = Unit.objects.all()
        
        if construction_object:
            self.instance.construction_object = construction_object
            self.instance.datetime = timezone.now()
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.total = instance.quantity * instance.price
        if commit:
            instance.save()
        return instance