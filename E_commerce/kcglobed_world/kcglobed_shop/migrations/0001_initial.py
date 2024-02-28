# Generated by Django 4.2.6 on 2024-02-27 09:40

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('ProductId', models.AutoField(primary_key=True, serialize=False)),
                ('UserId', models.CharField(max_length=50, null=True)),
                ('ProductName', models.CharField(max_length=500)),
                ('Description', models.CharField(max_length=5000)),
                ('Price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('StockQuantity', models.IntegerField()),
                ('Category', models.CharField(max_length=500)),
                ('CompanyName', models.CharField(max_length=500, null=True)),
                ('ProductImage', models.CharField(max_length=500)),
                ('AddedTime', models.DateTimeField(auto_now_add=True)),
                ('ModifiedTime', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProductBuyDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('TrackingId', models.CharField(max_length=50)),
                ('UserId', models.CharField(max_length=50)),
                ('ProductIds', models.CharField(max_length=200, null=True)),
                ('TotalPrice', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('TotalStockQuantity', models.IntegerField()),
                ('Email', models.CharField(max_length=100)),
                ('PhoneNumber', models.CharField(max_length=50)),
                ('Address', models.CharField(max_length=255)),
                ('State', models.CharField(max_length=100)),
                ('District', models.CharField(max_length=100)),
                ('Pincode', models.CharField(max_length=6)),
                ('ProductTrackingStatus', models.CharField(max_length=255)),
                ('OrderConfirm', models.IntegerField(default=0)),
                ('Otp', models.CharField(max_length=10, null=True)),
                ('BuyProductAddedTime', models.DateTimeField(auto_now_add=True)),
                ('BuyProductModifiedTime', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProductCartDetails',
            fields=[
                ('CartId', models.AutoField(primary_key=True, serialize=False)),
                ('UserId', models.CharField(max_length=50)),
                ('Email', models.CharField(max_length=100)),
                ('PhoneNumber', models.CharField(max_length=100)),
                ('ProductId', models.CharField(max_length=500)),
                ('ProductName', models.CharField(max_length=500)),
                ('Description', models.CharField(max_length=5000)),
                ('TotalPrice', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('TotalStockQuantity', models.IntegerField()),
                ('Category', models.CharField(max_length=500)),
                ('CompanyName', models.CharField(max_length=500, null=True)),
                ('CartProductAddedTime', models.DateTimeField(auto_now_add=True)),
                ('CartProductModifiedTime', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
