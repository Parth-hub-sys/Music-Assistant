import json
from sqlalchemy import text
from langchain_core.tools import tool
from retrieval.db_engine import engine

def safe_tool_result(result):
    """Ensures tool result is a non-empty JSON string for Groq compatibility."""
    res_str = json.dumps(result, default=str)
    return res_str if res_str and res_str != "[]" else "[]"

@tool
def get_invoices_by_customer_sorted_by_date(customer_id: int) -> str:
    """Retrieves all invoices for a customer, sorted by date (newest first)."""
    query = text("SELECT invoice_id, invoice_date, total FROM invoice WHERE customer_id = :cid ORDER BY invoice_date DESC LIMIT 100")
    with engine.connect() as connection:
        result = connection.execute(query, {"cid": customer_id})
        return safe_tool_result([{"InvoiceId": row[0], "InvoiceDate": row[1], "Total": row[2]} for row in result.fetchall()])

@tool
def get_invoices_sorted_by_unit_price(customer_id: int) -> str:
    """Retrieves all invoices for a customer, with line items sorted by unit price."""
    query = text("""
        SELECT i.invoice_id, i.invoice_date, il.track_id, t.name, il.unit_price 
        FROM invoice i 
        JOIN invoice_line il ON i.invoice_id = il.invoice_id 
        JOIN track t ON il.track_id = t.track_id
        WHERE i.customer_id = :cid 
        ORDER BY il.unit_price DESC
        LIMIT 100
    """)
    with engine.connect() as connection:
        result = connection.execute(query, {"cid": customer_id})
        return safe_tool_result([{"InvoiceId": row[0], "InvoiceDate": row[1], "TrackName": row[3], "UnitPrice": row[4]} for row in result.fetchall()])

@tool
def get_employee_by_invoice_and_customer(invoice_id: int, customer_id: int) -> str:
    """Retrieves the support representative (employee) for a specific customer and invoice."""
    query = text("""
        SELECT e.first_name, e.last_name, e.title
        FROM employee e
        JOIN customer c ON e.employee_id = c.support_rep_id
        JOIN invoice i ON c.customer_id = i.customer_id
        WHERE i.invoice_id = :iid AND i.customer_id = :cid
    """)
    with engine.connect() as connection:
        result = connection.execute(query, {"iid": invoice_id, "cid": customer_id})
        return safe_tool_result([{"FirstName": row[0], "LastName": row[1], "Title": row[2]} for row in result.fetchall()])

@tool
def get_support_rep_by_customer(customer_id: int) -> str:
    """Retrieves the assigned support representative for a customer directly by customer ID."""
    query = text("""
        SELECT e.first_name, e.last_name, e.title, e.email
        FROM employee e
        JOIN customer c ON e.employee_id = c.support_rep_id
        WHERE c.customer_id = :cid
    """)
    with engine.connect() as connection:
        result = connection.execute(query, {"cid": customer_id})
        row = result.fetchone()
        if not row:
            return safe_tool_result([])
        return safe_tool_result([{"FirstName": row[0], "LastName": row[1], "Title": row[2], "Email": row[3]}])

invoice_tools = [
    get_invoices_by_customer_sorted_by_date,
    get_invoices_sorted_by_unit_price,
    get_employee_by_invoice_and_customer,
    get_support_rep_by_customer,
]
