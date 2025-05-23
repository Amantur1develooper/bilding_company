# Generated by Django 5.2 on 2025-04-23 14:31

import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_alter_materialrecord_construction_object'),
    ]

    operations = [
        migrations.AlterField(
            model_name='materialrecord',
            name='payment_type',
            field=models.CharField(choices=[('cash', 'Наличные'), ('card', 'Безналичные')], max_length=20, verbose_name='Способ оплаты'),
        ),
        migrations.CreateModel(
            name='HistoryOdWarehouse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('operation_type', models.CharField(choices=[('income', 'Приход'), ('outcome', 'Расход'), ('transfer', 'Перемещение')], default='income', max_length=20, verbose_name='Тип операции')),
                ('datetime', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Дата/время')),
                ('payment_type', models.CharField(choices=[('cash', 'Наличные'), ('card', 'Безналичные')], max_length=20, verbose_name='Способ оплаты')),
                ('material', models.CharField(max_length=200, verbose_name='Материал')),
                ('barcode', models.CharField(blank=True, max_length=50, verbose_name='Штрих-код')),
                ('quantity', models.DecimalField(decimal_places=3, max_digits=12, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Количество')),
                ('price', models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Цена')),
                ('total', models.DecimalField(decimal_places=2, max_digits=12, verbose_name='Сумма')),
                ('comment', models.TextField(blank=True, verbose_name='Комментарий')),
                ('construction_object', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='core.constructionobject', verbose_name='Объект')),
                ('unit', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.unit', verbose_name='Ед. изм.')),
                ('warehouse', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='core.warehouse', verbose_name='Склад')),
            ],
            options={
                'verbose_name': 'Запись материала',
                'verbose_name_plural': 'Записи материалов',
                'ordering': ['-datetime'],
            },
        ),
    ]
