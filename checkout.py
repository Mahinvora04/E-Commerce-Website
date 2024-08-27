from bson import ObjectId
from flask import render_template, request
from connection import *
from auth import Customer
from cart import Cart
import datetime

db = connection.conn()

collection = db['checkout']
product_collection=db['product']
cart_collection=db['cart']

class Checkout:
    @staticmethod
    def checkout():

        full_name = request.form.get('name')
        address = request.form.get('address')
        phone_number = request.form.get('phone')
        email = request.form.get('email')
        amount = request.form.get('amt')
        payment_method = request.form.get('payment-method')
        
        if full_name and address and phone_number and email and amount and payment_method:
            # Generate a new ObjectId for checkout_id
            checkout_id = ObjectId()

            # Fetch cart items for the current user
            cart_items_cursor = cart_collection.find({'email': email})
            cart_items = list(cart_items_cursor)
            products = []

            # Retrieve product details for each item in the cart
            for cart_item in cart_items:
                print(cart_item)#temp code
                product_id = cart_item.get('product_id')
                print("product_id -------------------------------------------------",product_id)#temp code
                product_details = product_collection.find_one({'_id': ObjectId(product_id)})

                if product_details:
                    products.append({
                        'name': product_details.get('name'),
                        'price': product_details.get('price'),
                        'image': product_details.get('image')
                    })

            checkout_data = {
                '_id': checkout_id,
                'full_name': full_name,
                'address': address,
                'phone_number': phone_number,
                'email': email,
                'amount': amount,
                'payment_method': payment_method,
                'products': products  # Add product details to checkout data
            }

        try:
            db['checkout'].insert_one(checkout_data)
            
            # Empty cart
            db['cart'].delete_many({'email': email})
            
            bill_data = {
                'order_number': checkout_id,  # Assuming checkout_id is used as the order number
                'order_date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'full_name': full_name,
                'address': address,
                'phone_number': phone_number,
                'email': email,
                'products': products,  # Include product details here
                'total_amount': amount  # Assuming amount is the total amount
            }
            # Render the bill page with the data
            return render_template('blog/bill.html', bill_data=bill_data)  # Pass bill_data to the template

        except Exception as e:
            return f"Error inserting data: {str(e)}"

        # If validation fails, return the checkout template with default values
        return render_template('blog/checkout.html')

    def show():
       # Retrieve checkout data from the database
        checkout_data_cursor = collection.find()
        checkout_data = list(checkout_data_cursor)

        # Create a list to store formatted checkout details
        formatted_checkout_data = []

        # Iterate through each checkout record
        for checkout_record in checkout_data:
            # Extract relevant fields from the checkout record
            checkout_id = checkout_record.get('_id', '')
            full_name = checkout_record.get('full_name', '')
            address = checkout_record.get('address', '')
            phone_number = checkout_record.get('phone_number', '')
            email = checkout_record.get('email', '')
            amount = checkout_record.get('amount', '')
            payment_method = checkout_record.get('payment_method', '')
            products = checkout_record.get('products', [])

            # Append formatted checkout details to the list
            formatted_checkout_data.append({
                'checkout_id': checkout_id,
                'full_name': full_name,
                'address': address,
                'phone_number': phone_number,
                'email': email,
                'amount': amount,
                'payment_method': payment_method,
                'products': products
            })

        # Render the template to display checkout data
        return render_template('admin/show_checkout_data.html', checkout_data=formatted_checkout_data)
    
    @staticmethod
    def get_checkout_data_by_email():
        
        email=Customer.getEmail()
        checkout_data = collection.find({'email': email})
        detail = []

        for checkout_product in checkout_data:
            detail.append({
                '_id': checkout_product.get('_id', 'Id not available'),
                'full_name': checkout_product.get('full_name', 'Full Name not available'),
                'amount': checkout_product.get('amount', 'Amount not available'),
                'payment_method': checkout_product.get('payment_method', 'Payment Method not available')
            })
        
        return render_template('blog/order.html', checkout_data=detail)