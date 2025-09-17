import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from datetime import datetime
from gui_utils import create_labeled_entry, create_button_frame, create_card_frame
import logging

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

class SalesManager:
    def __init__(self, app, parent, db):
        self.app = app
        self.db = db
        self.sales_frame = ttk.Frame(parent, padding=10)
        self.create_sales_tab()

    def create_sales_tab(self):
        """Create the sales interface with modern styling"""
        # Header section
        header_frame = ttk.Frame(self.sales_frame)
        header_frame.pack(fill='x', pady=(0, 20))
        
        title = ttk.Label(header_frame, text="Point of Sale", 
                         font=("Helvetica", 24, "bold"), foreground="#007bff")
        title.pack(side='left')
        
        # Current time display
        time_label = ttk.Label(header_frame, text=datetime.now().strftime("%H:%M:%S"), 
                              font=("Helvetica", 14), foreground="#6c757d")
        time_label.pack(side='right')

        # Main container with two columns
        main_container = ttk.Frame(self.sales_frame)
        main_container.pack(fill='both', expand=True)
        main_container.columnconfigure(0, weight=1)
        main_container.columnconfigure(1, weight=1)

        # Left column - Sales form
        left_column = ttk.Frame(main_container)
        left_column.grid(row=0, column=0, padx=(0, 10), sticky="nsew")

        # Sales form card with enhanced styling
        form_card = create_card_frame(left_column, " New Sale")
        form_card.pack(fill='x', pady=(0, 20))

        # Product selection with modern styling
        self.product_var = tk.StringVar()
        product_frame = ttk.Frame(form_card)
        product_frame.pack(fill='x', pady=10)
        
        ttk.Label(product_frame, text="Select Product", 
                 font=("Helvetica", 12, "bold"), foreground="#495057").pack(anchor='w', pady=(0, 5))
        self.product_combo = ttk.Combobox(product_frame, textvariable=self.product_var, 
                                         font=("Helvetica", 11), height=10, state='readonly')
        self.product_combo.pack(fill='x', pady=(0, 10))
        self.product_combo.bind('<<ComboboxSelected>>', self.on_product_select)

        # Product info display cards
        info_container = ttk.Frame(form_card)
        info_container.pack(fill='x', pady=10)
        info_container.columnconfigure(0, weight=1)
        info_container.columnconfigure(1, weight=1)

        # Price card
        price_card = ttk.Frame(info_container, padding=10, relief="solid", borderwidth=1)
        price_card.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        ttk.Label(price_card, text="Unit Price", font=("Helvetica", 10), 
                 foreground="#6c757d").pack(anchor='w')
        self.price_var = tk.StringVar()
        self.price_label = ttk.Label(price_card, textvariable=self.price_var, 
                                    font=("Helvetica", 16, "bold"), foreground="#28a745")
        self.price_label.pack(anchor='w')

        # Stock card
        stock_card = ttk.Frame(info_container, padding=10, relief="solid", borderwidth=1)
        stock_card.grid(row=0, column=1, padx=(5, 0), sticky="ew")
        ttk.Label(stock_card, text="Available Stock", font=("Helvetica", 10), 
                 foreground="#6c757d").pack(anchor='w')
        self.stock_var = tk.StringVar()
        self.stock_label = ttk.Label(stock_card, textvariable=self.stock_var, 
                                    font=("Helvetica", 16, "bold"), foreground="#17a2b8")
        self.stock_label.pack(anchor='w')

        # Quantity input with modern styling
        quantity_frame = ttk.Frame(form_card)
        quantity_frame.pack(fill='x', pady=15)
        
        ttk.Label(quantity_frame, text="Quantity", 
                 font=("Helvetica", 12, "bold"), foreground="#495057").pack(anchor='w', pady=(0, 5))
        self.quantity_var = tk.StringVar()
        self.quantity_entry = ttk.Entry(quantity_frame, textvariable=self.quantity_var, 
                                       font=("Helvetica", 14), width=20)
        self.quantity_entry.pack(fill='x')
        self.quantity_entry.insert(0, "Enter quantity")
        self.quantity_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(self.quantity_entry, "Enter quantity"))
        self.quantity_entry.bind("<FocusOut>", lambda e: self.set_placeholder(self.quantity_entry, "Enter quantity"))
        self.quantity_var.trace('w', self.calculate_total)

        # Total display with prominent styling
        total_frame = ttk.Frame(form_card)
        total_frame.pack(fill='x', pady=15)
        
        total_card = ttk.Frame(total_frame, padding=15, relief="solid", borderwidth=2)
        total_card.pack(fill='x')
        
        ttk.Label(total_card, text="Total Amount", font=("Helvetica", 12), 
                 foreground="#6c757d").pack(anchor='w')
        self.total_var = tk.StringVar(value="GH₵ 0.00")
        total_label = ttk.Label(total_card, textvariable=self.total_var, 
                               font=("Helvetica", 24, "bold"), foreground="#dc3545")
        total_label.pack(anchor='w')

        # Action buttons with modern styling
        button_frame = ttk.Frame(form_card)
        button_frame.pack(fill='x', pady=20)
        
        make_sale_btn = ttk.Button(button_frame, text=" Complete Sale", 
                                  bootstyle="success", command=self.make_sale)
        make_sale_btn.pack(side='left', padx=(0, 10), fill='x', expand=True)
        
        clear_btn = ttk.Button(button_frame, text=" Clear Form", 
                              bootstyle="outline-secondary", command=self.clear_sale_form)
        clear_btn.pack(side='right', padx=(10, 0))

        # Right column - Recent sales
        right_column = ttk.Frame(main_container)
        right_column.grid(row=0, column=1, padx=(10, 0), sticky="nsew")

        # Recent sales card
        recent_card = create_card_frame(right_column, " Recent Sales")
        recent_card.pack(fill='both', expand=True)

        # Enhanced treeview with modern styling
        tree_frame = ttk.Frame(recent_card)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=10)

        columns = ('ID', 'Product', 'Qty', 'Total', 'Time')
        self.sales_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', 
                                      height=15, selectmode='extended')
        
        # Configure column headings and widths
        column_configs = {
            'ID': {'width': 50, 'anchor': 'center'},
            'Product': {'width': 150, 'anchor': 'w'},
            'Qty': {'width': 60, 'anchor': 'center'},
            'Total': {'width': 80, 'anchor': 'e'},
            'Time': {'width': 120, 'anchor': 'center'}
        }
        
        for col, config in column_configs.items():
            self.sales_tree.heading(col, text=col, anchor='center')
            self.sales_tree.column(col, width=config['width'], anchor=config['anchor'])

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.sales_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient='horizontal', command=self.sales_tree.xview)
        self.sales_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Grid layout for tree and scrollbars
        self.sales_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')

        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # Configure main container row weight
        main_container.rowconfigure(0, weight=1)

        # Initialize data
        self.refresh_product_list()
        self.refresh_recent_sales()
        logging.info("Modern sales tab UI initialized")

    def clear_placeholder(self, entry, placeholder, show=None):
        """Clear placeholder text when entry is focused"""
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            if show:
                entry.configure(show=show)
        logging.info(f"Cleared placeholder for {entry}")

    def set_placeholder(self, entry, placeholder, show=None):
        """Set placeholder text when entry loses focus"""
        if not entry.get():
            entry.insert(0, placeholder)
            if show:
                entry.configure(show="")
        logging.info(f"Set placeholder for {entry}")

    def refresh_product_list(self):
        """Refresh the product dropdown"""
        try:
            products = self.db.get_products()
            self.product_map = {f"{p[1]} (GH₵{p[2]:.2f}, Stock: {p[3]})": p[0] for p in products}
            product_names = list(self.product_map.keys())
            self.product_combo['values'] = product_names
            if product_names:
                self.product_var.set(product_names[0])
                self.on_product_select()
            logging.info("Sales product dropdown refreshed")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh product list: {str(e)}")
            logging.error(f"Error refreshing sales product dropdown: {str(e)}")

    def on_product_select(self, event=None):
        """Handle product selection"""
        if not self.product_var.get():
            return
        product_display = self.product_var.get()
        product_id = self.product_map.get(product_display)
        result = self.db.get_product_by_id(product_id)
        if result:
            price, stock = result
            self.price_var.set(f"{price:.2f}")
            self.stock_var.set(f"{stock}")
            self.quantity_entry.configure(validate="key", 
                                        validatecommand=(self.quantity_entry.register(self.validate_quantity), "%P", stock))
            self.calculate_total()
            logging.info(f"Selected product: {product_display}, ID: {product_id}")
        else:
            messagebox.showerror("Error", "Product not found")
            logging.error(f"Product not found for display: {product_display}")

    def validate_quantity(self, value, max_stock):
        """Validate quantity input"""
        if value == "" or value == "Enter quantity":
            return True
        try:
            qty = int(value)
            return qty > 0 and qty <= int(max_stock)
        except ValueError:
            return False

    def calculate_total(self, *args):
        """Calculate total price"""
        try:
            if self.quantity_var.get() == "Enter quantity":
                self.total_var.set("GH₵ 0.00")
                return
            quantity = float(self.quantity_var.get() or 0)
            price = float(self.price_var.get() or 0)
            self.total_var.set(f"GH₵ {quantity * price:.2f}")
        except ValueError:
            self.total_var.set("GH₵ 0.00")

    def make_sale(self):
        """Process a sale"""
        if not all([self.product_var.get(), self.quantity_var.get()]) or self.quantity_var.get() == "Enter quantity":
            messagebox.showerror("Error", "Please select product and enter a valid quantity")
            logging.warning("Sale attempt failed: Missing product or invalid quantity")
            return
        
        try:
            quantity = int(self.quantity_var.get())
            if quantity <= 0:
                messagebox.showerror("Error", "Quantity must be positive")
                logging.warning(f"Sale attempt failed: Invalid quantity {self.quantity_var.get()}")
                return
        except ValueError:
            messagebox.showerror("Error", "Invalid quantity")
            logging.warning(f"Sale attempt failed: Non-numeric quantity {self.quantity_var.get()}")
            return
        
        product_display = self.product_var.get()
        product_id = self.product_map.get(product_display)
        result = self.db.get_product_by_id(product_id)
        
        if not result:
            messagebox.showerror("Error", "Product not found")
            logging.error(f"Sale attempt failed: Product not found for display {product_display}")
            return
        
        unit_price, current_stock = result
        
        if quantity > current_stock:
            messagebox.showerror("Error", f"Insufficient stock. Available: {current_stock}")
            logging.warning(f"Sale attempt failed: Insufficient stock for {product_display}, requested: {quantity}, available: {current_stock}")
            return
        
        total_price = quantity * unit_price
        try:
            self.db.add_sale(product_id, quantity, total_price)
            logging.info(f"Sale completed: Product ID {product_id}, Quantity {quantity}, Total GH₵{total_price:.2f}, New stock {current_stock - quantity}")
            messagebox.showinfo("Success", f"Sale completed!\nTotal: GH₵{total_price:.2f}\nNew stock: {current_stock - quantity}")
            self.clear_sale_form()
            self.refresh_recent_sales()
            self.app.refresh_all_managers()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process sale: {str(e)}")
            logging.error(f"Sale processing error: {str(e)}")

    def clear_sale_form(self):
        """Clear the sales form"""
        self.product_var.set("")
        self.price_var.set("")
        self.stock_var.set("")
        self.quantity_var.set("")
        self.total_var.set("")
        self.quantity_entry.configure(validate="none")
        self.set_placeholder(self.quantity_entry, "Enter quantity")
        self.refresh_product_list()

    def refresh_recent_sales(self):
        """Refresh recent sales display"""
        try:
            for item in self.sales_tree.get_children():
                self.sales_tree.delete(item)
            
            for row in self.db.get_recent_sales():
                sale_id, product_name, quantity, total, date = row
                formatted_date = datetime.fromisoformat(date).strftime("%Y-%m-%d %H:%M:%S")
                self.sales_tree.insert("", "end", values=(
                    sale_id, product_name, quantity, f"GH₵{total:.2f}", formatted_date
                ))
            logging.info("Recent sales display refreshed")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh sales: {str(e)}")
            logging.error(f"Error refreshing recent sales: {str(e)}")