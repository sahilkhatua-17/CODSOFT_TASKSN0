import sqlite3
from pathlib import Path


class ContactDatabase:
    def __init__(self, database_file="contacts.db"):
        self.database_file = Path(__file__).with_name(database_file)
        self.create_table()

    def connect(self):
        connection = sqlite3.connect(self.database_file)
        connection.row_factory = sqlite3.Row
        return connection

    def create_table(self):
        with self.connect() as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS contacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    email TEXT DEFAULT '',
                    address TEXT DEFAULT ''
                )
            """)

    def add_contact(self, contact):
        with self.connect() as connection:
            connection.execute("""
                INSERT INTO contacts (name, phone, email, address)
                VALUES (?, ?, ?, ?)
            """, (contact["name"], contact["phone"],
                  contact["email"], contact["address"]))

    def get_contact(self, contact_id):
        with self.connect() as connection:
            row = connection.execute(
                "SELECT * FROM contacts WHERE id = ?", (contact_id,)
            ).fetchone()
            return dict(row) if row else None

    def search_contacts(self, query="", search_by="All Fields"):
        with self.connect() as connection:
            if not query:
                rows = connection.execute(
                    "SELECT * FROM contacts ORDER BY name COLLATE NOCASE"
                ).fetchall()
                return [dict(row) for row in rows]

            pattern = f"%{query}%"
            columns = {
                "name": "name",
                "phone": "phone",
                "phone number": "phone",
                "email": "email",
                "email address": "email",
                "address": "address",
            }

            column = columns.get(search_by.strip().lower())
            if column:
                query_sql = f"SELECT * FROM contacts WHERE {column} LIKE ? ORDER BY name COLLATE NOCASE"
                rows = connection.execute(query_sql, (pattern,)).fetchall()
            else:
                # Default / "All Fields": search across all columns
                rows = connection.execute("""
                    SELECT * FROM contacts
                    WHERE name LIKE ? OR phone LIKE ? OR email LIKE ? OR address LIKE ?
                    ORDER BY name COLLATE NOCASE
                """, (pattern, pattern, pattern, pattern)).fetchall()

            return [dict(row) for row in rows]

    def update_contact(self, contact_id, contact):
        with self.connect() as connection:
            connection.execute("""
                UPDATE contacts
                SET name = ?, phone = ?, email = ?, address = ?
                WHERE id = ?
            """, (contact["name"], contact["phone"], contact["email"],
                  contact["address"], contact_id))

    def delete_contact(self, contact_id):
        with self.connect() as connection:
            connection.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
