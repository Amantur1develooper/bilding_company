# Generated by Django 5.2 on 2025-04-21 17:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_materialrecord_material_delete_material'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='constructionobject',
            options={'verbose_name': 'Строительный объект', 'verbose_name_plural': 'Строительный объекты'},
        ),
        migrations.AlterModelOptions(
            name='unit',
            options={'verbose_name': 'Единица измерений', 'verbose_name_plural': 'Единици измерений'},
        ),
        migrations.RemoveField(
            model_name='constructionobject',
            name='client',
        ),
        migrations.RemoveField(
            model_name='constructionobject',
            name='status',
        ),
        migrations.AlterField(
            model_name='customuser',
            name='roles',
            field=models.ManyToManyField(blank=True, null=True, to='core.role'),
        ),
    ]
