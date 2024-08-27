import os
from bson import ObjectId
from flask import jsonify, redirect, render_template, request,flash
from connection import *

db = connection.conn()

collection = db['product']
class Product :
    
    def __init__(self):
        self.data=''
        self.category_data=''
    def insert():
        if request.method == 'POST':
            name = request.form['name']
            price = request.form['price']
            category = request.form['category']
            image = request.files['image']
            desc = request.form['desc']
            
            try:
                image_filename = name + '_' + str(ObjectId()) + os.path.splitext(image.filename)[-1]
                image_path = os.path.join('static', 'Image/product', image_filename)
                image.save(image_path)

                # Insert the form data into MongoDB
                collection.insert_one({
                    'name': name,
                    'price': price,
                    'category': category,
                    'image' : image_filename,
                    'description': desc
                })
                data = collection.find()
                flash('Product added successfully', 'success')
                # Pass the data to the template
                return render_template("admin/product.html", data=data)
            except Exception as e:
                return 'Error Occuring While Product save  ' + str(e)

    def show(page):
        # Retrieve data from MongoDB
        data = collection.find()
        category_data = db['category'].find()
         # Pass the data to the template
        return render_template(f'/{page}/product.html', data=data ,category_data= category_data)
    
    def product_by_category(page):
        category_name = request.args.get('category')
        category = db['category'].find_one({'name': category_name})
        if category:
            products = collection.find({'category': category_name})
            # Convert ObjectId to string for JSON serialization
            products_list = [{'_id': str(product['_id']), 'name': product['name'], 'price': product['price'],'image' : product['image'],'description':product['description']} for product in products]
            return render_template(f'/{page}/product.html', data=products_list )
        else:
            return render_template('blog/product.html', alert=f'Category Not Found !!', alert_type="danger")

        
    def delete(item_id):
        try:
            # Convert item_id to ObjectId
            obj_id = ObjectId(item_id)
            # Delete item from collection
            collection.delete_one({'_id': obj_id})
            flash('Product deleted successfully', 'danger')
            return redirect('/admin/product')
        
        except Exception as e:
            return f"An error occurred: {e}"
 
 
    def update():
        if request.method == 'POST':
            product_name = request.form['product_name']
            updated_name = request.form['name']
            updated_price = request.form['price']
            updated_category = request.form['category']
            updated_image = request.files['image']
            updated_desc = request.form['desc']

            # Check if the product exists based on the provided product name
            existing_product = collection.find_one({'name': product_name})
            if existing_product:
                try:
                    # Update product details
                    existing_product['name'] = updated_name
                    existing_product['price'] = updated_price
                    existing_product['category'] = updated_category
                    existing_product['description'] = updated_desc

                    # Handle image update if provided
                    if updated_image:
                        updated_image_filename = updated_name + '_' + str(ObjectId()) + os.path.splitext(updated_image.filename)[-1]
                        updated_image_path = os.path.join('static', 'Image/product', updated_image_filename)
                        updated_image.save(updated_image_path)
                        existing_product['image'] = updated_image_filename

                    # Update the product in the database
                    collection.update_one({'_id': existing_product['_id']}, {'$set': existing_product})

                    # Redirect to the product list page after update
                    return redirect('/admin/product')
                except Exception as e:
                    return 'Error Occurring While Product update: ' + str(e)
            else:
                return 'Product not found'

        else:
            return render_template("admin/update_product.html")
        
    @staticmethod
    def getProductData():
        data = collection.find()
        return data
    
    @staticmethod
    def getCategoryData():
        category_data = db['category'].find()
        return category_data
