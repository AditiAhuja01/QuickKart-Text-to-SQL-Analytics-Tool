from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import run_query, save_query_history, get_history, create_history_table
from gemini import generate_sql, explain_sql
import sqlite3

# ── App setup ──────────────────────────────────────────────
app = FastAPI(title="QuickKart Analytics API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # In production, replace * with your frontend URL
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create history table on startup
@app.on_event("startup")
def startup():
    create_history_table()

# ── Request Models ─────────────────────────────────────────
class AskRequest(BaseModel):
    question: str

class ExplainRequest(BaseModel):
    sql: str

# ── Routes ─────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "QuickKart Analytics API is running ✅"}


@app.post("/ask")
def ask(req: AskRequest):
    """
    Main route: takes plain English → returns SQL + query results.
    Steps:
      1. Send question to Gemini → get SQL
      2. Validate it's a SELECT query (safety)
      3. Run SQL on PostgreSQL
      4. Save to history
      5. Return everything to frontend
    """
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    # Step 1: Generate SQL
    try:
        sql = generate_sql(req.question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI error: {str(e)}")

    # Step 2: Safety check — only allow SELECT
    if not sql.strip().upper().startswith("SELECT"):
        raise HTTPException(
            status_code=400,
            detail="Only SELECT queries are allowed. Please ask a data question."
        )

    # Step 3: Run SQL
    try:
        result = run_query(sql)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    # Step 4: Save to history
    try:
        save_query_history(req.question, sql, result["count"])
    except Exception:
        pass  # History saving failure should not crash the main request

    # Step 5: Return to frontend
    return {
        "question": req.question,
        "sql": sql,
        "columns": result["columns"],
        "rows": result["rows"],
        "count": result["count"],
    }


@app.post("/explain")
def explain(req: ExplainRequest):
    """
    Takes a SQL query → returns plain English explanation.
    Used when user clicks 'What does this mean?' on the SQL explainer panel.
    """
    if not req.sql.strip():
        raise HTTPException(status_code=400, detail="SQL cannot be empty")

    try:
        explanation = explain_sql(req.sql)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI error: {str(e)}")

    return {"explanation": explanation}


@app.get("/history")
def history():
    """
    Returns last 20 queries from query_history table.
    Used to populate the History sidebar on the frontend.
    """
    try:
        records = get_history(limit=20)
        return {"history": records}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/history")
def clear_history():
    """Clear all query history."""
    from database import get_connection
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM query_history")
        conn.commit()
        return {"message": "History cleared"}
    finally:
        conn.close()


@app.get("/suggestions")
def suggestions():
    """
    Returns pre-built suggested questions for the store manager.
    Shown as clickable chips on the frontend.
    """
    return {
        "suggestions": [
            "Show me top 10 customers by loyalty points",
            "Which products are below reorder level?",
            "What was total revenue this month?",
            "Which product category generates the most sales?",
            "Who are the customers who haven't ordered in 60 days?",
            "Which cashier processed the most orders?",
            "Show me all active discounts",
            "Which products were returned the most?",
            "What is the profit margin for each product?",
            "Which supplier has the lowest rating?",
            "Show me all orders paid by UPI this month",
            "Which city has the most customers?",
            "What are the top 5 best selling products?",
            "Show me all pending stock that needs reorder",
            "Which age group spends the most money?",
        ]
    }


@app.get("/schema")
def schema():
    """
    Returns schema info for display in the frontend Schema Explorer.
    """
    return {
        "tables": [
            {
                "name": "customers",
                "description": "People who shop at QuickKart",
                "columns": ["customer_id", "name", "email", "phone", "city", "state", "gender", "age", "signup_date", "loyalty_points"]
            },
            {
                "name": "categories",
                "description": "Product groupings like Dairy, Beverages, Snacks",
                "columns": ["category_id", "name", "description"]
            },
            {
                "name": "suppliers",
                "description": "Companies that supply products to the store",
                "columns": ["supplier_id", "name", "contact_person", "phone", "city", "rating"]
            },
            {
                "name": "employees",
                "description": "Store staff — cashiers, managers, stock boys",
                "columns": ["employee_id", "name", "role", "salary", "joining_date", "shift"]
            },
            {
                "name": "products",
                "description": "All products sold at QuickKart",
                "columns": ["product_id", "name", "category_id", "brand", "price", "cost_price", "unit"]
            },
            {
                "name": "inventory",
                "description": "Current stock levels for each product",
                "columns": ["inventory_id", "product_id", "supplier_id", "quantity_in_stock", "reorder_level", "last_restocked"]
            },
            {
                "name": "orders",
                "description": "Each customer purchase transaction",
                "columns": ["order_id", "customer_id", "employee_id", "order_date", "total_amount", "discount_applied", "payment_method"]
            },
            {
                "name": "order_items",
                "description": "Individual products inside each order",
                "columns": ["item_id", "order_id", "product_id", "quantity", "unit_price", "subtotal"]
            },
            {
                "name": "discounts",
                "description": "Promotional offers and sale campaigns",
                "columns": ["discount_id", "product_id", "label", "discount_percent", "start_date", "end_date"]
            },
            {
                "name": "returns",
                "description": "Products returned by customers with reasons",
                "columns": ["return_id", "order_id", "product_id", "return_date", "reason", "refund_amount"]
            },
        ]
    }
