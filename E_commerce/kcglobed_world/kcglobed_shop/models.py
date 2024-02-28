import random
import string
from django.db import models


class Product(models.Model):
    ProductId = models.AutoField(primary_key=True)
    UserId = models.CharField(max_length=50, null=True)
    ProductName = models.CharField(max_length=500)
    Description = models.CharField(max_length=5000)
    Price = models.DecimalField(max_digits=10, decimal_places=2)
    StockQuantity = models.IntegerField()
    Category = models.CharField(max_length=500)
    CompanyName = models.CharField(max_length=500, null=True)
    # ProductImage = models.ImageField(upload_to='product_images/')
    ProductImage = models.CharField(max_length=500)
    AddedTime = models.DateTimeField(auto_now_add=True)
    ModifiedTime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.ProductName


class ProductCartDetails(models.Model):
    CartId = models.AutoField(primary_key=True)
    UserId = models.CharField(max_length=50)
    Email = models.CharField(max_length=100)
    PhoneNumber = models.CharField(max_length=100)
    ProductId = models.CharField(max_length=500)
    ProductName = models.CharField(max_length=500)
    Description = models.CharField(max_length=5000)
    TotalPrice = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    TotalStockQuantity = models.IntegerField()
    Category = models.CharField(max_length=500)
    CompanyName = models.CharField(max_length=500, null=True)
    CartProductAddedTime = models.DateTimeField(auto_now_add=True)
    CartProductModifiedTime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.ProductName


class ProductBuyDetails(models.Model):
    TrackingId = models.CharField(max_length=50)
    UserId = models.CharField(max_length=50)
    ProductId = models.CharField(max_length=200, null=True)
    TotalPrice = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    TotalStockQuantity = models.IntegerField()
    Email = models.CharField(max_length=100)
    PhoneNumber = models.CharField(max_length=50)
    Address = models.CharField(max_length=255)
    State = models.CharField(max_length=100)
    District = models.CharField(max_length=100)
    Pincode = models.CharField(max_length=6)
    ProductTrackingStatus = models.CharField(max_length=255)
    OrderConfirm = models.IntegerField(default=0)
    Otp = models.CharField(max_length=10, null=True)
    OrderDelivered = models.IntegerField(default=0)
    BuyProductAddedTime = models.DateTimeField(auto_now_add=True)
    BuyProductModifiedTime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.TrackingId
