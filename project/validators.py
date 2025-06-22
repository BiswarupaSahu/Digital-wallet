from decimal import Decimal, InvalidOperation

def validate_amount(amount):
    """Validate that amount is a positive number"""
    try:
        amount = Decimal(str(amount))
        if amount <= 0:
            return False, "Amount must be positive"
        if amount > Decimal('999999.99'):
            return False, "Amount exceeds maximum limit"
        return True, amount
    except (InvalidOperation, ValueError, TypeError):
        return False, "Invalid amount format"

def validate_username(username):
    """Validate username format"""
    if not username or not isinstance(username, str):
        return False, "Username is required"
    
    username = username.strip()
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    if len(username) > 50:
        return False, "Username must be less than 50 characters"
    if not username.replace('_', '').replace('-', '').isalnum():
        return False, "Username can only contain letters, numbers, underscores, and hyphens"
    
    return True, username

def validate_password(password):
    """Validate password strength"""
    if not password or not isinstance(password, str):
        return False, "Password is required"
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    if len(password) > 100:
        return False, "Password must be less than 100 characters"
    
    return True, password

def validate_product_data(data):
    """Validate product creation data"""
    errors = []
    
    if not data.get('name') or not isinstance(data['name'], str):
        errors.append("Product name is required")
    elif len(data['name'].strip()) < 2:
        errors.append("Product name must be at least 2 characters long")
    
    if 'price' not in data:
        errors.append("Product price is required")
    else:
        is_valid, result = validate_amount(data['price'])
        if not is_valid:
            errors.append(f"Invalid price: {result}")
    
    return len(errors) == 0, errors