import sqlite3
import datetime
import os

DB_NAME = "tk_tools.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS sku_mapping (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sku_id TEXT NOT NULL UNIQUE,
            product_name TEXT NOT NULL,
            created_at TEXT
        )
    ''')
    
    # Check if table is empty, if so, populate with defaults
    c.execute('SELECT count(*) FROM sku_mapping')
    if c.fetchone()[0] == 0:
        default_skus = [
            ("1732064124047627144", "BOSWELL 7.5QT White"),
            ("1732064124047561608", "BOSWELL 7.5QT Black"),
            ("1732144935945540488", "VEXON 4.5QT Green"),
            ("1732144935945409416", "VEXON 4.5QT Black"),
            ("1732144935945474952", "VEXON 4.5QT Pink")
        ]
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.executemany('INSERT INTO sku_mapping (sku_id, product_name, created_at) VALUES (?, ?, ?)', 
                      [(s[0], s[1], now) for s in default_skus])
        print("Initialized DB with default SKUs.")
    
    conn.commit()
    conn.close()

def get_all_skus():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM sku_mapping ORDER BY created_at DESC')
    rows = c.fetchall()
    conn.close()
    return rows

def get_sku_map_dict():
    """Returns a dictionary {sku_id: product_name}"""
    skus = get_all_skus()
    return {row['sku_id']: row['product_name'] for row in skus}

def add_sku(sku_id, product_name):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute('INSERT INTO sku_mapping (sku_id, product_name, created_at) VALUES (?, ?, ?)', 
                  (sku_id, product_name, now))
        conn.commit()
        conn.close()
        return True, "Success"
    except sqlite3.IntegrityError:
        return False, "SKU ID already exists."
    except Exception as e:
        return False, str(e)

def update_sku(original_sku_id, new_sku_id, new_product_name):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('UPDATE sku_mapping SET sku_id = ?, product_name = ? WHERE sku_id = ?', 
                  (new_sku_id, new_product_name, original_sku_id))
        conn.commit()
        conn.close()
        return True, "Success"
    except Exception as e:
        return False, str(e)

def delete_sku(sku_id):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('DELETE FROM sku_mapping WHERE sku_id = ?', (sku_id,))
        conn.commit()
        conn.close()
        return True, "Success"
    except Exception as e:
        return False, str(e)

# Initialize on module load if DB doesn't exist (optional, but good for first run)
if not os.path.exists(DB_NAME):
    init_db()
else:
    # Ensure table exists even if file exists
    init_db()
