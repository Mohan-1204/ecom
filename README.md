# Mini E-Commerce Platform

Full-stack e-commerce application converted to the requested technology stack while preserving the existing React UI and core functionality.

## Technology Stack

### Frontend
- HTML
- CSS
- JavaScript
- React.js

### Backend
- Python
- Flask

### Database
- MySQL

### API
- REST API

## Features

- Product listing
- Product search
- Product details
- Product ratings and stock status
- Quantity controls
- Add to cart
- Remove from cart
- Order summary
- Place order
- MySQL order storage
- Product stock reduction after order
- REST API integration between React and Flask

## Run Backend

1. Install Python 3.10+.
2. Open a terminal in `backend`.
3. Create and activate a virtual environment.
4. Install dependencies:

   `pip install -r requirements.txt`

5. Copy `.env.example` to `.env` and enter your MySQL password.
6. Make sure MySQL Server is running.
7. Run:

   `python app.py`

The API runs at `http://localhost:8000`.

The Flask application creates the `mini_ecom` database and tables automatically and seeds the original products when the products table is empty.

## Run Frontend

1. Open a second terminal in `frontend`.
2. Install dependencies:

   `npm install`

3. Copy `.env.example` to `.env` if needed.
4. Start React:

   `npm start`

The React application uses `REACT_APP_API_URL=http://localhost:8000/api/v1`.

## REST Endpoints

- `GET /api/v1/products`
- `GET /api/v1/products?keyword=laptop`
- `GET /api/v1/product/<id>`
- `POST /api/v1/order`
