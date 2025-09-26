#!/usr/bin/env python3
"""
Database initialization script for Shopping Cart Application
Run this script to create the database tables and populate with sample data.
"""

import os
import sys
from app import create_app, db
from app.models import User, Product
from app.utils import load_sample_products

def init_database():
    """Initialize database with tables and sample data."""
    app = create_app()
    
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("✓ Database tables created successfully!")
        
        # Check if products already exist
        if Product.query.count() > 0:
            print("✓ Products already exist in database.")
        else:
            print("Loading sample products...")
            sample_products = load_sample_products()
            
            if not sample_products:
                print("⚠ No sample products found in data/products.json")
            else:
                # Add sample products to database
                for product_data in sample_products:
                    product = Product(
                        name=product_data['name'],
                        description=product_data['description'],
                        price=product_data['price'],
                        stock_quantity=product_data['stock_quantity'],
                        image_url=product_data.get('image_url'),
                        category=product_data.get('category')
                    )
                    db.session.add(product)
                
                db.session.commit()
                print(f"✓ Added {len(sample_products)} sample products to database!")
        
        # Create a sample admin user if no users exist
        if User.query.count() == 0:
            print("Creating sample admin user...")
            admin_user = User(
                username='admin',
                email='admin@example.com',
                first_name='Admin',
                last_name='User'
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()
            print("✓ Created sample admin user (username: admin, password: admin123)")
        
        # Display summary
        total_products = Product.query.count()
        total_users = User.query.count()
        print(f"\nDatabase initialization complete!")
        print(f"Total products in database: {total_products}")
        print(f"Total users in database: {total_users}")

def reset_database():
    """Reset database by dropping and recreating all tables."""
    app = create_app()
    
    with app.app_context():
        print("Dropping all database tables...")
        db.drop_all()
        print("✓ All tables dropped!")
        
        print("Recreating database tables...")
        db.create_all()
        print("✓ Database tables recreated!")
        
        # Reload sample data
        init_database()

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'reset':
        reset_database()
    else:
        init_database()
