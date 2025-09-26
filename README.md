# Shopping Cart Application

A modern e-commerce shopping cart application built with Flask, featuring user authentication, clean MVC architecture, and MySQL database integration.

## Features

- **User Authentication**: Complete user registration, login, and profile management
- **Product Catalog**: Browse products with search and category filtering
- **Shopping Cart**: Add, update, and remove items from cart (supports both anonymous and authenticated users)
- **Checkout Process**: Complete order placement with pre-filled user information
- **Order Management**: View order history and detailed order tracking
- **User Profiles**: Edit profile information and change passwords
- **Responsive Design**: Mobile-friendly interface with Bootstrap 5
- **RESTful API**: AJAX endpoints for cart operations
- **Security**: Password hashing, CSRF protection, and input validation

## Architecture

```
├── app/
│   ├── __init__.py              # Flask app factory with Flask-Login
│   ├── config.py                # Configuration settings
│   ├── controllers/             # Route handlers
│   │   ├── home.py             # Home and product routes
│   │   ├── cart.py             # Cart and checkout routes
│   │   └── auth.py             # Authentication routes
│   ├── models/                  # Database models
│   │   └── shoppingcart.py     # User, Product, Cart, Order models
│   ├── services/                # Business logic layer
│   │   └── cart_service.py     # Cart operations
│   ├── static/                  # Static assets
│   │   ├── css/style.css       # Custom Bootstrap 5 styles
│   │   ├── js/main.js          # JavaScript functionality
│   │   └── images/             # Product images
│   ├── templates/               # HTML templates
│   │   ├── layout/app.html     # Base template with auth navigation
│   │   ├── products/           # Product pages
│   │   ├── cart/               # Cart and checkout pages
│   │   └── auth/               # Authentication pages
│   ├── tests/                   # Unit tests
│   │   └── test_cart.py        # Cart and auth functionality tests
│   └── utils/                   # Utility functions
│       └── helper.py           # Helper functions
├── data/
│   └── products.json           # Sample product data
├── main.py                     # Application entry point
├── init_db.py                  # Database initialization with sample user
├── requirements.txt            # Python dependencies
├── env.example                 # Environment variables template
└── README.md                   # This file
```

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd shopping-mvc-2
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your database credentials
   ```

5. **Set up MySQL database**
   - Create a MySQL database named `shopping_cart`
   - Update the database credentials in `.env`

6. **Initialize database**
   ```bash
   python init_db.py
   ```

7. **Run the application**
   ```bash
   python main.py
   ```

The application will be available at `http://localhost:5000`

### Sample User Account
After running `init_db.py`, you can login with:
- **Username**: `admin`
- **Password**: `admin123`

## Database Schema

### Users Table
- `id`: Primary key
- `username`: Unique username
- `email`: Unique email address
- `password_hash`: Hashed password
- `first_name`: User's first name
- `last_name`: User's last name
- `phone`: Phone number (optional)
- `address`: Address (optional)
- `is_active`: Account status
- `created_at`, `updated_at`: Timestamps

### Products Table
- `id`: Primary key
- `name`: Product name
- `description`: Product description
- `price`: Product price (decimal)
- `stock_quantity`: Available stock
- `image_url`: Product image URL
- `category`: Product category
- `created_at`, `updated_at`: Timestamps

### Carts Table
- `id`: Primary key
- `user_id`: Foreign key to users (nullable for anonymous users)
- `session_id`: Session identifier (for anonymous users)
- `created_at`, `updated_at`: Timestamps

### Cart Items Table
- `id`: Primary key
- `cart_id`: Foreign key to carts
- `product_id`: Foreign key to products
- `quantity`: Item quantity
- `created_at`, `updated_at`: Timestamps

### Orders Table
- `id`: Primary key
- `order_number`: Unique order identifier
- `user_id`: Foreign key to users (nullable for guest orders)
- `customer_name`: Customer name
- `customer_email`: Customer email
- `customer_phone`: Customer phone
- `shipping_address`: Shipping address
- `status`: Order status (pending, confirmed, shipped, delivered, cancelled)
- `total_amount`: Order total
- `created_at`, `updated_at`: Timestamps

### Order Items Table
- `id`: Primary key
- `order_id`: Foreign key to orders
- `product_id`: Foreign key to products
- `quantity`: Item quantity
- `price`: Price at time of order
- `created_at`: Timestamp

## API Endpoints

### Authentication
- `GET /auth/register` - User registration page
- `POST /auth/register` - Process user registration
- `GET /auth/login` - User login page
- `POST /auth/login` - Process user login
- `GET /auth/logout` - User logout
- `GET /auth/profile` - User profile page (requires login)
- `GET /auth/edit_profile` - Edit profile page (requires login)
- `POST /auth/edit_profile` - Update profile (requires login)
- `GET /auth/change_password` - Change password page (requires login)
- `POST /auth/change_password` - Update password (requires login)
- `GET /auth/orders` - User order history (requires login)
- `GET /auth/order/<id>` - Order details (requires login)

### Cart Operations
- `POST /api/add-to-cart` - Add product to cart
- `GET /api/cart-summary` - Get cart summary
- `POST /cart/update` - Update cart item quantity
- `POST /cart/remove` - Remove item from cart
- `POST /cart/clear` - Clear entire cart

### Pages
- `GET /` - Home page with products
- `GET /product/<id>` - Product detail page
- `GET /cart/` - Shopping cart page
- `GET /cart/checkout` - Checkout page (requires login)
- `POST /cart/checkout` - Process checkout (requires login)
- `GET /cart/order/<id>` - Order confirmation
- `GET /cart/orders` - Order history (for guest users)

## Testing

Run the test suite:
```bash
python -m pytest app/tests/
```

Or run specific tests:
```bash
python app/tests/test_cart.py
```

## Configuration

The application uses environment variables for configuration. Copy `env.example` to `.env` and update the values:

- `SECRET_KEY`: Flask secret key
- `MYSQL_HOST`: MySQL host
- `MYSQL_PORT`: MySQL port
- `MYSQL_USER`: MySQL username
- `MYSQL_PASSWORD`: MySQL password
- `MYSQL_DATABASE`: MySQL database name

## Features in Detail

### User Authentication
- **Registration**: Complete user registration with validation
- **Login/Logout**: Secure authentication with Flask-Login
- **Profile Management**: Edit personal information and change passwords
- **Password Security**: Werkzeug password hashing
- **Session Management**: Remember me functionality

### Shopping Cart
- **Dual Support**: Works for both anonymous and authenticated users
- **Seamless Transition**: Anonymous users can add to cart, login required for checkout
- **Real-time Updates**: AJAX-powered cart operations
- **Persistent Storage**: Cart persists across browser sessions

### Product Management
- **Product Catalog**: Browse with pagination, search, and category filtering
- **Product Details**: Detailed product pages with image galleries
- **Stock Management**: Real-time stock quantity tracking
- **Responsive Design**: Mobile-friendly product browsing

### Order Processing
- **Complete Checkout**: Streamlined checkout process
- **Pre-filled Forms**: User information automatically populated
- **Order Tracking**: Detailed order history and status tracking
- **Order Confirmation**: Email-style order confirmation pages

### User Interface
- **Modern Design**: Bootstrap 5 with custom styling
- **Responsive Layout**: Mobile-first responsive design
- **Interactive Elements**: Dropdown menus, form validation, loading states
- **User Experience**: Intuitive navigation and user feedback

## Development

### Adding New Features
1. Create models in `app/models/`
2. Add business logic in `app/services/`
3. Create routes in `app/controllers/`
4. Add templates in `app/templates/`
5. Update static assets as needed
6. Add tests in `app/tests/`

### Database Migrations
The application uses Flask-Migrate for database migrations:
```bash
flask db init
flask db migrate -m "Description"
flask db upgrade
```

### User Management
- **Registration**: Users can register with username, email, and password
- **Authentication**: Secure login with password hashing
- **Profile Management**: Users can update their information
- **Order History**: Users can view all their orders
- **Guest Checkout**: Anonymous users can still place orders

### Security Features
- **Password Hashing**: Uses Werkzeug's secure password hashing
- **CSRF Protection**: Built-in CSRF protection for forms
- **Input Validation**: Server-side and client-side validation
- **Session Security**: Secure session management with Flask-Login
- **SQL Injection Protection**: Uses SQLAlchemy ORM for safe database queries

## Technology Stack

- **Backend**: Flask, SQLAlchemy ORM, Flask-Login
- **Database**: MySQL with PyMySQL connector
- **Frontend**: Bootstrap 5, jQuery, Font Awesome
- **Security**: Werkzeug password hashing, CSRF protection
- **Testing**: Python unittest framework

## License

This project is licensed under the MIT License.
