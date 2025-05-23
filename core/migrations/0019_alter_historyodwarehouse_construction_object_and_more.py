# Generated by Django 5.2 on 2025-04-28 18:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_alter_storagelocation_construction_object'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historyodwarehouse',
            name='construction_object',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.constructionobject', verbose_name='Объект'),
        ),
        migrations.AlterField(
            model_name='historyodwarehouse',
            name='warehouse',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.warehouse', verbose_name='Склад'),
        ),
        migrations.AlterField(
            model_name='materialrecord',
            name='construction_object',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.constructionobject', verbose_name='Объект'),
        ),
        migrations.AlterField(
            model_name='materialrecord',
            name='warehouse',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.warehouse', verbose_name='Склад'),
        ),
        migrations.AlterField(
            model_name='storagelocation',
            name='construction_object',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.constructionobjectofwarehouse', verbose_name='Объект'),
        ),
    ]
