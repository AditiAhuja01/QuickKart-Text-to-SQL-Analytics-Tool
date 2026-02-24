import React, { useEffect, useState } from "react";
import { getSchema } from "../api";

export default function SchemaExplorer() {
  const [tables, setTables] = useState([]);
  const [open, setOpen] = useState(false);
  const [expanded, setExpanded] = useState(null);

  useEffect(() => {
    getSchema()
      .then((data) => setTables(data.tables || []))
      .catch(() => {});
  }, []);

  const toggle = (name) => setExpanded(expanded === name ? null : name);

  return (
    <div className={`schema-panel ${open ? "open" : ""}`}>
      <button className="schema-toggle" onClick={() => setOpen((o) => !o)}>
        {open ? "✕" : "🗂️"}
      </button>

      {open && (
        <div className="schema-content">
          <div className="schema-panel-header">
            <span>Database Schema</span>
            <span className="schema-subtitle">{tables.length} tables</span>
          </div>

          {tables.map((table) => (
            <div key={table.name} className="schema-table">
              <button
                className="schema-table-header"
                onClick={() => toggle(table.name)}
              >
                <span className="schema-table-icon">▶</span>
                <span className="schema-table-name">{table.name}</span>
                <span className="schema-col-count">
                  {table.columns.length} cols
                </span>
              </button>

              {expanded === table.name && (
                <div className="schema-table-body">
                  <p className="schema-description">{table.description}</p>
                  <ul className="schema-columns">
                    {table.columns.map((col) => (
                      <li key={col} className="schema-column">
                        <span className="col-dot" />
                        {col}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
