import json
import os
from datetime import datetime
from decimal import Decimal

import mysql.connector
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

app = Flask(__name__)
CORS(app)


def db_config(database=True):
    config = {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "3306")),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", ""),
    }
    if database:
        config["database"] = os.getenv("DB_NAME", "mini_ecom")
    return config


def get_connection(database=True):
    return mysql.connector.connect(**db_config(database))


def init_database():
    # Create database first so a fresh MySQL installation can be used directly.
    conn = get_connection(False)
    cursor = conn.cursor()
    db_name = os.getenv("DB_NAME", "mini_ecom")
    cursor.execute(
        f"CREATE DATABASE IF NOT EXISTS `{db_name}` "
        "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
    )
    cursor.close()
    conn.close()

    conn = get_connection(True)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS products (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            price DECIMAL(10,2) NOT NULL,
            description TEXT,
            ratings DECIMAL(3,2) DEFAULT 0,
            images JSON,
            category VARCHAR(100),
            seller VARCHAR(100),
            stock INT DEFAULT 0,
            num_of_reviews INT DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            id INT AUTO_INCREMENT PRIMARY KEY,
            cart_items JSON NOT NULL,
            amount DECIMAL(10,2) NOT NULL,
            status VARCHAR(50) NOT NULL DEFAULT 'Pending',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB
        """
    )
    conn.commit()
    cursor.close()
    conn.close()

    seed_products()


def seed_products():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM products")
    count = cursor.fetchone()[0]

    if count == 0:
        json_path = os.path.join(BASE_DIR, "data", "products.json")
        with open(json_path, "r", encoding="utf-8") as file:
            products = json.load(file)

        insert_sql = """
            INSERT INTO products
            (name, price, description, ratings, images, category, seller, stock, num_of_reviews)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        for product in products:
            cursor.execute(
                insert_sql,
                (
                    product.get("name"),
                    product.get("price", 0),
                    product.get("description", ""),
                    product.get("ratings", 0),
                    json.dumps(product.get("images", [])),
                    product.get("category", ""),
                    product.get("seller", ""),
                    product.get("stock", 0),
                    product.get("numOfReviews", 0),
                ),
            )
        conn.commit()

    cursor.close()
    conn.close()


def product_to_dict(row):
    (
        product_id,
        name,
        price,
        description,
        ratings,
        images,
        category,
        seller,
        stock,
        num_reviews,
        created_at,
    ) = row
    if isinstance(images, str):
        images = json.loads(images)
    return {
        "_id": str(product_id),
        "name": name,
        "price": float(price) if isinstance(price, Decimal) else price,
        "description": description,
        "ratings": float(ratings) if isinstance(ratings, Decimal) else ratings,
        "images": images or [],
        "category": category,
        "seller": seller,
        "stock": int(stock),
        "numOfReviews": int(num_reviews or 0),
        "createdAt": created_at.isoformat() if created_at else None,
    }


PRODUCT_COLUMNS = (
    "id, name, price, description, ratings, images, category, seller, "
    "stock, num_of_reviews, created_at"
)


@app.get("/")
def home():
    return jsonify({"success": True, "message": "Mini Ecom Flask API is running"})


@app.get("/api/v1/products")
def get_products():
    keyword = request.args.get("keyword", "").strip()
    conn = get_connection()
    cursor = conn.cursor()
    if keyword:
        cursor.execute(
            f"SELECT {PRODUCT_COLUMNS} FROM products WHERE name LIKE %s ORDER BY id",
            (f"%{keyword}%",),
        )
    else:
        cursor.execute(f"SELECT {PRODUCT_COLUMNS} FROM products ORDER BY id")
    products = [product_to_dict(row) for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return jsonify({"success": True, "product": products})


@app.get("/api/v1/product/<int:product_id>")
def get_single_product(product_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT {PRODUCT_COLUMNS} FROM products WHERE id = %s",
        (product_id,),
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if not row:
        return jsonify({"success": False, "message": "Unable to find product with this id"}), 404
    return jsonify({"success": True, "product": product_to_dict(row)})


@app.post("/api/v1/order")
def create_order():
    cart_items = request.get_json(silent=True)
    if not isinstance(cart_items, list) or not cart_items:
        return jsonify({"success": False, "message": "Cart is empty"}), 400

    conn = get_connection()
    cursor = conn.cursor()
    try:
        amount = Decimal("0.00")
        normalized_items = []

        for item in cart_items:
            product = item.get("product", {})
            product_id = int(product.get("_id"))
            qty = int(item.get("qty", 0))
            if qty < 1:
                raise ValueError("Invalid quantity")

            cursor.execute(
                "SELECT id, name, price, stock, description, ratings, images, category, seller, num_of_reviews, created_at "
                "FROM products WHERE id = %s FOR UPDATE",
                (product_id,),
            )
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Product {product_id} not found")
            if row[3] < qty:
                raise ValueError(f"Insufficient stock for {row[1]}")

            amount += Decimal(str(row[2])) * qty
            cursor.execute(
                "UPDATE products SET stock = stock - %s WHERE id = %s",
                (qty, product_id),
            )
            normalized_items.append({"product": product, "qty": qty})

        cursor.execute(
            "INSERT INTO orders (cart_items, amount, status, created_at) VALUES (%s, %s, %s, %s)",
            (json.dumps(normalized_items), amount, "Pending", datetime.now()),
        )
        order_id = cursor.lastrowid
        conn.commit()

        order = {
            "_id": str(order_id),
            "cartItems": normalized_items,
            "amount": f"{amount:.2f}",
            "status": "Pending",
            "createdAt": datetime.now().isoformat(),
        }
        return jsonify({"success": True, "order": order})
    except (ValueError, TypeError) as exc:
        conn.rollback()
        return jsonify({"success": False, "message": str(exc)}), 400
    except Exception:
        conn.rollback()
        app.logger.exception("Order creation failed")
        return jsonify({"success": False, "message": "Unable to place order"}), 500
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    init_database()
    port = int(os.getenv("PORT", "8000"))
    app.run(host="0.0.0.0", port=port, debug=os.getenv("FLASK_DEBUG", "True").lower() == "true")
