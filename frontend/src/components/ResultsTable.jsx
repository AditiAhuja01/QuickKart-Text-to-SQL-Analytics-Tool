import React from "react";

export default function ResultsTable({ data }) {
  if (!data) return null;

  const { question, columns, rows, count, sql } = data;

  return (
    <div className="results-section">
      <div className="results-header">
        <div>
          <p className="results-question">"{question}"</p>
          <p className="results-count">{count} row{count !== 1 ? "s" : ""} returned</p>
          {data.assumption && (
            <p className="results-assumption" style={{ fontSize: "0.85rem", color: "#64748B", marginTop: "4px" }}>
              <span style={{ fontWeight: 600, color: "#0F172A" }}>Assumption:</span> {data.assumption}
            </p>
          )}
        </div>
      </div>

      {rows.length === 0 ? (
        <div className="no-results">
          <p>No results found for this query.</p>
        </div>
      ) : (
        <div className="table-wrapper">
          <table className="results-table">
            <thead>
              <tr>
                {columns.map((col) => (
                  <th key={col}>{col.replace(/_/g, " ")}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row, i) => (
                <tr key={i}>
                  {columns.map((col) => (
                    <td key={col}>
                      {row[col] === null ? (
                        <span className="null-value">—</span>
                      ) : typeof row[col] === "number" && String(row[col]).includes(".") ? (
                        `₹${Number(row[col]).toLocaleString("en-IN", { minimumFractionDigits: 2 })}`
                      ) : (
                        String(row[col])
                      )}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
