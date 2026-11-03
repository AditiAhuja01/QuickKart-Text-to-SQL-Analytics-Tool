import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    """Establish a connection to the PostgreSQL database."""
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "quickkart"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "")
    )

def setup():
    conn = get_connection()
    c = conn.cursor()

    print("🚀 Starting QuickKart PostgreSQL database setup...")

    # Drop existing tables (order matters due to Foreign Keys)
    tables = ["returns","discounts","order_items","orders","inventory",
              "products","categories","suppliers","employees","customers","query_history"]
    for t in tables:
        c.execute(f"DROP TABLE IF EXISTS {t} CASCADE")

    # Create tables
    print("📁 Creating tables...")
    
    c.execute("""
    CREATE TABLE customers (
        customer_id   SERIAL PRIMARY KEY,
        name          TEXT, email TEXT, phone TEXT,
        city          TEXT, state TEXT, gender TEXT, age INTEGER,
        signup_date   DATE, loyalty_points INTEGER DEFAULT 0
    );
    """)

    c.execute("""
    CREATE TABLE categories (
        category_id SERIAL PRIMARY KEY,
        name TEXT, description TEXT
    );
    """)

    c.execute("""
    CREATE TABLE suppliers (
        supplier_id    SERIAL PRIMARY KEY,
        name TEXT, contact_person TEXT, phone TEXT, city TEXT,
        rating DECIMAL(3,1)
    );
    """)

    c.execute("""
    CREATE TABLE employees (
        employee_id  SERIAL PRIMARY KEY,
        name TEXT, role TEXT, salary DECIMAL(10,2), joining_date DATE, shift TEXT
    );
    """)

    c.execute("""
    CREATE TABLE products (
        product_id  SERIAL PRIMARY KEY,
        name TEXT, category_id INTEGER, brand TEXT,
        price DECIMAL(10,2), cost_price DECIMAL(10,2), unit TEXT
    );
    """)

    c.execute("""
    CREATE TABLE inventory (
        inventory_id      SERIAL PRIMARY KEY,
        product_id        INTEGER, supplier_id INTEGER,
        quantity_in_stock INTEGER DEFAULT 0,
        reorder_level     INTEGER DEFAULT 20,
        last_restocked    DATE
    );
    """)

    c.execute("""
    CREATE TABLE orders (
        order_id         SERIAL PRIMARY KEY,
        customer_id      INTEGER, employee_id INTEGER,
        order_date       TIMESTAMP, total_amount DECIMAL(10,2),
        discount_applied DECIMAL(10,2) DEFAULT 0, payment_method TEXT
    );
    """)

    c.execute("""
    CREATE TABLE order_items (
        item_id    SERIAL PRIMARY KEY,
        order_id   INTEGER, product_id INTEGER,
        quantity   INTEGER, unit_price DECIMAL(10,2), subtotal DECIMAL(10,2)
    );
    """)

    c.execute("""
    CREATE TABLE discounts (
        discount_id      SERIAL PRIMARY KEY,
        product_id       INTEGER, label TEXT,
        discount_percent DECIMAL(5,2), start_date DATE, end_date DATE
    );
    """)

    c.execute("""
    CREATE TABLE returns (
        return_id     SERIAL PRIMARY KEY,
        order_id      INTEGER, product_id INTEGER,
        return_date   DATE, reason TEXT, refund_amount DECIMAL(10,2)
    );
    """)

    c.execute("""
    CREATE TABLE query_history (
        id           SERIAL PRIMARY KEY,
        question     TEXT, sql_query TEXT,
        result_count INTEGER DEFAULT 0, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Seed Data
    print("🌱 Seeding data...")

    # Categories
    c.executemany("INSERT INTO categories (name, description) VALUES (%s, %s)", [
        ('Dairy',           'Milk, cheese, butter, curd, paneer'),
        ('Beverages',       'Juices, soft drinks, water, tea, coffee'),
        ('Snacks',          'Chips, biscuits, namkeen, chocolates'),
        ('Grains & Pulses', 'Rice, wheat, dal, flour, poha'),
        ('Personal Care',   'Shampoo, soap, toothpaste, skincare'),
        ('Household',       'Detergent, cleaning supplies, utensils'),
        ('Frozen Foods',    'Ice cream, frozen veggies, ready meals'),
        ('Electronics',     'Batteries, bulbs, cables, small appliances'),
    ])

    # Suppliers
    c.executemany("INSERT INTO suppliers (name, contact_person, phone, city, rating) VALUES (%s, %s, %s, %s, %s)", [
        ('Amul Distributors',    'Rajesh Patel',   '9876543210', 'Anand',     4.8),
        ('PepsiCo India',        'Suresh Menon',   '9876543211', 'Mumbai',    4.5),
        ('ITC Limited',          'Amit Sharma',    '9876543212', 'Kolkata',   4.3),
        ('Hindustan Unilever',   'Priya Nair',     '9876543213', 'Mumbai',    4.6),
        ('Britannia Industries', 'Vikram Joshi',   '9876543214', 'Bangalore', 4.4),
        ('Patanjali',            'Ramdev Yadav',   '9876543215', 'Haridwar',  3.9),
        ('Nestle India',         'Anil Kapoor',    '9876543216', 'Gurgaon',   4.7),
        ('Mother Dairy',         'Sunita Verma',   '9876543217', 'Delhi',     4.5),
        ('Godrej Consumer',      'Harsh Malhotra', '9876543218', 'Mumbai',    4.2),
        ('Local Fresh Farms',    'Raju Farmers',   '9876543219', 'Pune',      3.7),
    ])

    # Employees
    c.executemany("INSERT INTO employees (name, role, salary, joining_date, shift) VALUES (%s, %s, %s, %s, %s)", [
        ('Mohan Das',     'manager',   45000, '2020-01-15', 'morning'),
        ('Sunita Kumari', 'cashier',   22000, '2021-03-10', 'morning'),
        ('Ravi Shankar',  'cashier',   22000, '2021-06-20', 'evening'),
        ('Priya Dubey',   'cashier',   22000, '2022-01-05', 'morning'),
        ('Ajay Tiwari',   'stock_boy', 18000, '2022-04-15', 'morning'),
        ('Neha Singh',    'cashier',   22000, '2022-07-01', 'evening'),
        ('Deepak Yadav',  'stock_boy', 18000, '2023-01-10', 'night'),
        ('Kavita Sharma', 'cashier',   23000, '2023-03-22', 'evening'),
        ('Arjun Mehta',   'manager',   46000, '2019-08-01', 'evening'),
        ('Lata Mishra',   'stock_boy', 18500, '2023-09-01', 'night'),
    ])

    # Products
    c.executemany("INSERT INTO products (name, category_id, brand, price, cost_price, unit) VALUES (%s, %s, %s, %s, %s, %s)", [
        ('Full Cream Milk 1L',      1, 'Amul',         58,  45,  'litre'),
        ('Paneer 200g',             1, 'Amul',         90,  70,  'piece'),
        ('Curd 400g',               1, 'Mother Dairy', 45,  35,  'piece'),
        ('Butter 100g',             1, 'Amul',         55,  42,  'piece'),
        ('Cheese Slices 200g',      1, 'Amul',        110,  85,  'piece'),
        ('Tropicana Orange 1L',     2, 'Tropicana',   120,  90,  'litre'),
        ('Pepsi 2L',                2, 'PepsiCo',      95,  70,  'litre'),
        ('Bisleri Water 1L',        2, 'Bisleri',      20,  12,  'litre'),
        ('Red Bull 250ml',          2, 'Red Bull',    110,  85,  'piece'),
        ('Tata Tea 250g',           2, 'Tata',        105,  80,  'piece'),
        ('Lays Classic 75g',        3, 'PepsiCo',      30,  20,  'pack'),
        ('Hide & Seek 100g',        3, 'Parle',        35,  25,  'pack'),
        ('KitKat 50g',              3, 'Nestle',       40,  28,  'piece'),
        ('Haldiram Namkeen 200g',   3, 'Haldirams',    75,  55,  'pack'),
        ('Oreo 120g',               3, 'Cadbury',      55,  40,  'pack'),
        ('Basmati Rice 5kg',        4, 'India Gate',  450, 360,  'kg'),
        ('Atta 10kg',               4, 'Aashirvaad',  450, 360,  'kg'),
        ('Toor Dal 1kg',            4, 'Patanjali',   135, 105,  'kg'),
        ('Poha 500g',               4, 'Local',        40,  28,  'pack'),
        ('Moong Dal 1kg',            4, 'Patanjali',   120,  92,  'kg'),
        ('Dove Shampoo 400ml',      5, 'HUL',         285, 215,  'piece'),
        ('Colgate Toothpaste 200g', 5, 'Colgate',      95,  70,  'piece'),
        ('Lux Soap 100g',           5, 'HUL',          45,  32,  'piece'),
        ('Dettol Handwash 250ml',   5, 'Dettol',       99,  74,  'piece'),
        ('Surf Excel 1kg',          6, 'HUL',         215, 165,  'kg'),
        ('Vim Dishwash Bar',        6, 'HUL',          35,  24,  'piece'),
        ('Colin Glass Cleaner',     6, 'Godrej',      120,  90,  'piece'),
        ('Amul Ice Cream 500ml',    7, 'Amul',        160, 120,  'piece'),
        ('McCain Fries 400g',       7, 'McCain',      165, 125,  'piece'),
        ('Eveready Battery AA 4pk', 8, 'Eveready',    65,  45,  'pack'),
        ('Philips LED Bulb 9W',     8, 'Philips',     145, 105,  'piece'),
    ])

    # Inventory
    c.executemany("INSERT INTO inventory (product_id, supplier_id, quantity_in_stock, reorder_level, last_restocked) VALUES (%s, %s, %s, %s, %s)", [
        (1,1,250,50,'2024-11-01'),(2,1,80,20,'2024-11-01'),(3,8,120,30,'2024-11-02'),
        (4,1,100,25,'2024-11-01'),(5,1,45,20,'2024-10-28'),(6,2,90,25,'2024-10-30'),
        (7,2,150,40,'2024-10-30'),(8,2,300,60,'2024-11-01'),(9,2,35,20,'2024-10-25'),
        (10,7,60,20,'2024-10-29'),(11,2,200,50,'2024-11-01'),(12,5,95,30,'2024-10-28'),
        (13,7,55,20,'2024-10-27'),(14,3,70,25,'2024-10-29'),(15,7,80,25,'2024-10-28'),
        (16,6,180,40,'2024-10-30'),(17,6,160,40,'2024-10-30'),(18,6,90,30,'2024-10-29'),
        (19,10,110,30,'2024-10-31'),(20,6,75,25,'2024-10-29'),(21,4,120,30,'2024-10-30'),
        (22,4,200,50,'2024-10-30'),(23,4,180,45,'2024-10-30'),(24,4,95,30,'2024-10-28'),
        (25,4,140,35,'2024-10-30'),(26,4,220,50,'2024-10-31'),(27,9,60,20,'2024-10-27'),
        (28,1,50,20,'2024-10-26'),(29,7,15,20,'2024-10-20'),(30,8,300,60,'2024-11-01'),
        (31,8,40,20,'2024-10-22'),
    ])

    # Customers
    c.executemany("INSERT INTO customers (name,email,phone,city,state,gender,age,signup_date,loyalty_points) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", [
        ('Rahul Sharma','rahul.sharma@gmail.com','9811234567','Mumbai','Maharashtra','Male',32,'2022-01-15',1250),
        ('Priya Patel','priya.patel@gmail.com','9822345678','Ahmedabad','Gujarat','Female',28,'2022-02-20',890),
        ('Amit Kumar','amit.kumar@gmail.com','9833456789','Delhi','Delhi','Male',45,'2022-03-10',3400),
        ('Sneha Reddy','sneha.reddy@gmail.com','9844567890','Hyderabad','Telangana','Female',35,'2022-01-05',560),
        ('Vikram Singh','vikram.singh@gmail.com','9855678901','Jaipur','Rajasthan','Male',41,'2022-04-01',1210),
        ('Anjali Nair','anjali.nair@gmail.com','9866789012','Kochi','Kerala','Female',29,'2022-05-15',980),
        ('Rohan Gupta','rohan.gupta@gmail.com','9877890123','Kolkata','West Bengal','Male',22,'2022-06-22',340),
        ('Meera Iyer','meera.iyer@gmail.com','9888901234','Chennai','Tamil Nadu','Female',38,'2022-07-11',1890),
        ('Karan Mehta','karan.mehta@gmail.com','9899012345','Pune','Maharashtra','Male',27,'2022-08-03',720),
        ('Divya Joshi','divya.joshi@gmail.com','9800123456','Bangalore','Karnataka','Female',33,'2022-09-19',3150),
    ])

    # Orders (Simplified set for Seeding)
    c.executemany("INSERT INTO orders (customer_id,employee_id,order_date,total_amount,discount_applied,payment_method) VALUES (%s, %s, %s, %s, %s, %s)", [
        (3,2,'2024-01-05 10:23:00',892.00,0,'upi'),
        (10,3,'2024-01-07 15:44:00',1245.00,50,'card'),
        (1,2,'2024-01-12 09:30:00',678.00,30,'upi'),
    ])

    # Order Items (Simplified set for Seeding)
    c.executemany("INSERT INTO order_items (order_id,product_id,quantity,unit_price,subtotal) VALUES (%s, %s, %s, %s, %s)", [
        (1,1,3,58,174),(1,16,1,450,450),
        (2,5,2,110,220),(2,10,1,105,105),
    ])

    # Discounts
    c.executemany("INSERT INTO discounts (product_id,label,discount_percent,start_date,end_date) VALUES (%s, %s, %s, %s, %s)", [
        (7,'Diwali Sale',15.00,'2024-11-01','2024-11-15'),
        (11,'Diwali Sale',10.00,'2024-11-01','2024-11-15'),
    ])

    # Returns
    c.executemany("INSERT INTO returns (order_id,product_id,return_date,reason,refund_amount) VALUES (%s, %s, %s, %s, %s)", [
        (2,5,'2024-01-10','Product damaged',110.00),
    ])

    conn.commit()
    conn.close()
    print("✅ QuickKart PostgreSQL database setup complete!")

if __name__ == "__main__":
    setup()
