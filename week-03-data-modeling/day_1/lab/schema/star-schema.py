import psycopg2
from psycopg2.extras import execute_values

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="postgres",
    user="postgres",
    password="7089"  # change this if your password is different
)
cursor = conn.cursor()

# ── CREATE TABLES ─────────────────────────────────────────────────────────────
cursor.execute("""
    DROP TABLE IF EXISTS fact_orders;
    DROP TABLE IF EXISTS dim_customer;
    DROP TABLE IF EXISTS dim_product;
    DROP TABLE IF EXISTS dim_date;
""")

cursor.execute("""
    CREATE TABLE dim_customer (
        customer_id INT PRIMARY KEY,
        name VARCHAR,
        city VARCHAR,
        country VARCHAR
    )
""")

cursor.execute("""
    CREATE TABLE dim_product (
        product_id INT PRIMARY KEY,
        name VARCHAR,
        category VARCHAR,
        supplier VARCHAR
    )
""")

cursor.execute("""
    CREATE TABLE dim_date (
        date_id INT PRIMARY KEY,
        date DATE,
        month INT,
        quarter INT,
        year INT
    )
""")

cursor.execute("""
    CREATE TABLE fact_orders (
        order_id INT PRIMARY KEY,
        customer_id INT REFERENCES dim_customer(customer_id),
        product_id INT REFERENCES dim_product(product_id),
        date_id INT REFERENCES dim_date(date_id),
        quantity INT,
        revenue DECIMAL
    )
""")

# ── INSERT DATA ───────────────────────────────────────────────────────────────
execute_values(cursor, "INSERT INTO dim_customer VALUES %s", [
    (1, 'Alice', 'New York', 'USA'),
    (2, 'Bob', 'London', 'UK'),
    (3, 'Carol', 'Berlin', 'Germany'),
])

execute_values(cursor, "INSERT INTO dim_product VALUES %s", [
    (1, 'Shoes', 'Footwear', 'Nike'),
    (2, 'Shirt', 'Clothing', 'Zara'),
    (3, 'Bag', 'Accessories', 'Gucci'),
])

execute_values(cursor, "INSERT INTO dim_date VALUES %s", [
    (1, '2025-01-15', 1, 1, 2025),
    (2, '2025-04-20', 4, 2, 2025),
    (3, '2025-07-10', 7, 3, 2025),
])

execute_values(cursor, "INSERT INTO fact_orders VALUES %s", [
    (1, 1, 1, 1, 2, 150.00),
    (2, 2, 2, 2, 1, 45.00),
    (3, 1, 2, 2, 3, 135.00),
    (4, 3, 3, 3, 1, 320.00),
    (5, 2, 1, 3, 2, 180.00),
])

conn.commit()

# ── QUERIES ───────────────────────────────────────────────────────────────────
print("=== Revenue by Category per Quarter ===")
cursor.execute("""
    SELECT 
        p.category,
        d.quarter,
        SUM(f.revenue) AS total_revenue
    FROM fact_orders f
    JOIN dim_product p ON f.product_id = p.product_id
    JOIN dim_date d ON f.date_id = d.date_id
    GROUP BY p.category, d.quarter
    ORDER BY total_revenue DESC
""")
for row in cursor.fetchall():
    print(row)

print("\n=== Top Customers by Revenue ===")
cursor.execute("""
    SELECT 
        c.name,
        c.country,
        SUM(f.revenue) AS total_spent,
        COUNT(f.order_id) AS total_orders
    FROM fact_orders f
    JOIN dim_customer c ON f.customer_id = c.customer_id
    GROUP BY c.name, c.country
    ORDER BY total_spent DESC
""")
for row in cursor.fetchall():
    print(row)

cursor.close()
conn.close()
print("\n✅ Star Schema lab complete!")