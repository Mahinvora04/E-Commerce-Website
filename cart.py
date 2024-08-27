from bson import ObjectId
from flask import redirect, render_template, request,flash,get_flashed_messages
from auth import Customer
from connection import connection


# Mongo Connection 
db = connection.conn()
# Collection
collection = db['cart']
product_collection = db['product']

class Cart:
    def add():
        product_id = request.form.get('productId')

        if Customer.email == '':
            return redirect('/auth/log-in')

        email = Customer.email
        existing_item = collection.find_one({'product_id': product_id, 'email': email})
        product_details = product_collection.find_one({'_id': ObjectId(product_id)})

        if existing_item is None and product_details:
            # If the product is not already in the cart and product details are available, insert it
            if product_id is not "":
                collection.insert_one({
                    'product_id': product_id,
                    'email': email,
                    'name': product_details.get('name'),
                    'price': product_details.get('price'),
                    'image': product_details.get('image')
                })
                flash("Product added in your cart", "success")
        elif existing_item:
            flash("Product is already in your cart", "danger")
        else:
            flash("Product details not found", "danger")
        return redirect('/blog/cart')

  
    # def show():
        # cart_products_cursor = collection.find({'email': Customer.email})
        # cart_products = list(cart_products_cursor)
        # products = []
        
        # for cart_item in cart_products:
        #     product_id = cart_item.get('product_id')
        #     product_details = db['product'].find_one({'_id': ObjectId(product_id)})

        #     if product_details:
        #         # If product details are found, append them to the products list
        #         products.append({
        #             'name': product_details.get('name', 'Name not available'),
        #             'price': product_details.get('price', 'Price not available'),
        #             'image': product_details.get('image', 'Image not available')
        #         })
        #     else:
        #         # Handle case where product details are not found
        #         products.append({
        #             'name': 'Product not found',
        #             'price': 'N/A',
        #             'image': 'N/A'
        #         })    
        # return render_template('/blog/cart.html', data=products)
  
    @staticmethod
    def delete(item_id):
        try:
            collection.delete_one({'product_id': item_id,'email':Customer.getEmail()})
            flash('Product deleted successfully', 'danger')
            return redirect('/blog/cart')
        except Exception as e:
            return f"An error occurred: {e}"
      
    @staticmethod
    def calculate_total_price():
        
        total_price = 0.0
        
        if Customer.email == '' :
            return redirect('/auth/log-in')
    
        email = Customer.email 
        cart_products_cursor = collection.find({'email': email})
        
        for cart_item in cart_products_cursor:
            product_id = cart_item.get('product_id')
            product_details = product_collection.find_one({'_id': ObjectId(product_id)})
        
            if product_details:
                price=float(product_details.get('price',0))
                (total_price) = float(total_price) + float(price)
            
        return float(total_price)
    
    @staticmethod
    def show():
        total_price = Cart.calculate_total_price()  # Calculate total price
        
        cart_products_cursor = collection.find({'email': Customer.email})
        cart_products = list(cart_products_cursor)
        products = []
        
        data = collection.find()
        
        for cart_item in cart_products:
            product_id = cart_item.get('product_id')
            product_details = db['product'].find_one({'_id': ObjectId(product_id)})

            if product_details:
                # If product details are found, append them to the products list
                products.append({
                    '_id':product_details.get('_id', 'Id not available'),
                    'product_id':product_details.get('product_id', 'Product Id not available'),
                    'name': product_details.get('name', 'Name not available'),
                    'price': product_details.get('price', 'Price not available'),
                    'image': product_details.get('image', 'Image not available'),
                    'description':product_details.get('description', 'Description not available'),
                    'category':product_details.get('category', 'Category not available')
                })
            else:
                # Handle case where product details are not found
                products.append({
                    '_id':'',
                    'product_id':'',
                    'name': 'Product is currently unavailable',
                    'price': '',
                    'image': '',
                    'description':'',
                    'category':''
                })    

        return render_template('/blog/cart.html', data=products, total_price=total_price)

    @staticmethod
    def clear_cart():
        try:
            collection.delete_many({'email': Customer.email})
        except Exception as e:
            flash(f'An error occurred: {e}')