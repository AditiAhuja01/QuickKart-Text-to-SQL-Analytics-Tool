from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import run_query, save_query_history, get_history, create_history_table
from ai_service import generate_sql, explain_sql, retry_fix_sql
import re
import sqlite3

# App setup
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

# Request Models
class AskRequest(BaseModel):
    question: str

class ExplainRequest(BaseModel):
    sql: str

# Routes

@app.get("/")
def root():
    return {"message": "QuickKart Analytics API is running"}


def validate_sql_safety(sql: str):
    """
    Enforces strict SQL security guardrails before running any query.
    Blocks multiple statements, and any command other than SELECT.
    """
    clean_sql = sql.strip().rstrip(";")

    # Block multiple statements joined by semicolons (e.g. SELECT ...; DROP TABLE ...)
    if ";" in clean_sql:
        raise HTTPException(
            status_code=400,
            detail="Security error: Multiple SQL statements are not permitted."
        )

    # Only allow SELECT statements
    first_token = clean_sql.split()[0].upper() if clean_sql.split() else ""
    if first_token != "SELECT":
        raise HTTPException(
            status_code=400,
            detail="Security error: Only read-only SELECT queries are allowed."
        )

    # Block known data modification commands even if they appear mid-query
    forbidden_tokens = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "PRAGMA", "ATTACH"]
    for token in forbidden_tokens:
        if re.search(rf"\b{token}\b", clean_sql, re.IGNORECASE):
            raise HTTPException(
                status_code=400,
                detail=f"Security error: Modification command '{token}' is blocked."
            )


@app.post("/ask")
def ask(req: AskRequest):
    """
    Main route: takes a plain English question and returns SQL, assumption, and results.

    Steps:
      1. Send the question to the AI model to get SQL and a business assumption.
      2. Validate the SQL for safety (single SELECT only, no mutation commands).
      3. Run the SQL on a read-only database connection.
         If it fails, retry once with a self-healing model call.
      4. Save the question and SQL to the audit log (query_history table).
      5. Return the results to the frontend.
    """
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    # Step 1: Ask the AI model to generate SQL and a business assumption
    try:
        sql, assumption = generate_sql(req.question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation error: {str(e)}")

    # Step 2: Check the generated SQL is safe before running it
    validate_sql_safety(sql)

    # Step 3: Run the SQL — retry once if it fails
    try:
        result = run_query(sql)
    except Exception as first_err:
        # Send the error back to the model and let it fix the SQL (one attempt only)
        try:
            fixed_sql = retry_fix_sql(req.question, sql, str(first_err))
            validate_sql_safety(fixed_sql)
            result = run_query(fixed_sql)
            sql = fixed_sql
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="Could not execute query for this question. Please try rephrasing."
            )

    # Step 4: Save to audit log — failure here should not block the user response
    try:
        save_query_history(req.question, sql, result["count"])
    except Exception:
        pass

    # Step 5: Return to frontend
    return {
        "question": req.question,
        "sql": sql,
        "assumption": assumption,
        "columns": result["columns"],
        "rows": result["rows"],
        "count": result["count"],
    }


@app.post("/explain")
def explain(req: ExplainRequest):
    """
    Takes a SQL query and returns a plain English explanation.
    Used when the user clicks 'What does this mean?' in the SQL panel.
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
    Returns the last 20 queries from query_history.
    Used to populate the History sidebar panel on the frontend.
    """
    try:
        records = get_history(limit=20)
        return {"history": records}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/history")
def clear_history():
    """Clear all query history records."""
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
    Shown as clickable chips on the frontend home screen.
    """
    return {
        "suggestions": [
            "Show me top 10 customers by loyalty points",
            "Which products are below reorder level?",
            "What was total revenue this month?",
            "Which product category generates the most sales?",
            "Who are the customers who have not ordered in 60 days?",
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
    Returns table names, descriptions, and column lists.
    Used by the Schema Explorer panel on the frontend.
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
                "description": "Store staff: cashiers, managers, stock boys",
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
