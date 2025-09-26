from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required
from app.services import CartService
from app.models import Order

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/')
def view_cart():
    """View shopping cart"""
    cart_summary = CartService.get_cart_summary()
    return render_template('cart/view.html', cart=cart_summary)

@cart_bp.route('/update', methods=['POST'])
def update_cart():
    """Update cart item quantity"""
    try:
        data = request.get_json()
        cart_item_id = data.get('cart_item_id')
        quantity = data.get('quantity', 1)
        
        if not cart_item_id:
            return jsonify({'error': 'Cart item ID is required'}), 400
        
        cart_item = CartService.update_cart_item(cart_item_id, quantity)
        cart_summary = CartService.get_cart_summary()
        
        return jsonify({
            'success': True,
            'message': 'Cart updated',
            'cart_summary': cart_summary
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@cart_bp.route('/remove', methods=['POST'])
def remove_from_cart():
    """Remove item from cart"""
    try:
        data = request.get_json()
        cart_item_id = data.get('cart_item_id')
        
        if not cart_item_id:
            return jsonify({'error': 'Cart item ID is required'}), 400
        
        CartService.remove_from_cart(cart_item_id)
        cart_summary = CartService.get_cart_summary()
        
        return jsonify({
            'success': True,
            'message': 'Item removed from cart',
            'cart_summary': cart_summary
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@cart_bp.route('/clear', methods=['POST'])
def clear_cart():
    """Clear all items from cart"""
    try:
        CartService.clear_cart()
        return jsonify({
            'success': True,
            'message': 'Cart cleared'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@cart_bp.route('/checkout')
@login_required
def checkout():
    """Checkout page"""
    from flask_login import current_user
    
    cart_summary = CartService.get_cart_summary()
    
    if cart_summary['total_items'] == 0:
        flash('Your cart is empty', 'warning')
        return redirect(url_for('cart.view_cart'))
    
    return render_template('cart/checkout.html', cart=cart_summary, user=current_user)

@cart_bp.route('/checkout', methods=['POST'])
@login_required
def process_checkout():
    """Process checkout and create order"""
    from flask_login import current_user
    
    try:
        # Get form data
        customer_data = {
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone'),
            'address': request.form.get('address')
        }
        
        # Validate required fields
        required_fields = ['name', 'email', 'address']
        for field in required_fields:
            if not customer_data[field]:
                flash(f'{field.title()} is required', 'error')
                return redirect(url_for('cart.checkout'))
        
        # Create order
        order = CartService.create_order(customer_data)
        
        flash(f'Order {order.order_number} created successfully!', 'success')
        return redirect(url_for('cart.order_confirmation', order_id=order.id))
    
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('cart.checkout'))
    except Exception as e:
        flash('An error occurred while processing your order', 'error')
        return redirect(url_for('cart.checkout'))

@cart_bp.route('/order/<int:order_id>')
def order_confirmation(order_id):
    """Order confirmation page"""
    order = CartService.get_order(order_id)
    return render_template('cart/order_confirmation.html', order=order)

@cart_bp.route('/orders')
def order_history():
    """Order history page"""
    email = request.args.get('email')
    orders = []
    
    if email:
        orders = CartService.get_orders_by_email(email)
    
    return render_template('cart/order_history.html', orders=orders, email=email)
