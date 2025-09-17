import sqlite3
from datetime import datetime
import bcrypt
import logging

# Configure logging
logging.basicConfig(filename='pos.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

class DatabaseHandler:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.init_database()
        logging.info(f"Database connected: {db_name}")

    def init_database(self):
        """Initialize SQLite database with required tables"""
        try:
            with self.conn:
                cursor = self.conn.cursor()
                
                # Products table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    category TEXT,
                    type TEXT,
                    unit_price REAL NOT NULL,
                    stock INTEGER NOT NULL DEFAULT 0
                )
                ''')
                
                # Sales table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS sales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER,
                    quantity INTEGER,
                    total_price REAL,
                    sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products(id)
                )
                ''')
                
                # Inventory logs table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS inventory_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER,
                    change_qty INTEGER,
                    note TEXT,
                    log_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products(id)
                )
                ''')
                
                # Users table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password_hash BLOB NOT NULL
                )
                ''')
                
                # Add sample data if tables are empty
                cursor.execute("SELECT COUNT(*) FROM products")
                if cursor.fetchone()[0] == 0:
                    sample_products = [
                        ("5 inch Solid Block", "Block", "5 inch Solid", 5.0, 0),
                        ("6 inch Solid Block", "Block", "6 inch Solid", 6.0, 0),
                        ("9 inch Solid Block", "Block", "9 inch Solid", 9.0, 0),
                        ("Dangote Cement", "Cement", "Dangote Cement", 90.0, 0),
                        ("Ghacem Cement", "Cement", "Ghacem Cement", 85.0, 0)
                    ]
                    cursor.executemany(
                        "INSERT INTO products (name, category, type, unit_price, stock) VALUES (?, ?, ?, ?, ?)",
                        sample_products
                    )
                    logging.info("Sample products added to database")
                
                # Add a default admin user if none exists
                cursor.execute("SELECT COUNT(*) FROM users")
                if cursor.fetchone()[0] == 0:
                    default_password = "admin123".encode('utf-8')
                    hashed_password = bcrypt.hashpw(default_password, bcrypt.gensalt())
                    cursor.execute(
                        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                        ("admin", hashed_password)
                    )
                    logging.info("Default admin user created: username=admin, password=admin123")
        except sqlite3.Error as e:
            logging.error(f"Error initializing database: {str(e)}")
            raise

    def get_user(self, username):
        """Retrieve user credentials by username for login.py"""
        try:
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute("SELECT username, password_hash FROM users WHERE username = ?", (username,))
                user = cursor.fetchone()
                logging.info(f"User lookup for {username}: {'Found' if user else 'Not found'}")
                return user  # Returns (username, password_hash) or None
        except sqlite3.Error as e:
            logging.error(f"Error retrieving user {username}: {str(e)}")
            raise

    def authenticate_user(self, username, password):
        """Authenticate a user"""
        try:
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
                result = cursor.fetchone()
                if result:
                    stored_hash = result[0]  # Already bytes
                    authenticated = bcrypt.checkpw(password.encode('utf-8'), stored_hash)
                    logging.info(f"Authentication attempt for {username}: {'Success' if authenticated else 'Failed'}")
                    return authenticated
                logging.info(f"Authentication failed for {username}: User not found")
                return False
        except sqlite3.Error as e:
            logging.error(f"Error authenticating user {username}: {str(e)}")
            raise

    def get_products(self):
        """Retrieve all products for dropdowns"""
        try:
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute("SELECT id, name, unit_price, stock FROM products ORDER BY name")
                products = cursor.fetchall()
                logging.info(f"Fetched {len(products)} products")
                return products
        except sqlite3.Error as e:
            logging.error(f"Error retrieving products: {str(e)}")
            raise

    def get_product_by_name(self, name):
        """Get product details by name"""
        try:
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute("SELECT id, unit_price, stock FROM products WHERE name = ?", (name,))
                result = cursor.fetchone()
                logging.info(f"Product lookup by name {name}: {'Found' if result else 'Not found'}")
                return result
        except sqlite3.Error as e:
            logging.error(f"Error retrieving product by name {name}: {str(e)}")
            raise

    def get_product_by_id(self, product_id):
        """Get product details by ID"""
        try:
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute("SELECT unit_price, stock FROM products WHERE id = ?", (product_id,))
                result = cursor.fetchone()
                logging.info(f"Product lookup ID {product_id}: {'Found' if result else 'Not found'}")
                return result
        except sqlite3.Error as e:
            logging.error(f"Error retrieving product ID {product_id}: {str(e)}")
            raise

    def add_sale(self, product_id, quantity, total_price):
        """Record a sale and update stock"""
        try:
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute(
                    "INSERT INTO sales (product_id, quantity, total_price) VALUES (?, ?, ?)",
                    (product_id, quantity, total_price)
                )
                cursor.execute(
                    "UPDATE products SET stock = stock - ? WHERE id = ?",
                    (quantity, product_id)
                )
                logging.info(f"Sale recorded for product_id {product_id}, quantity {quantity}, stock reduced")
        except sqlite3.Error as e:
            logging.error(f"Error in add_sale: {str(e)}")
            raise

    def get_recent_sales(self):
        """Get recent sales for display"""
        try:
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute("""
                    SELECT s.id, p.name, s.quantity, s.total_price, s.sale_date
                    FROM sales s
                    JOIN products p ON s.product_id = p.id
                    ORDER BY s.sale_date DESC
                    LIMIT 20
                """)
                sales = cursor.fetchall()
                logging.info(f"Fetched {len(sales)} recent sales")
                return sales
        except sqlite3.Error as e:
            logging.error(f"Error retrieving recent sales: {str(e)}")
            raise

    def add_product(self, name, category, ptype, unit_price):
        """Add a new product"""
        try:
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute(
                    "INSERT INTO products (name, category, type, unit_price, stock) VALUES (?, ?, ?, ?, 0)",
                    (name, category, ptype, unit_price)
                )
                logging.info(f"Product added: {name}")
        except sqlite3.Error as e:
            logging.error(f"Error adding product {name}: {str(e)}")
            raise

    def update_product(self, product_id, name, category, ptype, unit_price):
        """Update an existing product"""
        try:
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute(
                    "UPDATE products SET name=?, category=?, type=?, unit_price=? WHERE id=?",
                    (name, category, ptype, unit_price, product_id)
                )
                logging.info(f"Product updated: ID {product_id}")
        except sqlite3.Error as e:
            logging.error(f"Error updating product ID {product_id}: {str(e)}")
            raise

    def delete_product(self, product_id):
        """Delete a product"""
        try:
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute("DELETE FROM products WHERE id=?", (product_id,))
                logging.info(f"Product deleted: ID {product_id}")
        except sqlite3.Error as e:
            logging.error(f"Error deleting product ID {product_id}: {str(e)}")
            raise

    def get_all_products(self):
        """Get all products for display"""
        try:
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute("SELECT id, name, category, type, unit_price, stock FROM products ORDER BY name")
                products = cursor.fetchall()
                logging.info(f"Fetched {len(products)} products with full details")
                return products
        except sqlite3.Error as e:
            logging.error(f"Error retrieving all products: {str(e)}")
            raise

    def update_stock(self, product_id, qty_change, note):
        """Update stock and log the change"""
        try:
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute("UPDATE products SET stock = stock + ? WHERE id = ?", (qty_change, product_id))
                cursor.execute(
                    "INSERT INTO inventory_logs (product_id, change_qty, note) VALUES (?, ?, ?)",
                    (product_id, qty_change, note)
                )
                logging.info(f"Stock updated for product_id {product_id}, change {qty_change}")
        except sqlite3.Error as e:
            logging.error(f"Error updating stock for product_id {product_id}: {str(e)}")
            raise

    def get_inventory_logs(self):
        """Get recent inventory logs"""
        try:
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute("""
                    SELECT l.id, p.name, l.change_qty, l.note, l.log_date
                    FROM inventory_logs l
                    JOIN products p ON l.product_id = p.id
                    ORDER BY l.log_date DESC
                    LIMIT 50
                """)
                logs = cursor.fetchall()
                logging.info(f"Fetched {len(logs)} inventory logs")
                return logs
        except sqlite3.Error as e:
            logging.error(f"Error retrieving inventory logs: {str(e)}")
            raise

    def get_product_history(self, product_id):
        """Get full transaction history for a product"""
        try:
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute("""
                    SELECT 'Sale' as type, -s.quantity as change_qty, 
                           'Sale ID: ' || s.id || ', Total: GH₵' || s.total_price as note, 
                           s.sale_date as date
                    FROM sales s
                    WHERE s.product_id = ?
                    
                    UNION ALL
                    
                    SELECT 'Adjustment' as type, l.change_qty, l.note, l.log_date as date
                    FROM inventory_logs l
                    WHERE l.product_id = ?
                    
                    ORDER BY date DESC
                """, (product_id, product_id))
                history = cursor.fetchall()
                logging.info(f"Fetched {len(history)} transaction history records for product_id {product_id}")
                return history
        except sqlite3.Error as e:
            logging.error(f"Error retrieving product history for product_id {product_id}: {str(e)}")
            raise

    def get_current_stocks(self):
        """Get current stock levels for all products"""
        try:
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute("""
                    SELECT id, name, category, stock
                    FROM products
                    ORDER BY name
                """)
                stocks = cursor.fetchall()
                logging.info(f"Fetched {len(stocks)} stock records")
                return stocks
        except sqlite3.Error as e:
            logging.error(f"Error retrieving current stocks: {str(e)}")
            raise

    def get_daily_sales(self, date):
        """Get daily sales report"""
        try:
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute("""
                    SELECT p.name, SUM(s.quantity) as total_qty, SUM(s.total_price) as total_amount
                    FROM sales s
                    JOIN products p ON s.product_id = p.id
                    WHERE date(s.sale_date) = ?
                    GROUP BY p.name
                    ORDER BY total_amount DESC
                """, (date,))
                sales = cursor.fetchall()
                logging.info(f"Fetched {len(sales)} daily sales records for {date}")
                return sales
        except sqlite3.Error as e:
            logging.error(f"Error retrieving daily sales for {date}: {str(e)}")
            raise

    def get_monthly_sales(self, month):
        """Get monthly sales report"""
        try:
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute("""
                    SELECT p.name, p.category, SUM(s.quantity) as total_qty, SUM(s.total_price) as total_amount
                    FROM sales s
                    JOIN products p ON s.product_id = p.id
                    WHERE strftime('%Y-%m', s.sale_date) = ?
                    GROUP BY p.name, p.category
                    ORDER BY p.category, total_amount DESC
                """, (month,))
                sales = cursor.fetchall()
                logging.info(f"Fetched {len(sales)} monthly sales records for {month}")
                return sales
        except sqlite3.Error as e:
            logging.error(f"Error retrieving monthly sales for {month}: {str(e)}")
            raise

    def get_stock_report(self):
        """Get stock report"""
        try:
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute("""
                    SELECT name, category, type, unit_price, stock, (unit_price * stock) as stock_value
                    FROM products
                    ORDER BY category, name
                """)
                stocks = cursor.fetchall()
                logging.info(f"Fetched {len(stocks)} stock report records")
                return stocks
        except sqlite3.Error as e:
            logging.error(f"Error retrieving stock report: {str(e)}")
            raise

    def get_sales_for_export(self):
        """Get sales data for CSV export"""
        try:
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute("""
                    SELECT s.id, p.name, p.category, s.quantity, p.unit_price, s.total_price, s.sale_date
                    FROM sales s
                    JOIN products p ON s.product_id = p.id
                    ORDER BY s.sale_date DESC
                """)
                sales = cursor.fetchall()
                logging.info(f"Fetched {len(sales)} sales records for export")
                return sales
        except sqlite3.Error as e:
            logging.error(f"Error retrieving sales for export: {str(e)}")
            raise

    def get_yearly_product_sales(self, year):
        """Get yearly sales data by product"""
        try:
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute("""
                    SELECT p.name, SUM(s.quantity) as total_qty, SUM(s.total_price) as total_revenue
                    FROM sales s
                    JOIN products p ON s.product_id = p.id
                    WHERE strftime('%Y', s.sale_date) = ?
                    GROUP BY p.name
                    ORDER BY total_revenue DESC
                """, (str(year),))
                sales = cursor.fetchall()
                logging.info(f"Fetched {len(sales)} yearly product sales records for {year}")
                return sales
        except sqlite3.Error as e:
            logging.error(f"Error retrieving yearly product sales for {year}: {str(e)}")
            raise

    def get_yearly_sales(self, year):
        """Get yearly sales report with category breakdown"""
        try:
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute("""
                    SELECT p.name, p.category, SUM(s.quantity) as total_qty, SUM(s.total_price) as total_amount
                    FROM sales s
                    JOIN products p ON s.product_id = p.id
                    WHERE strftime('%Y', s.sale_date) = ?
                    GROUP BY p.name, p.category
                    ORDER BY p.category, total_amount DESC
                """, (str(year),))
                sales = cursor.fetchall()
                logging.info(f"Fetched {len(sales)} yearly sales records for {year}")
                return sales
        except sqlite3.Error as e:
            logging.error(f"Error retrieving yearly sales for {year}: {str(e)}")
            raise

    def __del__(self):
        """Clean up database connection"""
        try:
            self.conn.close()
            logging.info("Database connection closed")
        except Exception as e:
            logging.error(f"Error closing database connection: {str(e)}")