# Generated by Django 4.2.6 on 2024-02-27 11:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kcglobed_shop', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='productbuydetails',
            old_name='ProductIds',
            new_name='ProductId',
        ),
    ]