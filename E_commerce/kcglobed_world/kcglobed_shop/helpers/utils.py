import re
import jwt
import uuid
import imghdr
import logging
import secrets
import smtplib
import traceback
import phonenumbers

import boto3
from botocore.exceptions import NoCredentialsError
from datetime import datetime
from email.mime.text import MIMEText
from django.http.response import JsonResponse
from email.mime.multipart import MIMEMultipart
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from kcglobed_shop.helpers.my_sql_connector import my_sql_execute_query
from phonenumbers.phonenumberutil import NumberParseException, PhoneNumberType


KEY_LENGTH = 32
NAME_LIMIT = 41
DESCRIPTION_LIMIT = 200

def check_email_validation(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def generate_api_key():
    response = {"status": "Internal Server Error", "status_code": 500, "message": "Error in creating SecretKey"}
    try:
        secret_key = secrets.token_urlsafe(KEY_LENGTH)
        response.update({"status": "Success", "status_code": 200, "message": "Secret Key Created Successfully", "SecretKey": secret_key})
        return response
    except Exception as e:
        error_message = e.__str__()
        logging.error(error_message)
        traceback.print_exc()
    return response


PRIVATE_KEY = """
MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCu+3hU65jUp2qi
+fRJDmjm2hUcNaq6FUH+QqhX/kZ8DXxAaorqs0BHzbpGUyizM01hxB5DeolbfBoB
ZWTnGw6UZqo1JUpxJKfqRy4zh8i3kfr3WnOHan2fJPtF470MihDgA1PgGK1IAddZ
25XIX1lmMRvTdWbUP0KsSz6dIeV7Al5CKAsD5sUI749k/J+6hROe8tDZGsliSt1N
8LVUqPwarfBhbnPYX5AetFspUB7hopjwDlhgL79ttSBtqpLYkSUqHteIe5t4yWld
402sYhCWtOO3PeqLlarzRBvfDr6tij/wUVlxFip/ZWBwVZN7c4KIeER3al64YOpb
i8A7TYW3AgMBAAECggEADqZxQbLj/dHyhKimwkMZl1Jk+BKqM6A6AT61d4CLiDFc
2MvSy6msVRatZNvriW1fKjNQUVf+DhHK35kMpKjIRLZ/w6lWnThzcpL5FElnDa+E
Mpd5GrpYwC1JeGWD23vnw8mjiRynzWKSFCzlUnxhMMQlz0OCE30kaOZ33JIM84pw
qWcrkZpKnhvwSD/Q3GVd9VcO+FvotKztsUQLv6BCvphq1LjAtlzC+tSESJTHmhkm
5ixXxdbtwCvrmE3uxXX1n0FqKMpT1UfAwBcNjwQf3B0A9BUALRyuNl6Fv10KUkCj
yXXdurpv+o/uXWMiZx/X9SRpOF6Yj454AJoNsnoY2QKBgQDldmhOcajaSP+G4GKj
zcJd1WTcOA8zi0/Jgt3866BeyjRVZTZa1AqakfWa8505uNvxC3ZOO6V03d0sLXCa
u/lq7NAk0ZSLgsap5h+nErDcjMonLbws3uRfomRd5tpo6A/XJqhiV9nzy40T6eoF
BUVz5ghKD84nNY/GdRc/UKBYxQKBgQDDOBdnb2WEdjIUXBmJJFEiLqgdbvFQqzAn
hQIoKoO4wTAOW74qgegwTvMj0K+q2GZP1qHu4ySN4aV7xnoeBkHUlwZQ0jharNPD
oKTT5lzDHusbSnofvVr3SV/yUpYj4fyTtNIzNcfeMlUzISdm+pPPOuQiTjzy93R0
tGQRGtW0SwKBgCR6zZxi/3gskMstkyD9jkACs/U6yFfmdvnPX2FdSHKpbOaCn8CS
41iticFnp4BMvlK1AsrvOp+4wffLBZLj/YQdP/4Kf7YqRVEvb6rNEucNTvopkDgF
+4Kku5YeJGz3L8WBtNVlqBXVL4mR7416yA7j7D9yAdFD96aSaO6877ENAoGAYIMK
jwhzl9kXSRl/Rl29/rgyRNrkUo1PcTpAprreBCj+KRsSGNHAiKF/cuVo832oly/1
PrTtDXfQ6DBnjxBo20EOzkYftjRbPQvecSQiGBThBsz7M1XZ8wdDd/l8YKEIzb1H
binYdfFMTcrGQBMBoCHtR0iGuVe9KzVDg3FQ1aECgYAF/5JQq9V2bPzauGqdMKIS
ce1JqVkuw8dansid7XejdVwH6QmgMrkt4elk5zV74vqOJs0D057cwVvW7bPj6dd6
DLSj0gTEvd97D8X8xMc/CeIifO8M16SwuoqDf5xdtOVDjnFFvc1y+25Pl9Z2Xkud
w3O4APa3T59+oY5XeyqfSg==
"""


ACCESS_KEY_ID = ""
SECRET_ACCESS_KEY = ""



def generate_bearer_token(results):
    response = {"status": "Internal Server Error", "status_code": 500, "message": "Error in Generating Bearer Token"}
    try:
        user_id = results[0][0]
        email = results[0][1]
        x_api_key = results[0][7]
        is_admin = results[0][9]
        jti = str(uuid.uuid4())  # generating unique JSON token id for more security
        date = datetime.now()
        current_timestamp = date.timestamp()

        payload = {
            "exp": current_timestamp + 86400,  # 30 mins expiry set
            "generated_at": current_timestamp,
            "jti": jti,
            "UserId": f"{user_id}",
            "Email": f"{email}",
            "XApiKey": f"{x_api_key}",
            "IsAdmin": f"{is_admin}"
        }

        token = jwt.encode(payload, PRIVATE_KEY, algorithm="HS256")
        if isinstance(token, bytes):
            token = token.decode('utf-8')
        response.update(
            {
                "status": "success",
                "Token": token,
                "XApiKey": x_api_key,
                "status_code": 200,
                "message": "Bearer Token Generated Successfully"
            }
        )

    except Exception as e:
        logging.info(e)
        traceback.print_exc()
        logging.error(f"Error in generate_bearer_token: {e}")
    return response


def generate_private_key():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    return pem.decode('utf-8')


def is_valid_image(file):
    # Use imghdr to determine the image format
    image_format = imghdr.what(file)
    # Check if the format is one of the allowed formats
    return image_format in ['jpeg', 'jpg', 'png']


def validate_phonenumber(phone_number):
    is_valid_number = False
    message = "Not a valid phone number"
    try:
        parsed_number = phonenumbers.parse(phone_number, None)
        number_type_result = phonenumbers.number_type(parsed_number)

        if number_type_result == PhoneNumberType.MOBILE:
            is_valid_number = True
            message = "valid phone number"
        else:
            is_valid_number = False
            message = "Not a valid phone number"

    except NumberParseException as ex:
        message = "Missing or invalid default region in phone number"

    if not is_valid_number:
        if len(phone_number) == 10:
            is_valid_number = True
            message = "valid phone number"
        elif len(phone_number) == 11 and phone_number[0] == "0":
            is_valid_number = True
            message = "valid phone number"

    return is_valid_number, message


states = ["andaman and nicobar islands", "andhra pradesh", "arunachal pradesh", "assam", "bihar", "chandigarh", "chhattisgarh", "dadra and nagar haveli", "daman and diu", "delhi", "goa", "gujarat", "haryana", "himachal pradesh", "jharkhand", "karnataka", "kerala", "ladakh", "lakshadweep", "madhya pradesh", "maharashtra", "manipur", "meghalaya", "mizoram", "nagaland", "odisha", "puducherry", "punjab", "rajasthan", "sikkim", "tamil nadu", "telangana", "tripura", "uttar pradesh", "uttarakhand", "west bengal"]


def email_sender(email, tracking_id=None, otp=None, order_status=None, confirm_order=None):
    response = {"status_code": 500, "message": "error in sending email"}

    try:
        email_sender = "ecommercemyshopindia@gmail.com"
        sender_password = "qpum wllm rvwq zloc"
        # Set up the SMTP server and login
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(email_sender, sender_password)

        # Create a message
        msg = MIMEMultipart()
        msg['From'] = email_sender
        msg['To'] = email
        if otp:
            msg['Subject'] = "Please Verify and Confirm Your Order"
            message = f"Hi Buyer,\n Your OTP is {otp}. You can use this OTP to Confirm Your Order\nYour TrackingId is {tracking_id}, Use this TrackingId to Track your Order."
            msg.attach(MIMEText(message, 'plain'))
        if confirm_order:
            msg['Subject'] = "Congratulations!!!! Your Order is Now Confirmed"
            message = f"Hi Buyer,\n Congratulations!!!! Your Order is Now Confirmed. You Can Track your Order\nOrder Status: {confirm_order}."
            msg.attach(MIMEText(message, 'plain'))
        elif order_status:
            msg['Subject'] = "Your Order Changed Track You Premium Order"
            message = f"Hi Buyer,\n Your Order Status is Updated\nOrder Status: {order_status}."
            msg.attach(MIMEText(message, 'plain'))

        # Send the message
        server.sendmail(email_sender, email, msg.as_string())

        try:
            server.sendmail(email_sender, email, msg.as_string())
            response.update({"status_code": 200, "message": "Email sent successfully"})
        except smtplib.SMTPException as e:
            response.update({"status_code": 500, "message": f"SMTP error in sending email: {str(e)}"})
        except Exception as e:
            # Catch any other unexpected exceptions
            response.update({"status_code": 500, "message": f"Error in sending email: {str(e)}"})

        # Quit the server
        server.quit()
        # response.update({"status_code": 200, "message": "Email sent successfully"})
        return response

    except Exception as e:
        response.update({"status_code": 500, "message": f"Error in sending email: {str(e)}"})
        return response


def upload_to_s3(file_content, bucket_name, s3_file_key):
    try:

        s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY_ID, aws_secret_access_key=SECRET_ACCESS_KEY)

        s3.upload_fileobj(file_content, bucket_name, s3_file_key)
        s3.put_object_acl(Bucket=bucket_name, Key=s3_file_key, ACL='public-read')
        return True

    except NoCredentialsError:
        print("Credentials not available")
        return False


def get_presigned_url(bucket_name, object_key):
    try:
        s3_client = boto3.client('s3', aws_access_key_id=ACCESS_KEY_ID, aws_secret_access_key=SECRET_ACCESS_KEY)
        presigned_url = s3_client.generate_presigned_url('get_object', Params={'Bucket': bucket_name, 'Key': object_key})
        return {"status_code": 200, "message": "Success", "image_url": presigned_url}
    except Exception as e:
        logging.info(e)
        traceback.print_exc()
        return {"status_code": 500, "message": "Error in fetching image link from S3", "error_details": str(e)}


def delete_objects_from_bucket(bucket_name, object_key):
    try:
        s3_client = boto3.client('s3', aws_access_key_id=ACCESS_KEY_ID, aws_secret_access_key=SECRET_ACCESS_KEY)

        s3_client.delete_objects(Bucket=bucket_name, Delete={"Objects": [{"Key": object_key}]})
        return {"status_code": 200, "message": "Successfully deleted object from S3"}

    except Exception as e:
        logging.info(e)
        traceback.print_exc()
        return {"status_code": 500, "message": "Error in deleting image from S3", "error_details": str(e)}


def params_validator(data):
    is_valid = True
    message = "Valid Parameter"

    name = data.get("Name", "")
    description = data.get("Description", "")

    if len(name) > NAME_LIMIT:
        is_valid = False
        message = "Name Length must be less than 40"

    if len(description) > DESCRIPTION_LIMIT:
        is_valid = False
        message = f"Description Length must be less than {DESCRIPTION_LIMIT}"

    return is_valid, message
