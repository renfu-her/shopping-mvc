from flask import session
from flask_login import current_user
from app import db
from app.models import Product, Cart, CartItem, Order, OrderItem
import uuid
from datetime import datetime

class CartService:
    
    @staticmethod
    def get_or_create_cart():
        """Get existing cart or create new one for current user or session"""
        cart = None
        
        if current_user.is_authenticated:
            # For logged-in users, use user_id
            cart = Cart.query.filter_by(user_id=current_user.id).first()
            if not cart:
                cart = Cart(user_id=current_user.id)
                db.session.add(cart)
                db.session.commit()
        else:
            # For anonymous users, use session_id
            session_id = session.get('cart_session_id')
            
            if not session_id:
                session_id = str(uuid.uuid4())
                session['cart_session_id'] = session_id
            
            cart = Cart.query.filter_by(session_id=session_id).first()
            
            if not cart:
                cart = Cart(session_id=session_id)
                db.session.add(cart)
                db.session.commit()
        
        return cart
    
    @staticmethod
    def add_to_cart(product_id, quantity=1):
        """Add product to cart"""
        cart = CartService.get_or_create_cart()
        product = Product.query.get_or_404(product_id)
        
        # Check if product is already in cart
        cart_item = CartItem.query.filter_by(
            cart_id=cart.id, 
            product_id=product_id
        ).first()
        
        if cart_item:
            # Update quantity
            cart_item.quantity += quantity
        else:
            # Create new cart item
            cart_item = CartItem(
                cart_id=cart.id,
                product_id=product_id,
                quantity=quantity
            )
            db.session.add(cart_item)
        
        db.session.commit()
        return cart_item
    
    @staticmethod
    def update_cart_item(cart_item_id, quantity):
        """Update cart item quantity"""
        cart_item = CartItem.query.get_or_404(cart_item_id)
        
        if quantity <= 0:
            db.session.delete(cart_item)
        else:
            cart_item.quantity = quantity
        
        db.session.commit()
        return cart_item
    
    @staticmethod
    def remove_from_cart(cart_item_id):
        """Remove item from cart"""
        cart_item = CartItem.query.get_or_404(cart_item_id)
        db.session.delete(cart_item)
        db.session.commit()
        return True
    
    @staticmethod
    def clear_cart():
        """Clear all items from cart"""
        cart = CartService.get_or_create_cart()
        CartItem.query.filter_by(cart_id=cart.id).delete()
        db.session.commit()
        return True
    
    @staticmethod
    def get_cart_items():
        """Get all items in current cart"""
        cart = CartService.get_or_create_cart()
        return cart.items
    
    @staticmethod
    def get_cart_summary():
        """Get cart summary with totals"""
        cart = CartService.get_or_create_cart()
        return {
            'total_items': cart.get_total_items(),
            'total_price': float(cart.get_total_price()),
            'items': [item.to_dict() for item in cart.items]
        }
    
    @staticmethod
    def create_order(customer_data):
        """Create order from current cart"""
        cart = CartService.get_or_create_cart()
        
        if not cart.items:
            raise ValueError("Cart is empty")
        
        # Generate order number
        order_number = f"ORD-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Calculate total amount
        total_amount = cart.get_total_price()
        
        # Create order
        order = Order(
            order_number=order_number,
            user_id=current_user.id if current_user.is_authenticated else None,
            customer_name=customer_data['name'],
            customer_email=customer_data['email'],
            customer_phone=customer_data.get('phone', ''),
            shipping_address=customer_data['address'],
            total_amount=total_amount,
            status='pending'
        )
        
        db.session.add(order)
        db.session.flush()  # Get order ID
        
        # Create order items
        for cart_item in cart.items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
            db.session.add(order_item)
        
        # Clear cart after successful order
        CartService.clear_cart()
        
        db.session.commit()
        return order
    
    @staticmethod
    def get_order(order_id):
        """Get order by ID"""
        return Order.query.get_or_404(order_id)
    
    @staticmethod
    def get_orders_by_email(email):
        """Get all orders for a customer email"""
        return Order.query.filter_by(customer_email=email).order_by(Order.created_at.desc()).all()
    
    @staticmethod
    def get_user_orders(user_id):
        """Get all orders for a user"""
        return Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()
