from groq import Groq
import os
import re
from dotenv import load_dotenv
from schema import DB_SCHEMA_CONTEXT

load_dotenv()

client = None
try:
    api_key = os.getenv("GROQ_API_KEY")
    if api_key:
        client = Groq(api_key=api_key)
except Exception:
    client = None

# Offline rule-based SQL generator and business assumptions for retail analytics
OFFLINE_QUERY_MAP = [
    (["reorder", "low stock", "pending stock", "below reorder"],
     "SELECT p.name, p.brand, i.quantity_in_stock, i.reorder_level FROM inventory i JOIN products p ON i.product_id = p.product_id WHERE i.quantity_in_stock <= i.reorder_level;",
     "Assuming products needing reorder have quantity in stock at or below reorder threshold."),
    
    (["loyalty", "points", "top 10 customer", "loyal"],
     "SELECT name, email, phone, city, loyalty_points FROM customers ORDER BY loyalty_points DESC LIMIT 10;",
     "Assuming top customers refers to members with the highest accumulated loyalty points."),
    
    (["revenue this month", "total revenue", "revenue"],
     "SELECT SUM(total_amount) AS total_revenue, COUNT(order_id) AS total_orders FROM orders;",
     "Assuming total revenue represents gross transaction value across all orders."),
    
    (["category", "categories", "most sales"],
     "SELECT c.name AS category, SUM(oi.subtotal) AS total_sales FROM categories c JOIN products p ON c.category_id = p.category_id JOIN order_items oi ON p.product_id = oi.product_id GROUP BY c.name ORDER BY total_sales DESC;",
     "Assuming highest category sales refers to sum of order item subtotals."),
    
    (["60 days", "not ordered", "haven't ordered", "inactive"],
     "SELECT name, email, phone, city FROM customers WHERE customer_id NOT IN (SELECT DISTINCT customer_id FROM orders WHERE order_date >= date('now', '-60 days'));",
     "Assuming inactive customers are those with no recorded orders in the past 60 days."),
    
    (["cashier", "processed the most"],
     "SELECT e.name, COUNT(o.order_id) AS orders_processed FROM employees e JOIN orders o ON e.employee_id = o.employee_id WHERE e.role = 'cashier' GROUP BY e.name ORDER BY orders_processed DESC LIMIT 1;",
     "Assuming top cashier refers to employee with the highest count of processed orders."),
    
    (["active discount", "discounts", "discount", "sale"],
     "SELECT p.name AS product, d.label, d.discount_percent, d.start_date, d.end_date FROM discounts d JOIN products p ON d.product_id = p.product_id;",
     "Assuming active promotional discounts configured across merchandise."),
    
    (["returned", "returns", "refund"],
     "SELECT p.name AS product, COUNT(r.return_id) AS return_count, SUM(r.refund_amount) AS total_refunded FROM returns r JOIN products p ON r.product_id = p.product_id GROUP BY p.name ORDER BY return_count DESC;",
     "Assuming return analysis aggregates items by total return frequency and refund volume."),
    
    (["profit margin", "margin"],
     "SELECT name, brand, price, cost_price, ROUND(((price - cost_price) / price * 100), 2) AS profit_margin_pct FROM products ORDER BY profit_margin_pct DESC;",
     "Assuming profit margin is calculated as ((price - cost_price) / price) * 100."),
    
    (["supplier", "lowest rating", "rating"],
     "SELECT name, contact_person, city, rating FROM suppliers ORDER BY rating ASC LIMIT 1;",
     "Assuming lowest rated supplier is determined by overall supplier quality score."),
    
    (["upi", "paid by upi"],
     "SELECT order_id, customer_id, total_amount, payment_method, order_date FROM orders WHERE payment_method = 'upi' LIMIT 50;",
     "Assuming orders filtered where payment method equals 'upi'."),
    
    (["city", "most customers"],
     "SELECT city, COUNT(*) AS customer_count FROM customers GROUP BY city ORDER BY customer_count DESC;",
     "Assuming customer count grouped by registered billing city."),
    
    (["best selling", "top 5 best", "best seller"],
     "SELECT p.name AS product, SUM(oi.quantity) AS total_quantity_sold FROM products p JOIN order_items oi ON p.product_id = oi.product_id GROUP BY p.name ORDER BY total_quantity_sold DESC LIMIT 5;",
     "Assuming best-selling products are ranked by total unit quantity sold."),
    
    (["age group", "age", "spends the most"],
     "SELECT CASE WHEN age < 25 THEN 'Under 25' WHEN age BETWEEN 25 AND 40 THEN '25-40' ELSE '40+' END AS age_group, SUM(o.total_amount) AS total_spent FROM customers c JOIN orders o ON c.customer_id = o.customer_id GROUP BY age_group ORDER BY total_spent DESC;",
     "Assuming customer demographic breakdown segmented into Under 25, 25-40, and 40+ cohorts."),
    
    (["employee", "staff"],
     "SELECT employee_id, name, role, salary, shift FROM employees;",
     "Assuming complete employee roster with operational roles and shifts."),
    
    (["all product", "products", "inventory"],
     "SELECT product_id, name, brand, price, unit FROM products LIMIT 50;",
     "Assuming standard product catalog view."),
    
    (["customer", "customers"],
     "SELECT customer_id, name, city, loyalty_points FROM customers LIMIT 50;",
     "Assuming registered customer profiles with current loyalty balances."),
    
    (["order", "orders", "recent"],
     "SELECT order_id, order_date, total_amount, payment_method FROM orders ORDER BY order_date DESC LIMIT 50;",
     "Assuming chronological list of most recent customer orders.")
]

def generate_sql(question: str) -> tuple[str, str]:
    """Generates SQL query and business interpretation assumption for a question."""
    # 1. Try Groq AI (groq/compound-mini or available model)
    if client:
        prompt_instruction = (
            f"Question: {question}\n\n"
            "Format your answer strictly as:\n"
            "ASSUMPTION: <one-line statement of business interpretation>\n"
            "SQL: <single valid SELECT SQL query>"
        )
        for model_id in ["groq/compound-mini", "llama-3.3-70b-versatile", "openai/gpt-oss-20b"]:
            try:
                response = client.chat.completions.create(
                    model=model_id,
                    messages=[
                        {"role": "system", "content": DB_SCHEMA_CONTEXT},
                        {"role": "user", "content": prompt_instruction}
                    ],
                    max_tokens=250,
                    timeout=5
                )
                text = response.choices[0].message.content.strip()
                assumption = "Interpreted directly from question terms."
                sql = text

                if "ASSUMPTION:" in text and "SQL:" in text:
                    assumption_part = text.split("ASSUMPTION:")[1].split("SQL:")[0].strip()
                    sql_part = text.split("SQL:")[1].strip()
                    if assumption_part:
                        assumption = assumption_part
                    if sql_part:
                        sql = sql_part

                sql = sql.replace("```sql", "").replace("```", "").strip()
                if sql.upper().startswith("SELECT"):
                    return sql, assumption
            except Exception:
                continue

    # 2. Resilient Offline Fallback Matcher
    q_lower = question.lower()
    for keywords, sql, assumption in OFFLINE_QUERY_MAP:
        if any(kw in q_lower for kw in keywords):
            return sql, assumption

    # Default fallback
    return (
        "SELECT product_id, name, brand, price, unit FROM products LIMIT 25;",
        "Defaulting to top products in inventory."
    )

def retry_fix_sql(question: str, failed_sql: str, error_msg: str) -> str:
    """Self-healing: sends the error back to the model once to correct syntax errors."""
    if not client:
        return failed_sql
    try:
        retry_prompt = (
            f"The following SQL query failed with an error:\n"
            f"Question: {question}\n"
            f"Failed SQL: {failed_sql}\n"
            f"Error Message: {error_msg}\n\n"
            "Fix the SQL query so it runs successfully. Return ONLY the corrected SELECT query."
        )
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": DB_SCHEMA_CONTEXT},
                {"role": "user", "content": retry_prompt}
            ],
            max_tokens=250,
            timeout=5
        )
        corrected = response.choices[0].message.content.strip()
        corrected = corrected.replace("```sql", "").replace("```", "").strip()
        if corrected.upper().startswith("SELECT"):
            return corrected
    except Exception:
        pass
    return failed_sql

def explain_sql(sql: str) -> str:
    """Generates a concise 2-sentence explanation of what the SQL query computes."""
    if client:
        for model_id in ["groq/compound-mini", "llama-3.3-70b-versatile", "openai/gpt-oss-20b"]:
            try:
                response = client.chat.completions.create(
                    model=model_id,
                    messages=[
                        {"role": "user", "content": f"Explain this SQL query in 2 simple sentences for a retail store manager:\n\n{sql}"}
                    ],
                    max_tokens=150,
                    timeout=5
                )
                return response.choices[0].message.content.strip()
            except Exception:
                continue

    sql_upper = sql.upper()
    tables = [t for t in ["PRODUCTS", "CUSTOMERS", "ORDERS", "ORDER_ITEMS", "INVENTORY", "DISCOUNTS", "RETURNS", "SUPPLIERS", "EMPLOYEES"] if t in sql_upper]
    table_list = ", ".join(tables) if tables else "the database"
    return f"This query scans {table_list} to filter and compute metrics answering your store question. It selects the relevant business fields and orders the results so you can take immediate action."
