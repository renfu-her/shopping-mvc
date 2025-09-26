#!/usr/bin/env python3
"""
Database initialization script for Shopping Cart application.

Run this script to create the database tables and populate with sample data.
"""

import os
import sys
from app import create_app, db
from app.models import User, Category, Product, ProductImage
from app.utils import load_sample_products

def init_database():
    """Initialize database with tables and sample data."""
    app = create_app()
    
    with app.app_context():
        try:
            # Create all tables
            print("Creating database tables...")
            db.create_all()
            print("✓ Database tables created successfully!")
            
            # Create sample categories first
            if Category.query.count() == 0:
                print("Creating sample categories...")
                categories_data = [
                    {'name': 'Electronics', 'description': 'Electronic devices and gadgets'},
                    {'name': 'Clothing', 'description': 'Fashion and apparel'},
                    {'name': 'Home & Kitchen', 'description': 'Home improvement and kitchen items'},
                    {'name': 'Sports & Fitness', 'description': 'Sports equipment and fitness gear'},
                    {'name': 'Accessories', 'description': 'Fashion accessories and jewelry'}
                ]
                
                for cat_data in categories_data:
                    category = Category(name=cat_data['name'], description=cat_data['description'])
                    db.session.add(category)
                
                db.session.commit()
                print(f"✓ Created {len(categories_data)} sample categories")
            else:
                print("✓ Categories already exist in database.")
            
            # Load and add sample products
            if Product.query.count() == 0:
                print("Loading sample products...")
                sample_products = load_sample_products()
                
                if not sample_products:
                    print("⚠ No sample products found in data/products.json")
                else:
                    # Add sample products to database
                    for product_data in sample_products:
                        # Find category by name
                        category = None
                        if 'category' in product_data:
                            category = Category.query.filter_by(name=product_data['category']).first()
                        
                        product = Product(
                            name=product_data['name'],
                            description=product_data['description'],
                            price=product_data['price'],
                            stock_quantity=product_data['stock_quantity'],
                            category_id=category.id if category else None
                        )
                        db.session.add(product)
                    
                    db.session.commit()
                    print(f"✓ Added {len(sample_products)} sample products to database!")
            else:
                print("✓ Products already exist in database.")
            
            # Create a sample admin user if no users exist
            if User.query.count() == 0:
                print("Creating sample admin user...")
                admin_user = User(
                    username='admin',
                    email='admin@example.com',
                    first_name='Admin',
                    last_name='User',
                    is_admin=True
                )
                admin_user.set_password('admin123')
                db.session.add(admin_user)
                db.session.commit()
                print("✓ Created sample admin user (username: admin, password: admin123)")
            else:
                print("✓ Users already exist in database.")
            
            # Display summary
            total_products = Product.query.count()
            total_users = User.query.count()
            total_categories = Category.query.count()
            print(f"\nDatabase initialization complete!")
            print(f"Total products in database: {total_products}")
            print(f"Total categories in database: {total_categories}")
            print(f"Total users in database: {total_users}")
            
        except Exception as e:
            print(f"❌ Error initializing database: {e}")
            db.session.rollback()
            sys.exit(1)

def reset_database():
    """Reset database by dropping and recreating all tables."""
    app = create_app()
    
    with app.app_context():
        try:
            print("Dropping all tables...")
            db.drop_all()
            print("✓ All tables dropped successfully!")
            
            print("Recreating tables...")
            db.create_all()
            print("✓ All tables recreated successfully!")
            
        except Exception as e:
            print(f"❌ Error resetting database: {e}")
            sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'reset':
        print("🔄 Resetting database...")
        reset_database()
        print("✓ Database reset complete!")
    else:
        print("🚀 Initializing database...")
        init_database()
        print("✓ Database initialization complete!")