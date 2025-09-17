import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from datetime import datetime
from gui_utils import create_labeled_entry, create_button_frame, create_card_frame
import logging

# Configure logging
logging.basicConfig(filename='pos.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
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
class InventoryManager:
    def __init__(self, app, parent, db):
        self.app = app
        self.db = db
        self.inventory_frame = ttk.Frame(parent, padding=10)
        self.create_inventory_tab()

    def create_inventory_tab(self):
        """Create the inventory management interface with modern styling"""
        # Header section
        header_frame = ttk.Frame(self.inventory_frame)
        header_frame.pack(fill='x', pady=(0, 20))
        
        title = ttk.Label(header_frame, text="Inventory Management", 
                         font=("Helvetica", 24, "bold"), foreground="#007bff")
        title.pack(side='left')
        
        # Quick stats in header
        stats_frame = ttk.Frame(header_frame)
        stats_frame.pack(side='right')
        
        # Get quick stats
        try:
            total_products = len(self.db.get_products())
            low_stock_count = len([p for p in self.db.get_products() if p[3] < 10])
            
            stats_text = f"Total Products: {total_products} | Low Stock Alerts: {low_stock_count}"
            stats_label = ttk.Label(stats_frame, text=stats_text, 
                                   font=("Helvetica", 12), foreground="#6c757d")
            stats_label.pack()
        except:
            pass

        # Main container with two columns
        main_container = ttk.Frame(self.inventory_frame)
        main_container.pack(fill='both', expand=True)
        main_container.columnconfigure(0, weight=1)
        main_container.columnconfigure(1, weight=2)

        # Left column - Stock adjustment
        left_column = ttk.Frame(main_container)
        left_column.grid(row=0, column=0, padx=(0, 15), sticky="nsew")

        # Stock adjustment card with enhanced styling
        adjust_card = create_card_frame(left_column, "📦 Stock Adjustment")
        adjust_card.pack(fill='x', pady=(0, 20))

        # Product selection with modern styling
        self.inv_product_var = tk.StringVar()
        product_frame = ttk.Frame(adjust_card)
        product_frame.pack(fill='x', pady=15)
        
        ttk.Label(product_frame, text="Select Product", 
                 font=("Helvetica", 12, "bold"), foreground="#495057").pack(anchor='w', pady=(0, 5))
        self.inv_product_combo = ttk.Combobox(product_frame, textvariable=self.inv_product_var, 
                                             font=("Helvetica", 11), height=10, state='readonly')
        self.inv_product_combo.pack(fill='x', pady=(0, 10))
        self.inv_product_combo.bind('<<ComboboxSelected>>', self.on_product_select)

        # Current stock display
        current_stock_frame = ttk.Frame(adjust_card)
        current_stock_frame.pack(fill='x', pady=10)
        
        stock_display_card = ttk.Frame(current_stock_frame, padding=10, relief="solid", borderwidth=1)
        stock_display_card.pack(fill='x')
        
        ttk.Label(stock_display_card, text="Current Stock", font=("Helvetica", 10), 
                 foreground="#6c757d").pack(anchor='w')
        self.current_stock_var = tk.StringVar(value="Select a product")
        current_stock_label = ttk.Label(stock_display_card, textvariable=self.current_stock_var, 
                                       font=("Helvetica", 18, "bold"), foreground="#17a2b8")
        current_stock_label.pack(anchor='w')

        # Quantity change input
        qty_frame = ttk.Frame(adjust_card)
        qty_frame.pack(fill='x', pady=15)
        
        ttk.Label(qty_frame, text="Quantity Change", 
                 font=("Helvetica", 12, "bold"), foreground="#495057").pack(anchor='w', pady=(0, 5))
        
        qty_input_frame = ttk.Frame(qty_frame)
        qty_input_frame.pack(fill='x')
        
        self.inv_qty_var = tk.StringVar()
        self.inv_qty_entry = ttk.Entry(qty_input_frame, textvariable=self.inv_qty_var, 
                                      font=("Helvetica", 14), width=15)
        self.inv_qty_entry.pack(side='left', padx=(0, 10))
        self.inv_qty_entry.insert(0, "Enter quantity")
        self.inv_qty_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(self.inv_qty_entry, "Enter quantity"))
        self.inv_qty_entry.bind("<FocusOut>", lambda e: self.set_placeholder(self.inv_qty_entry, "Enter quantity"))
        
        # Quick adjustment buttons
        ttk.Button(qty_input_frame, text="+10", bootstyle="outline-success", 
                  command=lambda: self.quick_adjust(10)).pack(side='left', padx=2)
        ttk.Button(qty_input_frame, text="+5", bootstyle="outline-success", 
                  command=lambda: self.quick_adjust(5)).pack(side='left', padx=2)
        ttk.Button(qty_input_frame, text="-5", bootstyle="outline-danger", 
                  command=lambda: self.quick_adjust(-5)).pack(side='left', padx=2)
        ttk.Button(qty_input_frame, text="-10", bootstyle="outline-danger", 
                  command=lambda: self.quick_adjust(-10)).pack(side='left', padx=2)

        # Note input
        note_frame = ttk.Frame(adjust_card)
        note_frame.pack(fill='x', pady=15)
        
        ttk.Label(note_frame, text="Adjustment Note", 
                 font=("Helvetica", 12, "bold"), foreground="#495057").pack(anchor='w', pady=(0, 5))
        self.inv_note_var = tk.StringVar()
        self.inv_note_entry = ttk.Entry(note_frame, textvariable=self.inv_note_var, 
                                       font=("Helvetica", 11))
        self.inv_note_entry.pack(fill='x')
        self.inv_note_entry.insert(0, "Enter note (optional)")
        self.inv_note_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(self.inv_note_entry, "Enter note (optional)"))
        self.inv_note_entry.bind("<FocusOut>", lambda e: self.set_placeholder(self.inv_note_entry, "Enter note (optional)"))

        # Action buttons
        button_frame = ttk.Frame(adjust_card)
        button_frame.pack(fill='x', pady=20)
        
        update_btn = ttk.Button(button_frame, text="📝 Update Stock", 
                               bootstyle="success", command=self.update_stock)
        update_btn.pack(fill='x', pady=(0, 10))
        
        clear_btn = ttk.Button(button_frame, text="🗑️ Clear Form", 
                              bootstyle="outline-secondary", command=self.clear_form)
        clear_btn.pack(fill='x')

        # Right column - Stock overview
        right_column = ttk.Frame(main_container)
        right_column.grid(row=0, column=1, padx=(15, 0), sticky="nsew")

        # Stock levels card
        stock_card = create_card_frame(right_column, "📊 Current Stock Levels")
        stock_card.pack(fill='both', expand=True)

        # Filter and search frame
        filter_frame = ttk.Frame(stock_card)
        filter_frame.pack(fill='x', padx=10, pady=(10, 5))
        
        ttk.Label(filter_frame, text="Filter:", font=("Helvetica", 10)).pack(side='left', padx=(0, 5))
        
        self.filter_var = tk.StringVar()
        filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_var, 
                                   values=["All", "Low Stock (<10)", "Out of Stock", "Normal Stock"], 
                                   state='readonly', width=15)
        filter_combo.pack(side='left', padx=(0, 10))
        filter_combo.set("All")
        filter_combo.bind('<<ComboboxSelected>>', self.filter_stock_display)
        
        # Search entry
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_var, 
                                font=("Helvetica", 10), width=20)
        search_entry.pack(side='left', padx=(0, 5))
        search_entry.insert(0, "Search products...")
        search_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(search_entry, "Search products..."))
        search_entry.bind("<FocusOut>", lambda e: self.set_placeholder(search_entry, "Search products..."))
        search_entry.bind("<KeyRelease>", self.search_products)

        # Enhanced treeview with modern styling
        tree_frame = ttk.Frame(stock_card)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=10)

        columns = ('ID', 'Product', 'Category', 'Stock', 'Status')
        self.stock_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', 
                                      height=20, selectmode='extended')
        
        # Configure column headings and widths
        column_configs = {
            'ID': {'width': 50, 'anchor': 'center'},
            'Product': {'width': 200, 'anchor': 'w'},
            'Category': {'width': 120, 'anchor': 'center'},
            'Stock': {'width': 80, 'anchor': 'center'},
            'Status': {'width': 100, 'anchor': 'center'}
        }
        
        for col, config in column_configs.items():
            self.stock_tree.heading(col, text=col, anchor='center')
            self.stock_tree.column(col, width=config['width'], anchor=config['anchor'])

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.stock_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient='horizontal', command=self.stock_tree.xview)
        self.stock_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Grid layout for tree and scrollbars
        self.stock_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')

        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # Configure main container row weight
        main_container.rowconfigure(0, weight=1)

        # Initialize data
        self.refresh_current_stocks()
        self.refresh_product_list()
        logging.info("Modern inventory tab UI initialized")

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

    def on_product_select(self, event=None):
        """Handle product selection and update current stock display"""
        if not self.inv_product_var.get():
            return
        
        product_display = self.inv_product_var.get()
        product_id = self.product_map.get(product_display)
        if product_id:
            result = self.db.get_product_by_id(product_id)
            if result:
                price, stock = result
                self.current_stock_var.set(f"{stock} units")
                logging.info(f"Selected product: {product_display}, Current stock: {stock}")

    def quick_adjust(self, amount):
        """Quick adjustment buttons"""
        self.inv_qty_var.set(str(amount))
        if self.inv_qty_entry.get() == "Enter quantity":
            self.inv_qty_entry.delete(0, tk.END)
            self.inv_qty_entry.insert(0, str(amount))

    def clear_form(self):
        """Clear the adjustment form"""
        self.inv_product_var.set("")
        self.inv_qty_var.set("")
        self.inv_note_var.set("")
        self.current_stock_var.set("Select a product")
        self.set_placeholder(self.inv_qty_entry, "Enter quantity")
        self.set_placeholder(self.inv_note_entry, "Enter note (optional)")

    def filter_stock_display(self, event=None):
        """Filter stock display based on selection"""
        self.refresh_current_stocks()

    def search_products(self, event=None):
        """Search products in real-time"""
        self.refresh_current_stocks()

    def refresh_product_list(self):
        """Refresh the product dropdown"""
        try:
            products = self.db.get_products()
            self.product_map = {f"{p[1]} (Stock: {p[3]})": p[0] for p in products}
            product_names = list(self.product_map.keys())
            self.inv_product_combo['values'] = product_names
            logging.info("Inventory product dropdown refreshed")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh product list: {str(e)}")
            logging.error(f"Error refreshing inventory product dropdown: {str(e)}")

    def update_stock(self):
        """Update product stock"""
        if not all([self.inv_product_var.get(), self.inv_qty_var.get()]):
            messagebox.showerror("Error", "Please select product and enter quantity change")
            logging.warning("Stock update failed: Missing product or quantity")
            return

        if self.inv_qty_var.get() == "Enter quantity":
            messagebox.showerror("Error", "Please enter a valid quantity")
            logging.warning("Stock update failed: Placeholder quantity detected")
            return
        
        try:
            qty_change = int(self.inv_qty_var.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid quantity")
            logging.warning(f"Stock update failed: Non-numeric quantity {self.inv_qty_var.get()}")
            return
        
        product_display = self.inv_product_var.get()
        product_id = self.product_map.get(product_display)
        result = self.db.get_product_by_id(product_id)
        
        if not result:
            messagebox.showerror("Error", "Product not found")
            logging.error(f"Stock update failed: Product not found for display {product_display}")
            return
        
        current_stock = result[1]
        new_stock = current_stock + qty_change
        
        if new_stock < 0:
            messagebox.showerror("Error", "Insufficient stock for this adjustment")
            logging.warning(f"Stock update failed: Insufficient stock for {product_display}, requested: {qty_change}, available: {current_stock}")
            return
        
        try:
            self.db.update_stock(product_id, qty_change, self.inv_note_var.get() if self.inv_note_var.get() != "Enter note (optional)" else "")
            messagebox.showinfo("Success", f"Stock updated. New stock: {new_stock}")
            logging.info(f"Stock updated: Product ID {product_id}, Change {qty_change}, New stock {new_stock}")
            self.inv_qty_var.set("")
            self.inv_note_var.set("")
            self.set_placeholder(self.inv_qty_entry, "Enter quantity")
            self.set_placeholder(self.inv_note_entry, "Enter note (optional)")
            self.refresh_current_stocks()
            self.refresh_product_list()
            if hasattr(self.app, 'products_manager'):
                self.app.products_manager.refresh_products_display()
            if hasattr(self.app, 'inventory_details_manager'):
                self.app.inventory_details_manager.refresh_history()
            if hasattr(self.app, 'reports_manager'):
                self.app.reports_manager.refresh_reports()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update stock: {str(e)}")
            logging.error(f"Stock update error: {str(e)}")

    def refresh_current_stocks(self):
        """Refresh current stock display with filtering and search"""
        try:
            for item in self.stock_tree.get_children():
                self.stock_tree.delete(item)
            
            # Get filter and search criteria
            filter_type = getattr(self, 'filter_var', tk.StringVar()).get() or "All"
            search_term = getattr(self, 'search_var', tk.StringVar()).get() or ""
            if search_term == "Search products...":
                search_term = ""
            
            for row in self.db.get_current_stocks():
                product_id, name, category, stock = row
                
                # Apply search filter
                if search_term and search_term.lower() not in name.lower():
                    continue
                
                # Determine status and apply filter
                if stock == 0:
                    status = "Out of Stock"
                    status_color = "danger"
                elif stock < 10:
                    status = "Low Stock"
                    status_color = "warning"
                else:
                    status = "Normal"
                    status_color = "success"
                
                # Apply status filter
                if filter_type == "Low Stock (<10)" and stock >= 10:
                    continue
                elif filter_type == "Out of Stock" and stock > 0:
                    continue
                elif filter_type == "Normal Stock" and stock < 10:
                    continue
                
                # Insert item with color coding
                item_id = self.stock_tree.insert("", "end", values=(
                    product_id, name, category, stock, status
                ))
                
                # Apply color coding based on stock level
                if stock == 0:
                    self.stock_tree.set(item_id, "Status", "🔴 Out of Stock")
                elif stock < 10:
                    self.stock_tree.set(item_id, "Status", "🟡 Low Stock")
                else:
                    self.stock_tree.set(item_id, "Status", "🟢 Normal")
                    
            logging.info("Current stocks display refreshed with filters")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh stocks: {str(e)}")
            logging.error(f"Error refreshing current stocks: {str(e)}")