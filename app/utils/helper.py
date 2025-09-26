import json
import os
from decimal import Decimal
import re

def load_sample_products():
    """Load sample products from JSON file"""
    try:
        data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'products.json')
        with open(data_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

def format_currency(amount):
    """Format amount as currency"""
    if isinstance(amount, Decimal):
        amount = float(amount)
    return f"${amount:.2f}"

def validate_email(email):
    """Validate email address format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validate phone number format"""
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    # Check if it's a valid length (7-15 digits)
    return 7 <= len(digits_only) <= 15

def generate_order_number():
    """Generate a unique order number"""
    import uuid
    from datetime import datetime
    
    timestamp = datetime.now().strftime('%Y%m%d')
    unique_id = str(uuid.uuid4())[:8].upper()
    return f"ORD-{timestamp}-{unique_id}"

def calculate_tax(amount, tax_rate=0.08):
    """Calculate tax amount"""
    return amount * tax_rate

def calculate_shipping(amount, free_shipping_threshold=50):
    """Calculate shipping cost"""
    if amount >= free_shipping_threshold:
        return 0
    return 5.99  # Standard shipping cost

def sanitize_input(text):
    """Sanitize user input"""
    if not text:
        return ""
    # Remove HTML tags and escape special characters
    import html
    return html.escape(text.strip())

def paginate_query(query, page, per_page=12):
    """Paginate SQLAlchemy query"""
    return query.paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )

def get_client_ip(request):
    """Get client IP address from request"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr

def is_ajax_request(request):
    """Check if request is AJAX"""
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'

def get_pagination_info(pagination):
    """Get pagination information"""
    return {
        'page': pagination.page,
        'pages': pagination.pages,
        'per_page': pagination.per_page,
        'total': pagination.total,
        'has_prev': pagination.has_prev,
        'has_next': pagination.has_next,
        'prev_num': pagination.prev_num,
        'next_num': pagination.next_num
    }
