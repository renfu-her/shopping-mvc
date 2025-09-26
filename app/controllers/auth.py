from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User
from app.utils import validate_email, validate_phone

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        phone = request.form.get('phone', '').strip()
        
        # Validation
        errors = []
        
        if not username:
            errors.append('Username is required')
        elif len(username) < 3:
            errors.append('Username must be at least 3 characters long')
        elif User.query.filter_by(username=username).first():
            errors.append('Username already exists')
        
        if not email:
            errors.append('Email is required')
        elif not validate_email(email):
            errors.append('Please enter a valid email address')
        elif User.query.filter_by(email=email).first():
            errors.append('Email already registered')
        
        if not password:
            errors.append('Password is required')
        elif len(password) < 6:
            errors.append('Password must be at least 6 characters long')
        elif password != confirm_password:
            errors.append('Passwords do not match')
        
        if not first_name:
            errors.append('First name is required')
        
        if not last_name:
            errors.append('Last name is required')
        
        if phone and not validate_phone(phone):
            errors.append('Please enter a valid phone number')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('auth/register.html')
        
        # Create user
        try:
            user = User(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone=phone
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'error')
            return render_template('auth/register.html')
    
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('home.index'))
    
    if request.method == 'POST':
        username_or_email = request.form.get('username_or_email', '').strip()
        password = request.form.get('password', '')
        remember_me = request.form.get('remember_me') == 'on'
        
        if not username_or_email or not password:
            flash('Please fill in all fields', 'error')
            return render_template('auth/login.html')
        
        # Find user by username or email
        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact support.', 'error')
                return render_template('auth/login.html')
            
            login_user(user, remember=remember_me)
            
            # Redirect to next page or home
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            
            flash(f'Welcome back, {user.first_name}!', 'success')
            return redirect(url_for('home.index'))
        else:
            flash('Invalid username/email or password', 'error')
            return render_template('auth/login.html')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('home.index'))

@auth_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    return render_template('auth/profile.html', user=current_user)

@auth_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit user profile"""
    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        
        # Validation
        errors = []
        
        if not first_name:
            errors.append('First name is required')
        
        if not last_name:
            errors.append('Last name is required')
        
        if not email:
            errors.append('Email is required')
        elif not validate_email(email):
            errors.append('Please enter a valid email address')
        elif email != current_user.email and User.query.filter_by(email=email).first():
            errors.append('Email already registered')
        
        if phone and not validate_phone(phone):
            errors.append('Please enter a valid phone number')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('auth/edit_profile.html', user=current_user)
        
        # Update user
        try:
            current_user.first_name = first_name
            current_user.last_name = last_name
            current_user.email = email
            current_user.phone = phone
            current_user.address = address
            
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('auth.profile'))
        
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating your profile. Please try again.', 'error')
            return render_template('auth/edit_profile.html', user=current_user)
    
    return render_template('auth/edit_profile.html', user=current_user)

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change user password"""
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        errors = []
        
        if not current_password:
            errors.append('Current password is required')
        elif not current_user.check_password(current_password):
            errors.append('Current password is incorrect')
        
        if not new_password:
            errors.append('New password is required')
        elif len(new_password) < 6:
            errors.append('New password must be at least 6 characters long')
        elif new_password == current_password:
            errors.append('New password must be different from current password')
        
        if new_password != confirm_password:
            errors.append('New passwords do not match')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('auth/change_password.html')
        
        # Update password
        try:
            current_user.set_password(new_password)
            db.session.commit()
            flash('Password changed successfully!', 'success')
            return redirect(url_for('auth.profile'))
        
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while changing your password. Please try again.', 'error')
            return render_template('auth/change_password.html')
    
    return render_template('auth/change_password.html')

@auth_bp.route('/orders')
@login_required
def user_orders():
    """User's order history"""
    orders = current_user.orders.order_by(Order.created_at.desc()).all()
    return render_template('auth/orders.html', orders=orders)

@auth_bp.route('/order/<int:order_id>')
@login_required
def user_order_detail(order_id):
    """User's order detail"""
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    return render_template('auth/order_detail.html', order=order)
