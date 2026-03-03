from fastapi import APIRouter
from fastapi.responses import HTMLResponse
import sqlite3

router = APIRouter()

def load_payments():
    conn = sqlite3.connect("db.sqlite")
    cur = conn.cursor()
    cur.execute(
        "SELECT user_id, transaction_id, status, amount, created_at "
        "FROM payments ORDER BY created_at DESC"
    )
    data = cur.fetchall()
    conn.close()
    return data

@router.get("/admin/payments", response_class=HTMLResponse)
def payments_panel():
    rows = load_payments()

    html_header = """
    <html>
    <head>
        <title>Panel płatności</title>
        <link rel="stylesheet"
            href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    </head>
    <body class="p-4">
        <h2 class="mb-4">Panel admina — BLIK Level 0</h2>
        <table class="table table-bordered table-striped">
            <thead>
                <tr>
                    <th>User ID</th>
                    <th>ID Transakcji</th>
                    <th>Status</th>
                    <th>Kwota</th>
                    <th>Data</th>
                </tr>
            </thead>
            <tbody>
    """

    html_rows = ""
    for r in rows:
        html_rows += f"""
            <tr>
                <td>{r[0]}</td>
                <td>{r[1]}</td>
                <td>{r[2]}</td>
                <td>{r[3]}</td>
                <td>{r[4]}</td>
            </tr>
        """

    html_footer = """
            </tbody>
        </table>
    </body>
    </html>
    """

    return HTMLResponse(content=html_header + html_rows + html_footer)
