# Digital Wallet Backend API (FastAPI)

A comprehensive backend service for a digital wallet system with user authentication, fund transfers, transaction history, and product purchases built with FastAPI.

## Features

✅ **User Management**
- User registration with secure password hashing (bcrypt)
- HTTP Basic Authentication for protected endpoints

✅ **Wallet Operations**
- Fund account (deposit money)
- Pay other users
- Check balance with optional currency conversion
- View transaction history

✅ **Product Catalog**
- Add products to global catalog
- List all available products
- Purchase products using wallet balance

✅ **Security & Validation**
- Pydantic models for input validation and serialization
- Secure password storage with bcrypt
- Protected API endpoints with dependency injection
- Comprehensive error handling

✅ **API Documentation**
- Automatic OpenAPI/Swagger documentation at `/docs`
- ReDoc documentation at `/redoc`
- Type hints and response models

## Tech Stack

- **Backend**: Python FastAPI
- **Database**: MySQL with SQLAlchemy ORM
- **Authentication**: HTTP Basic Auth with bcrypt password hashing
- **External API**: Currency conversion via currencyapi.com
- **Validation**: Pydantic models for request/response validation
- **Server**: Uvicorn ASGI server

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Database Setup

1. Install MySQL and create a database:
```sql
CREATE DATABASE wallet_db;
```

2. Run the database schema script:
```bash
mysql -u your_username -p wallet_db < database_setup.sql
```

### 3. Environment Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Update the `.env` file with your configurations:
```env
DATABASE_URL=mysql+pymysql://username:password@localhost/wallet_db
CURRENCY_API_KEY=your_currency_api_key_from_currencyapi.com
SECRET_KEY=your-secret-key-here
```

### 4. Run the Application

#### Development Mode (with auto-reload):
```bash
npm run dev
# or
uvicorn app:app --host 0.0.0.0 --port 5000 --reload
```

#### Production Mode:
```bash
npm start
# or
uvicorn app:app --host 0.0.0.0 --port 5000
```

The API will be available at `http://localhost:5000`

## API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: `http://localhost:5000/docs`
- **ReDoc**: `http://localhost:5000/redoc`

### Authentication

All protected endpoints require HTTP Basic Authentication header:
```
Authorization: Basic <base64(username:password)>
```

### Endpoints

#### 1. Register User
```http
POST /register
Content-Type: application/json

{
  "username": "john_doe",
  "password": "secure123"
}
```

#### 2. Fund Account
```http
POST /fund
Authorization: Basic <credentials>
Content-Type: application/json

{
  "amt": 10000
}
```

#### 3. Pay Another User
```http
POST /pay
Authorization: Basic <credentials>
Content-Type: application/json

{
  "to": "jane_doe",
  "amt": 500
}
```

#### 4. Check Balance
```http
GET /bal?currency=USD
Authorization: Basic <credentials>
```

#### 5. Transaction History
```http
GET /stmt
Authorization: Basic <credentials>
```

#### 6. Add Product
```http
POST /product
Authorization: Basic <credentials>
Content-Type: application/json

{
  "name": "Wireless Mouse",
  "price": 599,
  "description": "2.4 GHz wireless mouse"
}
```

#### 7. List Products
```http
GET /product
```

#### 8. Buy Product
```http
POST /buy
Authorization: Basic <credentials>
Content-Type: application/json

{
  "product_id": 1
}
```

## Sample Usage with curl

### Register a new user
```bash
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "password123"}'
```

### Fund account
```bash
curl -X POST http://localhost:5000/fund \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic $(echo -n 'alice:password123' | base64)" \
  -d '{"amt": 5000}'
```

### Check balance in USD
```bash
curl -X GET "http://localhost:5000/bal?currency=USD" \
  -H "Authorization: Basic $(echo -n 'alice:password123' | base64)"
```

### Pay another user
```bash
curl -X POST http://localhost:5000/pay \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic $(echo -n 'alice:password123' | base64)" \
  -d '{"to": "bob", "amt": 100}'
```

## FastAPI Advantages

### 1. **Automatic API Documentation**
- Interactive Swagger UI at `/docs`
- Alternative ReDoc interface at `/redoc`
- Automatically generated from code annotations

### 2. **Type Safety & Validation**
- Pydantic models for request/response validation
- Automatic data serialization/deserialization
- Runtime type checking and validation

### 3. **Modern Python Features**
- Full support for Python type hints
- Async/await support for better performance
- Dependency injection system

### 4. **Performance**
- Built on Starlette for high performance
- Async support for concurrent requests
- Faster than Flask in most benchmarks

### 5. **Developer Experience**
- Excellent IDE support with autocomplete
- Clear error messages and validation
- Easy testing with TestClient

## Error Handling

FastAPI provides detailed error responses with proper HTTP status codes:

```json
{
  "error": "Error description"
}
```

Common HTTP status codes:
- `200`: Success
- `201`: Created
- `400`: Bad Request (validation errors)
- `401`: Unauthorized (authentication required)
- `404`: Not Found
- `422`: Unprocessable Entity (validation error)
- `500`: Internal Server Error

## Input Validation

FastAPI uses Pydantic models for automatic input validation:

- **Type checking**: Ensures correct data types
- **Range validation**: Min/max values for numbers
- **String validation**: Length limits, pattern matching
- **Custom validators**: Business logic validation

## Currency Conversion

The API supports currency conversion using currencyapi.com. If no API key is provided, it falls back to approximate exchange rates:

- USD: 1 INR = 0.012 USD
- EUR: 1 INR = 0.011 EUR
- GBP: 1 INR = 0.0095 GBP

## Security Features

- **Password Hashing**: Uses bcrypt with salt
- **Input Validation**: Pydantic models prevent invalid data
- **SQL Injection Prevention**: SQLAlchemy ORM with parameterized queries
- **Balance Validation**: Prevents negative balances and overdrafts
- **Transaction Integrity**: Database transactions ensure data consistency

## Database Schema

The system uses four main tables:
- `users`: User accounts and balances
- `transactions`: All financial transactions
- `products`: Product catalog
- `purchases`: Purchase history linking users, products, and transactions

## Testing

Run the test suite:
```bash
npm run test
# or
python -m pytest tests/ -v
```

FastAPI provides excellent testing support with `TestClient`:
- Automatic test database setup
- Easy mocking of dependencies
- Full request/response testing

## Production Deployment

For production deployment:

1. Use a production ASGI server like Uvicorn with Gunicorn workers
2. Set up proper environment variables
3. Use a managed MySQL database service
4. Implement proper logging and monitoring
5. Set up SSL/TLS certificates
6. Configure rate limiting and security headers

Example production command:
```bash
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:5000
```

## Health Check

Check if the API is running:
```bash
curl http://localhost:5000/health
```

## Migration from Flask

Key improvements in the FastAPI version:

1. **Automatic API Documentation**: No need for separate documentation
2. **Better Validation**: Pydantic models replace manual validation
3. **Type Safety**: Full type hints throughout the application
4. **Better Error Handling**: More detailed error responses
5. **Async Support**: Ready for high-concurrency scenarios
6. **Modern Architecture**: Dependency injection and better separation of concerns

## License

This project is for educational purposes as part of an API design exercise.