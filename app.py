from flask import Flask, jsonify , render_template, request,flash,get_flashed_messages
from auth import Customer
from cart import Cart
from connection import *
from product import *
from category import *
from admin import Admin
from wishlist import WishList
from checkout import Checkout

# App Name
app = Flask(__name__ , static_folder='D:/python_FINAL/static')
app.config['SECRET_KEY'] = 'abkdjksjdkshfdgdkfjsdjcd'

# Mongo Connection 
db = connection.conn()

# Collection
collection = db['product']

def get_email():
    return Customer.email

@app.context_processor
def inject_email():
    email = get_email()
    return dict(email=email)

@app.route("/")
def default():
    return render_template('main_page.html')

@app.route("/home")
def home():
    products_data = Product.getProductData()
    category_data = Product.getCategoryData()
    return render_template('home.html', products_data=products_data, category_data=category_data)

@app.route("/auth/<page>")
def render_auth_page(page):
    return render_template(f"/auth/{page}.html")

#For Admin log-in
@app.route('/admin/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        try:
            return Admin.authenticate(request)
        except Exception as e:
            return f'Error occurred: {e}' 
    else:
        return render_template('admin/admin_login.html')


# This section For Save & Show 
@app.route("/admin/<page>", methods=['POST','GET'])
def render_admin_page(page):
    if page == 'product':
        if request.method == 'POST':
            return Product.insert()
        else:
            return Product.show('admin')
    elif page == 'category':
        if request.method == 'POST':
            return Category.insert()
        else:
            return Category.show('admin')
    else:
        return render_template(f"admin/{page}.html")
    
# This section For Update product (For admin)
@app.route("/admin/product/update", methods=['GET', 'POST'])
def update_product():
    return Product.update()
    
# This section For Update category (For admin)
@app.route("/admin/category/update", methods=['GET', 'POST'])
def update_category():
    return Category.update()

# This section For Delete (For admin)
@app.route('/admin/<page>/<string:item_id>', methods=['POST'])
def delete_item(item_id,page):
    if page == "product":
        return Product.delete(item_id)
    elif page == 'category':
        return Category.delete(item_id)
    else:
        return render_template(f"/admin/{page}.html")
 
@app.route('/show_checkout_data', methods=['GET'])
def show_checkout_data():
    if request.method=="GET":
        return Checkout.show()

#log-in for existing customer 
@app.route('/auth/log-in', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            return Customer.authenticate(request)
        except Exception as e:
            return f'Error occurred: {e}' 
    else:
        return render_template('auth/log-in.html')
    
#Sign-up for new Customers
@app.route('/auth/sign-up', methods=['POST'])
def signup():
    if request.method == 'POST':
        try:
            return Customer.insert()
        except Exception as e:
            return render_template('auth/sign-up.html', alert=f'Error Occurred While Customer Sign Up: {e}', alert_type="danger")
    else:
        return render_template('auth/sign-up.html')
 
#For cart and Wishlist
@app.route("/blog/<page>", methods=['GET', 'POST'])
def render_blog_page(page):
    if request.method == 'POST' and request.path == '/blog/wishlist':
        return WishList.add(page)
    elif request.method == 'GET' and request.path == '/blog/wishlist':
        return WishList.show()
    elif request.method == 'GET' and request.path == '/blog/cart':
        return Cart.show()
    elif request.method == 'POST' and request.path == '/blog/cart':
        return Cart.add()
    elif page == "product" and request.args.get('category'):
        return Product.product_by_category('blog')
    elif page == 'product':
        return Product.show('blog')
    elif page == 'category':
        return Category.show('blog')
    else:
        return render_template(f"/blog/{page}.html")
    
@app.route('/blog/<page>/<string:item_id>', methods=['POST'])
def blog_delete_item(item_id, page):
    print("Requested URL:", request.url)
    if page == 'cart':
        return Cart.delete(item_id)
    elif page == 'wishlist':
        return WishList.delete(item_id)
    else:
        return render_template(f"/blog/{page}.html")
    
#For checkout
@app.route('/checkout', methods=['GET','POST'])
def checkout():
    c_name = Customer.getName()
    c_email = Customer.getEmail()
    amt=Cart.calculate_total_price()
    if request.method == 'GET':
        return render_template('blog/checkout.html', default_name=c_name, default_email=c_email,default_amt=amt)
    if request.method == 'POST':
        return Checkout.checkout()

@app.route('/get_checkout_modal_content')
def get_checkout_modal_content():
    checkout_id = request.args.get('checkout_id')
    checkout_data = db['checkout'].find_one({'_id': ObjectId(checkout_id)})

    if checkout_data:
        # Return the product details for the checkout ID
        products = checkout_data.get('products', [])
        return jsonify(products)
    else:
        return jsonify({'error': 'Checkout data not found'}), 404
    
@app.route('/blog/order')
def order():
    return Checkout.get_checkout_data_by_email()

@app.route('/auth/profile')
def profile():
    if not Customer.email:
        return redirect('/auth/log-in')
    
    customer_details = Customer.get_details()
    if not customer_details:
        return render_template('error.html', message="Customer details not found.")

    return render_template('auth/profile.html', customer=customer_details)

@app.route('/change-password', methods=['GET', 'POST'])
def change_password():
    if request.method == 'POST':
        return Customer.change_password()
    else:
        return render_template('auth/change_password.html')

@app.route('/auth/logout')
def logout():
    return Customer.logout()

@app.route('/blog/cart/clear', methods=['POST'])
def clear_cart():
    try:
        Cart.clear_cart()  # Call the method to clear the cart
        flash('Cart cleared successfully', 'success')
    except Exception as e:
        flash(f'An error occurred: {e}', 'danger')
    return redirect('/blog/cart')


if __name__ == '__main__':
    app.run(debug=True)