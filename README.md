# Django React E-Commerce Application

A full-stack e-commerce platform built with Django REST Framework for the backend and React for the frontend. This project demonstrates modern web development practices, comprehensive testing, and integration with payment processing systems.

---

## Table of Contents

1. [Overview](#overview)
2. [Technology Stack](#technology-stack)
3. [Architecture](#architecture)
4. [Project Structure](#project-structure)
5. [Installation & Setup](#installation--setup)
6. [Running the Application](#running-the-application)
7. [Database Models](#database-models)
8. [API Endpoints](#api-endpoints)
9. [Frontend Components](#frontend-components)
10. [Testing](#testing)
11. [Key Features](#key-features)
12. [Development Workflow](#development-workflow)
13. [Troubleshooting](#troubleshooting)
14. [Implementation Notes](#implementation-notes)
15. [Additional Resources](#additional-resources)

---

## Overview

This e-commerce application provides a complete shopping experience including:
- User authentication and profile management
- Product catalog with categories and filtering
- Shopping cart functionality with item variations
- Order processing and payment integration
- User-friendly React interface with responsive design
- Comprehensive API endpoints for all operations
- Full test coverage with unit, integration, and UI tests

---

## Technology Stack

### Backend Technologies

**Framework & ORM**
- **Django 3.x**: Web framework for building the API and handling server-side logic
- **Django REST Framework 3.14**: RESTful API toolkit for creating robust API endpoints
- **SQLite / PostgreSQL**: Database for data persistence

**Authentication & Authorization**
- **django-allauth**: Comprehensive authentication solution supporting email verification and social authentication
- **dj-rest-auth**: JWT token-based authentication for REST APIs
- **djangorestframework-authtoken**: Token authentication for API requests

**Additional Backend Libraries**
- **django-cors-headers**: Handles Cross-Origin Resource Sharing for frontend-backend communication
- **django-countries**: Provides country field types for shipping addresses
- **Pillow**: Image processing for product images
- **stripe**: Payment processing integration for transactions
- **gunicorn**: WSGI HTTP server for production deployments
- **python-decouple**: Environment variable management for configuration

**Code Quality & Testing**
- **pytest**: Testing framework with fixtures and plugins
- **pytest-cov**: Code coverage analysis
- **pylint**: Static code analysis
- **autopep8**: Code style formatting
- **isort**: Import statement organization

### Frontend Technologies

**Framework & Libraries**
- **React 16.8.6**: JavaScript library for building user interfaces with hooks
- **React DOM**: Rendering React components in the browser

**State Management**
- **Redux**: Predictable state management for complex application state
- **react-redux**: React bindings for Redux
- **redux-thunk**: Middleware for handling asynchronous Redux actions

**Routing & Navigation**
- **react-router-dom 5.0.1**: Client-side routing for single-page application navigation

**UI Components & Styling**
- **semantic-ui-react**: Semantic UI React components for consistent styling
- **semantic-ui-css**: CSS framework for modern, responsive design

**API Communication**
- **axios 0.19.0**: HTTP client for making requests to Django API

**Payment Integration**
- **react-stripe-elements 4.0.0**: React components for Stripe payment processing

**Build & Development**
- **react-scripts 5.0.1**: Build scripts and configuration for Create React App
- **npm**: Package manager for managing frontend dependencies

---

## Architecture

### System Overview

The application follows a classic three-tier architecture:

**Frontend Layer (React)**
- Runs on port 3000 using `npm start`
- Single-page application with Redux for state management
- Uses Axios to communicate with Django API
- Semantic UI for styling and components
- Token stored in browser local storage for authenticated requests

**Backend Layer (Django REST Framework)**
- Runs on port 8000 using `python manage.py runserver`
- Provides REST API endpoints for all operations
- Handles authentication using dj-rest-auth with token-based auth
- Manages business logic (cart, orders, payments, stock)
- Integrates with Stripe for payment processing

**Database Layer (SQLite)**
- Stores all models: users, products, orders, addresses, payments, coupons
- Default Django ORM for database operations
- Can be replaced with PostgreSQL for production

**How the Parts Connect**

When you start the application with both servers running, here's what happens:

1. Browser makes HTTP requests to `http://localhost:8000/api/` endpoints
2. Django processes the request and returns JSON responses
3. React receives the response and updates the UI
4. For authenticated requests, React includes the auth token in the header
5. Django validates the token before processing the request
6. All data is stored/retrieved from SQLite database

Essentially, React is just a client that talks to Django through HTTP - the two could even run on completely different machines in production.

### Authentication Flow

The authentication system uses token-based authentication via dj-rest-auth:

1. User fills registration form on React app (Signup component)
2. React sends POST to `/rest-auth/registration/` with credentials
3. Django creates user and returns auth token in response
4. React stores token in localStorage
5. For subsequent requests, React adds `Authorization: Token <token>` header
6. Django validates token in middleware before processing request
7. Protected endpoints return 401 if token missing or invalid


### Payment Flow (Stripe Integration)

The payment process integrates with Stripe for secure credit card processing:

1. User adds items to cart via `POST /api/add-to-cart/`
2. User navigates to Checkout component with cart items
3. User enters billing/shipping address using Address models
4. Checkout component displays Stripe card element using react-stripe-elements
5. User submits payment form with card details
6. Stripe validates card and returns a payment token (not the card itself)
7. React sends token + order details to `POST /api/checkout/`
8. Django backend receives token and uses Stripe SDK to charge the card
9. If successful, Django creates Payment record and Order is marked as ordered
10. React redirects to order confirmation with order reference code
11. User can view order history in Profile component

This approach keeps card data secure - sensitive data never touches your server.

---

## Project Structure

```
project-root/
│
├── core/                          # Main Django application
│   ├── migrations/                # Database migration files
│   ├── management/
│   │   └── commands/              # Custom Django management commands
│   ├── api/
│   │   ├── serializers.py         # DRF serializers for API
│   │   ├── views.py               # API viewsets and views
│   │   └── urls.py                # API URL routing
│   ├── templatetags/              # Custom Django template tags
│   ├── models.py                  # Database models
│   ├── views.py                   # Django views
│   ├── forms.py                   # Django forms
│   ├── urls.py                    # URL routing
│   ├── admin.py                   # Django admin configuration
│   ├── apps.py                    # Django app configuration
│   └── tests.py                   # Django app tests
│
├── home/                          # Django project configuration
│   ├── settings/
│   │   ├── base.py               # Base settings for all environments
│   │   ├── dev.py                # Development environment settings
│   │   └── prod.py               # Production environment settings
│   ├── urls.py                    # Root URL configuration
│   └── wsgi/
│       ├── dev.py                # Development WSGI application
│       └── prod.py               # Production WSGI application
│
├── src/                           # React source code
│   ├── containers/
│   │   ├── Home.js               # Home page container
│   │   ├── ProductList.js        # Product listing container
│   │   ├── ProductDetail.js      # Product detail view
│   │   ├── Checkout.js           # Checkout process
│   │   ├── OrderSummary.js       # Order summary
│   │   ├── Login.js              # Login form
│   │   ├── Signup.js             # Registration form
│   │   ├── Profile.js            # User profile
│   │   └── Layout.js             # Main layout wrapper
│   ├── store/
│   │   ├── actions/              # Redux action creators
│   │   ├── reducers/             # Redux reducers
│   │   └── utility.js            # Redux utility functions
│   ├── hoc/
│   │   └── hoc.js                # Higher-order components
│   ├── App.js                     # Root React component
│   ├── App.test.js               # App component tests
│   ├── index.js                  # React entry point
│   ├── constants.js              # Application constants
│   ├── routes.js                 # Route definitions
│   ├── utils.js                  # Utility functions
│   └── registerServiceWorker.js  # PWA service worker
│
├── tests/                         # Automated tests
│   ├── test_api_auth.py          # Authentication API tests
│   ├── test_api_checkout.py      # Checkout API tests
│   ├── test_api_products.py      # Products API tests
│   ├── test_unit.py              # Unit tests
│   ├── test_tdd_feature1_stock.py        # TDD stock feature tests
│   ├── test_tdd_feature1_refactor.py     # TDD refactor tests
│   └── test_ui_selenium.py       # Selenium UI tests
│
├── public/                        # Static files for React
│   ├── index.html                # HTML entry point
│   └── manifest.json             # PWA manifest
│
├── env/                           # Python virtual environment
│
├── manage.py                      # Django command-line tool
├── conftest.py                    # Pytest configuration
├── pytest.ini                     # Pytest settings
├── requirements.txt               # Python dependencies
├── requirements-test.txt          # Testing dependencies
├── package.json                   # Node.js dependencies
├── db.sqlite3                     # SQLite database
├── metrics_tracker.py             # Metrics and tracking utility
└── README.md                      # This file
```

---

## Installation & Setup

### Prerequisites

- Python 3.8 or higher
- Node.js 12.x or higher and npm
- Git
- Virtual environment manager (venv or virtualenv)

### Backend Setup

1. **Clone the repository and navigate to project**
   ```bash
   cd path/to/Test-Test-Automaton-Project
   ```

2. **Create and activate Python virtual environment**
   ```bash
   # On Windows
   python -m venv env
   env\Scripts\activate

   # On macOS/Linux
   python3 -m venv env
   source env/bin/activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install testing dependencies (optional)**
   ```bash
   pip install -r requirements-test.txt
   ```

5. **Configure environment variables**
   Create a `.env` file in the project root:
   ```
   DEBUG=True
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=sqlite:///db.sqlite3
   STRIPE_PUBLIC_KEY=your-stripe-public-key
   STRIPE_SECRET_KEY=your-stripe-secret-key
   ALLOWED_HOSTS=localhost,127.0.0.1
   ```

6. **Apply database migrations**
   ```bash
   python manage.py migrate
   ```

### Frontend Setup

1. **Navigate to project root** (if not already there)

2. **Install Node.js dependencies**
   ```bash
   npm install
   ```

3. **Verify installation**
   ```bash
   npm list react redux axios
   ```

---

## Running the Application

### Development Environment

**Terminal 1 - Start Django Backend**
```bash
# Make sure virtual environment is activated
env\Scripts\activate  # On Windows
source env/bin/activate  # On macOS/Linux

# Run development server (runs on http://localhost:8000)
python manage.py runserver
```

**Terminal 2 - Start React Frontend**
```bash
# Run React development server (runs on http://localhost:3000)
npm start
```

The application will:
- Backend API available at `http://localhost:8000/api/`
- Authentication endpoints available at `http://localhost:8000/rest-auth/`
- React frontend available at `http://localhost:3000`

### Production Build

1. **Build React frontend**
   ```bash
   npm run build
   ```
   This creates a `build/` directory with optimized production files.

2. **Collect static files**
   ```bash
   python manage.py collectstatic
   ```

3. **Run production server**
   ```bash
   gunicorn home.wsgi:application
   ```

---

## Database Models

### Core Models

**User (Django Built-in)**
- Provided by Django authentication system
- Fields: username, email, password, first_name, last_name, etc.

**UserProfile**
- Extends Django User model with e-commerce specific fields
- `stripe_customer_id`: Customer ID from Stripe for payment processing
- `one_click_purchasing`: Boolean flag for saved payment method preference

**Item**
- Represents products in the catalog
- Fields:
  - `title`: Product name (max 100 chars)
  - `price`: Current selling price (float)
  - `discount_price`: Optional discounted price
  - `category`: Category choice (Shirt, Sport wear, Outwear)
  - `label`: Product label/badge (primary, secondary, danger)
  - `slug`: URL-friendly identifier
  - `description`: Detailed product description
  - `image`: Product image file
  - `stock_quantity`: Available quantity in inventory

**Order**
- Represents a customer order
- Fields:
  - `user`: Foreign key to User
  - `ref_code`: Unique order reference code
  - `items`: Many-to-many relationship to OrderItem
  - `start_date`: Order creation timestamp
  - `ordered_date`: When order was completed
  - `ordered`: Boolean flag indicating completion status
  - `billing_address`: Foreign key to Address
  - `shipping_address`: Foreign key to Address
  - `payment`: Foreign key to Payment
  - `coupon`: Optional foreign key to applied Coupon

**OrderItem**
- Individual items within an order
- Fields:
  - `user`: Foreign key to User
  - `ordered`: Boolean completion status
  - `item`: Foreign key to Item
  - `quantity`: Number of items
  - `item_variations`: Many-to-many to ItemVariation

**Variation**
- Represents variation types (size, color, etc.)
- Fields:
  - `item`: Foreign key to Item
  - `name`: Variation type name (e.g., "Size", "Color")

**ItemVariation**
- Specific values for variations
- Fields:
  - `variation`: Foreign key to Variation
  - `value`: Variation value (e.g., "S", "M", "L")
  - `attachment`: Optional image for variation

**Address**
- Shipping and billing addresses
- Fields:
  - `user`: Foreign key to User
  - `street_address`: Street address
  - `apartment_address`: Apartment/suite number
  - `country`: Country selection
  - `zip`: Postal code
  - `address_type`: Billing or Shipping

**Payment**
- Records payment transactions
- Fields:
  - `user`: Foreign key to User
  - `amount`: Payment amount
  - `timestamp`: Transaction time
  - `stripe_charge_id`: Stripe transaction ID

**Coupon**
- Discount coupon codes
- Fields:
  - `code`: Coupon code (max 15 chars)
  - `discount_type`: Either 'fixed' or 'percentage'
  - `discount_value`: Amount or percentage value
  - `minimum_order_amount`: Minimum order total to use coupon
  - `expiry_date`: When coupon expires
  - `max_uses`: Maximum number of uses
  - `current_uses`: Current usage count

**Refund**
- Refund request records
- Fields:
  - `order`: Foreign key to Order
  - `reason`: Refund reason text
  - `accepted`: Boolean indicating if refund was approved
  - `email`: Customer email

---

## API Endpoints

All API endpoints require authentication via token header: `Authorization: Token <token>`

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/rest-auth/registration/` | User registration |
| POST | `/rest-auth/login/` | User login (returns token) |
| POST | `/rest-auth/logout/` | User logout |
| POST | `/rest-auth/password/reset/` | Request password reset |
| POST | `/rest-auth/password/reset/confirm/` | Confirm password reset |

### Product Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/products/` | List all products |
| GET | `/api/products/{id}/` | Retrieve single product details |

### Order & Cart Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/order-summary/` | Get current cart/order summary |
| POST | `/api/add-to-cart/` | Add item to cart |
| POST | `/api/order-item/update-quantity/` | Update item quantity in cart |
| DELETE | `/api/order-items/{id}/delete/` | Remove item from cart |
| GET | `/api/payments/` | List user's past payments |

### Checkout & Payment Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/checkout/` | Process payment via Stripe |
| POST | `/api/add-coupon/` | Apply discount coupon |
| GET | `/api/countries/` | List available countries |

### Address & User Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/user-id/` | Get current user ID |
| GET | `/api/addresses/` | List user addresses |
| POST | `/api/addresses/create/` | Create new address |
| PUT | `/api/addresses/{id}/update/` | Update address |
| DELETE | `/api/addresses/{id}/delete/` | Delete address |

---

## Frontend Components

### Container Components

**Layout**
- Main wrapper component providing header, footer, and navigation
- Manages global navigation state
- Renders child components based on routes

**Home**
- Landing page with featured products
- Category overview
- Marketing banners

**ProductList**
- Displays paginated product grid
- Filtering by category, price range
- Search functionality
- Product cards with images and prices

**ProductDetail**
- Full product information view
- Product images (gallery)
- Detailed description and specifications
- Variation selection (size, color)
- Add to cart button
- Related products

**Checkout**
- Multi-step checkout process
- Billing/shipping address forms
- Saved addresses display
- Order summary
- Stripe payment form integration

**OrderSummary**
- Displays current order details
- Shows order items, quantities, prices
- Total price calculation with tax/shipping

**Login**
- User login form
- Email/password input
- Remember me checkbox
- Link to sign up page

**Signup**
- User registration form
- Email validation
- Password strength requirements
- Terms acceptance checkbox

**Profile**
- User account information display
- Order history
- Saved addresses
- Account settings
- Password change

---

## Key Features

### User Authentication & Authorization
- User registration with email verification
- Secure login with JWT token authentication
- Social authentication support via django-allauth
- User profile management
- Password reset functionality

### Product Management
- Product catalog with detailed information
- Product categorization (Shirt, Sport wear, Outwear)
- Product variations (size, color, etc.)
- Stock inventory tracking
- Discount pricing support
- Image upload and management

### Shopping Cart
- Add/remove items from cart
- Quantity adjustment
- Cart persistence across sessions
- Cart summary with pricing
- Clear cart functionality

### Checkout & Payment
- Shipping and billing address management
- Address validation
- Order creation and tracking
- Stripe integration for secure payment processing
- Payment confirmation and receipts
- Order history and status tracking

### Admin Interface
- Django admin panel for content management
- User management
- Product administration
- Order management
- Payment tracking

### API Documentation
- RESTful API endpoints for all operations
- Token-based authentication
- JSON request/response format
- Comprehensive error handling
