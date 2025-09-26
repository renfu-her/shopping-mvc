from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from app.models import Product
from app.services import CartService
from app import db

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def index():
    """Home page with product listing"""
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', '')
    search = request.args.get('search', '')
    
    query = Product.query
    
    if category:
        query = query.filter(Product.category_id == category)
    
    if search:
        query = query.filter(Product.name.contains(search))
    
    products = query.paginate(
        page=page, per_page=12, error_out=False
    )
    
    # Get unique categories for filter
    from app.models import Category
    categories = Category.query.filter_by(is_active=True).all()
    
    return render_template('products/index.html', 
                         products=products, 
                         categories=categories,
                         current_category=category,
                         current_search=search)

@home_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    """Product detail page"""
    product = Product.query.get_or_404(product_id)
    return render_template('products/detail.html', product=product)

@home_bp.route('/api/add-to-cart', methods=['POST'])
def add_to_cart():
    """API endpoint to add product to cart"""
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)
        
        if not product_id:
            return jsonify({'error': 'Product ID is required'}), 400
        
        cart_item = CartService.add_to_cart(product_id, quantity)
        cart_summary = CartService.get_cart_summary()
        
        return jsonify({
            'success': True,
            'message': 'Product added to cart',
            'cart_summary': cart_summary
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@home_bp.route('/api/cart-summary')
def cart_summary():
    """API endpoint to get cart summary"""
    try:
        cart_summary = CartService.get_cart_summary()
        return jsonify(cart_summary)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
