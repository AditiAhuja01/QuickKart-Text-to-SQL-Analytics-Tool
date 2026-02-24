// All backend API calls live here.
// If you change your backend URL (e.g. after deploying to Render),
// just update BASE_URL below — nothing else needs to change.

const BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

/**
 * Ask a plain English question.
 * Returns: { question, sql, columns, rows, count }
 */
export async function askQuestion(question) {
  const res = await fetch(`${BASE_URL}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Something went wrong");
  }
  return res.json();
}

/**
 * Explain what a SQL query does in plain English.
 * Returns: { explanation }
 */
export async function explainSQL(sql) {
  const res = await fetch(`${BASE_URL}/explain`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ sql }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Could not explain query");
  }
  return res.json();
}

/**
 * Get query history.
 * Returns: { history: [...] }
 */
export async function getHistory() {
  const res = await fetch(`${BASE_URL}/history`);
  if (!res.ok) throw new Error("Could not load history");
  return res.json();
}

/**
 * Clear all query history.
 */
export async function clearHistory() {
  const res = await fetch(`${BASE_URL}/history`, { method: "DELETE" });
  if (!res.ok) throw new Error("Could not clear history");
  return res.json();
}

/**
 * Get suggested starter questions.
 * Returns: { suggestions: [...] }
 */
export async function getSuggestions() {
  const res = await fetch(`${BASE_URL}/suggestions`);
  if (!res.ok) throw new Error("Could not load suggestions");
  return res.json();
}

/**
 * Get database schema info.
 * Returns: { tables: [...] }
 */
export async function getSchema() {
  const res = await fetch(`${BASE_URL}/schema`);
  if (!res.ok) throw new Error("Could not load schema");
  return res.json();
}
