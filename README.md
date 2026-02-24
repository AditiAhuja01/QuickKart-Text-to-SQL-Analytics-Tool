# 🛒 QuickKart Analytics

> Ask business questions in plain English. Get instant answers from your store's data.

A **Text-to-SQL** web application built for retail store managers who want data insights without knowing SQL. Powered by Llama 3 via Groq AI.

---

## 🎯 What It Does

Type a question like:

> *"Which products are below reorder level?"*

The app:
1. Sends your question to **Groq AI**
2. Groq writes the correct **SQL query** for your database
3. SQL runs on **SQLite**
4. Results appear as a table on screen

No SQL knowledge needed. No waiting for a data analyst.

---

## ✨ Features

| Feature | Description |
|---|---|
| **Natural Language Query** | Type plain English, get real database results |
| **SQL Explainer** | Click "What does this mean?" to get a plain English explanation of the SQL that ran |
| **Query History** | Every question you ask is saved — click any to re-run it |
| **Schema Explorer** | See all 10 tables and their columns in a side panel |
| **Suggested Questions** | 15 pre-built starter questions for common retail insights |

---

## 🗃️ Database Schema

QuickKart uses a realistic retail supermarket database with **10 tables**.

### Entity Relationship Overview

```
customers ──────< orders >──────── employees (cashier)
                    │
                    └──< order_items >── products ──< categories
                                             │
                                         inventory >── suppliers
                                             │
                                         discounts
                    │
                    └──< returns >──── products
```

---

### Table 1: `customers`
People who shop at QuickKart (via loyalty program / app / WhatsApp billing).

| Column | Type | Description |
|---|---|---|
| customer_id | SERIAL PK | Unique ID |
| name | VARCHAR | Full name |
| email | VARCHAR | Email address |
| phone | VARCHAR | Mobile number |
| city | VARCHAR | City of residence |
| state | VARCHAR | State |
| gender | VARCHAR | Male / Female |
| age | INTEGER | Age in years |
| signup_date | DATE | When they joined the loyalty program |
| loyalty_points | INTEGER | Points accumulated from purchases |

---

### Table 2: `categories`
Product groupings used to organize the store's inventory.

| Column | Type | Description |
|---|---|---|
| category_id | SERIAL PK | Unique ID |
| name | VARCHAR | e.g. Dairy, Beverages, Snacks |
| description | TEXT | What products belong here |

**Categories in QuickKart:** Dairy, Beverages, Snacks, Grains & Pulses, Personal Care, Household, Frozen Foods, Electronics

---

### Table 3: `suppliers`
Companies that supply products to QuickKart.

| Column | Type | Description |
|---|---|---|
| supplier_id | SERIAL PK | Unique ID |
| name | VARCHAR | Company name (e.g. Amul, PepsiCo) |
| contact_person | VARCHAR | Name of account manager |
| phone | VARCHAR | Contact number |
| city | VARCHAR | Supplier's city |
| rating | DECIMAL(2,1) | Reliability rating from 1.0 to 5.0 |

---

### Table 4: `employees`
Staff members at QuickKart — cashiers, managers, stock boys.

| Column | Type | Description |
|---|---|---|
| employee_id | SERIAL PK | Unique ID |
| name | VARCHAR | Full name |
| role | VARCHAR | cashier / manager / stock_boy |
| salary | DECIMAL | Monthly salary (INR) |
| joining_date | DATE | When they joined |
| shift | VARCHAR | morning / evening / night |

---

### Table 5: `products`
Every product sold at QuickKart.

| Column | Type | Description |
|---|---|---|
| product_id | SERIAL PK | Unique ID |
| name | VARCHAR | Product name |
| category_id | FK | Links to categories |
| brand | VARCHAR | Brand name |
| price | DECIMAL | Selling price (INR) |
| cost_price | DECIMAL | Purchase/wholesale price |
| unit | VARCHAR | kg / piece / litre / pack |

> 💡 `price - cost_price` = profit. `(price - cost_price) / price * 100` = profit margin %

---

### Table 6: `inventory`
Current stock levels for each product.

| Column | Type | Description |
|---|---|---|
| inventory_id | SERIAL PK | Unique ID |
| product_id | FK | Links to products |
| supplier_id | FK | Which supplier provides this |
| quantity_in_stock | INTEGER | How many units currently in store |
| reorder_level | INTEGER | Minimum threshold — below this = reorder needed |
| last_restocked | DATE | When stock was last replenished |

> 💡 `quantity_in_stock <= reorder_level` means the product needs restocking.

---

### Table 7: `orders`
Each customer purchase session at the checkout counter.

| Column | Type | Description |
|---|---|---|
| order_id | SERIAL PK | Unique ID |
| customer_id | FK | Which customer placed the order |
| employee_id | FK | Which cashier processed it |
| order_date | TIMESTAMP | Date and time of purchase |
| total_amount | DECIMAL | Total bill amount (INR) |
| discount_applied | DECIMAL | Discount amount given |
| payment_method | VARCHAR | cash / upi / card / wallet |

---

### Table 8: `order_items`
Individual product lines within each order. One row per product per order.

| Column | Type | Description |
|---|---|---|
| item_id | SERIAL PK | Unique ID |
| order_id | FK | Which order this belongs to |
| product_id | FK | Which product was bought |
| quantity | INTEGER | How many units |
| unit_price | DECIMAL | Price at time of purchase |
| subtotal | DECIMAL | quantity × unit_price |

---

### Table 9: `discounts`
Promotional campaigns and sale events.

| Column | Type | Description |
|---|---|---|
| discount_id | SERIAL PK | Unique ID |
| product_id | FK | Which product is discounted |
| label | VARCHAR | Campaign name (e.g. "Diwali Sale") |
| discount_percent | DECIMAL | e.g. 15.00 = 15% off |
| start_date | DATE | When the offer starts |
| end_date | DATE | When the offer ends |

> 💡 Active discounts: `CURRENT_DATE BETWEEN start_date AND end_date`

---

### Table 10: `returns`
Products returned by customers with reasons and refund amounts.

| Column | Type | Description |
|---|---|---|
| return_id | SERIAL PK | Unique ID |
| order_id | FK | The original order |
| product_id | FK | Which product was returned |
| return_date | DATE | When it was returned |
| reason | VARCHAR | e.g. "Damaged", "Expired", "Wrong item" |
| refund_amount | DECIMAL | How much was refunded (INR) |

---

### Table 11: `query_history` *(auto-created by app)*
Stores every question asked through the app.

| Column | Type | Description |
|---|---|---|
| id | SERIAL PK | Unique ID |
| question | TEXT | The plain English question |
| sql_query | TEXT | The SQL Gemini generated |
| result_count | INTEGER | How many rows were returned |
| created_at | TIMESTAMP | When it was asked |

---

## 🔧 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 |
| Backend | FastAPI (Python) |
| Database | SQLite |
| AI | Llama 3 via Groq (free tier) |
| Styling | Custom CSS |

---

## 🚀 Local Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- SQLite (included with Python)
- Free Groq API key from [console.groq.com](https://console.groq.com/keys)

---

### Step 1: Clone and set up database

```bash
cd backend
# Run setup script (creates quickkart.db + sample data)
python setup_db.py
```

---

### Step 2: Backend setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Copy env file and fill in your values
cp .env.example .env
# Edit .env: add your GROQ_API_KEY

# Start the server
uvicorn main:app --reload
# Backend runs at http://localhost:8000
```

---

### Step 3: Frontend setup

```bash
cd frontend

# Install dependencies
npm install

# Start the dev server
npm start
# Frontend runs at http://localhost:3000
```

---

### Step 4: Open the app

Go to **http://localhost:3000** and ask your first question!

---

## 💡 Sample Questions to Try

```
Show me top 10 customers by loyalty points
Which products are below reorder level?
What was total revenue this month?
Which cashier processed the most orders?
Show me all active discounts
Which products were returned the most?
What is the profit margin for each product?
Which supplier has the lowest rating?
Which city has the most customers?
Which age group spends the most money?
Show me all orders paid by UPI this month
Who are customers who haven't ordered in 60 days?
```

---

## 🌐 Deployment

### Deploy Backend to Render
1. Push code to GitHub
2. Create new **Web Service** on [render.com](https://render.com)
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables (GEMINI_API_KEY, DB_HOST, etc.)
6. Add a **PostgreSQL** database on Render and connect it

### Deploy Frontend to Vercel
1. Create new project on [vercel.com](https://vercel.com)
2. Connect your GitHub repo, select `frontend` as root
3. Add environment variable: `REACT_APP_API_URL=https://your-render-url.onrender.com`
4. Deploy!

---

## 📁 Project Structure

```
quickkart/
├── backend/
│   ├── main.py          ← FastAPI routes (/ask, /explain, /history, /schema, /suggestions)
│   ├── database.py      ← PostgreSQL connection + query runner
│   ├── gemini.py        ← Groq AI calls (text→SQL, SQL→explanation)
│   ├── schema.py        ← DB schema context sent to Gemini
│   ├── .env.example     ← Environment variable template
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx               ← Root component, state management
│   │   ├── App.css               ← All styles
│   │   ├── api.js                ← All fetch calls to backend
│   │   └── components/
│   │       ├── SearchBar.jsx     ← Question input
│   │       ├── ResultsTable.jsx  ← Query results display
│   │       ├── SQLExplainer.jsx  ← SQL + plain English explanation
│   │       ├── History.jsx       ← Query history sidebar
│   │       ├── Suggestions.jsx   ← Starter question chips
│   │       └── SchemaExplorer.jsx← Database schema side panel
│   └── package.json
│
└── database/
    └── setup.sql         ← All 10 tables + realistic Indian retail sample data
```

---

## 👨‍💻 Built By

MCA project — QuickKart Analytics demonstrates full-stack development with AI integration for real-world retail analytics use cases.
