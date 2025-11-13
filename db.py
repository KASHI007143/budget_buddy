# db.py
import sqlite3
from datetime import datetime

DB_NAME = "budgetbuddy.db"

def get_connection():
    """
    Establish and return a connection to the SQLite database.
    Sets row_factory to access columns by name.
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # access columns by name
    return conn

def create_table():
    """
    Create the expenses table if it does not exist.
    Columns: id, date, category, amount, notes.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                notes TEXT
            )
        """)
        conn.commit()

# ---- Validation helpers ----
def validate_date(date_str):
    """
    Validate that the date string is in 'YYYY-MM-DD' format.
    Raises ValueError if invalid.
    """
    try:
        # will raise ValueError if format wrong
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
    except Exception:
        raise ValueError("Date must be in YYYY-MM-DD format")

def validate_amount(amount):
    """
    Validate that the amount can be converted to a float.
    Raises ValueError if invalid.
    """
    try:
        val = float(amount)
        return val
    except Exception:
        raise ValueError("Amount must be a number")

# ---- CRUD operations ----
def add_expense(date, category, amount, notes=""):
    """
    Add a new expense record to the database.
    Validates date and amount before insertion.
    """
    date = validate_date(date)
    amount = validate_amount(amount)
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO expenses (date, category, amount, notes) VALUES (?, ?, ?, ?)",
            (date, category.strip(), amount, notes.strip())
        )
        conn.commit()
        return cursor.lastrowid

def get_all_expenses():
    """
    Retrieve all expenses ordered by date descending, then id descending.
    Returns a list of dictionaries.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM expenses ORDER BY date DESC, id DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def get_expense_by_id(expense_id):
    """
    Retrieve a single expense by its ID.
    Returns a dictionary or None if not found.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def update_expense(expense_id, date, category, amount, notes=""):
    """
    Update an existing expense record by ID.
    Validates date and amount before update.
    Returns True if update was successful, False otherwise.
    """
    if not get_expense_by_id(expense_id):
        return False
    date = validate_date(date)
    amount = validate_amount(amount)
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE expenses SET date=?, category=?, amount=?, notes=? WHERE id=?",
            (date, category.strip(), amount, notes.strip(), expense_id)
        )
        conn.commit()
        return cursor.rowcount > 0

def delete_expense(expense_id):
    """
    Delete an expense record by ID.
    Returns True if deletion was successful, False otherwise.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
        conn.commit()
        return cursor.rowcount > 0

def get_expenses_by_category(category):
    """
    Retrieve expenses filtered by category.
    Returns a list of dictionaries ordered by date descending.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM expenses WHERE category = ? ORDER BY date DESC, id DESC", (category,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def get_expenses_by_date_range(start_date, end_date):
    """
    Retrieve expenses within a date range (inclusive).
    Returns a list of dictionaries ordered by date descending.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM expenses WHERE date BETWEEN ? AND ? ORDER BY date DESC, id DESC", (start_date, end_date))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def get_monthly_summary():
    """
    Retrieve total expenses aggregated by month.
    Returns a list of dictionaries with 'month' and 'total' keys.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT strftime('%Y-%m', date) AS month, SUM(amount) AS total
            FROM expenses
            GROUP BY month
            ORDER BY month DESC
        """)
        rows = cursor.fetchall()
        return [{'month': row['month'], 'total': row['total']} for row in rows]

def get_all_expenses_for_export():
    """
    Retrieve all expenses for CSV export.
    Returns rows with date, category, amount, and notes.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT date, category, amount, notes FROM expenses ORDER BY date DESC, id DESC")
        rows = cursor.fetchall()
        return rows
