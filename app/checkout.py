"""
Checkout module for handling cart and payment operations.
"""
from flask import Blueprint, jsonify, request
from datetime import datetime
import uuid
import secrets

checkout_bp = Blueprint('checkout', __name__)

# In-memory storage for demonstration (in production, use a database)
carts = {}
checkout_sessions = {}
payment_transactions = {}

# Mock payment gateway configuration
PAYMENT_GATEWAY_CONFIG = {
    'test_mode': True,
    'supported_currencies': ['USD', 'EUR', 'GBP'],
    'mock_success_rate': 0.9  # 90% success rate for demo
}


class CartItem:
    """Represents an item in the shopping cart."""
    
    def __init__(self, item_id, name, price, quantity=1):
        self.item_id = item_id
        self.name = name
        self.price = price
        self.quantity = quantity
        self.added_at = datetime.utcnow().isoformat()
    
    def to_dict(self):
        return {
            'item_id': self.item_id,
            'name': self.name,
            'price': self.price,
            'quantity': self.quantity,
            'subtotal': self.price * self.quantity,
            'added_at': self.added_at
        }


class Cart:
    """Represents a shopping cart."""
    
    def __init__(self, cart_id):
        self.cart_id = cart_id
        self.items = []
        self.created_at = datetime.utcnow().isoformat()
        self.updated_at = datetime.utcnow().isoformat()
    
    def add_item(self, item_id, name, price, quantity=1):
        """Add an item to the cart or update quantity if it already exists."""
        for item in self.items:
            if item.item_id == item_id:
                item.quantity += quantity
                self.updated_at = datetime.utcnow().isoformat()
                return item
        
        new_item = CartItem(item_id, name, price, quantity)
        self.items.append(new_item)
        self.updated_at = datetime.utcnow().isoformat()
        return new_item
    
    def remove_item(self, item_id):
        """Remove an item from the cart."""
        self.items = [item for item in self.items if item.item_id != item_id]
        self.updated_at = datetime.utcnow().isoformat()
    
    def get_total(self):
        """Calculate the total price of items in the cart."""
        return sum(item.price * item.quantity for item in self.items)
    
    def get_item_count(self):
        """Get the total number of items in the cart."""
        return sum(item.quantity for item in self.items)
    
    def to_dict(self):
        return {
            'cart_id': self.cart_id,
            'items': [item.to_dict() for item in self.items],
            'total': self.get_total(),
            'item_count': self.get_item_count(),
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }


class CheckoutSession:
    """Represents a checkout session."""
    
    def __init__(self, session_id, cart_id):
        self.session_id = session_id
        self.cart_id = cart_id
        self.status = 'pending'  # pending, completed, failed, expired
        self.created_at = datetime.utcnow().isoformat()
        self.updated_at = datetime.utcnow().isoformat()
        self.payment_details = None
        self.transaction_id = None
    
    def to_dict(self):
        return {
            'session_id': self.session_id,
            'cart_id': self.cart_id,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'transaction_id': self.transaction_id
        }


def get_or_create_cart(cart_id=None):
    """Get an existing cart or create a new one."""
    if cart_id and cart_id in carts:
        return carts[cart_id]
    
    new_cart_id = cart_id or str(uuid.uuid4())
    cart = Cart(new_cart_id)
    carts[new_cart_id] = cart
    return cart


def validate_payment_details(payment_details):
    """Validate payment details (mock validation)."""
    required_fields = ['card_number', 'cvv', 'expiry_month', 'expiry_year', 'cardholder_name']
    
    for field in required_fields:
        if field not in payment_details or not payment_details[field]:
            return False, f"Missing required field: {field}"
    
    # Basic validation for demo purposes
    card_number = str(payment_details['card_number']).replace(' ', '')
    if not card_number.isdigit() or len(card_number) < 13 or len(card_number) > 19:
        return False, "Invalid card number format"
    
    cvv = str(payment_details['cvv'])
    if not cvv.isdigit() or len(cvv) not in [3, 4]:
        return False, "Invalid CVV format"
    
    try:
        expiry_month = int(payment_details['expiry_month'])
        expiry_year = int(payment_details['expiry_year'])
        
        if not (1 <= expiry_month <= 12):
            return False, "Invalid expiry month"
        
        current_year = datetime.utcnow().year
        current_month = datetime.utcnow().month
        
        # Check if card is expired
        if expiry_year < current_year:
            return False, "Card has expired"
        
        if expiry_year == current_year and expiry_month < current_month:
            return False, "Card has expired"
        
        # Check if expiry year is too far in the future
        if expiry_year > current_year + 20:
            return False, "Invalid expiry year"
    except (ValueError, TypeError):
        return False, "Invalid expiry date format"
    
    return True, None


def process_payment_mock(amount, payment_details, currency='USD'):
    """Mock payment processing (simulates payment gateway)."""
    # Validate payment details
    is_valid, error_message = validate_payment_details(payment_details)
    if not is_valid:
        return {
            'success': False,
            'error': error_message,
            'transaction_id': None
        }
    
    # Check currency support
    if currency not in PAYMENT_GATEWAY_CONFIG['supported_currencies']:
        return {
            'success': False,
            'error': f"Currency {currency} not supported",
            'transaction_id': None
        }
    
    # Simulate payment processing with mock success rate
    # For demo purposes, we'll make it deterministic based on card number
    card_number = str(payment_details['card_number']).replace(' ', '')
    
    # Special test card numbers
    if card_number == '4242424242424242':  # Success test card
        success = True
    elif card_number.startswith('4000000000000'):  # Failure test cards
        success = False
    else:
        # Use a deterministic approach based on card number
        success = int(card_number[-1]) % 10 >= 1  # 90% success rate
    
    if success:
        transaction_id = f"txn_{uuid.uuid4().hex[:16]}"
        payment_transactions[transaction_id] = {
            'amount': amount,
            'currency': currency,
            'status': 'completed',
            'timestamp': datetime.utcnow().isoformat(),
            'card_last4': card_number[-4:]
        }
        return {
            'success': True,
            'transaction_id': transaction_id,
            'message': 'Payment processed successfully'
        }
    else:
        return {
            'success': False,
            'error': 'Payment declined by bank',
            'transaction_id': None
        }


# API Endpoints

@checkout_bp.route('/api/cart', methods=['POST'])
def add_to_cart():
    """Add an item to the cart."""
    data = request.get_json()
    
    # Validate required fields
    if not data or 'item_id' not in data or 'name' not in data or 'price' not in data:
        return jsonify({
            'status': 'error',
            'message': 'Missing required fields: item_id, name, price'
        }), 400
    
    try:
        price = float(data['price'])
        if price <= 0:
            return jsonify({
                'status': 'error',
                'message': 'Price must be greater than 0'
            }), 400
    except (ValueError, TypeError):
        return jsonify({
            'status': 'error',
            'message': 'Invalid price format'
        }), 400
    
    quantity = data.get('quantity', 1)
    try:
        quantity = int(quantity)
        if quantity <= 0:
            return jsonify({
                'status': 'error',
                'message': 'Quantity must be greater than 0'
            }), 400
    except (ValueError, TypeError):
        return jsonify({
            'status': 'error',
            'message': 'Invalid quantity format'
        }), 400
    
    # Get or create cart
    cart_id = data.get('cart_id')
    cart = get_or_create_cart(cart_id)
    
    # Add item to cart
    item = cart.add_item(
        item_id=data['item_id'],
        name=data['name'],
        price=price,
        quantity=quantity
    )
    
    return jsonify({
        'status': 'success',
        'message': 'Item added to cart',
        'cart': cart.to_dict(),
        'item': item.to_dict()
    }), 200


@checkout_bp.route('/api/cart/<cart_id>', methods=['GET'])
def get_cart(cart_id):
    """Get cart summary."""
    if cart_id not in carts:
        return jsonify({
            'status': 'error',
            'message': 'Cart not found'
        }), 404
    
    cart = carts[cart_id]
    return jsonify({
        'status': 'success',
        'cart': cart.to_dict()
    }), 200


@checkout_bp.route('/api/cart/<cart_id>/items/<item_id>', methods=['DELETE'])
def remove_from_cart(cart_id, item_id):
    """Remove an item from the cart."""
    if cart_id not in carts:
        return jsonify({
            'status': 'error',
            'message': 'Cart not found'
        }), 404
    
    cart = carts[cart_id]
    cart.remove_item(item_id)
    
    return jsonify({
        'status': 'success',
        'message': 'Item removed from cart',
        'cart': cart.to_dict()
    }), 200


@checkout_bp.route('/api/checkout', methods=['POST'])
def create_checkout_session():
    """Initialize a checkout session."""
    data = request.get_json()
    
    if not data or 'cart_id' not in data:
        return jsonify({
            'status': 'error',
            'message': 'Missing required field: cart_id'
        }), 400
    
    cart_id = data['cart_id']
    
    if cart_id not in carts:
        return jsonify({
            'status': 'error',
            'message': 'Cart not found'
        }), 404
    
    cart = carts[cart_id]
    
    if len(cart.items) == 0:
        return jsonify({
            'status': 'error',
            'message': 'Cannot checkout with an empty cart'
        }), 400
    
    # Create checkout session
    session_id = str(uuid.uuid4())
    session = CheckoutSession(session_id, cart_id)
    checkout_sessions[session_id] = session
    
    return jsonify({
        'status': 'success',
        'message': 'Checkout session created',
        'session': session.to_dict(),
        'cart': cart.to_dict()
    }), 200


@checkout_bp.route('/api/checkout/payment', methods=['POST'])
def process_payment():
    """Process payment for a checkout session."""
    data = request.get_json()
    
    # Validate required fields
    if not data or 'session_id' not in data or 'payment_details' not in data:
        return jsonify({
            'status': 'error',
            'message': 'Missing required fields: session_id, payment_details'
        }), 400
    
    session_id = data['session_id']
    
    if session_id not in checkout_sessions:
        return jsonify({
            'status': 'error',
            'message': 'Checkout session not found'
        }), 404
    
    session = checkout_sessions[session_id]
    
    if session.status == 'completed':
        return jsonify({
            'status': 'error',
            'message': 'Payment already processed for this session'
        }), 400
    
    # Get cart
    cart = carts.get(session.cart_id)
    if not cart:
        return jsonify({
            'status': 'error',
            'message': 'Cart not found'
        }), 404
    
    # Process payment
    amount = cart.get_total()
    currency = data.get('currency', 'USD')
    payment_details = data['payment_details']
    
    payment_result = process_payment_mock(amount, payment_details, currency)
    
    if payment_result['success']:
        session.status = 'completed'
        session.transaction_id = payment_result['transaction_id']
        session.updated_at = datetime.utcnow().isoformat()
        
        return jsonify({
            'status': 'success',
            'message': payment_result['message'],
            'session': session.to_dict(),
            'transaction_id': payment_result['transaction_id'],
            'redirect_url': f'/api/checkout/confirmation/{session_id}'
        }), 200
    else:
        session.status = 'failed'
        session.updated_at = datetime.utcnow().isoformat()
        
        return jsonify({
            'status': 'error',
            'message': payment_result['error'],
            'session': session.to_dict(),
            'retry_allowed': True
        }), 400


@checkout_bp.route('/api/checkout/confirmation/<session_id>', methods=['GET'])
def get_confirmation(session_id):
    """Get confirmation details for a completed checkout."""
    if session_id not in checkout_sessions:
        return jsonify({
            'status': 'error',
            'message': 'Checkout session not found'
        }), 404
    
    session = checkout_sessions[session_id]
    
    if session.status != 'completed':
        return jsonify({
            'status': 'error',
            'message': f'Checkout not completed. Current status: {session.status}'
        }), 400
    
    # Get cart details
    cart = carts.get(session.cart_id)
    if not cart:
        return jsonify({
            'status': 'error',
            'message': 'Cart information not available'
        }), 404
    
    # Get transaction details
    transaction = payment_transactions.get(session.transaction_id, {})
    
    return jsonify({
        'status': 'success',
        'message': 'Order completed successfully',
        'session': session.to_dict(),
        'order_summary': {
            'items': [item.to_dict() for item in cart.items],
            'total': cart.get_total(),
            'item_count': cart.get_item_count()
        },
        'transaction': {
            'transaction_id': session.transaction_id,
            'amount': transaction.get('amount'),
            'currency': transaction.get('currency', 'USD'),
            'timestamp': transaction.get('timestamp'),
            'card_last4': transaction.get('card_last4')
        }
    }), 200
