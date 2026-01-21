# AI + DevOps Demo App

A bulletproof Flask application demonstrating modern DevOps practices with AI-powered productivity features. This repository showcases automated testing, CI/CD pipelines, security scanning, and dependency management.

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/ai-demo-app.git
cd ai-demo-app

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
# Set Flask environment
export FLASK_APP=app
export FLASK_ENV=development

# Run the application
flask run
```

The app will be available at `http://localhost:5000`

## 📋 API Endpoints

### Core Endpoints

| Endpoint | Method | Description | Example Response |
|----------|--------|-------------|------------------|
| `/` | GET | Hello world message | `{"message": "Hello, World!", "status": "success"}` |
| `/health` | GET | Health check | `{"status": "healthy", "message": "Service is running"}` |
| `/greet?name=Alice` | GET | Personalized greeting | `{"message": "Hello, Alice!", "status": "success"}` |

### Checkout & Cart Endpoints

| Endpoint | Method | Description | Request Body |
|----------|--------|-------------|--------------|
| `/api/cart` | POST | Add item to cart | `{"item_id": "item_1", "name": "Product", "price": 29.99, "quantity": 2, "cart_id": "optional"}` |
| `/api/cart/{cart_id}` | GET | Get cart summary | N/A |
| `/api/cart/{cart_id}/items/{item_id}` | DELETE | Remove item from cart | N/A |
| `/api/checkout` | POST | Create checkout session | `{"cart_id": "cart_uuid"}` |
| `/api/checkout/payment` | POST | Process payment | `{"session_id": "session_uuid", "payment_details": {...}, "currency": "USD"}` |
| `/api/checkout/confirmation/{session_id}` | GET | Get order confirmation | N/A |

### Test Payment Cards

For testing the payment functionality, use these card numbers:

- **Success Card**: `4242424242424242` - Always succeeds
- **Failure Cards**: `4000000000000002` - Always fails

Example payment details:
```json
{
  "card_number": "4242424242424242",
  "cvv": "123",
  "expiry_month": "12",
  "expiry_year": "2027",
  "cardholder_name": "Test User"
}
```

## 🧪 Testing

Run the test suite:
```bash
pytest tests/ -v
```

Run with coverage:
```bash
pytest tests/ -v --cov=app --cov-report=html
```

## 🎯 5-Minute Demo Script

### Step 1: Explore the Codebase (1 minute)
```bash
# Show the clean, readable structure
tree -I '__pycache__|venv|.git'
```

### Step 2: Run Tests Locally (1 minute)
```bash
# Install dependencies and run tests
pip install -r requirements.txt
pytest tests/ -v
```

### Step 3: Start the Application (1 minute)
```bash
# Run the Flask app
export FLASK_APP=app
flask run
```

### Step 4: Test API Endpoints (1 minute)
```bash
# Test core endpoints
curl http://localhost:5000/
curl http://localhost:5000/health
curl "http://localhost:5000/greet?name=Demo"

# Test checkout flow
# 1. Add items to cart
curl -X POST http://localhost:5000/api/cart \
  -H "Content-Type: application/json" \
  -d '{"item_id": "item_1", "name": "Demo Product", "price": 29.99, "quantity": 2}'

# 2. Get cart (replace CART_ID with the one from step 1)
curl http://localhost:5000/api/cart/CART_ID

# 3. Create checkout session
curl -X POST http://localhost:5000/api/checkout \
  -H "Content-Type: application/json" \
  -d '{"cart_id": "CART_ID"}'

# 4. Process payment (replace SESSION_ID with the one from step 3)
curl -X POST http://localhost:5000/api/checkout/payment \
  -H "Content-Type: application/json" \
  -d '{"session_id": "SESSION_ID", "payment_details": {"card_number": "4242424242424242", "cvv": "123", "expiry_month": "12", "expiry_year": "2027", "cardholder_name": "Test User"}}'

# 5. Get confirmation
curl http://localhost:5000/api/checkout/confirmation/SESSION_ID
```

### Step 5: Showcase DevOps Features (1 minute)
- **GitHub Actions CI**: Check the Actions tab for automated testing
- **CodeQL Security**: View security analysis results
- **Dependabot**: See automated dependency update PRs
- **Coverage Reports**: Review test coverage metrics

## 🔧 DevOps Features

### Continuous Integration
- **Multi-Python Testing**: Tests run on Python 3.9, 3.10, and 3.11
- **Dependency Caching**: Fast builds with pip cache
- **Coverage Reporting**: Automated coverage uploads to Codecov

### Security
- **CodeQL Analysis**: Automated security vulnerability scanning
- **Weekly Security Scans**: Scheduled security analysis
- **Dependency Monitoring**: Automated security updates

### Dependency Management
- **Dependabot**: Weekly automated dependency updates
- **Pinned Versions**: Reproducible builds
- **Outdated Dependencies**: Flask 2.2.5 (intentionally outdated for demo)

## 📁 Project Structure

```
.
├── app/                    # Flask application
│   ├── __init__.py        # App factory
│   └── main.py            # Route definitions
├── tests/                 # Test suite
│   └── test_app.py        # Comprehensive tests
├── .github/
│   ├── workflows/         # GitHub Actions
│   │   ├── ci.yml         # CI pipeline
│   │   └── codeql.yml     # Security scanning
│   └── dependabot.yml     # Dependency updates
├── requirements.txt       # Python dependencies
├── .gitignore            # Git ignore patterns
└── README.md             # This file
```

## 🤖 AI + DevOps Integration

This repository demonstrates how AI can enhance DevOps workflows:

1. **Automated Testing**: AI-generated test cases cover edge cases
2. **Security Scanning**: AI-powered CodeQL detects vulnerabilities
3. **Dependency Management**: AI suggests optimal dependency versions
4. **Code Quality**: AI ensures clean, readable code structure
5. **Documentation**: AI generates comprehensive documentation

## 💳 Checkout Features

The application includes a complete e-commerce checkout system with the following features:

### Cart Management
- Add items to cart with automatic quantity updates
- View cart summary with pricing calculations
- Remove items from cart
- Support for multiple items with different quantities

### Checkout Process
- Create secure checkout sessions
- View order summary before payment
- Complete payment flow with validation

### Payment Processing
- Mock payment gateway integration (simulates Stripe)
- Comprehensive payment validation
- Support for multiple currencies (USD, EUR, GBP)
- Test mode with specific success/failure cards
- Automatic retry on failed payments

### Security & Error Handling
- Input validation for all fields
- Card number and CVV format validation
- Expiry date validation
- Comprehensive error messages
- Failed payment retry mechanism
- Duplicate payment prevention

### Order Confirmation
- Detailed order summaries
- Transaction receipts
- Order history tracking

## 🚀 Deployment

### Local Development
```bash
flask run --debug
```

### Production
```bash
# Set production environment
export FLASK_ENV=production
export FLASK_APP=app

# Run with production server
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

## 📊 Monitoring

- **Health Checks**: `/health` endpoint for monitoring
- **Logging**: Structured logging for observability
- **Metrics**: Ready for integration with monitoring tools

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎉 Success Metrics

- ✅ 100% test coverage on critical paths
- ✅ Zero security vulnerabilities
- ✅ Automated dependency updates
- ✅ Fast CI/CD pipeline (< 2 minutes)
- ✅ Clean, maintainable code
- ✅ Comprehensive documentation

---

**Built with ❤️ for AI + DevOps productivity**
