# **assignment_kcglobed**
**An e-commerce website built using the Django Rest Framework.**

1. Please follow this link for the DDLs of the tables: https://drive.google.com/drive/folders/1AltpZDo3KqhYemmsDx3Y5zZ1ka8mRjbV
2. Clone this repository into your local system.
3. Create and activate your own virtual environment.
4. Download this requirement.txt file which includes all the libraries: https://drive.google.com/drive/folders/1AltpZDo3KqhYemmsDx3Y5zZ1ka8mRjbV
5. Use the above requirement.txt file and Install the required libraries by running the following command: **pip install -r requirements.txt**
6. Run the following commands to make migrations for your models tables:
**- python manage.py makemigrations**
**- python manage.py migrate**
5. To start the server, run: **python manage.py runserver**
6. Explore the assignment APIs using the provided Postman collection: https://drive.google.com/drive/folders/1AltpZDo3KqhYemmsDx3Y5zZ1ka8mRjbV.


**API Descriptions:**

**/admins/:** Registers admins' email addresses into the database.

**/signup/:** Registers normal users and administrators (if the email is already in the admins table).

**/login/:** Logs users into the system and retrieves access tokens and x-api keys for accessing other APIs.

**/logout/:** Logs users out of the system by deleting the access token from the database.

**/search/:** Searches for products by ProductName, Price, CompanyName, and Category.

**/get_product_details/:** Retrieves product details including all attributes.

**/add_product/:** Allows admins to add products and their details to the database.

**/update_product/:** Allows admins to update product details in the database.

**/delete_product/:** Allows admins to delete products from the database.

**/get_cart_products/:** Lists all products added to the cart.

**/cart_product_add/:** Adds products to the cart.

**/update_cart/:** Updates or removes product quantities in the cart.

**/clear_cart/:** Clears the cart.

**/track_all_order_details/:** Displays all delivered and undelivered products along with their order statuses.

**/buy_order/:** Allows users to purchase products from the cart.

**/confirm_order/:** Confirms orders by verifying OTP and tracking IDs.

**/track_order/:** Tracks a specific order for the user.

**/update_order_status/:** Allows admins to update the order status.
