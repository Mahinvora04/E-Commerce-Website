from bson import ObjectId
from flask import  redirect,jsonify, render_template, request,flash
from auth import Customer
from connection import connection

# Mongo Connection 
db = connection.conn()

# Collection
collection = db['wishlist']

class WishList :
  def add(page):

    product_id = request.form.get('productId')

    if Customer.email == '' :
        return redirect('/auth/log-in')
    
    email = Customer.email 
    existing_item = collection.find_one({'product_id': product_id, 'email': email})
        
    if existing_item is None:
        # If the product is not already in the wishlist, insert it
        collection.insert_one({'product_id': product_id, 'email': email})
        flash("Product added to your wishlist", "success")
    else:
        flash("Product is already in your wishlist", "danger")
    return redirect('/blog/wishlist')
  
  def show():
      
    wishlist_products_cursor = collection.find({'email': Customer.email})
    wishlist_products = list(wishlist_products_cursor)
    print(wishlist_products)
    # Prepare a list to store product details
    products = []
    for wishlist_item in wishlist_products:
        product_id = wishlist_item.get('product_id')
        
        # product collection to get product details using the product_id
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
                '_id': '',
                'name': 'Product not found',
                'price': 'N/A',
                'image': 'N/A'
            })
        print(products)
    # Render the template with the products data
    return render_template('/blog/wishlist.html', data=products)

  def delete(item_id):
        try:  
            collection.delete_one({'product_id': item_id,'email':Customer.getEmail()})
            flash('Product deleted from your wishlist', 'danger')
            return redirect('/blog/wishlist')
        except Exception as e:
            return f"An error occurred: {e}"