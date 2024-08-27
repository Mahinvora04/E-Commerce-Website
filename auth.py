import re
from flask import app, redirect, render_template, request, url_for
from connection import *
import bcrypt 

db = connection.conn()

collection = db['customer']

class Customer:
    email = ''
    name=''
    def insert():
        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            
            if not confirm_password == password:
                return render_template('auth/sign-up.html', alert="Re-enter confirmed password!!!", alert_type="danger")

            if len(password) < 8:  # Check if password length is less than 8
                return render_template('auth/sign-up.html', alert="Password must be at least 4 characters long!", alert_type="danger")

            # Check if password contains at least one digit
            if not re.search(r"\d", password):
                return render_template('auth/sign-up.html', alert="Password must contain at least one digit!", alert_type="danger")

            # Check if password contains at least one special character
            if not re.search(r"[!@#$%^&*]", password):
                return render_template('auth/sign-up.html', alert="Password must contain at least one special character (!@#$%^&*)!", alert_type="danger")

            if Customer.email_notExist(email):
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                try:
                    collection.insert_one({
                        'name': name,
                        'email': email,
                        'password': hashed_password,
                    })
                    return redirect('/auth/log-in')

                except Exception as e:
                    return render_template('auth/sign-up.html', alert=f'Error Occurring While Customer Sign Up: {e}', alert_type="danger")
            else:
                return render_template('auth/sign-up.html', alert="Username already exists!!!", alert_type="danger")
        return render_template('auth/sign-up.html', alert='Something Went Wrong!', alert_type='danger')
    
    @staticmethod
    def authenticate(request):
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')

            customer = collection.find_one({'email': email})
            if customer and bcrypt.checkpw(password.encode('utf-8'), customer['password']):
                Customer.email = customer['email']
                # Redirect to home page upon successful login
                return render_template('home.html')
            else:
                # Email does not exist or incorrect password
                return render_template('auth/log-in.html', alert="Invalid email or password. Please try again.", alert_type="danger")
        else:
            # GET request
            return render_template('auth/log-in.html')

    def logout():
        Customer.email = ''
        return redirect('/auth/log-in')
    
    @staticmethod
    def email_notExist(email):
        existing_email = collection.find_one({'email': email})
        return not existing_email

    def getName():
        if Customer.email == '' :
            return redirect('/auth/log-in')
    
        email = Customer.email 
        customer_cursor = collection.find({'email': email})
        
        for customer in customer_cursor:
            c_name = customer.get('name')
            
        if c_name:
            return c_name
        
        return ""
    
    def getEmail():
        if Customer.email == '' :
            return redirect('/auth/log-in')
    
        email = Customer.email 
        
        return email
        
    @staticmethod
    def get_details():
        if not Customer.email:
            return None

        customer_details = collection.find_one({'email': Customer.email})
        return customer_details
    
    @staticmethod
    def change_password():
        if request.method == 'POST':
            email = request.form.get('email')
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_new_password = request.form.get('confirm_new_password')
            # hashed_current_password=current_password.bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            # if not collection.find({'email': email,'password':hashed_current_password}):
            customer = collection.find_one({'email':email })
            
            alert = 'danger'
            # Verify if the new password matches the confirm new password
            if new_password != confirm_new_password:
                return render_template('auth/change_password.html', alert_line='New Password and Confirm Password do not match!', alert_type='danger',alert = alert)

            # Get the current user's email
            email = Customer.getEmail()

            # Fetch the user's document from the database
            customer = collection.find_one({'email': Customer.email})

            # Verify if the current password matches the password in the database
            if bcrypt.checkpw(current_password.encode('utf-8'), customer['password']):
                # Hash the new password
                hashed_new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

                # Update the user's password in the database
                collection.update_one({'email': email}, {'$set': {'password': hashed_new_password}})        
                alert = 'success'
                return render_template('auth/change_password.html', alert_line='Password changed successfully!', alert_type='success',alert=alert)
            else:
                alert = 'danger'
                return render_template('auth/change_password.html', alert_line='Invalid current password!', alert_type='danger',alert=alert)

        # If the request method is not POST, render the change password page
        return render_template('auth/change_password.html')