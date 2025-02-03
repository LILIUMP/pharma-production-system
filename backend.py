from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
import uvicorn
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# اتصال قاعدة البيانات
DATABASE_URL = os.getenv("DATABASE_URL")
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

# إنشاء جدول أوامر الإنتاج إذا لم يكن موجودًا
cursor.execute('''
CREATE TABLE IF NOT EXISTS suppliers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    contact_info TEXT
);

CREATE TABLE IF NOT EXISTS raw_materials (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    supplier_id INT REFERENCES suppliers(id),
    stock_quantity FLOAT NOT NULL
);

CREATE TABLE IF NOT EXISTS production_orders (
    id SERIAL PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    quantity_required FLOAT NOT NULL,
    status VARCHAR(50) CHECK (status IN ('Pending', 'In Production', 'Completed', 'Rejected')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS production_rooms (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    capacity INT NOT NULL
);

CREATE TABLE IF NOT EXISTS production_workflow (
    id SERIAL PRIMARY KEY,
    order_id INT REFERENCES production_orders(id),
    room_id INT REFERENCES production_rooms(id),
    stage VARCHAR(255) NOT NULL,
    status VARCHAR(50) CHECK (status IN ('Waiting', 'Processing', 'Completed')),
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS quality_control (
    id SERIAL PRIMARY KEY,
    order_id INT REFERENCES production_orders(id),
    stage VARCHAR(255) NOT NULL,
    passed BOOLEAN NOT NULL,
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
''')
conn.commit()

# نموذج بيانات لأوامر الإنتاج
class ProductionOrder(BaseModel):
    product_name: str
    quantity_required: float

@app.post("/create_production_order/")
def create_production_order(order: ProductionOrder):
    cursor.execute("INSERT INTO production_orders (product_name, quantity_required) VALUES (%s, %s) RETURNING id", 
                   (order.product_name, order.quantity_required))
    order_id = cursor.fetchone()[0]
    conn.commit()
    return {"message": "Order created successfully", "order_id": order_id}

@app.get("/get_production_orders/")
def get_production_orders():
    cursor.execute("SELECT * FROM production_orders")
    orders = cursor.fetchall()
    return [{"id": row[0], "product_name": row[1], "quantity_required": row[2]} for row in orders]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
