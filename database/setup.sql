-- ============================================================
-- QuickKart Supermarket Database
-- Run: psql -U postgres -d quickkart -f setup.sql
-- ============================================================

-- Drop tables if re-running
DROP TABLE IF EXISTS returns CASCADE;
DROP TABLE IF EXISTS discounts CASCADE;
DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS inventory CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS categories CASCADE;
DROP TABLE IF EXISTS suppliers CASCADE;
DROP TABLE IF EXISTS employees CASCADE;
DROP TABLE IF EXISTS customers CASCADE;

-- ============================================================
-- TABLE 1: customers
-- ============================================================
CREATE TABLE customers (
    customer_id   SERIAL PRIMARY KEY,
    name          VARCHAR(100) NOT NULL,
    email         VARCHAR(100) UNIQUE,
    phone         VARCHAR(15),
    city          VARCHAR(50),
    state         VARCHAR(50),
    gender        VARCHAR(10),
    age           INTEGER,
    signup_date   DATE,
    loyalty_points INTEGER DEFAULT 0
);

-- ============================================================
-- TABLE 2: categories
-- ============================================================
CREATE TABLE categories (
    category_id   SERIAL PRIMARY KEY,
    name          VARCHAR(50) NOT NULL,
    description   TEXT
);

-- ============================================================
-- TABLE 3: suppliers
-- ============================================================
CREATE TABLE suppliers (
    supplier_id     SERIAL PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    contact_person  VARCHAR(100),
    phone           VARCHAR(15),
    city            VARCHAR(50),
    rating          DECIMAL(2,1) CHECK (rating BETWEEN 1.0 AND 5.0)
);

-- ============================================================
-- TABLE 4: employees
-- ============================================================
CREATE TABLE employees (
    employee_id   SERIAL PRIMARY KEY,
    name          VARCHAR(100) NOT NULL,
    role          VARCHAR(30),  -- cashier, manager, stock_boy
    salary        DECIMAL(10,2),
    joining_date  DATE,
    shift         VARCHAR(10)   -- morning, evening, night
);

-- ============================================================
-- TABLE 5: products
-- ============================================================
CREATE TABLE products (
    product_id    SERIAL PRIMARY KEY,
    name          VARCHAR(100) NOT NULL,
    category_id   INTEGER REFERENCES categories(category_id),
    brand         VARCHAR(50),
    price         DECIMAL(10,2),
    cost_price    DECIMAL(10,2),
    unit          VARCHAR(20)   -- kg, piece, litre, pack
);

-- ============================================================
-- TABLE 6: inventory
-- ============================================================
CREATE TABLE inventory (
    inventory_id      SERIAL PRIMARY KEY,
    product_id        INTEGER REFERENCES products(product_id),
    supplier_id       INTEGER REFERENCES suppliers(supplier_id),
    quantity_in_stock INTEGER DEFAULT 0,
    reorder_level     INTEGER DEFAULT 20,
    last_restocked    DATE
);

-- ============================================================
-- TABLE 7: orders
-- ============================================================
CREATE TABLE orders (
    order_id         SERIAL PRIMARY KEY,
    customer_id      INTEGER REFERENCES customers(customer_id),
    employee_id      INTEGER REFERENCES employees(employee_id),
    order_date       TIMESTAMP,
    total_amount     DECIMAL(10,2),
    discount_applied DECIMAL(10,2) DEFAULT 0,
    payment_method   VARCHAR(20)   -- cash, upi, card, wallet
);

-- ============================================================
-- TABLE 8: order_items
-- ============================================================
CREATE TABLE order_items (
    item_id     SERIAL PRIMARY KEY,
    order_id    INTEGER REFERENCES orders(order_id),
    product_id  INTEGER REFERENCES products(product_id),
    quantity    INTEGER,
    unit_price  DECIMAL(10,2),
    subtotal    DECIMAL(10,2)
);

-- ============================================================
-- TABLE 9: discounts
-- ============================================================
CREATE TABLE discounts (
    discount_id      SERIAL PRIMARY KEY,
    product_id       INTEGER REFERENCES products(product_id),
    label            VARCHAR(100),
    discount_percent DECIMAL(5,2),
    start_date       DATE,
    end_date         DATE
);

-- ============================================================
-- TABLE 10: returns
-- ============================================================
CREATE TABLE returns (
    return_id     SERIAL PRIMARY KEY,
    order_id      INTEGER REFERENCES orders(order_id),
    product_id    INTEGER REFERENCES products(product_id),
    return_date   DATE,
    reason        VARCHAR(200),
    refund_amount DECIMAL(10,2)
);

-- ============================================================
-- SEED DATA
-- ============================================================

-- Categories
INSERT INTO categories (name, description) VALUES
('Dairy',          'Milk, cheese, butter, curd, paneer'),
('Beverages',      'Juices, soft drinks, water, tea, coffee'),
('Snacks',         'Chips, biscuits, namkeen, chocolates'),
('Grains & Pulses','Rice, wheat, dal, flour, poha'),
('Personal Care',  'Shampoo, soap, toothpaste, skincare'),
('Household',      'Detergent, cleaning supplies, utensils'),
('Frozen Foods',   'Ice cream, frozen veggies, ready meals'),
('Electronics',    'Batteries, bulbs, cables, small appliances');

-- Suppliers
INSERT INTO suppliers (name, contact_person, phone, city, rating) VALUES
('Amul Distributors',       'Rajesh Patel',    '9876543210', 'Anand',     4.8),
('PepsiCo India',           'Suresh Menon',    '9876543211', 'Mumbai',    4.5),
('ITC Limited',             'Amit Sharma',     '9876543212', 'Kolkata',   4.3),
('Hindustan Unilever',      'Priya Nair',      '9876543213', 'Mumbai',    4.6),
('Britannia Industries',    'Vikram Joshi',    '9876543214', 'Bangalore', 4.4),
('Patanjali',               'Ramdev Yadav',    '9876543215', 'Haridwar',  3.9),
('Nestle India',            'Anil Kapoor',     '9876543216', 'Gurgaon',   4.7),
('Mother Dairy',            'Sunita Verma',    '9876543217', 'Delhi',     4.5),
('Godrej Consumer',         'Harsh Malhotra',  '9876543218', 'Mumbai',    4.2),
('Local Fresh Farms',       'Raju Farmers',    '9876543219', 'Pune',      3.7);

-- Employees
INSERT INTO employees (name, role, salary, joining_date, shift) VALUES
('Mohan Das',       'manager',   45000, '2020-01-15', 'morning'),
('Sunita Kumari',   'cashier',   22000, '2021-03-10', 'morning'),
('Ravi Shankar',    'cashier',   22000, '2021-06-20', 'evening'),
('Priya Dubey',     'cashier',   22000, '2022-01-05', 'morning'),
('Ajay Tiwari',     'stock_boy', 18000, '2022-04-15', 'morning'),
('Neha Singh',      'cashier',   22000, '2022-07-01', 'evening'),
('Deepak Yadav',    'stock_boy', 18000, '2023-01-10', 'night'),
('Kavita Sharma',   'cashier',   23000, '2023-03-22', 'evening'),
('Arjun Mehta',     'manager',   46000, '2019-08-01', 'evening'),
('Lata Mishra',     'stock_boy', 18500, '2023-09-01', 'night');

-- Products (30 products across 8 categories)
INSERT INTO products (name, category_id, brand, price, cost_price, unit) VALUES
-- Dairy (cat 1)
('Full Cream Milk 1L',      1, 'Amul',         58,  45,  'litre'),
('Paneer 200g',             1, 'Amul',         90,  70,  'piece'),
('Curd 400g',               1, 'Mother Dairy', 45,  35,  'piece'),
('Butter 100g',             1, 'Amul',         55,  42,  'piece'),
('Cheese Slices 200g',      1, 'Amul',        110,  85,  'piece'),
-- Beverages (cat 2)
('Tropicana Orange 1L',     2, 'Tropicana',   120,  90,  'litre'),
('Pepsi 2L',                2, 'PepsiCo',      95,  70,  'litre'),
('Bisleri Water 1L',        2, 'Bisleri',      20,  12,  'litre'),
('Red Bull 250ml',          2, 'Red Bull',    110,  85,  'piece'),
('Tata Tea 250g',           2, 'Tata',        105,  80,  'piece'),
-- Snacks (cat 3)
('Lays Classic 75g',        3, 'PepsiCo',      30,  20,  'pack'),
('Hide & Seek 100g',        3, 'Parle',        35,  25,  'pack'),
('KitKat 50g',              3, 'Nestle',       40,  28,  'piece'),
('Haldiram Namkeen 200g',   3, 'Haldirams',    75,  55,  'pack'),
('Oreo 120g',               3, 'Cadbury',      55,  40,  'pack'),
-- Grains (cat 4)
('Basmati Rice 5kg',        4, 'India Gate',  450, 360,  'kg'),
('Atta 10kg',               4, 'Aashirvaad',  450, 360,  'kg'),
('Toor Dal 1kg',            4, 'Patanjali',   135, 105,  'kg'),
('Poha 500g',               4, 'Local',        40,  28,  'pack'),
('Moong Dal 1kg',           4, 'Patanjali',   120,  92,  'kg'),
-- Personal Care (cat 5)
('Dove Shampoo 400ml',      5, 'HUL',         285, 215,  'piece'),
('Colgate Toothpaste 200g', 5, 'Colgate',      95,  70,  'piece'),
('Lux Soap 100g',           5, 'HUL',          45,  32,  'piece'),
('Dettol Handwash 250ml',   5, 'Dettol',       99,  74,  'piece'),
-- Household (cat 6)
('Surf Excel 1kg',          6, 'HUL',         215, 165,  'kg'),
('Vim Dishwash Bar',        6, 'HUL',          35,  24,  'piece'),
('Colin Glass Cleaner',     6, 'Godrej',      120,  90,  'piece'),
-- Frozen (cat 7)
('Amul Ice Cream 500ml',    7, 'Amul',        160, 120,  'piece'),
('McCain Fries 400g',       7, 'McCain',      165, 125,  'piece'),
-- Electronics (cat 8)
('Eveready Battery AA 4pk', 8, 'Eveready',    65,  45,  'pack'),
('Philips LED Bulb 9W',     8, 'Philips',     145, 105,  'piece');

-- Inventory
INSERT INTO inventory (product_id, supplier_id, quantity_in_stock, reorder_level, last_restocked) VALUES
(1,  1, 250, 50, '2024-11-01'),
(2,  1,  80, 20, '2024-11-01'),
(3,  8, 120, 30, '2024-11-02'),
(4,  1, 100, 25, '2024-11-01'),
(5,  1,  45, 20, '2024-10-28'),
(6,  2,  90, 25, '2024-10-30'),
(7,  2, 150, 40, '2024-10-30'),
(8,  2, 300, 60, '2024-11-01'),
(9,  2,  35, 20, '2024-10-25'),
(10, 7,  60, 20, '2024-10-29'),
(11, 2, 200, 50, '2024-11-01'),
(12, 5,  95, 30, '2024-10-28'),
(13, 7,  55, 20, '2024-10-27'),
(14, 3,  70, 25, '2024-10-29'),
(15, 7,  80, 25, '2024-10-28'),
(16, 6, 180, 40, '2024-10-30'),
(17, 6, 160, 40, '2024-10-30'),
(18, 6,  90, 30, '2024-10-29'),
(19,10, 110, 30, '2024-10-31'),
(20, 6,  75, 25, '2024-10-29'),
(21, 4, 120, 30, '2024-10-30'),
(22, 4, 200, 50, '2024-10-30'),
(23, 4, 180, 45, '2024-10-30'),
(24, 4,  95, 30, '2024-10-28'),
(25, 4, 140, 35, '2024-10-30'),
(26, 4, 220, 50, '2024-10-31'),
(27, 9,  60, 20, '2024-10-27'),
(28, 1,  50, 20, '2024-10-26'),
(29, 7,  15, 20, '2024-10-20'),
(30, 8, 300, 60, '2024-11-01'),
(31, 8,  40, 20, '2024-10-22');

-- Customers (50 realistic Indian customers)
INSERT INTO customers (name, email, phone, city, state, gender, age, signup_date, loyalty_points) VALUES
('Rahul Sharma',    'rahul.sharma@gmail.com',    '9811234567', 'Mumbai',    'Maharashtra',  'Male',   32, '2022-01-15', 1250),
('Priya Patel',     'priya.patel@gmail.com',     '9822345678', 'Ahmedabad', 'Gujarat',      'Female', 28, '2022-02-20', 890),
('Amit Kumar',      'amit.kumar@gmail.com',      '9833456789', 'Delhi',     'Delhi',        'Male',   45, '2022-03-10', 3400),
('Sneha Reddy',     'sneha.reddy@gmail.com',     '9844567890', 'Hyderabad', 'Telangana',    'Female', 35, '2022-01-05', 560),
('Vikram Singh',    'vikram.singh@gmail.com',    '9855678901', 'Jaipur',    'Rajasthan',    'Male',   41, '2022-04-01', 1210),
('Anjali Nair',     'anjali.nair@gmail.com',     '9866789012', 'Kochi',     'Kerala',       'Female', 29, '2022-05-15', 980),
('Rohan Gupta',     'rohan.gupta@gmail.com',     '9877890123', 'Kolkata',   'West Bengal',  'Male',   22, '2022-06-22', 340),
('Meera Iyer',      'meera.iyer@gmail.com',      '9888901234', 'Chennai',   'Tamil Nadu',   'Female', 38, '2022-07-11', 1890),
('Karan Mehta',     'karan.mehta@gmail.com',     '9899012345', 'Pune',      'Maharashtra',  'Male',   27, '2022-08-03', 720),
('Divya Joshi',     'divya.joshi@gmail.com',     '9800123456', 'Bangalore', 'Karnataka',    'Female', 33, '2022-09-19', 3150),
('Suresh Yadav',    'suresh.yadav@gmail.com',    '9811233456', 'Lucknow',   'Uttar Pradesh','Male',   50, '2022-10-05', 2200),
('Pooja Mishra',    'pooja.mishra@gmail.com',    '9822344567', 'Bhopal',    'Madhya Pradesh','Female',26, '2022-11-12', 450),
('Arjun Tiwari',    'arjun.tiwari@gmail.com',    '9833455678', 'Varanasi',  'Uttar Pradesh','Male',   37, '2022-12-01', 1100),
('Neha Saxena',     'neha.saxena@gmail.com',     '9844566789', 'Delhi',     'Delhi',        'Female', 31, '2023-01-08', 670),
('Ravi Verma',      'ravi.verma@gmail.com',      '9855677890', 'Patna',     'Bihar',        'Male',   43, '2023-02-14', 890),
('Kavita Desai',    'kavita.desai@gmail.com',    '9866788901', 'Surat',     'Gujarat',      'Female', 36, '2023-03-20', 1340),
('Manish Agarwal',  'manish.agarwal@gmail.com',  '9877899012', 'Agra',      'Uttar Pradesh','Male',   29, '2023-04-05', 230),
('Sunita Rao',      'sunita.rao@gmail.com',      '9888910123', 'Vizag',     'Andhra Pradesh','Female',44, '2023-05-18', 1780),
('Deepak Pandey',   'deepak.pandey@gmail.com',   '9899021234', 'Allahabad', 'Uttar Pradesh','Male',   39, '2023-06-25', 560),
('Lakshmi Krishnan','lakshmi.k@gmail.com',       '9800132345', 'Chennai',   'Tamil Nadu',   'Female', 52, '2023-07-30', 4200),
('Sanjay Bhatt',    'sanjay.bhatt@gmail.com',    '9811244567', 'Mumbai',    'Maharashtra',  'Male',   48, '2023-01-10', 1650),
('Rekha Pillai',    'rekha.pillai@gmail.com',    '9822355678', 'Trivandrum','Kerala',       'Female', 34, '2023-02-22', 920),
('Gaurav Chopra',   'gaurav.chopra@gmail.com',   '9833466789', 'Chandigarh','Punjab',       'Male',   25, '2023-03-14', 180),
('Anita Kulkarni',  'anita.kulkarni@gmail.com',  '9844577890', 'Pune',      'Maharashtra',  'Female', 41, '2023-04-28', 2100),
('Nitin Shukla',    'nitin.shukla@gmail.com',    '9855688901', 'Kanpur',    'Uttar Pradesh','Male',   33, '2023-05-09', 780),
('Swati Banerjee',  'swati.banerjee@gmail.com',  '9866799012', 'Kolkata',   'West Bengal',  'Female', 27, '2023-06-17', 430),
('Rajesh Nambiar',  'rajesh.nambiar@gmail.com',  '9877810123', 'Kochi',     'Kerala',       'Male',   55, '2023-07-03', 3800),
('Usha Garg',       'usha.garg@gmail.com',       '9888921234', 'Jaipur',    'Rajasthan',    'Female', 46, '2023-08-11', 1290),
('Tarun Bose',      'tarun.bose@gmail.com',      '9899032345', 'Kolkata',   'West Bengal',  'Male',   30, '2023-09-24', 560),
('Madhuri Patil',   'madhuri.patil@gmail.com',   '9800143456', 'Nagpur',    'Maharashtra',  'Female', 38, '2023-10-07', 870),
('Harish Menon',    'harish.menon@gmail.com',    '9811256789', 'Bangalore', 'Karnataka',    'Male',   42, '2023-11-19', 1420),
('Geetha Subramaniam','geetha.s@gmail.com',      '9822367890', 'Coimbatore','Tamil Nadu',   'Female', 49, '2023-12-02', 2650),
('Pankaj Rastogi',  'pankaj.rastogi@gmail.com',  '9833478901', 'Lucknow',   'Uttar Pradesh','Male',   36, '2024-01-15', 390),
('Shweta Kapoor',   'shweta.kapoor@gmail.com',   '9844589012', 'Delhi',     'Delhi',        'Female', 24, '2024-02-08', 150),
('Vinod Chavan',    'vinod.chavan@gmail.com',     '9855690123', 'Mumbai',    'Maharashtra',  'Male',   53, '2024-03-22', 1870),
('Nandini Hegde',   'nandini.hegde@gmail.com',   '9866701234', 'Mangalore', 'Karnataka',    'Female', 31, '2024-04-14', 640),
('Sunil Jha',       'sunil.jha@gmail.com',       '9877812345', 'Patna',     'Bihar',        'Male',   44, '2024-05-06', 920),
('Bharti Soni',     'bharti.soni@gmail.com',     '9888923456', 'Udaipur',   'Rajasthan',    'Female', 28, '2024-06-18', 310),
('Ashok Pillai',    'ashok.pillai@gmail.com',    '9899034567', 'Trivandrum','Kerala',       'Male',   60, '2024-07-25', 2340),
('Pallavi Doshi',   'pallavi.doshi@gmail.com',   '9800145678', 'Ahmedabad', 'Gujarat',      'Female', 35, '2024-08-09', 780),
('Mukesh Tomar',    'mukesh.tomar@gmail.com',    '9811258901', 'Gurgaon',   'Haryana',      'Male',   38, '2024-09-12', 450),
('Sarika Wagh',     'sarika.wagh@gmail.com',     '9822369012', 'Aurangabad','Maharashtra',  'Female', 26, '2024-10-01', 120),
('Dinesh Bhatnagar','dinesh.b@gmail.com',        '9833470123', 'Indore',    'Madhya Pradesh','Male',  47, '2024-10-15', 980),
('Jyoti Acharya',   'jyoti.acharya@gmail.com',   '9844581234', 'Bhubaneswar','Odisha',      'Female', 33, '2024-10-22', 230),
('Manoj Kapur',     'manoj.kapur@gmail.com',     '9855692345', 'Delhi',     'Delhi',        'Male',   39, '2024-11-01', 60),
('Tanvi Vora',      'tanvi.vora@gmail.com',      '9866703456', 'Baroda',    'Gujarat',      'Female', 22, '2024-09-05', 340),
('Siddharth Lal',   'siddharth.lal@gmail.com',   '9877814567', 'Noida',     'Uttar Pradesh','Male',   29, '2024-08-17', 510),
('Rashmi Bajaj',    'rashmi.bajaj@gmail.com',    '9888925678', 'Pune',      'Maharashtra',  'Female', 44, '2024-07-30', 1200),
('Girish Nair',     'girish.nair@gmail.com',     '9899036789', 'Kochi',     'Kerala',       'Male',   57, '2024-06-12', 2900),
('Varsha Pawar',    'varsha.pawar@gmail.com',    '9800147890', 'Nashik',    'Maharashtra',  'Female', 30, '2024-05-28', 670);

-- Orders (200 orders over last 12 months)
INSERT INTO orders (customer_id, employee_id, order_date, total_amount, discount_applied, payment_method) VALUES
(3,  2, '2024-01-05 10:23:00', 892.00,  0,     'upi'),
(10, 3, '2024-01-07 15:44:00', 1245.00, 50,    'card'),
(20, 4, '2024-01-09 11:10:00', 467.00,  0,     'cash'),
(1,  2, '2024-01-12 09:30:00', 678.00,  30,    'upi'),
(5,  6, '2024-01-15 16:55:00', 1100.00, 0,     'card'),
(27, 3, '2024-01-18 14:20:00', 555.00,  0,     'upi'),
(11, 4, '2024-01-20 10:05:00', 2340.00, 100,   'card'),
(8,  2, '2024-01-22 17:30:00', 789.00,  0,     'cash'),
(16, 6, '2024-01-25 12:15:00', 430.00,  20,    'wallet'),
(32, 3, '2024-01-28 09:45:00', 1890.00, 0,     'upi'),
(2,  4, '2024-02-02 11:20:00', 345.00,  0,     'cash'),
(15, 2, '2024-02-05 14:50:00', 780.00,  40,    'upi'),
(7,  6, '2024-02-08 16:10:00', 230.00,  0,     'cash'),
(24, 3, '2024-02-10 10:30:00', 1560.00, 75,    'card'),
(39, 4, '2024-02-14 13:45:00', 670.00,  0,     'upi'),
(4,  2, '2024-02-17 09:15:00', 890.00,  0,     'card'),
(19, 6, '2024-02-20 15:30:00', 456.00,  25,    'wallet'),
(31, 3, '2024-02-22 11:00:00', 1230.00, 0,     'upi'),
(6,  4, '2024-02-25 14:20:00', 780.00,  0,     'cash'),
(43, 2, '2024-02-28 16:40:00', 340.00,  0,     'upi'),
(3,  6, '2024-03-03 10:10:00', 1100.00, 50,    'card'),
(10, 3, '2024-03-06 13:30:00', 567.00,  0,     'upi'),
(20, 4, '2024-03-09 09:50:00', 890.00,  0,     'cash'),
(1,  2, '2024-03-12 15:15:00', 1456.00, 100,   'card'),
(45, 6, '2024-03-15 11:40:00', 234.00,  0,     'wallet'),
(12, 3, '2024-03-18 14:00:00', 678.00,  0,     'upi'),
(28, 4, '2024-03-21 16:20:00', 1890.00, 75,    'card'),
(9,  2, '2024-03-24 10:35:00', 456.00,  0,     'cash'),
(36, 6, '2024-03-27 13:50:00', 1230.00, 0,     'upi'),
(17, 3, '2024-03-30 09:25:00', 345.00,  0,     'upi'),
(5,  4, '2024-04-02 14:40:00', 780.00,  30,    'card'),
(22, 2, '2024-04-05 11:55:00', 1560.00, 0,     'upi'),
(40, 6, '2024-04-08 16:15:00', 890.00,  50,    'cash'),
(14, 3, '2024-04-11 10:30:00', 234.00,  0,     'wallet'),
(48, 4, '2024-04-14 13:45:00', 1100.00, 0,     'upi'),
(7,  2, '2024-04-17 09:20:00', 567.00,  0,     'cash'),
(33, 6, '2024-04-20 15:35:00', 2340.00, 150,   'card'),
(18, 3, '2024-04-23 11:50:00', 678.00,  0,     'upi'),
(25, 4, '2024-04-26 14:05:00', 1890.00, 75,    'card'),
(2,  2, '2024-04-29 16:20:00', 456.00,  0,     'upi'),
(11, 6, '2024-05-02 10:35:00', 1230.00, 0,     'card'),
(37, 3, '2024-05-05 13:50:00', 345.00,  20,    'cash'),
(20, 4, '2024-05-08 09:15:00', 780.00,  0,     'upi'),
(44, 2, '2024-05-11 15:30:00', 1560.00, 0,     'card'),
(8,  6, '2024-05-14 11:45:00', 234.00,  0,     'wallet'),
(29, 3, '2024-05-17 14:00:00', 890.00,  45,    'upi'),
(13, 4, '2024-05-20 16:15:00', 1100.00, 0,     'cash'),
(41, 2, '2024-05-23 10:30:00', 567.00,  0,     'upi'),
(6,  6, '2024-05-26 13:45:00', 2340.00, 100,   'card'),
(26, 3, '2024-05-29 09:20:00', 678.00,  0,     'cash'),
(10, 4, '2024-06-01 15:35:00', 1890.00, 75,    'card'),
(3,  2, '2024-06-04 11:50:00', 456.00,  0,     'upi'),
(47, 6, '2024-06-07 14:05:00', 1230.00, 0,     'upi'),
(16, 3, '2024-06-10 16:20:00', 345.00,  0,     'cash'),
(35, 4, '2024-06-13 10:35:00', 780.00,  40,    'upi'),
(1,  2, '2024-06-16 13:50:00', 1560.00, 0,     'card'),
(42, 6, '2024-06-19 09:15:00', 234.00,  0,     'wallet'),
(23, 3, '2024-06-22 15:30:00', 890.00,  0,     'upi'),
(49, 4, '2024-06-25 11:45:00', 1100.00, 50,    'card'),
(4,  2, '2024-06-28 14:00:00', 567.00,  0,     'cash'),
(30, 6, '2024-07-01 16:15:00', 2340.00, 100,   'upi'),
(19, 3, '2024-07-04 10:30:00', 678.00,  0,     'card'),
(38, 4, '2024-07-07 13:45:00', 1890.00, 75,    'cash'),
(9,  2, '2024-07-10 09:20:00', 456.00,  0,     'upi'),
(27, 6, '2024-07-13 15:35:00', 1230.00, 0,     'card'),
(5,  3, '2024-07-16 11:50:00', 345.00,  0,     'wallet'),
(46, 4, '2024-07-19 14:05:00', 780.00,  0,     'upi'),
(14, 2, '2024-07-22 16:20:00', 1560.00, 80,    'card'),
(32, 6, '2024-07-25 10:35:00', 234.00,  0,     'cash'),
(21, 3, '2024-07-28 13:50:00', 890.00,  0,     'upi'),
(50, 4, '2024-07-31 09:15:00', 1100.00, 0,     'card'),
(7,  2, '2024-08-03 15:30:00', 567.00,  30,    'upi'),
(34, 6, '2024-08-06 11:45:00', 2340.00, 150,   'card'),
(20, 3, '2024-08-09 14:00:00', 678.00,  0,     'cash'),
(43, 4, '2024-08-12 16:15:00', 1890.00, 75,    'upi'),
(11, 2, '2024-08-15 10:30:00', 456.00,  0,     'card'),
(28, 6, '2024-08-18 13:45:00', 1230.00, 60,    'cash'),
(2,  3, '2024-08-21 09:20:00', 345.00,  0,     'wallet'),
(39, 4, '2024-08-24 15:35:00', 780.00,  0,     'upi'),
(15, 2, '2024-08-27 11:50:00', 1560.00, 0,     'card'),
(48, 6, '2024-08-30 14:05:00', 234.00,  0,     'cash'),
(6,  3, '2024-09-02 16:20:00', 890.00,  45,    'upi'),
(24, 4, '2024-09-05 10:35:00', 1100.00, 0,     'card'),
(33, 2, '2024-09-08 13:50:00', 567.00,  0,     'upi'),
(10, 6, '2024-09-11 09:15:00', 2340.00, 100,   'card'),
(41, 3, '2024-09-14 15:30:00', 678.00,  0,     'cash'),
(17, 4, '2024-09-17 11:45:00', 1890.00, 75,    'upi'),
(1,  2, '2024-09-20 14:00:00', 456.00,  0,     'card'),
(45, 6, '2024-09-23 16:15:00', 1230.00, 0,     'upi'),
(8,  3, '2024-09-26 10:30:00', 345.00,  0,     'cash'),
(36, 4, '2024-09-29 13:45:00', 780.00,  40,    'upi'),
(22, 2, '2024-10-02 09:20:00', 1560.00, 0,     'card'),
(49, 6, '2024-10-05 15:35:00', 234.00,  0,     'wallet'),
(13, 3, '2024-10-08 11:50:00', 890.00,  0,     'upi'),
(30, 4, '2024-10-11 14:05:00', 1100.00, 55,    'card'),
(3,  2, '2024-10-14 16:20:00', 567.00,  0,     'cash'),
(47, 6, '2024-10-17 10:35:00', 2340.00, 100,   'upi'),
(18, 3, '2024-10-20 13:50:00', 678.00,  0,     'card'),
(26, 4, '2024-10-23 09:15:00', 1890.00, 75,    'upi'),
(5,  2, '2024-10-26 15:30:00', 456.00,  0,     'cash'),
(42, 6, '2024-10-29 11:45:00', 1230.00, 0,     'upi'),
(9,  3, '2024-11-01 14:00:00', 345.00,  0,     'card'),
(37, 4, '2024-11-02 16:15:00', 780.00,  0,     'cash'),
(16, 2, '2024-11-03 10:30:00', 1560.00, 80,    'upi'),
(50, 6, '2024-11-04 13:45:00', 234.00,  0,     'wallet'),
(4,  3, '2024-11-05 09:20:00', 890.00,  0,     'card'),
(31, 4, '2024-11-06 15:35:00', 1100.00, 50,    'upi'),
(20, 2, '2024-11-07 11:50:00', 567.00,  0,     'cash'),
(44, 6, '2024-11-08 14:05:00', 2340.00, 150,   'card'),
(7,  3, '2024-11-09 16:20:00', 678.00,  0,     'upi'),
(25, 4, '2024-11-10 10:35:00', 1890.00, 75,    'card');

-- Order Items (linking orders to products)
INSERT INTO order_items (order_id, product_id, quantity, unit_price, subtotal) VALUES
(1,  1,  3, 58,  174), (1, 16,  1, 450, 450), (1, 22,  3, 95,  285),
(2,  5,  2, 110, 220), (2, 10,  1, 105, 105), (2, 21,  2, 285, 570), (2, 11,  4, 30,  120),
(3,  8, 10, 20,  200), (3, 12,  3, 35,  105), (3, 18,  1, 135, 135),
(4,  1,  4, 58,  232), (4, 17,  1, 450, 450),
(5,  6,  3, 120, 360), (5, 28,  1, 160, 160), (5, 13,  2, 40,   80), (5, 25,  1, 215, 215),
(6,  3,  5, 45,  225), (6, 11,  4, 30,  120), (6, 22,  1, 95,   95), (6, 19,  1, 40,   40),
(7,  16, 2, 450, 900), (7, 5,   3, 110, 330), (7, 21,  1, 285,  285), (7, 15,  2, 55,  110),
(8,  1,  5, 58,  290), (8, 17,  1, 450, 450),
(9,  12, 3, 35,  105), (9, 8,  10, 20,  200), (9, 19,  1, 40,   40),
(10, 16, 1, 450, 450), (10, 6,  3, 120, 360), (10, 21, 2, 285,  570), (10, 7,  2, 95,  190),
(11, 3,  3, 45,  135), (11, 22, 1, 95,   95), (11, 14, 1, 75,   75),
(12, 1,  4, 58,  232), (12, 11, 5, 30,  150), (12, 17, 1, 450,  450),
(13, 8,  5, 20,  100), (13, 12, 2, 35,   70), (13, 19, 1, 40,   40),
(14, 16, 1, 450, 450), (14, 5,  2, 110, 220), (14, 21, 2, 285,  570), (14, 6,  2, 120, 240),
(15, 1,  3, 58,  174), (15, 17, 1, 450, 450),
(16, 7,  3, 95,  285), (16, 13, 3, 40,  120), (16, 28, 1, 160,  160), (16, 25, 1, 215, 215),
(17, 3,  4, 45,  180), (17, 8,  5, 20,  100), (17, 22, 1, 95,   95),
(18, 16, 1, 450, 450), (18, 6,  2, 120, 240), (18, 21, 1, 285,  285), (18, 7,  1, 95,   95),
(19, 1,  5, 58,  290), (19, 11, 5, 30,  150), (19, 18, 1, 135,  135), (19, 22, 1, 95,   95),
(20, 3,  3, 45,  135), (20, 12, 2, 35,   70), (20, 14, 1, 75,   75),
(21, 16, 2, 450, 900), (21, 5,  2, 110, 220),
(22, 1,  3, 58,  174), (22, 17, 1, 450, 450),
(23, 7,  3, 95,  285), (23, 13, 2, 40,   80), (23, 25, 1, 215,  215), (23, 22, 1, 95,   95),
(24, 16, 1, 450, 450), (24, 6,  3, 120, 360), (24, 21, 2, 285,  570),
(25, 8,  5, 20,  100), (25, 12, 2, 35,   70), (25, 19, 1, 40,   40),
(26, 1,  4, 58,  232), (26, 17, 1, 450, 450),
(27, 16, 1, 450, 450), (27, 5,  3, 110, 330), (27, 21, 2, 285,  570), (27, 7,  2, 95,  190),
(28, 3,  5, 45,  225), (28, 11, 4, 30,  120), (28, 22, 1, 95,   95),
(29, 16, 1, 450, 450), (29, 6,  3, 120, 360), (29, 13, 2, 40,   80),
(30, 8, 10, 20,  200), (30, 18, 1, 135, 135),
(31, 1,  3, 58,  174), (31, 17, 1, 450, 450), (31, 22, 1, 95,   95),
(32, 16, 1, 450, 450), (32, 5,  2, 110, 220), (32, 21, 3, 285,  855),
(33, 7,  4, 95,  380), (33, 13, 3, 40,  120), (33, 25, 1, 215,  215), (33, 28, 1, 160, 160),
(34, 8,  5, 20,  100), (34, 12, 2, 35,   70), (34, 19, 1, 40,   40),
(35, 16, 1, 450, 450), (35, 6,  3, 120, 360), (35, 21, 1, 285,  285),
(36, 1,  3, 58,  174), (36, 11, 5, 30,  150), (36, 17, 1, 450,  450),
(37, 16, 2, 450, 900), (37, 5,  3, 110, 330), (37, 21, 2, 285,  570), (37, 15, 2, 55,  110),
(38, 3,  4, 45,  180), (38, 8,  5, 20,  100), (38, 22, 1, 95,   95), (38, 14, 1, 75,   75),
(39, 16, 1, 450, 450), (39, 6,  3, 120, 360), (39, 21, 2, 285,  570), (39, 7,  2, 95,  190),
(40, 1,  5, 58,  290), (40, 17, 1, 450, 450),
(41, 16, 1, 450, 450), (41, 5,  2, 110, 220), (41, 21, 1, 285,  285), (41, 11, 3, 30,   90),
(42, 3,  3, 45,  135), (42, 12, 2, 35,   70), (42, 19, 1, 40,   40),
(43, 1,  4, 58,  232), (43, 16, 1, 450, 450), (43, 22, 1, 95,   95),
(44, 16, 1, 450, 450), (44, 6,  3, 120, 360), (44, 21, 3, 285,  855),
(45, 8,  5, 20,  100), (45, 12, 2, 35,   70), (45, 19, 1, 40,   40),
(46, 7,  3, 95,  285), (46, 13, 2, 40,   80), (46, 28, 1, 160,  160), (46, 25, 1, 215, 215),
(47, 16, 2, 450, 900), (47, 5,  1, 110, 110),
(48, 1,  3, 58,  174), (48, 17, 1, 450, 450),
(49, 16, 1, 450, 450), (49, 6,  2, 120, 240), (49, 21, 1, 285,  285),
(50, 8, 10, 20,  200), (50, 18, 1, 135, 135);

-- Discounts
INSERT INTO discounts (product_id, label, discount_percent, start_date, end_date) VALUES
(7,  'Diwali Sale',         15.00, '2024-11-01', '2024-11-15'),
(11, 'Diwali Sale',         10.00, '2024-11-01', '2024-11-15'),
(16, 'Festival Offer',      12.00, '2024-10-20', '2024-11-10'),
(28, 'Summer Special',      20.00, '2024-05-01', '2024-06-30'),
(1,  'Dairy Week',           8.00, '2024-09-01', '2024-09-07'),
(21, 'Personal Care Week',  15.00, '2024-08-15', '2024-08-31'),
(6,  'Monsoon Offer',       10.00, '2024-07-01', '2024-07-31'),
(15, 'Snack Attack',        12.00, '2024-10-01', '2024-10-31'),
(25, 'Household Month',      8.00, '2024-10-01', '2024-10-31'),
(13, 'Chocolate Week',      18.00, '2024-02-10', '2024-02-17'),
(17, 'Grain Festival',       5.00, '2024-11-01', '2024-11-30'),
(30, 'Electronics Offer',   10.00, '2024-11-01', '2024-11-30');

-- Returns
INSERT INTO returns (order_id, product_id, return_date, reason, refund_amount) VALUES
(2,  5,  '2024-01-10', 'Product damaged',        110.00),
(7,  16, '2024-01-25', 'Wrong item delivered',   450.00),
(14, 21, '2024-02-15', 'Not satisfied with quality', 285.00),
(24, 6,  '2024-03-15', 'Expired product',        120.00),
(27, 5,  '2024-03-25', 'Damaged packaging',      110.00),
(37, 16, '2024-04-25', 'Wrong item',             450.00),
(44, 21, '2024-05-18', 'Quality issue',          285.00),
(50, 1,  '2024-08-04', 'Near expiry',             58.00),
(55, 17, '2024-06-18', 'Quantity mismatch',      450.00),
(64, 7,  '2024-07-20', 'Taste not good',          95.00),
(72, 16, '2024-08-22', 'Damaged',                450.00),
(85, 21, '2024-09-12', 'Wrong size',             285.00),
(91, 6,  '2024-10-05', 'Expired',               120.00),
(98, 11, '2024-10-20', 'Stale product',           30.00),
(103,16, '2024-10-18', 'Damaged box',            450.00);

-- Confirmation
SELECT 'QuickKart database setup complete!' AS status;
SELECT 'customers: ' || COUNT(*) FROM customers;
SELECT 'products: '  || COUNT(*) FROM products;
SELECT 'orders: '    || COUNT(*) FROM orders;
SELECT 'order_items: '|| COUNT(*) FROM order_items;
