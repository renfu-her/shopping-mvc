import unittest
import json
from flask import Flask
from app import create_app, db
from app.models import User, Product, Cart, CartItem, Order
from app.services import CartService

class CartTestCase(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['WTF_CSRF_ENABLED'] = False
        
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        db.create_all()
        
        # Create test user
        self.user = User(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        self.user.set_password('testpass')
        
        # Create test products
        self.product1 = Product(
            name='Test Product 1',
            description='Test Description 1',
            price=29.99,
            stock_quantity=10,
            category='Test'
        )
        self.product2 = Product(
            name='Test Product 2',
            description='Test Description 2',
            price=39.99,
            stock_quantity=5,
            category='Test'
        )
        
        db.session.add(self.user)
        db.session.add(self.product1)
        db.session.add(self.product2)
        db.session.commit()
    
    def tearDown(self):
        """Tear down test fixtures after each test method."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_add_to_cart(self):
        """Test adding product to cart."""
        with self.client.session_transaction() as sess:
            sess['cart_session_id'] = 'test-session-123'
        
        cart_item = CartService.add_to_cart(self.product1.id, 2)
        
        self.assertIsNotNone(cart_item)
        self.assertEqual(cart_item.product_id, self.product1.id)
        self.assertEqual(cart_item.quantity, 2)
        
        # Test adding same product again
        cart_item = CartService.add_to_cart(self.product1.id, 1)
        self.assertEqual(cart_item.quantity, 3)
    
    def test_get_cart_summary(self):
        """Test getting cart summary."""
        with self.client.session_transaction() as sess:
            sess['cart_session_id'] = 'test-session-456'
        
        # Add items to cart
        CartService.add_to_cart(self.product1.id, 2)
        CartService.add_to_cart(self.product2.id, 1)
        
        summary = CartService.get_cart_summary()
        
        self.assertEqual(summary['total_items'], 3)
        self.assertEqual(summary['total_price'], 99.97)  # (29.99 * 2) + (39.99 * 1)
        self.assertEqual(len(summary['items']), 2)
    
    def test_update_cart_item(self):
        """Test updating cart item quantity."""
        with self.client.session_transaction() as sess:
            sess['cart_session_id'] = 'test-session-789'
        
        cart_item = CartService.add_to_cart(self.product1.id, 2)
        
        # Update quantity
        updated_item = CartService.update_cart_item(cart_item.id, 5)
        self.assertEqual(updated_item.quantity, 5)
        
        # Test removing item by setting quantity to 0
        CartService.update_cart_item(cart_item.id, 0)
        cart_item = CartItem.query.get(cart_item.id)
        self.assertIsNone(cart_item)
    
    def test_remove_from_cart(self):
        """Test removing item from cart."""
        with self.client.session_transaction() as sess:
            sess['cart_session_id'] = 'test-session-101'
        
        cart_item = CartService.add_to_cart(self.product1.id, 2)
        
        # Remove item
        result = CartService.remove_from_cart(cart_item.id)
        self.assertTrue(result)
        
        # Verify item is removed
        cart_item = CartItem.query.get(cart_item.id)
        self.assertIsNone(cart_item)
    
    def test_clear_cart(self):
        """Test clearing entire cart."""
        with self.client.session_transaction() as sess:
            sess['cart_session_id'] = 'test-session-202'
        
        # Add items to cart
        CartService.add_to_cart(self.product1.id, 2)
        CartService.add_to_cart(self.product2.id, 1)
        
        # Clear cart
        result = CartService.clear_cart()
        self.assertTrue(result)
        
        # Verify cart is empty
        summary = CartService.get_cart_summary()
        self.assertEqual(summary['total_items'], 0)
        self.assertEqual(summary['total_price'], 0)
    
    def test_create_order(self):
        """Test creating order from cart."""
        with self.client.session_transaction() as sess:
            sess['cart_session_id'] = 'test-session-303'
        
        # Add items to cart
        CartService.add_to_cart(self.product1.id, 2)
        CartService.add_to_cart(self.product2.id, 1)
        
        customer_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '123-456-7890',
            'address': '123 Main St, City, State 12345'
        }
        
        order = CartService.create_order(customer_data)
        
        self.assertIsNotNone(order)
        self.assertEqual(order.customer_name, 'John Doe')
        self.assertEqual(order.customer_email, 'john@example.com')
        self.assertEqual(order.total_amount, 99.97)
        self.assertEqual(len(order.items), 2)
        
        # Verify cart is cleared after order
        summary = CartService.get_cart_summary()
        self.assertEqual(summary['total_items'], 0)
    
    def test_home_page(self):
        """Test home page loads correctly."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Products', response.data)
    
    def test_product_detail_page(self):
        """Test product detail page loads correctly."""
        response = self.client.get(f'/product/{self.product1.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.product1.name.encode(), response.data)
    
    def test_cart_page(self):
        """Test cart page loads correctly."""
        response = self.client.get('/cart/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Shopping Cart', response.data)
    
    def test_add_to_cart_api(self):
        """Test add to cart API endpoint."""
        response = self.client.post('/api/add-to-cart',
                                  data=json.dumps({
                                      'product_id': self.product1.id,
                                      'quantity': 2
                                  }),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['cart_summary']['total_items'], 2)
    
    def test_cart_summary_api(self):
        """Test cart summary API endpoint."""
        with self.client.session_transaction() as sess:
            sess['cart_session_id'] = 'test-session-api'
        
        # Add item to cart
        CartService.add_to_cart(self.product1.id, 3)
        
        response = self.client.get('/api/cart-summary')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['total_items'], 3)
        self.assertEqual(data['total_price'], 89.97)  # 29.99 * 3

if __name__ == '__main__':
    unittest.main()
