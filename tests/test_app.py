import pytest
from app import create_app

@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app = create_app()
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        yield client

def test_hello_endpoint(client):
    """Test the root endpoint returns hello message."""
    response = client.get('/')
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Hello, World!'
    assert data['status'] == 'success'

def test_health_endpoint(client):
    """Test the health endpoint returns 200 OK."""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert data['message'] == 'Service is running'

def test_greet_endpoint_with_name(client):
    """Test the greet endpoint with a specific name."""
    response = client.get('/greet?name=Alice')
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Hello, Alice!'
    assert data['status'] == 'success'

def test_greet_defaults_to_world(client):
    """Test the greet endpoint defaults to 'World' when no name is provided."""
    response = client.get('/greet')
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Hello, World!'
    assert data['status'] == 'success'        

def test_greet_endpoint_with_empty_name(client):
    """Test the greet endpoint with an empty name parameter."""
    response = client.get('/greet?name=')
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Hello, !'
    assert data['status'] == 'success'

def test_greet_endpoint_with_special_characters(client):
    """Test the greet endpoint with special characters in the name."""
    response = client.get('/greet?name=John%20Doe')
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Hello, John Doe!'
    assert data['status'] == 'success'                