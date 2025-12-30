"""Database viewer and query tool for SQLite database."""

import streamlit as st
import sqlite3
import pandas as pd
import sys
import os
from pathlib import Path

# Add project root to path (go up from src/ui/db_viewer.py to project root)
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.agent.database.setup import get_database_path

st.set_page_config(page_title="Database Viewer", page_icon="🗄️", layout="wide")

st.title("🗄️ Database Viewer")

# Get database path and resolve to absolute path
db_path_str = get_database_path()
# Resolve relative paths to absolute
if not os.path.isabs(db_path_str):
    # Get project root (go up from src/ui/db_viewer.py)
    project_root = Path(__file__).resolve().parent.parent.parent
    db_path = (project_root / db_path_str.lstrip("./")).resolve()
else:
    db_path = Path(db_path_str)

st.sidebar.info(f"Database: `{db_path}`")

# Connect to database
try:
    # Ensure database file exists
    if not db_path.exists():
        st.warning(f"Database file not found at: {db_path}")
        st.info("The database will be created when you first use the agent.")
        st.stop()

    # Convert Path to string for sqlite3
    conn = sqlite3.connect(str(db_path))
except Exception as e:
    st.error(f"Failed to connect to database: {e}")
    st.error(f"Path attempted: {db_path}")
    st.stop()

# Get table list
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [row[0] for row in cursor.fetchall()]

# Sidebar for table selection
st.sidebar.header("Tables")
selected_table = st.sidebar.selectbox("Select a table", tables)

if selected_table:
    # Display table data
    st.subheader(f"Table: `{selected_table}`")

    # Get table info
    cursor.execute(f"PRAGMA table_info({selected_table})")
    columns = cursor.fetchall()

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Columns", len(columns))

    # Get row count
    cursor.execute(f"SELECT COUNT(*) FROM {selected_table}")
    row_count = cursor.fetchone()[0]
    with col2:
        st.metric("Rows", row_count)

    # Display columns info
    with st.expander("📋 Column Information"):
        if columns:
            df_columns = pd.DataFrame(
                columns, columns=["CID", "Name", "Type", "Not Null", "Default", "PK"]
            )
            st.dataframe(df_columns, use_container_width=True)

    # Display data
    st.subheader("Data")
    query = f"SELECT * FROM {selected_table} LIMIT 100"
    df = pd.read_sql_query(query, conn)
    st.dataframe(df, use_container_width=True, height=400)

    # Download button
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download as CSV", data=csv, file_name=f"{selected_table}.csv", mime="text/csv"
    )

# Custom SQL query
st.divider()
st.subheader("🔍 Custom SQL Query")

query_text = st.text_area(
    "Enter SQL query", height=100, placeholder="SELECT * FROM customers LIMIT 10;"
)

if st.button("Execute Query"):
    if query_text.strip():
        try:
            result_df = pd.read_sql_query(query_text, conn)
            st.dataframe(result_df, use_container_width=True)
            st.success(f"Query executed successfully. Returned {len(result_df)} rows.")
        except Exception as e:
            st.error(f"Query error: {e}")
    else:
        st.warning("Please enter a SQL query.")

# Predefined queries
st.divider()
st.subheader("📊 Predefined Queries")

predefined_queries = {
    "All Customers": "SELECT * FROM customers ORDER BY created_at DESC LIMIT 20;",
    "All Orders": "SELECT o.*, c.name as customer_name, c.email FROM orders o JOIN customers c ON o.customer_id = c.id ORDER BY o.created_at DESC LIMIT 20;",
    "All Tickets": "SELECT t.*, c.name as customer_name, c.email FROM tickets t JOIN customers c ON t.customer_id = c.id ORDER BY t.created_at DESC LIMIT 20;",
    "Knowledge Base Articles": "SELECT * FROM knowledge_base ORDER BY created_at DESC;",
    "Orders by Status": "SELECT status, COUNT(*) as count FROM orders GROUP BY status;",
    "Tickets by Priority": "SELECT priority, COUNT(*) as count FROM tickets GROUP BY priority;",
    "Tickets by Status": "SELECT status, COUNT(*) as count FROM tickets GROUP BY status;",
    "Customer Order Summary": """
        SELECT 
            c.id,
            c.name,
            c.email,
            COUNT(o.id) as total_orders,
            SUM(o.total) as total_spent,
            COUNT(t.id) as total_tickets
        FROM customers c
        LEFT JOIN orders o ON c.id = o.customer_id
        LEFT JOIN tickets t ON c.id = t.customer_id
        GROUP BY c.id, c.name, c.email
        ORDER BY total_spent DESC
        LIMIT 20;
    """,
}

for query_name, query in predefined_queries.items():
    if st.button(f"Run: {query_name}", key=f"predef_{query_name}"):
        try:
            result_df = pd.read_sql_query(query, conn)
            st.dataframe(result_df, use_container_width=True)
            st.success(f"Query '{query_name}' executed. Returned {len(result_df)} rows.")
        except Exception as e:
            st.error(f"Query error: {e}")

conn.close()
