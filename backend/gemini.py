from groq import Groq
import os
from dotenv import load_dotenv
from schema import DB_SCHEMA_CONTEXT

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_sql(question: str) -> str:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": DB_SCHEMA_CONTEXT},
            {"role": "user", "content": f"Question: {question}\n\nSQL Query:"}
        ]
    )
    sql = response.choices[0].message.content.strip()
    sql = sql.replace("```sql", "").replace("```", "").strip()
    return sql

def explain_sql(sql: str) -> str:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": f"Explain this SQL query in 2-3 simple sentences for a non-technical retail store manager:\n\n{sql}"}
        ]
    )
    return response.choices[0].message.content.strip()
