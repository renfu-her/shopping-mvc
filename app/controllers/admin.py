from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user, login_user, logout_user
from app import db
from app.models import User, Category, Product, ProductImage, Order
from app.utils import validate_email, validate_phone
from functools import wraps
import os
import uuid
from werkzeug.utils import secure_filename

backend_bp = Blueprint('backend', __name__)

# Image upload configuration
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file, product_id):
    """Save uploaded file and return file info"""
    if file and allowed_file(file.filename):
        # Generate unique filename
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        unique_filename = f"{uuid.uuid4()}{ext}"
        
        # Create upload directory if it doesn't exist
        upload_dir = os.path.join(current_app.static_folder, 'uploads', 'products', str(product_id))
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_dir, unique_filename)
        file.save(file_path)
        
        # Get file info
        file_size = os.path.getsize(file_path)
        mime_type = file.content_type
        
        return {
            'filename': unique_filename,
            'original_filename': filename,
            'file_path': f'/static/uploads/products/{product_id}/{unique_filename}',
            'file_size': file_size,
            'mime_type': mime_type
        }
    return None

def backend_required(f):
    """Decorator to require backend access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Backend access required', 'error')
            return redirect(url_for('backend.backend_login'))
        return f(*args, **kwargs)
    return decorated_function

@backend_bp.route('/login', methods=['GET', 'POST'])
def backend_login():
    """Backend login page"""
    if current_user.is_authenticated and current_user.is_admin:
        return redirect(url_for('backend.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Please enter both username and password', 'error')
            return render_template('backend/login.html')
        
        # Find user by username or email
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if user and user.check_password(password):
            if user.is_admin:
                login_user(user, remember=True)
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                return redirect(url_for('backend.dashboard'))
            else:
                flash('Access denied. Backend access required.', 'error')
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('backend/login.html')

@backend_bp.route('/logout')
@login_required
@backend_required
def backend_logout():
    """Backend logout"""
    logout_user()
    flash('You have been logged out from the backend', 'info')
    return redirect(url_for('backend.backend_login'))

@backend_bp.route('/')
@login_required
@backend_required
def dashboard():
    """Admin dashboard"""
    stats = {
        'total_users': User.query.count(),
        'total_products': Product.query.count(),
        'total_categories': Category.query.count(),
        'total_orders': Order.query.count(),
        'pending_orders': Order.query.filter_by(status='pending').count(),
        'active_products': Product.query.filter_by(is_active=True).count()
    }
    
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                         stats=stats, 
                         recent_orders=recent_orders,
                         recent_users=recent_users)

# Product Management
@backend_bp.route('/products')
@login_required
@backend_required
def products():
    """Product management page"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    category_id = request.args.get('category', '')
    
    query = Product.query
    
    if search:
        query = query.filter(Product.name.contains(search))
    
    if category_id:
        query = query.filter(Product.category_id == category_id)
    
    products = query.paginate(page=page, per_page=10, error_out=False)
    categories = Category.query.filter_by(is_active=True).all()
    
    return render_template('admin/products.html', 
                         products=products, 
                         categories=categories,
                         current_search=search,
                         current_category=category_id)

@backend_bp.route('/products/add', methods=['GET', 'POST'])
@login_required
@backend_required
def add_product():
    """Add new product"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        price = request.form.get('price', '')
        stock_quantity = request.form.get('stock_quantity', '')
        category_id = request.form.get('category_id', '')
        
        # Validation
        errors = []
        
        if not name:
            errors.append('Product name is required')
        
        if not price:
            errors.append('Price is required')
        else:
            try:
                price = float(price)
                if price <= 0:
                    errors.append('Price must be greater than 0')
            except ValueError:
                errors.append('Invalid price format')
        
        if not stock_quantity:
            errors.append('Stock quantity is required')
        else:
            try:
                stock_quantity = int(stock_quantity)
                if stock_quantity < 0:
                    errors.append('Stock quantity cannot be negative')
            except ValueError:
                errors.append('Invalid stock quantity format')
        
        if category_id:
            try:
                category_id = int(category_id)
                if not Category.query.get(category_id):
                    errors.append('Invalid category')
            except ValueError:
                errors.append('Invalid category')
        else:
            category_id = None
        
        # Check if at least one image is uploaded
        uploaded_files = request.files.getlist('images')
        if not uploaded_files or not uploaded_files[0].filename:
            errors.append('At least one image is required')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            categories = Category.query.filter_by(is_active=True).all()
            return render_template('admin/add_product.html', categories=categories)
        
        # Create product
        try:
            product = Product(
                name=name,
                description=description,
                price=price,
                stock_quantity=stock_quantity,
                category_id=category_id
            )
            
            db.session.add(product)
            db.session.flush()  # Get the product ID
            
            # Handle image uploads
            if uploaded_files and uploaded_files[0].filename:
                for i, file in enumerate(uploaded_files):
                    if file.filename:  # Check if file was actually selected
                        file_info = save_uploaded_file(file, product.id)
                        if file_info:
                            product_image = ProductImage(
                                product_id=product.id,
                                filename=file_info['filename'],
                                original_filename=file_info['original_filename'],
                                file_path=file_info['file_path'],
                                file_size=file_info['file_size'],
                                mime_type=file_info['mime_type'],
                                is_primary=(i == 0),  # First image is primary
                                sort_order=i
                            )
                            db.session.add(product_image)
            
            db.session.commit()
            
            flash('Product added successfully!', 'success')
            return redirect(url_for('backend.products'))
        
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while adding the product', 'error')
            categories = Category.query.filter_by(is_active=True).all()
            return render_template('admin/add_product.html', categories=categories)
    
    categories = Category.query.filter_by(is_active=True).all()
    return render_template('admin/add_product.html', categories=categories)

@backend_bp.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
@backend_required
def edit_product(product_id):
    """Edit product"""
    product = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        price = request.form.get('price', '')
        stock_quantity = request.form.get('stock_quantity', '')
        category_id = request.form.get('category_id', '')
        is_active = request.form.get('is_active') == 'on'
        
        # Validation
        errors = []
        
        if not name:
            errors.append('Product name is required')
        
        if not price:
            errors.append('Price is required')
        else:
            try:
                price = float(price)
                if price <= 0:
                    errors.append('Price must be greater than 0')
            except ValueError:
                errors.append('Invalid price format')
        
        if not stock_quantity:
            errors.append('Stock quantity is required')
        else:
            try:
                stock_quantity = int(stock_quantity)
                if stock_quantity < 0:
                    errors.append('Stock quantity cannot be negative')
            except ValueError:
                errors.append('Invalid stock quantity format')
        
        if category_id:
            try:
                category_id = int(category_id)
                if not Category.query.get(category_id):
                    errors.append('Invalid category')
            except ValueError:
                errors.append('Invalid category')
        else:
            category_id = None
        
        if errors:
            for error in errors:
                flash(error, 'error')
            categories = Category.query.filter_by(is_active=True).all()
            return render_template('admin/edit_product.html', product=product, categories=categories)
        
        # Update product
        try:
            product.name = name
            product.description = description
            product.price = price
            product.stock_quantity = stock_quantity
            product.category_id = category_id
            product.is_active = is_active
            
            # Handle new image uploads
            uploaded_files = request.files.getlist('images')
            if uploaded_files and uploaded_files[0].filename:
                # Get current max sort order
                max_sort_order = db.session.query(db.func.max(ProductImage.sort_order)).filter_by(product_id=product.id).scalar() or -1
                
                for i, file in enumerate(uploaded_files):
                    if file.filename:  # Check if file was actually selected
                        file_info = save_uploaded_file(file, product.id)
                        if file_info:
                            product_image = ProductImage(
                                product_id=product.id,
                                filename=file_info['filename'],
                                original_filename=file_info['original_filename'],
                                file_path=file_info['file_path'],
                                file_size=file_info['file_size'],
                                mime_type=file_info['mime_type'],
                                is_primary=False,  # Don't auto-set as primary on edit
                                sort_order=max_sort_order + i + 1
                            )
                            db.session.add(product_image)
            
            db.session.commit()
            
            flash('Product updated successfully!', 'success')
            return redirect(url_for('backend.products'))
        
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the product', 'error')
            categories = Category.query.filter_by(is_active=True).all()
            return render_template('admin/edit_product.html', product=product, categories=categories)
    
    categories = Category.query.filter_by(is_active=True).all()
    return render_template('admin/edit_product.html', product=product, categories=categories)

@backend_bp.route('/products/delete/<int:product_id>', methods=['POST'])
@login_required
@backend_required
def delete_product(product_id):
    """Delete product"""
    product = Product.query.get_or_404(product_id)
    
    try:
        db.session.delete(product)
        db.session.commit()
        flash('Product deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the product', 'error')
    
    return redirect(url_for('backend.products'))

# Category Management
@backend_bp.route('/categories')
@login_required
@backend_required
def categories():
    """Category management page"""
    categories = Category.query.order_by(Category.name).all()
    return render_template('admin/categories.html', categories=categories)

@backend_bp.route('/categories/add', methods=['GET', 'POST'])
@login_required
@backend_required
def add_category():
    """Add new category"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        
        # Validation
        errors = []
        
        if not name:
            errors.append('Category name is required')
        elif Category.query.filter_by(name=name).first():
            errors.append('Category name already exists')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('admin/add_category.html')
        
        # Create category
        try:
            category = Category(name=name, description=description)
            db.session.add(category)
            db.session.commit()
            
            flash('Category added successfully!', 'success')
            return redirect(url_for('backend.categories'))
        
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while adding the category', 'error')
            return render_template('admin/add_category.html')
    
    return render_template('admin/add_category.html')

@backend_bp.route('/categories/edit/<int:category_id>', methods=['GET', 'POST'])
@login_required
@backend_required
def edit_category(category_id):
    """Edit category"""
    category = Category.query.get_or_404(category_id)
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        is_active = request.form.get('is_active') == 'on'
        
        # Validation
        errors = []
        
        if not name:
            errors.append('Category name is required')
        elif name != category.name and Category.query.filter_by(name=name).first():
            errors.append('Category name already exists')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('admin/edit_category.html', category=category)
        
        # Update category
        try:
            category.name = name
            category.description = description
            category.is_active = is_active
            
            db.session.commit()
            
            flash('Category updated successfully!', 'success')
            return redirect(url_for('backend.categories'))
        
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the category', 'error')
            return render_template('admin/edit_category.html', category=category)
    
    return render_template('admin/edit_category.html', category=category)

@backend_bp.route('/categories/delete/<int:category_id>', methods=['POST'])
@login_required
@backend_required
def delete_category(category_id):
    """Delete category"""
    category = Category.query.get_or_404(category_id)
    
    # Check if category has products
    if category.products:
        flash('Cannot delete category with existing products', 'error')
        return redirect(url_for('backend.categories'))
    
    try:
        db.session.delete(category)
        db.session.commit()
        flash('Category deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the category', 'error')
    
    return redirect(url_for('backend.categories'))

# User Management
@backend_bp.route('/users')
@login_required
@backend_required
def users():
    """User management page"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = User.query
    
    if search:
        query = query.filter(
            (User.username.contains(search)) | 
            (User.email.contains(search)) |
            (User.first_name.contains(search)) |
            (User.last_name.contains(search))
        )
    
    users = query.paginate(page=page, per_page=10, error_out=False)
    
    return render_template('admin/users.html', users=users, current_search=search)

@backend_bp.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@backend_required
def edit_user(user_id):
    """Edit user"""
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        is_active = request.form.get('is_active') == 'on'
        is_admin = request.form.get('is_admin') == 'on'
        
        # Validation
        errors = []
        
        if not username:
            errors.append('Username is required')
        elif username != user.username and User.query.filter_by(username=username).first():
            errors.append('Username already exists')
        
        if not email:
            errors.append('Email is required')
        elif not validate_email(email):
            errors.append('Please enter a valid email address')
        elif email != user.email and User.query.filter_by(email=email).first():
            errors.append('Email already registered')
        
        if not first_name:
            errors.append('First name is required')
        
        if not last_name:
            errors.append('Last name is required')
        
        if phone and not validate_phone(phone):
            errors.append('Please enter a valid phone number')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('admin/edit_user.html', user=user)
        
        # Update user
        try:
            user.username = username
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.phone = phone
            user.address = address
            user.is_active = is_active
            user.is_admin = is_admin
            
            db.session.commit()
            
            flash('User updated successfully!', 'success')
            return redirect(url_for('backend.users'))
        
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the user', 'error')
            return render_template('admin/edit_user.html', user=user)
    
    return render_template('admin/edit_user.html', user=user)

# Order Management (View Only)
@backend_bp.route('/orders')
@login_required
@backend_required
def orders():
    """Order management page (view only)"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    search = request.args.get('search', '')
    
    query = Order.query
    
    if status:
        query = query.filter(Order.status == status)
    
    if search:
        query = query.filter(
            (Order.order_number.contains(search)) |
            (Order.customer_name.contains(search)) |
            (Order.customer_email.contains(search))
        )
    
    orders = query.order_by(Order.created_at.desc()).paginate(page=page, per_page=10, error_out=False)
    
    return render_template('admin/orders.html', 
                         orders=orders, 
                         current_status=status,
                         current_search=search)

@backend_bp.route('/orders/<int:order_id>')
@login_required
@backend_required
def order_detail(order_id):
    """Order detail page (view only)"""
    order = Order.query.get_or_404(order_id)
    return render_template('admin/order_detail.html', order=order)

@backend_bp.route('/orders/<int:order_id>/update-status', methods=['POST'])
@login_required
@backend_required
def update_order_status(order_id):
    """Update order status"""
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status', '')
    
    valid_statuses = ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']
    
    if new_status not in valid_statuses:
        flash('Invalid status', 'error')
        return redirect(url_for('backend.order_detail', order_id=order_id))
    
    try:
        order.status = new_status
        db.session.commit()
        flash(f'Order status updated to {new_status.title()}', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while updating the order status', 'error')
    
    return redirect(url_for('backend.order_detail', order_id=order_id))

@backend_bp.route('/products/<int:product_id>/images')
@login_required
@backend_required
def product_images(product_id):
    """Manage product images"""
    product = Product.query.get_or_404(product_id)
    images = ProductImage.query.filter_by(product_id=product_id).order_by(ProductImage.sort_order).all()
    return render_template('admin/product_images.html', product=product, images=images)

@backend_bp.route('/products/<int:product_id>/images/<int:image_id>/delete', methods=['POST'])
@login_required
@backend_required
def delete_product_image(product_id, image_id):
    """Delete a product image"""
    image = ProductImage.query.filter_by(id=image_id, product_id=product_id).first_or_404()
    
    try:
        # Delete file from filesystem
        file_path = os.path.join(current_app.static_folder, 'uploads', 'products', str(product_id), image.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Delete from database
        db.session.delete(image)
        db.session.commit()
        
        flash('Image deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the image', 'error')
    
    return redirect(url_for('backend.product_images', product_id=product_id))

@backend_bp.route('/products/<int:product_id>/images/<int:image_id>/set-primary', methods=['POST'])
@login_required
@backend_required
def set_primary_image(product_id, image_id):
    """Set an image as primary"""
    try:
        # Remove primary from all images of this product
        ProductImage.query.filter_by(product_id=product_id).update({'is_primary': False})
        
        # Set the selected image as primary
        image = ProductImage.query.filter_by(id=image_id, product_id=product_id).first_or_404()
        image.is_primary = True
        
        db.session.commit()
        flash('Primary image updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while updating the primary image', 'error')
    
    return redirect(url_for('backend.product_images', product_id=product_id))
