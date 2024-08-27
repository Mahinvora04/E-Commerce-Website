import os
from bson import ObjectId
from flask import app, redirect, render_template, request,flash
from connection import *

db = connection.conn()

collection = db['category']
class Category :
    name=''
    def insert():
      if request.method == 'POST':
        try:
            name = request.form['name']
            image = request.files['image']

            # Save image with filename as ObjectId followed by extension
            image_filename = name + '_' + str(ObjectId()) + os.path.splitext(image.filename)[-1]
            image_path = os.path.join('static', 'Image/category', image_filename)
            image.save(image_path)

            # Insert the form data into MongoDB
            collection.insert_one({
                'name': name,
                'image': image_filename  # Add the image name field to the database
            })

            data = collection.find()
            flash('Category added successfully', 'success')

            # Pass the data to the template and render the admin page
            return render_template("admin/category.html", data=data)
        except Exception as e:
            print("Error occurred:", e)  # Print the exact error message
            return str(e)
            
    def show(page):
        # Retrieve data from MongoDB
        data = collection.find()
         # Pass the data to the template
        return render_template(f'/{page}/category.html', data=data)
    
    def delete(item_id):
        try:
            # Convert item_id to ObjectId
            obj_id = ObjectId(item_id)
            # Delete item from collection
            collection.delete_one({'_id': obj_id})
            flash('Category deleted successfully', 'danger')
            return redirect('/admin/category')
        
        except Exception as e:
            return f"An error occurred: {e}"
        
        
    def update():
        if request.method == 'POST':
            try:
                # Get category name from form
                category_name = request.form['category_name']

                # Check if category exists in the database
                category = collection.find_one({'name': category_name})
                if category:
                    # If category exists, retrieve its details
                    category_id = category['_id']
                    category_image = category['image']

                    # Get updated details from form
                    updated_name = request.form['name']
                    updated_image = request.files['image']

                    # If admin uploaded a new image, save it and update image filename
                    if updated_image:
                        updated_image_filename = updated_name + '_' + str(ObjectId()) + os.path.splitext(updated_image.filename)[-1]
                        updated_image_path = os.path.join('static', 'Image/category', updated_image_filename)
                        updated_image.save(updated_image_path)
                    else:
                        # If no new image uploaded, keep the existing image filename
                        updated_image_filename = category_image

                    # Update category details in the database
                    collection.update_one(
                        {'_id': category_id},
                        {'$set': {
                            'name': updated_name,
                            'image': updated_image_filename
                        }}
                    )

                    # Redirect admin to the admin category page
                    return redirect('/admin/category')
                else:
                    return "Category not found"
            except Exception as e:
                print("Error occurred:", e)
                return str(e)
        else:
            return "Invalid request method"
 