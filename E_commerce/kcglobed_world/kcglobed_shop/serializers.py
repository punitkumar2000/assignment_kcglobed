from rest_framework import serializers
from kcglobed_shop.models import Product, ProductCartDetails, ProductBuyDetails


class UsersProductSerializers(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ('ProductId', 'ProductName', 'Description', 'Price', 'StockQuantity', 'Category', 'CompanyName', 'ProductImage')


class UpdateStockSerializers(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ('ProductId',  'StockQuantity')



class ProductSerializers(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ('ProductId', 'UserId', 'ProductName', 'Description', 'Price', 'StockQuantity', 'Category', 'CompanyName', 'ProductImage', 'AddedTime', 'ModifiedTime')


class ProductSerializersPut(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ('ProductId', 'UserId', 'ProductName', 'Description', 'Price', 'StockQuantity', 'Category', 'CompanyName', 'AddedTime', 'ModifiedTime')


class ProductCartSerializers(serializers.ModelSerializer):

    class Meta:
        model = ProductCartDetails
        fields = ('CartId', 'UserId', 'Email', 'PhoneNumber', 'ProductId', 'ProductName', 'Description', 'TotalPrice', 'TotalStockQuantity', 'Category', 'CompanyName', 'CartProductAddedTime', 'CartProductModifiedTime')


class ProductBuySerializers(serializers.ModelSerializer):

    class Meta:
        model = ProductBuyDetails
        fields = ('TrackingId', 'UserId', 'ProductId', 'TotalPrice', 'TotalStockQuantity', 'Email', 'PhoneNumber', 'Address', 'State', 'District', 'Pincode', 'ProductTrackingStatus', 'OrderConfirm', 'Otp', 'BuyProductAddedTime', 'BuyProductModifiedTime')


class TrackAllOrderDetailsSerializers(serializers.ModelSerializer):

    class Meta:
        model = ProductBuyDetails
        fields = ('TrackingId', 'ProductId', 'TotalPrice', 'TotalStockQuantity', 'Email', 'PhoneNumber', 'Address', 'State', 'District', 'Pincode', 'ProductTrackingStatus', 'OrderConfirm', 'OrderDelivered', 'BuyProductAddedTime')


class TrackOrderSerializers(serializers.ModelSerializer):

    class Meta:
        model = ProductBuyDetails
        fields = ('TrackingId', 'ProductId', 'TotalPrice', 'TotalStockQuantity', 'Email', 'PhoneNumber', 'Address', 'State', 'District', 'Pincode', 'ProductTrackingStatus', 'OrderConfirm', 'BuyProductAddedTime')


class OrderStatusUpdateSerializers(serializers.ModelSerializer):

    class Meta:
        model = ProductBuyDetails
        fields = ('TrackingId', 'ProductId', 'TotalPrice', 'TotalStockQuantity', 'Email', 'PhoneNumber', 'Address', 'State', 'District', 'Pincode', 'ProductTrackingStatus', 'OrderConfirm', 'Otp', 'BuyProductAddedTime', 'BuyProductModifiedTime')


