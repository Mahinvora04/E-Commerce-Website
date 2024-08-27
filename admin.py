import re
from flask import app, redirect, render_template, request, url_for
from connection import *
import bcrypt 

db = connection.conn()

collection = db['admin']
class Admin:
    
    @staticmethod
    def authenticate(request):
        if request.method == 'POST':
            uname = request.form.get('uname')
            password = request.form.get('password')

            admin = collection.find_one({'uname': uname})
            if admin and bcrypt.checkpw(password.encode('utf-8'), admin['password']):
                return render_template('admin/admin_panel.html')
            else:
                return render_template('admin/admin_login.html', alert="Invalid username or password. Please try again.", alert_type="danger")
        return render_template('admin/admin_login.html', alert='Something Went Wrong!', alert_type='danger')

    def logout():
        Customer.email = ''
        return redirect('/admin/admin_login')
    
