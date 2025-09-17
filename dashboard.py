import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from datetime import datetime, timedelta
import logging
from gui_utils import create_card_frame
import calendar

# Safe ToolTip import
try:
    from ttkbootstrap.tooltip import ToolTip
except ImportError:
    try:
        from ttkbootstrap import ToolTip
    except ImportError:
        class ToolTip:
            def __init__(self, widget, text="", bootstyle=None, **kwargs):
                pass

# Configure logging
logging.basicConfig(filename='pos.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

class DashboardManager:
    def __init__(self, app, parent, db):
        self.app = app
        self.db = db
        self.dashboard_frame = ttk.Frame(parent, padding=10)
        self.create_dashboard()

    def create_dashboard(self):
        """Create a professional dashboard with modern design"""
        # Header section
        header_frame = ttk.Frame(self.dashboard_frame)
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Welcome message and date
        welcome_label = ttk.Label(header_frame, text="Dashboard", 
                                 font=("Helvetica", 24, "bold"), bootstyle="primary")
        welcome_label.pack(side='left')
        
        date_label = ttk.Label(header_frame, text=datetime.now().strftime("%B %d, %Y"), 
                              font=("Helvetica", 14), bootstyle="secondary")
        date_label.pack(side='right')

        # Main content container with scrollable frame
        main_container = ttk.Frame(self.dashboard_frame)
        main_container.pack(fill='both', expand=True)

        # Create scrollable canvas
        canvas = tk.Canvas(main_container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Create dashboard sections
        self.create_metrics_overview()
        self.create_stock_overview()
        self.create_sales_analytics()
        self.create_recent_activity()

        # Refresh data
        self.refresh_dashboard()
        logging.info("Dashboard initialized")

    def create_metrics_overview(self):
        """Create key metrics overview cards"""
        metrics_frame = ttk.Frame(self.scrollable_frame)
        metrics_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(metrics_frame, text="Key Metrics", 
                 font=("Helvetica", 16, "bold"), bootstyle="info").pack(anchor='w', pady=(0, 10))

        # Metrics cards container
        cards_frame = ttk.Frame(metrics_frame)
        cards_frame.pack(fill='x')

        # Configure grid weights for responsive design (now 5 columns)
        for i in range(5):
            cards_frame.columnconfigure(i, weight=1)

        # Today's Sales Card
        self.today_sales_card = self.create_metric_card(cards_frame, "Today's Sales", "GH₵0.00", 
                                                       "success", 0, 0)
        
        # This Month's Sales Card
        self.month_sales_card = self.create_metric_card(cards_frame, "This Month", "GH₵0.00", 
                                                       "info", 0, 1)
        
        # This Year's Sales Card
        self.year_sales_card = self.create_metric_card(cards_frame, "This Year", "GH₵0.00", 
                                                      "primary", 0, 2)
        
        # Total Products Card
        self.total_products_card = self.create_metric_card(cards_frame, "Total Products", "0", 
                                                          "warning", 0, 3)
        
        # Low Stock Alert Card
        self.low_stock_card = self.create_metric_card(cards_frame, "Low Stock Items", "0", 
                                                     "danger", 0, 4)

    def create_metric_card(self, parent, title, value, style, row, col):
        """Create a modern metric card"""
        card = ttk.Frame(parent, bootstyle="light", padding=15, relief="raised", borderwidth=1)
        card.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
        
        # Title
        title_label = ttk.Label(card, text=title, font=("Helvetica", 11))
        title_label.pack(anchor='w')
        
        # Value with color based on style
        color_map = {
            "success": "#28a745",
            "info": "#17a2b8", 
            "primary": "#007bff",
            "warning": "#ffc107",
            "danger": "#dc3545"
        }
        value_label = ttk.Label(card, text=value, font=("Helvetica", 20, "bold"),
                               foreground=color_map.get(style, "#000000"))
        value_label.pack(anchor='w', pady=(5, 0))
        
        return {"card": card, "title": title_label, "value": value_label}

    def create_stock_overview(self):
        """Create stock overview section"""
        stock_frame = ttk.Frame(self.scrollable_frame)
        stock_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(stock_frame, text="Stock Overview", 
                 font=("Helvetica", 16, "bold"), bootstyle="info").pack(anchor='w', pady=(0, 10))

        # Stock cards container
        self.stock_cards_frame = ttk.Frame(stock_frame)
        self.stock_cards_frame.pack(fill='x')

    def create_sales_analytics(self):
        """Create sales analytics section"""
        analytics_frame = ttk.Frame(self.scrollable_frame)
        analytics_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(analytics_frame, text="Sales Analytics", 
                 font=("Helvetica", 16, "bold"), bootstyle="info").pack(anchor='w', pady=(0, 10))

        # Analytics container with two columns
        analytics_container = ttk.Frame(analytics_frame)
        analytics_container.pack(fill='x')
        analytics_container.columnconfigure(0, weight=1)
        analytics_container.columnconfigure(1, weight=1)

        # Daily Sales Chart
        daily_card = create_card_frame(analytics_container, "Daily Sales (Last 7 Days)")
        daily_card.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="ew")
        
        self.daily_sales_tree = ttk.Treeview(daily_card, columns=('Date', 'Sales'), 
                                           show='headings', height=6, bootstyle="info")
        self.daily_sales_tree.heading('Date', text='Date')
        self.daily_sales_tree.heading('Sales', text='Sales (GH₵)')
        self.daily_sales_tree.column('Date', width=120)
        self.daily_sales_tree.column('Sales', width=120)
        self.daily_sales_tree.pack(fill='x', padx=10, pady=10)

        # Monthly Sales Chart
        monthly_card = create_card_frame(analytics_container, "Monthly Sales (Last 6 Months)")
        monthly_card.grid(row=0, column=1, padx=(10, 0), pady=5, sticky="ew")
        
        self.monthly_sales_tree = ttk.Treeview(monthly_card, columns=('Month', 'Sales'), 
                                             show='headings', height=6, bootstyle="info")
        self.monthly_sales_tree.heading('Month', text='Month')
        self.monthly_sales_tree.heading('Sales', text='Sales (GH₵)')
        self.monthly_sales_tree.column('Month', width=120)
        self.monthly_sales_tree.column('Sales', width=120)
        self.monthly_sales_tree.pack(fill='x', padx=10, pady=10)

        # Yearly Product Sales
        yearly_card = create_card_frame(analytics_container, "Top Products This Year")
        yearly_card.grid(row=1, column=0, columnspan=2, pady=(10, 0), sticky="ew")
        
        self.yearly_sales_tree = ttk.Treeview(yearly_card, columns=('Product', 'Quantity', 'Revenue'), 
                                            show='headings', height=8, bootstyle="info")
        self.yearly_sales_tree.heading('Product', text='Product')
        self.yearly_sales_tree.heading('Quantity', text='Quantity Sold')
        self.yearly_sales_tree.heading('Revenue', text='Revenue (GH₵)')
        self.yearly_sales_tree.column('Product', width=200)
        self.yearly_sales_tree.column('Quantity', width=120)
        self.yearly_sales_tree.column('Revenue', width=120)
        self.yearly_sales_tree.pack(fill='x', padx=10, pady=10)

    def create_recent_activity(self):
        """Create recent activity section"""
        activity_frame = ttk.Frame(self.scrollable_frame)
        activity_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        ttk.Label(activity_frame, text="Recent Activity", 
                 font=("Helvetica", 16, "bold"), bootstyle="info").pack(anchor='w', pady=(0, 10))

        # Recent activity container
        activity_container = ttk.Frame(activity_frame)
        activity_container.pack(fill='both', expand=True)
        activity_container.columnconfigure(0, weight=1)
        activity_container.columnconfigure(1, weight=1)

        # Recent Sales
        sales_card = create_card_frame(activity_container, "Recent Sales")
        sales_card.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        
        self.recent_sales_tree = ttk.Treeview(sales_card, columns=('Product', 'Quantity', 'Total'), 
                                            show='headings', height=8, bootstyle="light")
        self.recent_sales_tree.heading('Product', text='Product')
        self.recent_sales_tree.heading('Quantity', text='Qty')
        self.recent_sales_tree.heading('Total', text='Total')
        self.recent_sales_tree.column('Product', width=150)
        self.recent_sales_tree.column('Quantity', width=60)
        self.recent_sales_tree.column('Total', width=80)
        self.recent_sales_tree.pack(fill='both', expand=True, padx=10, pady=10)

        # Recent Inventory Changes
        inventory_card = create_card_frame(activity_container, "Recent Inventory Changes")
        inventory_card.grid(row=0, column=1, padx=(10, 0), sticky="nsew")
        
        self.recent_inventory_tree = ttk.Treeview(inventory_card, columns=('Product', 'Change', 'Note'), 
                                                show='headings', height=8, bootstyle="light")
        self.recent_inventory_tree.heading('Product', text='Product')
        self.recent_inventory_tree.heading('Change', text='Change')
        self.recent_inventory_tree.heading('Note', text='Note')
        self.recent_inventory_tree.column('Product', width=120)
        self.recent_inventory_tree.column('Change', width=60)
        self.recent_inventory_tree.column('Note', width=100)
        self.recent_inventory_tree.pack(fill='both', expand=True, padx=10, pady=10)

        # Configure row weight for expansion
        activity_container.rowconfigure(0, weight=1)

    def refresh_dashboard(self):
        """Refresh all dashboard data"""
        try:
            self.refresh_metrics()
            self.refresh_stock_overview()
            self.refresh_sales_analytics()
            self.refresh_recent_activity()
            logging.info("Dashboard data refreshed")
        except Exception as e:
            logging.error(f"Error refreshing dashboard: {str(e)}")
            messagebox.showerror("Error", f"Failed to refresh dashboard: {str(e)}")

    def refresh_metrics(self):
        """Refresh key metrics cards"""
        try:
            # Today's sales
            today = datetime.now().strftime('%Y-%m-%d')
            today_sales = self.db.get_daily_sales(today)
            today_total = sum(row[2] for row in today_sales) if today_sales else 0
            self.today_sales_card["value"].configure(text=f"GH₵{today_total:.2f}")

            # This month's sales
            current_month = datetime.now().strftime('%Y-%m')
            month_sales = self.db.get_monthly_sales(current_month)
            month_total = sum(row[3] for row in month_sales) if month_sales else 0
            self.month_sales_card["value"].configure(text=f"GH₵{month_total:.2f}")

            # This year's sales
            current_year = datetime.now().year
            year_sales = self.db.get_yearly_product_sales(current_year)
            year_total = sum(row[2] for row in year_sales) if year_sales else 0
            self.year_sales_card["value"].configure(text=f"GH₵{year_total:.2f}")

            # Total products
            products = self.db.get_all_products()
            self.total_products_card["value"].configure(text=str(len(products)))

            # Low stock items
            low_stock_count = 0
            for product in products:
                _, _, category, _, _, stock = product
                if (category == 'Block' and stock < 10) or (category == 'Cement' and stock < 5):
                    low_stock_count += 1
            self.low_stock_card["value"].configure(text=str(low_stock_count))

        except Exception as e:
            logging.error(f"Error refreshing metrics: {str(e)}")

    def refresh_stock_overview(self):
        """Refresh stock overview cards"""
        try:
            # Clear existing stock cards
            for widget in self.stock_cards_frame.winfo_children():
                widget.destroy()

            # Get products grouped by category
            products = self.db.get_all_products()
            categories = {}
            
            for product in products:
                _, name, category, _, _, stock = product
                if category not in categories:
                    categories[category] = {"total_stock": 0, "products": []}
                categories[category]["total_stock"] += stock
                categories[category]["products"].append({"name": name, "stock": stock})

            # Create cards for each category
            col = 0
            for category, data in categories.items():
                self.create_stock_category_card(self.stock_cards_frame, category, 
                                              data["total_stock"], data["products"], col)
                col += 1

        except Exception as e:
            logging.error(f"Error refreshing stock overview: {str(e)}")

    def create_stock_category_card(self, parent, category, total_stock, products, col):
        """Create a stock category card"""
        card = ttk.Frame(parent, padding=15, relief="raised", borderwidth=1)
        card.grid(row=0, column=col, padx=10, pady=5, sticky="ew")
        parent.columnconfigure(col, weight=1)

        # Category title
        ttk.Label(card, text=category, font=("Helvetica", 14, "bold"), 
                 foreground="#007bff").pack(anchor='w')
        
        # Total stock
        ttk.Label(card, text=f"Total Stock: {total_stock}", font=("Helvetica", 12), 
                 foreground="#17a2b8").pack(anchor='w', pady=(5, 10))

        # Individual products
        for product in products[:5]:  # Show top 5 products
            product_frame = ttk.Frame(card)
            product_frame.pack(fill='x', pady=2)
            
            ttk.Label(product_frame, text=product["name"], font=("Helvetica", 10)).pack(side='left')
            
            # Color code stock levels
            stock = product["stock"]
            if (category == 'Block' and stock < 10) or (category == 'Cement' and stock < 5):
                color = "#dc3545"  # Red for danger
            elif stock < 20:
                color = "#ffc107"  # Yellow for warning
            else:
                color = "#28a745"  # Green for success
                
            ttk.Label(product_frame, text=str(stock), font=("Helvetica", 10, "bold"), 
                     foreground=color).pack(side='right')

    def refresh_sales_analytics(self):
        """Refresh sales analytics data"""
        try:
            # Daily sales (last 7 days)
            self.refresh_daily_sales()
            
            # Monthly sales (last 6 months)
            self.refresh_monthly_sales()
            
            # Yearly product sales
            self.refresh_yearly_sales()

        except Exception as e:
            logging.error(f"Error refreshing sales analytics: {str(e)}")

    def refresh_daily_sales(self):
        """Refresh daily sales data"""
        # Clear existing data
        for item in self.daily_sales_tree.get_children():
            self.daily_sales_tree.delete(item)

        # Get last 7 days of sales
        for i in range(6, -1, -1):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            sales_data = self.db.get_daily_sales(date)
            total = sum(row[2] for row in sales_data) if sales_data else 0
            
            display_date = (datetime.now() - timedelta(days=i)).strftime('%m/%d')
            self.daily_sales_tree.insert("", "end", values=(display_date, f"{total:.2f}"))

    def refresh_monthly_sales(self):
        """Refresh monthly sales data"""
        # Clear existing data
        for item in self.monthly_sales_tree.get_children():
            self.monthly_sales_tree.delete(item)

        # Get last 6 months of sales
        for i in range(5, -1, -1):
            date = datetime.now() - timedelta(days=i*30)
            month_str = date.strftime('%Y-%m')
            sales_data = self.db.get_monthly_sales(month_str)
            total = sum(row[3] for row in sales_data) if sales_data else 0
            
            display_month = date.strftime('%b %Y')
            self.monthly_sales_tree.insert("", "end", values=(display_month, f"{total:.2f}"))

    def refresh_yearly_sales(self):
        """Refresh yearly product sales data"""
        # Clear existing data
        for item in self.yearly_sales_tree.get_children():
            self.yearly_sales_tree.delete(item)

        # Get current year sales by product
        current_year = datetime.now().year
        yearly_sales = self.db.get_yearly_product_sales(current_year)
        
        for row in yearly_sales:
            product_name, total_qty, total_revenue = row
            self.yearly_sales_tree.insert("", "end", values=(
                product_name, total_qty, f"{total_revenue:.2f}"
            ))

    def refresh_recent_activity(self):
        """Refresh recent activity data"""
        try:
            # Recent sales
            for item in self.recent_sales_tree.get_children():
                self.recent_sales_tree.delete(item)
            
            recent_sales = self.db.get_recent_sales()
            for sale in recent_sales[:10]:  # Show last 10 sales
                _, product_name, quantity, total_price, _ = sale
                self.recent_sales_tree.insert("", "end", values=(
                    product_name, quantity, f"GH₵{total_price:.2f}"
                ))

            # Recent inventory changes
            for item in self.recent_inventory_tree.get_children():
                self.recent_inventory_tree.delete(item)
            
            recent_logs = self.db.get_inventory_logs()
            for log in recent_logs[:10]:  # Show last 10 changes
                _, product_name, change_qty, note, _ = log
                change_text = f"+{change_qty}" if change_qty > 0 else str(change_qty)
                self.recent_inventory_tree.insert("", "end", values=(
                    product_name, change_text, note or "N/A"
                ))

        except Exception as e:
            logging.error(f"Error refreshing recent activity: {str(e)}")
