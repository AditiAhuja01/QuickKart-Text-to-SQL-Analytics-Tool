import os
import sys
import unittest

# Ensure backend directory is in path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import main
import database

class TestQuickKartSafety(unittest.TestCase):
    """Unit tests validating SQL security guardrails and read-only database enforcement."""

    def test_valid_select_allowed(self):
        """Verifies standard read-only SELECT queries pass validation."""
        sql = "SELECT product_id, name, price FROM products LIMIT 10;"
        # Should execute without raising HTTPException
        main.validate_sql_safety(sql)

    def test_blocks_multiple_statements(self):
        """Verifies chained multi-statement SQL injection attacks are blocked."""
        sql = "SELECT * FROM products; DROP TABLE customers;"
        with self.assertRaises(Exception) as ctx:
            main.validate_sql_safety(sql)
        self.assertIn("Multiple SQL statements", str(ctx.exception))

    def test_blocks_drop_table(self):
        """Verifies DROP TABLE statements are blocked."""
        sql = "DROP TABLE customers;"
        with self.assertRaises(Exception) as ctx:
            main.validate_sql_safety(sql)
        self.assertIn("Only read-only SELECT queries", str(ctx.exception))

    def test_blocks_delete_statement(self):
        """Verifies DELETE statements are blocked."""
        sql = "DELETE FROM orders WHERE order_id = 1;"
        with self.assertRaises(Exception) as ctx:
            main.validate_sql_safety(sql)
        self.assertIn("Only read-only SELECT queries", str(ctx.exception))

    def test_blocks_update_statement(self):
        """Verifies UPDATE statements are blocked."""
        sql = "UPDATE products SET price = 100 WHERE product_id = 1;"
        with self.assertRaises(Exception) as ctx:
            main.validate_sql_safety(sql)
        self.assertIn("Only read-only SELECT queries", str(ctx.exception))

    def test_readonly_connection_blocks_direct_writes(self):
        """Verifies that SQLite physical engine blocks writes in mode=ro."""
        conn, _ = database.get_readonly_connection()
        cursor = conn.cursor()
        with self.assertRaises(Exception) as ctx:
            cursor.execute("UPDATE products SET price = 999 WHERE product_id = 1;")
        self.assertIn("readonly", str(ctx.exception).lower())
        conn.close()

if __name__ == "__main__":
    unittest.main()
