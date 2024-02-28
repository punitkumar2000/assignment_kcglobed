import uuid
import logging
import traceback
from decimal import Decimal
from django.db.models import Sum
from rest_framework.parsers import JSONParser
from django.forms.models import model_to_dict
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.uploadedfile import InMemoryUploadedFile

from kcglobed_shop.helpers.my_sql_connector import my_sql_execute_query
from kcglobed_shop.authorizer.authorizer import token_required, validate_token_time
from kcglobed_shop.models import Product, ProductCartDetails, ProductBuyDetails
from kcglobed_shop.serializers import UsersProductSerializers, UpdateStockSerializers, ProductSerializers, ProductSerializersPut, ProductCartSerializers, ProductBuySerializers, TrackAllOrderDetailsSerializers, TrackOrderSerializers, OrderStatusUpdateSerializers
from kcglobed_shop.helpers.utils import check_email_validation, generate_api_key, generate_bearer_token, is_valid_image, validate_phonenumber, states, email_sender, upload_to_s3, get_presigned_url, delete_objects_from_bucket, params_validator


@csrf_exempt
def admins_api(request):
    if request.method == 'POST':
        try:
            data = JSONParser().parse(request)
            email = data.get('Email', None)
            secret_password = data.get('SecretPassword', None)

            if not email:
                return JsonResponse({"message": "Email is required."}, status=400, safe=False)

            if not secret_password:
                return JsonResponse({"message": "SecretPassword is required."}, status=400, safe=False)

            if secret_password != "Admin@kcglobed":
                return JsonResponse({"message": "Incorrect SecretPassword."}, status=400, safe=False)

            email_valid = check_email_validation(email)
            if not email_valid:
                return JsonResponse({"message": "Invalid Email Format."}, status=400, safe=False)

            query = f"select * from kcglobed_admins where Email='{email}';"
            results, status_code = my_sql_execute_query(query)
            if status_code == 500:
                return JsonResponse({"message": "Internal Server Error."}, status=500, safe=False)
            if status_code == 200 and results:
                return JsonResponse({"message": "Email Already Exists."}, status=400, safe=False)

            query2 = f"insert into kcglobed_admins (Email, Created_At) VALUES ('{email}', NOW());"
            results, status_code = my_sql_execute_query(query2)
            if status_code == 500:
                return JsonResponse({"message": "Error in Inserting Data into Database."}, status=500, safe=False)

            return JsonResponse({"message": f"Admin Added into Database Successfully"}, status=200, safe=False)

        except Exception as e:
            error_message = e.__str__()
            logging.error(error_message)
            traceback.print_exc()
        return JsonResponse({"message": f"Exception Raised in Adding Admin"}, status=500, safe=False)


@csrf_exempt
def signupapi(request):
    if request.method == 'POST':
        try:
            data = JSONParser().parse(request)
            email = data.get('Email', None)
            phone_number = data.get('PhoneNumber', None)
            password = data.get('Password', None)
            confirm_password = data.get('ConfirmPassword', None)
            user_name = data.get('UserName', None)
            is_admin = 0

            if not email:
                return JsonResponse({"message": "Email is required."}, status=400, safe=False)
            if not phone_number:
                return JsonResponse({"message": "PhoneNumber is required."}, status=400, safe=False)
            if not password:
                return JsonResponse({"message": "Password is required."}, status=400, safe=False)
            if not confirm_password:
                return JsonResponse({"message": "ConfirmPassword is required."}, status=400, safe=False)
            if password != confirm_password:
                return JsonResponse({"message": "Password and ConfirmPasswords should be same."}, status=400, safe=False)
            if not user_name:
                return JsonResponse({"message": "UserName is required."}, status=400, safe=False)

            email_valid = check_email_validation(email)
            if not email_valid:
                return JsonResponse({"message": "Invalid Email Format."}, status=400, safe=False)

            is_valid, message = validate_phonenumber(phone_number)
            if not is_valid:
                return JsonResponse({"message": message}, status=400, safe=False)

            query = f"select * from user_accounts_table where Email='{email}';"
            results, status_code = my_sql_execute_query(query)
            if status_code == 500:
                return JsonResponse({"message": "Internal Server Error."}, status=500, safe=False)
            if status_code == 200:
                email_exists = any(item[1] == email for item in results)
                if email_exists:
                    return JsonResponse({"message": "Email Already Exists."}, status=400, safe=False)

            query = f"select * from kcglobed_admins where Email='{email}';"
            results, status_code = my_sql_execute_query(query)
            if status_code == 500:
                return JsonResponse({"message": "Internal Server Error."}, status=500, safe=False)
            if status_code == 200 and results:
                is_admin = 1

            result = generate_api_key()
            if result.get("status_code") == 500:
                return JsonResponse({"message": result.get("message")}, status=500, safe=False)
            x_api_key = result.get("SecretKey")

            query2 = f"insert into user_accounts_table (Email, PhoneNumber, UserName, Password, CreatedAt, XApiKey, IsAdmin) VALUES ('{email}', '{phone_number}', '{user_name}', '{password}', NOW(), '{x_api_key}', '{is_admin}');"
            results, status_code = my_sql_execute_query(query2)
            if status_code == 500:
                return JsonResponse({"message": "Error in Inserting Data into Database."}, status=500, safe=False)

            return JsonResponse({"message": f"User with Email {email} Signed Up Successfully x-api-key: {x_api_key}."}, status=200, safe=False)

        except Exception as e:
            error_message = e.__str__()
            logging.error(error_message)
            traceback.print_exc()
        return JsonResponse({"message": f"Exception Raised in Signing up"}, status=500, safe=False)


@csrf_exempt
def loginapi(request):
    if request.method == 'POST':
        try:
            data = JSONParser().parse(request)
            email = data.get('Email', None)
            password = data.get('Password', None)
            if not email:
                return JsonResponse({"message": "Email is required."}, status=400, safe=False)
            if not password:
                return JsonResponse({"message": "Password is required."}, status=400, safe=False)

            email_valid = check_email_validation(email)
            if not email_valid:
                return JsonResponse({"message": "Invalid Email Format."}, status=400, safe=False)

            query = f"select * from user_accounts_table where Email='{email}';"
            results, status_code = my_sql_execute_query(query)
            if status_code == 500:
                return JsonResponse({"message": "Internal Server Error."}, status=500, safe=False)
            if status_code == 200:
                email_exists = any(item[1] == email for item in results)
                password_exists = any(item[4] == password for item in results)
                if not email_exists:
                    return JsonResponse({"message": "Invalid Email."}, status=400, safe=False)
                if not password_exists:
                    return JsonResponse({"message": "Invalid Password."}, status=400, safe=False)

            token = generate_bearer_token(results)
            if token.get("status_code") == 500:
                return JsonResponse({"message": token.get("message")}, status=500, safe=False)
            bearer_token = token.get("Token", "")
            x_api_key = token.get("XApiKey", "")

            query2 = f"UPDATE user_accounts_table SET AccessToken='{bearer_token}', LastLogin=NOW() where Email = '{email}'"
            results, status_code = my_sql_execute_query(query2)
            if status_code == 200:
                return JsonResponse({"message": "Login Successfully.", "Authorization": bearer_token, "x-api-key": x_api_key}, status=200, safe=False)
            return JsonResponse({"message": "Internal Server Error."}, status=500, safe=False)

        except Exception as e:
            error_message = e.__str__()
            logging.error(error_message)
            traceback.print_exc()
        return JsonResponse({"message": "Exception Raised in Loging in"}, status=500, safe=False)


@csrf_exempt
@token_required
def logoutapi(request):
    if request.method == 'POST':
        try:
            user_id = request.user.get("UserId", None)
            data = JSONParser().parse(request)
            email = data.get('Email', None)
            if not email:
                return JsonResponse({"message": "Email is required to Logout."}, status=400, safe=False)

            email_valid = check_email_validation(email)
            if not email_valid:
                return JsonResponse({"message": "Invalid Email Format."}, status=400, safe=False)

            query = f"select * from user_accounts_table where id='{user_id}' and Email='{email}';"
            results, status_code = my_sql_execute_query(query)
            if status_code == 500 or not results:
                return JsonResponse({"message": "Internal Server Error."}, status=500, safe=False)

            query2 = f"UPDATE user_accounts_table SET AccessToken='' where Email = '{email}' and id='{user_id}'"
            results, status_code = my_sql_execute_query(query2)
            if status_code == 200:
                return JsonResponse({"message": "Logout Successfully."}, status=200, safe=False)
            return JsonResponse({"message": "Internal Server Error."}, status=500, safe=False)

        except Exception as e:
            error_message = e.__str__()
            logging.error(error_message)
            traceback.print_exc()
        return JsonResponse({"message": "Exception Raised in Loging in"}, status=500, safe=False)


@csrf_exempt
@token_required
def productsApi_admin(request):
    if request.method == 'POST':
        try:
            user_id = request.user.get("UserId", None)
            is_admin = request.user.get("IsAdmin", "0")

            if is_admin == "0":
                return JsonResponse({"message": "Only Admins are Allowed."}, status=401, safe=False)

            product_data = {}
            product_data['UserId'] = user_id
            product_data['ProductName'] = request.POST.get('ProductName', None)
            product_data['Description'] = request.POST.get('Description', None)
            product_data['Price'] = request.POST.get('Price', None)
            product_data['StockQuantity'] = request.POST.get('StockQuantity', None)
            product_data['Category'] = request.POST.get('Category', None)
            product_data['CompanyName'] = request.POST.get('CompanyName', None)
            product_image = request.FILES.get('ProductImage', None)

            if not product_data['ProductName']:
                return JsonResponse({"message": "ProductName is required."}, status=400, safe=False)
            if not product_data['Description']:
                return JsonResponse({"message": "Description is required."}, status=400, safe=False)
            if not product_data['Price']:
                return JsonResponse({"message": "Price is required."}, status=400, safe=False)
            if not product_data['StockQuantity']:
                return JsonResponse({"message": "StockQuantity is required."}, status=400, safe=False)
            if not product_data['StockQuantity'].isdigit():
                return JsonResponse({"message": "StockQuantity should be an integer."}, status=400, safe=False)
            if not product_data['Category']:
                return JsonResponse({"message": "Category is required."}, status=400, safe=False)
            if not product_data['CompanyName']:
                return JsonResponse({"message": "CompanyName is required."}, status=400, safe=False)
            if not product_image or not isinstance(product_image, InMemoryUploadedFile):
                return JsonResponse({"message": "ProductImage is required."}, status=400, safe=False)
            if not is_valid_image(product_image):
                return JsonResponse({"message": "Invalid image format. Only JPEG/  JPG or PNG allowed."}, status=400, safe=False)

            product_data['ProductImage'] = product_image

            product_exists = Product.objects.filter(ProductName=product_data['ProductName'], UserId=user_id)
            if product_exists:
                return JsonResponse({"message": "Product Name Already Exists"}, status=400, safe=False)

            s3_file_key = f"products_images" + "_" + f"{product_image}"
            if not upload_to_s3(product_image, 'ecommercemyshopindia', s3_file_key):
                return JsonResponse({"message": "Failed to upload image to S3."}, status=500, safe=False)

            product_data['ProductImage'] = s3_file_key

            product_serializers = ProductSerializers(data=product_data)
            if product_serializers.is_valid():
                product_serializers.save()
                return JsonResponse({"message": "Added Successfully"}, status=200, safe=False)

            errors = product_serializers.errors
            return JsonResponse({"message": "Failed to Add", "errors": errors}, status=500, safe=False)

        except Exception as e:
            error_message = e.__str__()
            logging.error(error_message)
            traceback.print_exc()
        return JsonResponse({"message": "Exception Raised in Adding"}, status=500, safe=False)

    if request.method == 'GET':
        try:
            products = Product.objects.all()
            if not products:
                return JsonResponse({"message": "Data not Found"}, status=400, safe=False)

            products_serializers = UsersProductSerializers(products, many=True)
            serialized_data = products_serializers.data
            products_by_category = {}

            for data in serialized_data:
                s3_file_key = data["ProductImage"]
                image_url = get_presigned_url('ecommercemyshopindia', s3_file_key)
                if not image_url["status_code"] == 200:
                    return JsonResponse({"data": image_url["message"]}, status=400, safe=False)
                data["ProductImage"] = image_url["image_url"]

                category = data["Category"]
                if category not in products_by_category:
                    products_by_category[category] = []

                products_by_category[category].append(data)
            print("products_by_category", products_by_category)
            return JsonResponse({"data": products_by_category}, status=200, safe=False)

        except Exception as e:
            error_message = e.__str__()
            logging.error(error_message)
            traceback.print_exc()
            return JsonResponse({"message": "Exception Raised in Fetching All Products"}, status=500, safe=False)

    if request.method == "PUT":
        try:
            user_id = request.user.get("UserId", None)
            is_admin = request.user.get("IsAdmin", "0")
            if is_admin == "0":
                return JsonResponse({"message": "Only Admins are Allowed."}, status=401, safe=False)

            update_product_data = JSONParser().parse(request)
            product_data = {}
            product_data['ProductId'] = update_product_data.get('ProductId', None)
            product_data['ProductName'] = update_product_data.get('ProductName', None)
            product_data['Description'] = update_product_data.get('Description', None)
            product_data['Price'] = update_product_data.get('Price', None)
            product_data['StockQuantity'] = update_product_data.get('StockQuantity', None)
            product_data['Category'] = update_product_data.get('Category', None)
            product_data['CompanyName'] = update_product_data.get('CompanyName', None)

            if not product_data['ProductId']:
                return JsonResponse({"message": "ProductId is required."}, status=400, safe=False)
            if not product_data['ProductId'].isdigit():
                return JsonResponse({"message": "ProductId should be integer."}, status=400, safe=False)
            if not product_data['ProductName']:
                return JsonResponse({"message": "ProductName is required."}, status=400, safe=False)
            if not product_data['Description']:
                return JsonResponse({"message": "Description is required."}, status=400, safe=False)
            if not product_data['Price']:
                return JsonResponse({"message": "Price is required."}, status=400, safe=False)
            if not isinstance(product_data['Price'], float):
                return JsonResponse({"message": "Price should be in decimal i.e 200.00."}, status=400, safe=False)
            if not product_data['StockQuantity']:
                return JsonResponse({"message": "StockQuantity is required."}, status=400, safe=False)
            if not product_data['StockQuantity'].isdigit():
                return JsonResponse({"message": "StockQuantity should be an integer."}, status=400, safe=False)
            if not product_data['Category']:
                return JsonResponse({"message": "Category is required."}, status=400, safe=False)
            if not product_data['CompanyName']:
                return JsonResponse({"message": "Company is required."}, status=400, safe=False)

            if product_data['ProductId']:
                try:
                    existing_product = Product.objects.get(ProductId=product_data['ProductId'], UserId=user_id)
                    if existing_product.ProductName != product_data['ProductName']:
                        product_exists = Product.objects.filter(ProductName=product_data['ProductName']).exists()
                        if product_exists:
                            return JsonResponse({"message": "Product Name Already Exists"}, status=400, safe=False)
                except Product.DoesNotExist:
                    return JsonResponse({"message": "Product Not Found with the provided ProductId."}, status=400, safe=False)

                product_serializers = ProductSerializersPut(instance=existing_product, data=update_product_data)

                if product_serializers.is_valid():
                    product_serializers.save()
                    return JsonResponse({"message": "Updated Successfully"}, status=200, safe=False)

                errors = product_serializers.errors
                return JsonResponse({"message": "Failed to Add", "errors": errors}, status=500, safe=False)

        except Exception as e:
            error_message = e.__str__()
            logging.error(error_message)
            traceback.print_exc()
        return JsonResponse({"message": "Exception Raised in Updating"}, status=500, safe=False)

    if request.method == 'DELETE':
        try:
            user_id = request.user.get("UserId", None)
            is_admin = request.user.get("IsAdmin", "0")
            if is_admin == "0":
                return JsonResponse({"message": "Only Admins are Allowed."}, status=401, safe=False)

            product_data = JSONParser().parse(request)
            product_id = product_data.get('ProductId', None)
            if not product_id:
                return JsonResponse({"message": "ProductId is required."}, status=400, safe=False)
            if not product_data['ProductId'].isdigit():
                return JsonResponse({"message": "ProductId should be integer."}, status=400, safe=False)
            try:
                product = Product.objects.get(ProductId=product_id, UserId=user_id)
                s3_file_key = product_image = product.ProductImage
                if Product.objects.filter(ProductImage=product_image).count() < 2:
                    product_delete = delete_objects_from_bucket('ecommercemyshopindia', s3_file_key)
                    if product_delete["status_code"] == 200:
                        product.delete()
                        return JsonResponse({"message": "Delete Successfully"}, status=200, safe=False)
                else:
                    product.delete()
                    return JsonResponse({"message": "Delete Successfully"}, status=200, safe=False)

            except Product.DoesNotExist:
                return JsonResponse({"message": "Product Not Found."}, status=400, safe=False)

        except Exception as e:
            error_message = e.__str__()
            logging.error(error_message)
            traceback.print_exc()
        return JsonResponse({"message": "Exception Raised in Deleting"}, status=500, safe=False)

    return JsonResponse({"message": "Invalid request method"}, status=500, safe=False)


@csrf_exempt
@token_required
def searchApi(request):
    if request.method == 'GET':
        try:
            user_data = JSONParser().parse(request)
            product_name = user_data.get('ProductName', None)
            price = user_data.get('Price', None)
            category = user_data.get('Category', None)
            company_name = user_data.get('CompanyName', None)

            item_to_search = {}
            if product_name:
                item_to_search['ProductName__icontains'] = product_name

            if price:
                item_to_search['Price__lte'] = price

            if category:
                item_to_search['Category__icontains'] = category

            if company_name:
                item_to_search['CompanyName__icontains'] = company_name

            if not item_to_search:
                return JsonResponse({"message": "No search criteria provided"}, status=400)

            results = Product.objects.filter(**item_to_search)

            if not results:
                return JsonResponse({"message": "No results found for the provided search criteria"}, status=400)
            products_by_category = {}
            for product in results:
                category = product.Category
                product_dict = model_to_dict(product)  # Convert Product object to dictionary
                if category not in products_by_category:
                    products_by_category[category] = []

                products_by_category[category].append(product_dict)
            return JsonResponse({"message": "Search successful", "results": products_by_category})

        except Exception as e:
            return JsonResponse({"message": "Error occurred during search", "error": str(e)}, status=500)


@csrf_exempt
@token_required
def cartApi(request):

    if request.method == 'POST':
        try:
            EXISTS_IN_CART = False
            user_id = request.user.get("UserId")

            cart_data = JSONParser().parse(request)
            product_cart_data = {}

            product_cart_data['ProductId'] = cart_data.get('ProductId', None)
            product_cart_data['TotalStockQuantity'] = cart_data.get('TotalStockQuantity', None)

            if not product_cart_data['ProductId']:
                return JsonResponse({"message": "ProductId is required."}, status=400, safe=False)
            if not product_cart_data['TotalStockQuantity']:
                return JsonResponse({"message": "TotalStockQuantity is required."}, status=400, safe=False)
            if not product_cart_data['TotalStockQuantity'].isdigit():
                return JsonResponse({"message": "TotalStockQuantity should be an integer."}, status=400, safe=False)

            try:
                product_exists = Product.objects.get(ProductId=product_cart_data['ProductId'])
                if product_exists:
                    stock_quantity = product_exists.StockQuantity
                    price = product_exists.Price
                    product_name = product_exists.ProductName
                    description = product_exists.Description
                    category = product_exists.Category
                    company_name = product_exists.CompanyName

            except Product.DoesNotExist:
                return JsonResponse({"message": "Product Not Found with the provided ProductId."}, status=400, safe=False)

            try:
                product_exists_in_cart = ProductCartDetails.objects.get(ProductId=product_cart_data['ProductId'],
                                                                       UserId=user_id)
                if product_exists_in_cart:
                    EXISTS_IN_CART = True
                    total_stock_quantity = product_exists_in_cart.TotalStockQuantity
                    final_total_quantity = int(product_cart_data['TotalStockQuantity']) + total_stock_quantity

                    if stock_quantity < final_total_quantity:
                        return JsonResponse({"message": f"Your Product TotalStockQuantity is {final_total_quantity} but we have only {stock_quantity}."}, status=400, safe=False)

                    product_cart_data['TotalStockQuantity'] = final_total_quantity
                    product_cart_data['TotalPrice'] = Decimal(final_total_quantity) * price

            except ProductCartDetails.DoesNotExist:

                if stock_quantity < int(product_cart_data['TotalStockQuantity']):
                    return JsonResponse({"message": f"Your Product TotalStockQuantity is {product_cart_data['TotalStockQuantity']} but we have only {stock_quantity}."},
                                        status=400, safe=False)

                product_cart_data['ProductId'] = cart_data.get('ProductId', None)
                product_cart_data['TotalStockQuantity'] = cart_data.get('TotalStockQuantity', None)
                product_cart_data['TotalPrice'] = Decimal(product_cart_data['TotalStockQuantity']) * price

            query = f"select * from user_accounts_table where id='{user_id}';"
            results, status_code = my_sql_execute_query(query)
            if status_code == 500:
                return JsonResponse({"message": "Internal Server Error."}, status=500, safe=False)
            if status_code == 200 and results:
                email = results[0][1]
                phone_number = results[0][2]

            product_cart_data['UserId'] = user_id
            product_cart_data['Email'] = email
            product_cart_data['PhoneNumber'] = phone_number

            product_cart_data['ProductName'] = product_name
            product_cart_data['Description'] = description
            product_cart_data['Category'] = category
            product_cart_data['CompanyName'] = company_name

            if not product_cart_data['Email']:
                return JsonResponse({"message": "Your Email not Found."}, status=400, safe=False)
            if not product_cart_data['PhoneNumber']:
                return JsonResponse({"message": "Your PhoneNumber not Found."}, status=400, safe=False)

            if EXISTS_IN_CART:
                product_cart_serializers = ProductCartSerializers(instance=product_exists_in_cart, data=product_cart_data)
                if product_cart_serializers.is_valid():
                    product_cart_serializers.save()
                    return JsonResponse({"message": "Product Added to Cart Successfully"}, status=200, safe=False)

                errors = product_cart_serializers.errors
                return JsonResponse({"message": "Failed to Add", "errors": errors}, status=500, safe=False)

            else:
                product_cart_serializers = ProductCartSerializers(data=product_cart_data)
                if product_cart_serializers.is_valid():
                    product_cart_serializers.save()
                    return JsonResponse({"message": "Product Added to Cart Successfully"}, status=200, safe=False)

                errors = product_cart_serializers.errors
                return JsonResponse({"message": "Failed to Add Product to Cart", "errors": errors}, status=500, safe=False)

        except Exception as e:
            error_message = e.__str__()
            logging.error(error_message)
            traceback.print_exc()
        return JsonResponse({"message": "Exception Raised in Adding Product to Cart"}, status=500, safe=False)

    if request.method == 'GET':
        try:
            user_id = request.user.get("UserId", None)
            try:
                cart_items = ProductCartDetails.objects.filter(UserId=user_id)

                # Check if the cart is empty
                if not cart_items:
                    return JsonResponse({"message": "Your cart is empty! Add items to it now."}, status=400, safe=False)

                cart_summary = cart_items.aggregate(TotalPrice=Sum('TotalPrice'), TotalStockQuantity=Sum('TotalStockQuantity'))
                # Serialize the data
                summary_data = {
                    "TotalPrice": cart_summary['TotalPrice'],
                    "TotalStockQuantity": cart_summary['TotalStockQuantity'],
                    "Cart_Items": ProductCartSerializers(cart_items, many=True).data
                }

                return JsonResponse(summary_data, status=200, safe=False)
            except ProductCartDetails.DoesNotExist:
                return JsonResponse({"message": "Your cart is empty! Add items to it now."}, status=400, safe=False)

        except Exception as e:
            error_message = e.__str__()
            logging.error(error_message)
            traceback.print_exc()
        return JsonResponse({"message": "Exception Raised in Fetching"}, status=200, safe=False)


    if request.method == 'PUT':
        try:
            user_id = request.user.get("UserId")
            cart_data = JSONParser().parse(request)
            product_cart_data = {}

            product_cart_data['ProductId'] = cart_data.get('ProductId', None)
            product_cart_data['TotalStockQuantity'] = cart_data.get('TotalStockQuantity', None)

            if not product_cart_data['ProductId']:
                return JsonResponse({"message": "ProductId is required."}, status=400, safe=False)
            if not product_cart_data['TotalStockQuantity']:
                return JsonResponse({"message": "TotalStockQuantity is required."}, status=400, safe=False)
            if not product_cart_data['TotalStockQuantity'].isdigit():
                return JsonResponse({"message": "TotalStockQuantity should be an integer."}, status=400, safe=False)

            try:
                product_exists = Product.objects.get(ProductId=product_cart_data['ProductId'])
                if product_exists:
                    stock_quantity = product_exists.StockQuantity
                    price = product_exists.Price
                    product_name = product_exists.ProductName
                    description = product_exists.Description
                    category = product_exists.Category
                    company_name = product_exists.CompanyName

            except Product.DoesNotExist:
                return JsonResponse({"message": "Product Not Found with the provided ProductId."}, status=400,
                                    safe=False)

            if product_cart_data['TotalStockQuantity'] == "0":
                try:
                    product_cart = ProductCartDetails.objects.filter(ProductId=product_cart_data['ProductId'], UserId=user_id)
                    if product_cart:
                        product_cart.delete()
                        return JsonResponse({"message": "Your Product is now Removed from the Cart"}, status=200, safe=False)
                    if not product_cart:
                        product_cart.delete()
                        return JsonResponse(
                            {"message": "Invalid ProductId or Unable to Remove the Product from the Cart."}, status=400,
                            safe=False)

                except ProductCartDetails.DoesNotExist:
                    return JsonResponse({"message": "Invalid ProductId or Unable to Remove the Product from the Cart."}, status=400, safe=False)

            try:
                product_exists_in_cart = ProductCartDetails.objects.get(ProductId=product_cart_data['ProductId'], UserId=user_id)
                if product_exists_in_cart:
                    if stock_quantity < int(product_cart_data['TotalStockQuantity']):
                        return JsonResponse({"message": f"Your Product TotalStockQuantity is {product_cart_data['TotalStockQuantity']} but we have only {quantity}."}, status=400, safe=False)

                    product_cart_data['TotalPrice'] = Decimal(product_cart_data['TotalStockQuantity']) * price

            except ProductCartDetails.DoesNotExist:
                return JsonResponse({"message": "Product Not Found in Your Cart Please Add this Product First."}, status=400, safe=False)

            query = f"select * from user_accounts_table where id='{user_id}';"
            results, status_code = my_sql_execute_query(query)
            if status_code == 500:
                return JsonResponse({"message": "Internal Server Error."}, status=500, safe=False)
            if status_code == 200 and results:
                email = results[0][1]
                phone_number = results[0][2]

            product_cart_data['UserId'] = user_id
            product_cart_data['Email'] = email
            product_cart_data['PhoneNumber'] = phone_number

            product_cart_data['ProductName'] = product_name
            product_cart_data['Description'] = description
            product_cart_data['Category'] = category
            product_cart_data['CompanyName'] = company_name

            if not product_cart_data['Email']:
                return JsonResponse({"message": "Your Email not Found."}, status=400, safe=False)
            if not product_cart_data['PhoneNumber']:
                return JsonResponse({"message": "Your PhoneNumber not Found."}, status=400, safe=False)

            product_cart_serializers = ProductCartSerializers(instance=product_exists_in_cart,
                                                              data=product_cart_data)
            if product_cart_serializers.is_valid():
                product_cart_serializers.save()
                return JsonResponse({"message": "Product Updated to Cart Successfully"}, status=200, safe=False)

            errors = product_cart_serializers.errors
            return JsonResponse({"message": "Failed to Update", "errors": errors}, status=500, safe=False)

        except Exception as e:
            error_message = e.__str__()
            logging.error(error_message)
            traceback.print_exc()
        return JsonResponse({"message": "Exception Raised in Updating Product to Cart"}, status=500, safe=False)

    if request.method == 'DELETE':
        try:
            user_id = request.user.get("UserId", None)
            product_cart = ProductCartDetails.objects.filter(UserId=user_id)
            if product_cart.exists():
                product_cart.delete()
                return JsonResponse({"message": "Your Cart is Empty Now!"}, status=200, safe=False)
            else:
                return JsonResponse({"message": "You Don't Nothing in Your Cart."}, status=400, safe=False)

        except Exception as e:
            error_message = e.__str__()
            logging.error(error_message)
            traceback.print_exc()
        return JsonResponse({"message": "Exception Raised in Empty Your Cart"}, status=500, safe=False)

    return JsonResponse({"message": "Invalid request method"}, status=500, safe=False)


@csrf_exempt
@token_required
def buyorderApi(request):
    if request.method == 'POST':
        try:
            user_id = request.user.get("UserId")

            cart_data = JSONParser().parse(request)
            product_buy_data = {}
            product_id_check = {}

            product_buy_data['ProductId'] = cart_data.get('ProductId', None)
            product_buy_data['UserId'] = user_id
            product_buy_data['TrackingId'] = str(uuid.uuid4())[:8]
            product_buy_data['Address'] = cart_data.get('Address', None)
            product_buy_data['State'] = cart_data.get('State', None)
            product_buy_data['District'] = cart_data.get('District', None)
            product_buy_data['Pincode'] = cart_data.get('Pincode', None)
            product_buy_data['OrderConfirm'] = 0
            product_buy_data['ProductTrackingStatus'] = "Your Order is Not Verified Yet Please Verify it."

            product_id_check['ProductId'] = cart_data.get('ProductId', None)
            if not product_id_check['ProductId']:
                return JsonResponse({"message": "ProductId is required."}, status=400, safe=False)

            if not product_buy_data['Address']:
                return JsonResponse({"message": "Your Address is Required."}, status=400, safe=False)
            if len(product_buy_data['Address']) > 1000:
                return JsonResponse({"message": "Your Address is Too Long."}, status=400, safe=False)

            if not product_buy_data['State']:
                return JsonResponse({"message": "Your State is Required."}, status=400, safe=False)
            if product_buy_data['State'].lower() not in states:
                return JsonResponse({"message": f"The state name should only be from India States:{states}."}, status=400, safe=False)
            if not product_buy_data['District']:
                return JsonResponse({"message": "Your District is Required."}, status=400, safe=False)
            if len(product_buy_data['District']) > 200:
                return JsonResponse({"message": "Your District is Too Long."}, status=400, safe=False)

            if not product_buy_data['Pincode']:
                return JsonResponse({"message": "Your Pincode is Required."}, status=400, safe=False)
            if not product_buy_data['Pincode'].isdigit():
                return JsonResponse({"message": "Pincode should be an integer."}, status=400, safe=False)

            if len(product_buy_data['Pincode']) != 6:
                return JsonResponse({"message": "Invalid! Pincode."}, status=400, safe=False)

            try:
                total_price = 0
                total_stock_quantity = 0

                product_id_exists_in_cart = ProductCartDetails.objects.filter(ProductId=product_id_check['ProductId'], UserId=user_id).first()
                if product_id_exists_in_cart:
                    total_price += product_id_exists_in_cart.TotalPrice
                    total_stock_quantity += product_id_exists_in_cart.TotalStockQuantity
                    email = product_id_exists_in_cart.Email
                    phone_number = product_id_exists_in_cart.PhoneNumber
                else:
                    return JsonResponse({"message": f"Product ID {product_id_check['ProductId']} not Found in Your Cart."}, status=400, safe=False)

                product_instance = Product.objects.filter(ProductId=product_id_check['ProductId'],
                                                          UserId=user_id).first()
                if product_instance:
                    total_stock_present = product_instance.StockQuantity
                    if total_stock_present < total_stock_quantity:
                        return JsonResponse({"message": f"We currently have {total_stock_present} units in stock. Please adjust the stock quantity accordingly."}, status=400, safe=False)

                    product_instance.StockQuantity -= total_stock_quantity

                # To Check that the user is again Ordering the same order before the Order Confirmation
                product_order_confirm_id = ProductBuyDetails.objects.filter(ProductId=product_buy_data['ProductId'], UserId=user_id)
                if product_order_confirm_id.exists():
                    return JsonResponse({"message": "The Product is Already Ordered Once. After you Verify with an OTP, You can Order this Product Again."}, status=400, safe=False)

            except ProductCartDetails.DoesNotExist:
                return JsonResponse({"message": "Product Not Found in Your Cart."}, status=400, safe=False)

            otp = str(uuid.uuid4())[:6]

            product_buy_data['TotalPrice'] = total_price
            product_buy_data['TotalStockQuantity'] = total_stock_quantity
            product_buy_data['Email'] = email
            product_buy_data['PhoneNumber'] = phone_number
            product_buy_data['Otp'] = otp

            # To Add those products which is now finally ordered
            product_buy_serializers = ProductBuySerializers(data=product_buy_data)
            email_sent = None  # Initialize the email_sent variable

            if product_buy_serializers.is_valid():
                product_buy_serializers.save()
                # Attempt to send an email
                try:
                    email_sent = email_sender(email=product_buy_data['Email'], otp=product_buy_data['Otp'], tracking_id=product_buy_data['TrackingId'])
                    # If email is sent successfully
                    if email_sent["status_code"] == 200:
                        if product_instance:
                            product_instance.save()
                            product_id_exists_in_cart.delete()
                            return JsonResponse({"message": f"An Email has been Sent to {product_buy_data['Email']}. Please Confirm Your Order by Verifying the OTP. Your TrackingId is {product_buy_data['TrackingId']}"}, status=200, safe=False)

                    else:
                        # If OrderConfirm saving fails, delete ProductBuy
                        if hasattr(product_buy_serializers, 'instance') and product_buy_serializers.instance:
                            product_buy_serializers.instance.delete()
                        error = product_buy_serializers.errors
                        return JsonResponse({"message": f"Failed to Sent the Email to {product_buy_data['Email']}", "errors": error}, status=500, safe=False)

                except Exception as e:
                    # Handle any unexpected exception
                    if hasattr(product_buy_serializers, 'instance') and product_buy_serializers.instance:
                        product_buy_serializers.instance.delete()

                    errors = product_buy_serializers.errors
                    return JsonResponse({"message": "Failed to Order the Product from Cart1", "errors": errors}, status=500, safe=False)

            # If ProductBuy serialization fails
            errors = product_buy_serializers.errors
            return JsonResponse({"message": "Failed to Order the Product from Cart2", "errors": errors}, status=500, safe=False)

        except Exception as e:
            error_message = e.__str__()
            logging.error(error_message)
            traceback.print_exc()
            return JsonResponse({"message": "Exception Raised in Ordering the Products"}, status=500, safe=False)

    if request.method == 'GET':
        try:
            user_id = request.user.get("UserId", None)
            try:
                product_tracking_details = ProductBuyDetails.objects.filter(UserId=user_id)
                if not product_tracking_details:
                    return JsonResponse({"message": "Invalid! You haven't made any purchases yet."}, status=400,
                                        safe=False)

            except ProductCartDetails.DoesNotExist:
                return JsonResponse({"message": "No Data Found"}, status=500, safe=False)

            undelivered_orders = []
            delivered_orders = []

            for product in product_tracking_details:
                if product.OrderDelivered == 1:
                    delivered_orders.append(product)
                else:
                    undelivered_orders.append(product)

            response_data = {
                "UndeliveredOrders": TrackAllOrderDetailsSerializers(undelivered_orders, many=True).data,
                "DeliveredOrders": TrackAllOrderDetailsSerializers(delivered_orders, many=True).data
            }

            return JsonResponse(response_data, status=200, safe=False)

        except Exception as e:
            error_message = e.__str__()
            logging.error(error_message)
            traceback.print_exc()
            return JsonResponse({"message": "Exception Raised in Fetching"}, status=500, safe=False)

    if request.method == 'PUT':
        try:
            tracking_id = request.GET.get("tracking_id")
            otp = request.GET.get("otp")
            order_delivered = request.GET.get("OrderDelivered")
            user_id = request.user.get("UserId")
            confirm_order = {}

            confirm_order['UserId'] = user_id
            confirm_order['TrackingId'] = tracking_id
            confirm_order['OrderDelivered'] = order_delivered
            confirm_order['OrderConfirm'] = 1
            confirm_order['ProductTrackingStatus'] = "We have initiated your order, and the items will be picked soon."

            if tracking_id is None:
                return JsonResponse({"message": "Please Add TrackingId to Confirm the Order"}, status=400,safe=False)

            if otp is None:
                return JsonResponse({"message": "Please Add OTP to Confirm the Order"}, status=400,safe=False)

            product_exists = ProductBuyDetails.objects.filter(TrackingId=confirm_order['TrackingId'], UserId=user_id).first()
            if not product_exists:
                return JsonResponse({"message": "TrackingId is Invalid! Please use Correct TrackingId"}, status=400,
                                    safe=False)

            if product_exists:
                table_otp = product_exists.Otp
                confirm_order['TotalStockQuantity'] = product_exists.TotalStockQuantity
                confirm_order['Email'] = product_exists.Email
                confirm_order['PhoneNumber'] = product_exists.PhoneNumber
                confirm_order['Address'] = product_exists.Address
                confirm_order['State'] = product_exists.State
                confirm_order['District'] = product_exists.District
                confirm_order['Pincode'] = product_exists.Pincode

                if table_otp != otp:
                    return JsonResponse({"message": "Your Otp is incorrect"}, status=500, safe=False)

            try:
                confirm_order_serializers = ProductBuySerializers(instance=product_exists, data=confirm_order)
                if confirm_order_serializers.is_valid():
                    email_sent = email_sender(email=confirm_order['Email'], confirm_order=confirm_order['ProductTrackingStatus'])
                    if email_sent["status_code"] == 200:
                        confirm_order_serializers.save()
                        return JsonResponse({"message": "Your Ordered Confirmed Successfully"}, status=200, safe=False)
                    else:
                        return JsonResponse({"message": f"Error in Sending Email"}, status=500, safe=False)

                errors = confirm_order_serializers.errors
                return JsonResponse({"message": "Failed to Confirm Your Order", "errors": errors}, status=500, safe=False)
            except ProductBuySerializers.DoesNotExist:
                return JsonResponse({"message": "Your Otp is incorrect"}, status=500, safe=False)

        except Exception as e:
            error_message = e.__str__()
            logging.error(error_message)
            traceback.print_exc()
        return JsonResponse({"message": "Exception Raised in Ordering the Products"}, status=500, safe=False)


@csrf_exempt
@token_required
def trackorderApi(request):
    if request.method == 'GET':
        try:
            user_id = request.user.get("UserId", None)
            tracking_id = request.GET.get("tracking_id")
            if not tracking_id:
                return JsonResponse({"message": "Please Enter Your TrackingId to Track Your Order."}, status=400, safe=False)

            try:
                product_tracking_details = ProductBuyDetails.objects.filter(UserId=user_id, TrackingId=tracking_id)
                if not product_tracking_details:
                    return JsonResponse({"message": "Invalid! You haven't made any purchases yet."}, status=400, safe=False)

            except ProductCartDetails.DoesNotExist:
                return JsonResponse({"message": "Invalid TrackingId or No Data Found"}, status=500, safe=False)
            products_serializers = TrackOrderSerializers(product_tracking_details, many=True)
            return JsonResponse(products_serializers.data, status=200, safe=False)

        except Exception as e:
            error_message = e.__str__()
            logging.error(error_message)
            traceback.print_exc()
        return JsonResponse({"message": "Exception Raised in Fetching"}, status=200, safe=False)

    if request.method == 'PUT':
        try:
            user_id = request.user.get("UserId")
            is_admin = request.user.get("IsAdmin", "0")
            if is_admin == "0":
                return JsonResponse({"message": "Only Admins are Allowed."}, status=401, safe=False)

            user_data = JSONParser().parse(request)
            order_status = {}

            # confirm_order['UserId'] = user_id
            order_status['TrackingId'] = user_data.get('TrackingId', None)
            order_status['ProductTrackingStatus'] = user_data.get('ProductTrackingStatus', None)
            order_status['OrderConfirm'] = user_data.get('OrderConfirm', '1')

            if not order_status['TrackingId']:
                return JsonResponse({"message": "Please Add TrackingId to Update the Order Status"}, status=400,safe=False)

            if not order_status['ProductTrackingStatus']:
                return JsonResponse({"message": "Please Add ProductTrackingStatus to Update the Order Status"}, status=400,safe=False)

            product_exists = ProductBuyDetails.objects.filter(TrackingId=order_status['TrackingId']).first()
            if not product_exists:
                return JsonResponse({"message": "TrackingId is Invalid! Please use Correct TrackingId to Update the Order Status"}, status=400,
                                    safe=False)

            if product_exists:
                order_status['TotalStockQuantity'] = product_exists.TotalStockQuantity
                order_status['Email'] = product_exists.Email
                order_status['PhoneNumber'] = product_exists.PhoneNumber
                order_status['Address'] = product_exists.Address
                order_status['State'] = product_exists.State
                order_status['District'] = product_exists.District
                order_status['Pincode'] = product_exists.Pincode

            confirm_order_serializers = OrderStatusUpdateSerializers(instance=product_exists, data=order_status)
            if confirm_order_serializers.is_valid():
                email_sent = email_sender(email=order_status['Email'], order_status=order_status['ProductTrackingStatus'])
                if email_sent["status_code"] == 200:
                    confirm_order_serializers.save()
                    return JsonResponse({"message": "User Order Status Successfully Updated"}, status=200, safe=False)
                else:
                    return JsonResponse({"message": f"Error in Sending Email to {order_status['Email']}"}, status=500, safe=False)

            errors = confirm_order_serializers.errors
            return JsonResponse({"message": "Failed to Update Order Status", "errors": errors}, status=500, safe=False)

        except Exception as e:
            error_message = e.__str__()
            logging.error(error_message)
            traceback.print_exc()
        return JsonResponse({"message": "Exception Raised in Updating the Order Status"}, status=500, safe=False)

    from django.http import JsonResponse
    from rest_framework.parsers import JSONParser
    from .models import Product

