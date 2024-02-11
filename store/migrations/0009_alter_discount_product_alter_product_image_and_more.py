# Generated by Django 5.0.1 on 2024-02-11 18:46

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0008_discount_valid_till_alter_inventory_product_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='discount',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='discount', to='store.product'),
        ),
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='products/images/', validators=[django.core.validators.validate_image_file_extension]),
        ),
        migrations.AlterField(
            model_name='subcategory',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='category', to='store.category'),
        ),
    ]
