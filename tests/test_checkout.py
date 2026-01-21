import pytest
from app import create_app


@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app = create_app()
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        yield client


class TestCartOperations:
    """Test cart management operations."""
    
    def test_add_item_to_cart(self, client):
        """Test adding an item to the cart."""
        response = client.post('/api/cart', json={
            'item_id': 'item_1',
            'name': 'Test Product',
            'price': 29.99,
            'quantity': 2
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'cart' in data
        assert data['cart']['total'] == 59.98
        assert data['cart']['item_count'] == 2
    
    def test_add_item_with_cart_id(self, client):
        """Test adding an item to an existing cart."""
        # First item
        response1 = client.post('/api/cart', json={
            'item_id': 'item_1',
            'name': 'Product 1',
            'price': 10.00,
            'quantity': 1
        })
        
        cart_id = response1.get_json()['cart']['cart_id']
        
        # Second item to same cart
        response2 = client.post('/api/cart', json={
            'cart_id': cart_id,
            'item_id': 'item_2',
            'name': 'Product 2',
            'price': 20.00,
            'quantity': 1
        })
        
        assert response2.status_code == 200
        data = response2.get_json()
        assert data['cart']['item_count'] == 2
        assert data['cart']['total'] == 30.00
    
    def test_add_duplicate_item_increases_quantity(self, client):
        """Test adding the same item twice increases quantity."""
        # First add
        response1 = client.post('/api/cart', json={
            'item_id': 'item_1',
            'name': 'Product 1',
            'price': 15.00,
            'quantity': 1
        })
        
        cart_id = response1.get_json()['cart']['cart_id']
        
        # Add same item again
        response2 = client.post('/api/cart', json={
            'cart_id': cart_id,
            'item_id': 'item_1',
            'name': 'Product 1',
            'price': 15.00,
            'quantity': 2
        })
        
        assert response2.status_code == 200
        data = response2.get_json()
        assert data['cart']['item_count'] == 3
        assert len(data['cart']['items']) == 1  # Still one unique item
        assert data['cart']['total'] == 45.00
    
    def test_add_item_missing_fields(self, client):
        """Test adding item with missing required fields."""
        response = client.post('/api/cart', json={
            'name': 'Product'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['status'] == 'error'
        assert 'Missing required fields' in data['message']
    
    def test_add_item_invalid_price(self, client):
        """Test adding item with invalid price."""
        response = client.post('/api/cart', json={
            'item_id': 'item_1',
            'name': 'Product',
            'price': -10.00
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['status'] == 'error'
        assert 'Price must be greater than 0' in data['message']
    
    def test_add_item_invalid_quantity(self, client):
        """Test adding item with invalid quantity."""
        response = client.post('/api/cart', json={
            'item_id': 'item_1',
            'name': 'Product',
            'price': 10.00,
            'quantity': 0
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['status'] == 'error'
        assert 'Quantity must be greater than 0' in data['message']
    
    def test_get_cart(self, client):
        """Test retrieving cart details."""
        # Create a cart
        response1 = client.post('/api/cart', json={
            'item_id': 'item_1',
            'name': 'Product',
            'price': 25.00,
            'quantity': 1
        })
        
        cart_id = response1.get_json()['cart']['cart_id']
        
        # Get cart
        response2 = client.get(f'/api/cart/{cart_id}')
        
        assert response2.status_code == 200
        data = response2.get_json()
        assert data['status'] == 'success'
        assert data['cart']['cart_id'] == cart_id
        assert data['cart']['total'] == 25.00
    
    def test_get_nonexistent_cart(self, client):
        """Test getting a cart that doesn't exist."""
        response = client.get('/api/cart/nonexistent_cart_id')
        
        assert response.status_code == 404
        data = response.get_json()
        assert data['status'] == 'error'
        assert 'Cart not found' in data['message']
    
    def test_remove_item_from_cart(self, client):
        """Test removing an item from the cart."""
        # Create cart with items
        response1 = client.post('/api/cart', json={
            'item_id': 'item_1',
            'name': 'Product 1',
            'price': 10.00,
            'quantity': 1
        })
        
        cart_id = response1.get_json()['cart']['cart_id']
        
        client.post('/api/cart', json={
            'cart_id': cart_id,
            'item_id': 'item_2',
            'name': 'Product 2',
            'price': 20.00,
            'quantity': 1
        })
        
        # Remove one item
        response3 = client.delete(f'/api/cart/{cart_id}/items/item_1')
        
        assert response3.status_code == 200
        data = response3.get_json()
        assert data['status'] == 'success'
        assert data['cart']['item_count'] == 1
        assert data['cart']['total'] == 20.00
    
    def test_remove_item_from_nonexistent_cart(self, client):
        """Test removing item from a cart that doesn't exist."""
        response = client.delete('/api/cart/nonexistent/items/item_1')
        
        assert response.status_code == 404
        data = response.get_json()
        assert data['status'] == 'error'
        assert 'Cart not found' in data['message']


class TestCheckoutFlow:
    """Test checkout process."""
    
    def test_create_checkout_session(self, client):
        """Test creating a checkout session."""
        # Create cart
        response1 = client.post('/api/cart', json={
            'item_id': 'item_1',
            'name': 'Product',
            'price': 50.00,
            'quantity': 1
        })
        
        cart_id = response1.get_json()['cart']['cart_id']
        
        # Create checkout session
        response2 = client.post('/api/checkout', json={
            'cart_id': cart_id
        })
        
        assert response2.status_code == 200
        data = response2.get_json()
        assert data['status'] == 'success'
        assert 'session' in data
        assert data['session']['status'] == 'pending'
        assert data['cart']['total'] == 50.00
    
    def test_create_checkout_with_empty_cart(self, client):
        """Test creating checkout with empty cart."""
        # Create empty cart
        response1 = client.post('/api/cart', json={
            'item_id': 'item_1',
            'name': 'Product',
            'price': 10.00,
            'quantity': 1
        })
        
        cart_id = response1.get_json()['cart']['cart_id']
        
        # Remove the item
        client.delete(f'/api/cart/{cart_id}/items/item_1')
        
        # Try to checkout
        response2 = client.post('/api/checkout', json={
            'cart_id': cart_id
        })
        
        assert response2.status_code == 400
        data = response2.get_json()
        assert data['status'] == 'error'
        assert 'empty cart' in data['message']
    
    def test_create_checkout_missing_cart_id(self, client):
        """Test creating checkout without cart_id."""
        response = client.post('/api/checkout', json={})
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['status'] == 'error'
        assert 'Missing required field' in data['message']
    
    def test_create_checkout_nonexistent_cart(self, client):
        """Test creating checkout with nonexistent cart."""
        response = client.post('/api/checkout', json={
            'cart_id': 'nonexistent'
        })
        
        assert response.status_code == 404
        data = response.get_json()
        assert data['status'] == 'error'
        assert 'Cart not found' in data['message']


class TestPaymentProcessing:
    """Test payment processing."""
    
    def test_successful_payment(self, client):
        """Test successful payment processing."""
        # Create cart and checkout session
        response1 = client.post('/api/cart', json={
            'item_id': 'item_1',
            'name': 'Product',
            'price': 100.00,
            'quantity': 1
        })
        
        cart_id = response1.get_json()['cart']['cart_id']
        
        response2 = client.post('/api/checkout', json={
            'cart_id': cart_id
        })
        
        session_id = response2.get_json()['session']['session_id']
        
        # Process payment with test success card
        response3 = client.post('/api/checkout/payment', json={
            'session_id': session_id,
            'payment_details': {
                'card_number': '4242424242424242',
                'cvv': '123',
                'expiry_month': '12',
                'expiry_year': '2027',
                'cardholder_name': 'Test User'
            },
            'currency': 'USD'
        })
        
        assert response3.status_code == 200
        data = response3.get_json()
        assert data['status'] == 'success'
        assert 'transaction_id' in data
        assert 'redirect_url' in data
        assert data['session']['status'] == 'completed'
    
    def test_failed_payment(self, client):
        """Test failed payment processing."""
        # Create cart and checkout session
        response1 = client.post('/api/cart', json={
            'item_id': 'item_1',
            'name': 'Product',
            'price': 50.00,
            'quantity': 1
        })
        
        cart_id = response1.get_json()['cart']['cart_id']
        
        response2 = client.post('/api/checkout', json={
            'cart_id': cart_id
        })
        
        session_id = response2.get_json()['session']['session_id']
        
        # Process payment with test failure card
        response3 = client.post('/api/checkout/payment', json={
            'session_id': session_id,
            'payment_details': {
                'card_number': '4000000000000002',
                'cvv': '123',
                'expiry_month': '12',
                'expiry_year': '2027',
                'cardholder_name': 'Test User'
            }
        })
        
        assert response3.status_code == 400
        data = response3.get_json()
        assert data['status'] == 'error'
        assert data['retry_allowed'] == True
        assert data['session']['status'] == 'failed'
    
    def test_payment_with_invalid_card_number(self, client):
        """Test payment with invalid card number."""
        # Create cart and checkout session
        response1 = client.post('/api/cart', json={
            'item_id': 'item_1',
            'name': 'Product',
            'price': 30.00,
            'quantity': 1
        })
        
        cart_id = response1.get_json()['cart']['cart_id']
        
        response2 = client.post('/api/checkout', json={
            'cart_id': cart_id
        })
        
        session_id = response2.get_json()['session']['session_id']
        
        # Process payment with invalid card
        response3 = client.post('/api/checkout/payment', json={
            'session_id': session_id,
            'payment_details': {
                'card_number': '1234',
                'cvv': '123',
                'expiry_month': '12',
                'expiry_year': '2027',
                'cardholder_name': 'Test User'
            }
        })
        
        assert response3.status_code == 400
        data = response3.get_json()
        assert data['status'] == 'error'
        assert 'card number' in data['message'].lower()
    
    def test_payment_with_missing_fields(self, client):
        """Test payment with missing required fields."""
        # Create cart and checkout session
        response1 = client.post('/api/cart', json={
            'item_id': 'item_1',
            'name': 'Product',
            'price': 25.00,
            'quantity': 1
        })
        
        cart_id = response1.get_json()['cart']['cart_id']
        
        response2 = client.post('/api/checkout', json={
            'cart_id': cart_id
        })
        
        session_id = response2.get_json()['session']['session_id']
        
        # Process payment without CVV
        response3 = client.post('/api/checkout/payment', json={
            'session_id': session_id,
            'payment_details': {
                'card_number': '4242424242424242',
                'expiry_month': '12',
                'expiry_year': '2027',
                'cardholder_name': 'Test User'
            }
        })
        
        assert response3.status_code == 400
        data = response3.get_json()
        assert data['status'] == 'error'
    
    def test_payment_nonexistent_session(self, client):
        """Test payment with nonexistent session."""
        response = client.post('/api/checkout/payment', json={
            'session_id': 'nonexistent',
            'payment_details': {
                'card_number': '4242424242424242',
                'cvv': '123',
                'expiry_month': '12',
                'expiry_year': '2027',
                'cardholder_name': 'Test User'
            }
        })
        
        assert response.status_code == 404
        data = response.get_json()
        assert data['status'] == 'error'
        assert 'session not found' in data['message'].lower()
    
    def test_payment_already_completed(self, client):
        """Test payment for already completed session."""
        # Create cart and checkout session
        response1 = client.post('/api/cart', json={
            'item_id': 'item_1',
            'name': 'Product',
            'price': 40.00,
            'quantity': 1
        })
        
        cart_id = response1.get_json()['cart']['cart_id']
        
        response2 = client.post('/api/checkout', json={
            'cart_id': cart_id
        })
        
        session_id = response2.get_json()['session']['session_id']
        
        # First payment
        client.post('/api/checkout/payment', json={
            'session_id': session_id,
            'payment_details': {
                'card_number': '4242424242424242',
                'cvv': '123',
                'expiry_month': '12',
                'expiry_year': '2027',
                'cardholder_name': 'Test User'
            }
        })
        
        # Try to pay again
        response3 = client.post('/api/checkout/payment', json={
            'session_id': session_id,
            'payment_details': {
                'card_number': '4242424242424242',
                'cvv': '123',
                'expiry_month': '12',
                'expiry_year': '2027',
                'cardholder_name': 'Test User'
            }
        })
        
        assert response3.status_code == 400
        data = response3.get_json()
        assert data['status'] == 'error'
        assert 'already processed' in data['message']


class TestConfirmation:
    """Test order confirmation."""
    
    def test_get_confirmation(self, client):
        """Test getting confirmation for completed order."""
        # Create cart, checkout, and complete payment
        response1 = client.post('/api/cart', json={
            'item_id': 'item_1',
            'name': 'Product',
            'price': 75.00,
            'quantity': 2
        })
        
        cart_id = response1.get_json()['cart']['cart_id']
        
        response2 = client.post('/api/checkout', json={
            'cart_id': cart_id
        })
        
        session_id = response2.get_json()['session']['session_id']
        
        client.post('/api/checkout/payment', json={
            'session_id': session_id,
            'payment_details': {
                'card_number': '4242424242424242',
                'cvv': '123',
                'expiry_month': '12',
                'expiry_year': '2027',
                'cardholder_name': 'Test User'
            }
        })
        
        # Get confirmation
        response4 = client.get(f'/api/checkout/confirmation/{session_id}')
        
        assert response4.status_code == 200
        data = response4.get_json()
        assert data['status'] == 'success'
        assert 'order_summary' in data
        assert data['order_summary']['total'] == 150.00
        assert 'transaction' in data
        assert 'transaction_id' in data['transaction']
    
    def test_confirmation_for_nonexistent_session(self, client):
        """Test getting confirmation for nonexistent session."""
        response = client.get('/api/checkout/confirmation/nonexistent')
        
        assert response.status_code == 404
        data = response.get_json()
        assert data['status'] == 'error'
    
    def test_confirmation_for_incomplete_checkout(self, client):
        """Test getting confirmation for incomplete checkout."""
        # Create cart and checkout but don't complete payment
        response1 = client.post('/api/cart', json={
            'item_id': 'item_1',
            'name': 'Product',
            'price': 20.00,
            'quantity': 1
        })
        
        cart_id = response1.get_json()['cart']['cart_id']
        
        response2 = client.post('/api/checkout', json={
            'cart_id': cart_id
        })
        
        session_id = response2.get_json()['session']['session_id']
        
        # Try to get confirmation
        response3 = client.get(f'/api/checkout/confirmation/{session_id}')
        
        assert response3.status_code == 400
        data = response3.get_json()
        assert data['status'] == 'error'
        assert 'not completed' in data['message'].lower()


class TestPaymentRetry:
    """Test payment retry functionality."""
    
    def test_retry_after_failed_payment(self, client):
        """Test that payment can be retried after failure."""
        # Create cart and checkout session
        response1 = client.post('/api/cart', json={
            'item_id': 'item_1',
            'name': 'Product',
            'price': 60.00,
            'quantity': 1
        })
        
        cart_id = response1.get_json()['cart']['cart_id']
        
        response2 = client.post('/api/checkout', json={
            'cart_id': cart_id
        })
        
        session_id = response2.get_json()['session']['session_id']
        
        # First attempt with failing card
        response3 = client.post('/api/checkout/payment', json={
            'session_id': session_id,
            'payment_details': {
                'card_number': '4000000000000002',
                'cvv': '123',
                'expiry_month': '12',
                'expiry_year': '2027',
                'cardholder_name': 'Test User'
            }
        })
        
        assert response3.status_code == 400
        
        # Retry with success card
        response4 = client.post('/api/checkout/payment', json={
            'session_id': session_id,
            'payment_details': {
                'card_number': '4242424242424242',
                'cvv': '123',
                'expiry_month': '12',
                'expiry_year': '2027',
                'cardholder_name': 'Test User'
            }
        })
        
        assert response4.status_code == 200
        data = response4.get_json()
        assert data['status'] == 'success'
        assert data['session']['status'] == 'completed'
