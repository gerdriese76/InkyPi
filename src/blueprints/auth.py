from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
import functools

auth_bp = Blueprint('auth', __name__)

@auth_bp.before_app_request
def check_auth():
    if request.endpoint and (
        'static' in request.endpoint or 
        request.endpoint in ['auth.login', 'auth.logout']
    ):
        return

    user_manager = current_app.config['DEVICE_CONFIG'].get_user_manager()
    has_users = user_manager.has_users()

    # If no users exist, we must allow access to user creation endpoints
    if not has_users:
        if request.endpoint in ['auth.users', 'auth.add_user']:
            return
        # Redirect to user creation page
        return redirect(url_for('auth.users'))

    # If users exist, enforce login
    if session.get('user_id') is None:
        return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_manager = current_app.config['DEVICE_CONFIG'].get_user_manager()
        
        if user_manager.verify_user(username, password):
            session.clear()
            session['user_id'] = username
            return redirect(url_for('main.main_page'))
        
        flash('Invalid username or password')

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

@auth_bp.route('/users', methods=('GET',))
def users():
    user_manager = current_app.config['DEVICE_CONFIG'].get_user_manager()
    users = user_manager.get_users()
    return render_template('users.html', users=users, has_users=user_manager.has_users())

@auth_bp.route('/users/add', methods=('POST',))
def add_user():
    user_manager = current_app.config['DEVICE_CONFIG'].get_user_manager()
    
    username = request.form['username']
    password = request.form['password']
    
    if not username or not password:
        flash('Username and password are required')
        return redirect(url_for('auth.users'))

    if user_manager.add_user(username, password):
        flash('User added successfully')
        # If this was the first user (we were not logged in), log them in automatically
        if session.get('user_id') is None:
             session['user_id'] = username
             return redirect(url_for('main.main_page'))
    else:
        flash('User already exists')
    
    return redirect(url_for('auth.users'))

@auth_bp.route('/users/delete/<username>', methods=('POST',))
def delete_user(username):
    user_manager = current_app.config['DEVICE_CONFIG'].get_user_manager()
    
    if username == session.get('user_id'):
        flash("Cannot delete yourself")
        return redirect(url_for('auth.users'))

    user_manager.delete_user(username)
    flash('User deleted')
    
    return redirect(url_for('auth.users'))
