# Generated by Django 5.0.2 on 2025-01-31 06:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0002_inventory_inventorytransaction'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customer',
            options={'ordering': ['customer_code'], 'verbose_name': '得意先', 'verbose_name_plural': '得意先一覧'},
        ),
    ]
