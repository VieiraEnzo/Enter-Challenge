import sqlite3
import os
from typing import Optional

# Use absolute path to avoid issues with different working directories (Docker, Flask, CLI)
DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "template_cache.db")

# Ensure the directory exists
os.makedirs(DB_DIR, exist_ok=True)

def init_db():
    """Initialize the database and create tables if they don't exist."""
    # check_same_thread=False allows SQLite to be used from different threads
    with sqlite3.connect(DB_PATH, check_same_thread=False) as conn:
        cursor = conn.cursor()
        # Table for current regex rules
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS regex_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                label TEXT NOT NULL,
                field_name TEXT NOT NULL,
                rule_name TEXT NOT NULL,
                UNIQUE(label, field_name)
            )
        """)
        # Table for tracking rule conflicts
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS regex_conflicts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                label TEXT NOT NULL,
                field_name TEXT NOT NULL,
                UNIQUE(label, field_name)
            )
        """)
        conn.commit()

def save_regex_rule(conn, label: str, field_name: str, rule_name: str) -> None:
    """
    Save or update a regex rule for a field in a specific document type.
    If a different rule already exists, mark the field as conflicting.
    
    Args:
        conn: Database connection object
        label (str): Document type identifier
        field_name (str): Name of the field
        rule_name (str): Name of the regex rule (e.g., "CPF", "DATA_BR")
    """
    # First check if this field is already marked as conflicting
    if is_field_conflicting(conn, label, field_name):
        return
        
    cursor = conn.cursor()
    # Check if a different rule already exists
    cursor.execute("""
        SELECT rule_name FROM regex_rules
        WHERE label = ? AND field_name = ?
    """, (label, field_name))
    result = cursor.fetchone()
    
    if result:
        existing_rule = result[0]
        if existing_rule != rule_name:
            # Different rule found - mark as conflicting
            print(f"[DB] Found conflicting rules for field '{field_name}' in label '{label}': {existing_rule} vs {rule_name}")
            mark_field_as_conflicting(conn, label, field_name)
            return
    
    # No conflict - save the rule
    cursor.execute("""
        INSERT OR REPLACE INTO regex_rules (label, field_name, rule_name)
        VALUES (?, ?, ?)
    """, (label, field_name, rule_name))
    conn.commit()
    print(f"[DB] Saved rule '{rule_name}' for field '{field_name}' in label '{label}'")

def get_regex_rule(conn, label: str, field_name: str) -> Optional[str]:
    """
    Retrieve the regex rule for a field in a specific document type.
    
    Args:
        conn: Database connection object
        label (str): Document type identifier
        field_name (str): Name of the field
        
    Returns:
        Optional[str]: Name of the regex rule or None if not found
    """
    cursor = conn.cursor()
    cursor.execute("""
        SELECT rule_name FROM regex_rules
        WHERE label = ? AND field_name = ?
    """, (label, field_name))
    result = cursor.fetchone()
    if result:
        rule_name = result[0]
        print(f"[DB] Retrieved rule '{rule_name}' for field '{field_name}' in label '{label}'")
        return rule_name
    return None

def mark_field_as_conflicting(conn, label: str, field_name: str) -> None:
    """
    Mark a field as having conflicting regex rules across documents.
    
    Args:
        conn: Database connection object
        label (str): Document type identifier
        field_name (str): Name of the field
    """
    cursor = conn.cursor()
    # Delete any existing regex rule for this field
    cursor.execute("""
        DELETE FROM regex_rules
        WHERE label = ? AND field_name = ?
    """, (label, field_name))
    
    # Mark field as conflicting
    cursor.execute("""
        INSERT OR REPLACE INTO regex_conflicts (label, field_name)
        VALUES (?, ?)
    """, (label, field_name))
    conn.commit()
    print(f"[DB] Marked field '{field_name}' in label '{label}' as having conflicting patterns")

def is_field_conflicting(conn, label: str, field_name: str) -> bool:
    """
    Check if a field has been marked as having conflicting regex patterns.
    
    Args:
        conn: Database connection object
        label (str): Document type identifier
        field_name (str): Name of the field
        
    Returns:
        bool: True if the field has conflicting patterns, False otherwise
    """
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 1 FROM regex_conflicts
        WHERE label = ? AND field_name = ?
    """, (label, field_name))
    return cursor.fetchone() is not None

# Don't initialize at import time - let process_dataset handle it
# This avoids race conditions when multiple threads/processes start up
