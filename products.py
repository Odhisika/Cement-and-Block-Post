import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
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

class ProductsManager:
    def __init__(self, app, parent, db):
        self.app = app
        self.db = db
        self.products_frame = ttk.Frame(parent, padding=10)
        self.selected_product_id = None
        self.create_products_tab()

    def create_products_tab(self):
        """Create the products management interface with modern styling"""
        # Header section
        header_frame = ttk.Frame(self.products_frame)
        header_frame.pack(fill='x', pady=(0, 20))
        
        title = ttk.Label(header_frame, text="Product Management", 
                         font=("Helvetica", 24, "bold"), foreground="#007bff")
        title.pack(side='left')
        
        # Quick stats in header
        stats_frame = ttk.Frame(header_frame)
        stats_frame.pack(side='right')
        
        try:
            total_products = len(self.db.get_all_products())
            total_value = sum(p[4] * p[5] for p in self.db.get_all_products())  # price * stock
            
            stats_text = f"Total Products: {total_products} | Inventory Value: GH₵{total_value:.2f}"
            stats_label = ttk.Label(stats_frame, text=stats_text, 
                                   font=("Helvetica", 12), foreground="#6c757d")
            stats_label.pack()
        except:
            pass

        # Main container with two columns
        main_container = ttk.Frame(self.products_frame)
        main_container.pack(fill='both', expand=True)
        main_container.columnconfigure(0, weight=1)
        main_container.columnconfigure(1, weight=2)

        # Left column - Product form
        left_column = ttk.Frame(main_container)
        left_column.grid(row=0, column=0, padx=(0, 15), sticky="nsew")

        # Product form card with enhanced styling
        form_card = create_card_frame(left_column, "🏷️ Product Form")
        form_card.pack(fill='x', pady=(0, 20))

        # Product name input
        name_frame = ttk.Frame(form_card)
        name_frame.pack(fill='x', pady=15)
        
        ttk.Label(name_frame, text="Product Name", 
                 font=("Helvetica", 12, "bold"), foreground="#495057").pack(anchor='w', pady=(0, 5))
        self.prod_name_var = tk.StringVar()
        self.prod_name_entry = ttk.Entry(name_frame, textvariable=self.prod_name_var, 
                                        font=("Helvetica", 11))
        self.prod_name_entry.pack(fill='x')
        self.prod_name_entry.insert(0, "Enter product name")
        self.prod_name_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(self.prod_name_entry, "Enter product name"))
        self.prod_name_entry.bind("<FocusOut>", lambda e: self.set_placeholder(self.prod_name_entry, "Enter product name"))

        # Category and Type in a row
        cat_type_frame = ttk.Frame(form_card)
        cat_type_frame.pack(fill='x', pady=15)
        cat_type_frame.columnconfigure(0, weight=1)
        cat_type_frame.columnconfigure(1, weight=1)

        # Category
        category_frame = ttk.Frame(cat_type_frame)
        category_frame.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        
        ttk.Label(category_frame, text="Category", 
                 font=("Helvetica", 12, "bold"), foreground="#495057").pack(anchor='w', pady=(0, 5))
        self.prod_category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(category_frame, textvariable=self.prod_category_var, 
                                          values=['Block', 'Cement'], state='readonly',
                                          font=("Helvetica", 11))
        self.category_combo.pack(fill='x')

        # Type
        type_frame = ttk.Frame(cat_type_frame)
        type_frame.grid(row=0, column=1, padx=(10, 0), sticky="ew")
        
        ttk.Label(type_frame, text="Product Type", 
                 font=("Helvetica", 12, "bold"), foreground="#495057").pack(anchor='w', pady=(0, 5))
        self.prod_type_var = tk.StringVar()
        self.prod_type_entry = ttk.Entry(type_frame, textvariable=self.prod_type_var, 
                                        font=("Helvetica", 11))
        self.prod_type_entry.pack(fill='x')
        self.prod_type_entry.insert(0, "Enter product type")
        self.prod_type_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(self.prod_type_entry, "Enter product type"))
        self.prod_type_entry.bind("<FocusOut>", lambda e: self.set_placeholder(self.prod_type_entry, "Enter product type"))

        # Price input with prominent styling
        price_frame = ttk.Frame(form_card)
        price_frame.pack(fill='x', pady=15)
        
        ttk.Label(price_frame, text="Unit Price (GH₵)", 
                 font=("Helvetica", 12, "bold"), foreground="#495057").pack(anchor='w', pady=(0, 5))
        
        price_input_frame = ttk.Frame(price_frame)
        price_input_frame.pack(fill='x')
        
        currency_label = ttk.Label(price_input_frame, text="GH₵", 
                                  font=("Helvetica", 14, "bold"), foreground="#28a745")
        currency_label.pack(side='left', padx=(0, 5))
        
        self.prod_price_var = tk.StringVar()
        self.prod_price_entry = ttk.Entry(price_input_frame, textvariable=self.prod_price_var, 
                                         font=("Helvetica", 14), width=15)
        self.prod_price_entry.pack(side='left')
        self.prod_price_entry.insert(0, "Enter price")
        self.prod_price_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(self.prod_price_entry, "Enter price"))
        self.prod_price_entry.bind("<FocusOut>", lambda e: self.set_placeholder(self.prod_price_entry, "Enter price"))

        # Action buttons with modern styling
        button_frame = ttk.Frame(form_card)
        button_frame.pack(fill='x', pady=20)
        
        # Primary action buttons
        primary_buttons = ttk.Frame(button_frame)
        primary_buttons.pack(fill='x', pady=(0, 10))
        
        add_btn = ttk.Button(primary_buttons, text="➕ Add Product", 
                            bootstyle="success", command=self.add_product)
        add_btn.pack(side='left', padx=(0, 5), fill='x', expand=True)
        
        update_btn = ttk.Button(primary_buttons, text="✏️ Update Product", 
                               bootstyle="primary", command=self.update_product)
        update_btn.pack(side='left', padx=(5, 0), fill='x', expand=True)
        
        # Secondary action buttons
        secondary_buttons = ttk.Frame(button_frame)
        secondary_buttons.pack(fill='x')
        
        delete_btn = ttk.Button(secondary_buttons, text="🗑️ Delete Product", 
                               bootstyle="danger", command=self.delete_product)
        delete_btn.pack(side='left', padx=(0, 5), fill='x', expand=True)
        
        clear_btn = ttk.Button(secondary_buttons, text="🔄 Clear Form", 
                              bootstyle="outline-secondary", command=self.clear_product_form)
        clear_btn.pack(side='left', padx=(5, 0), fill='x', expand=True)

        # Selection indicator
        self.selection_frame = ttk.Frame(form_card)
        self.selection_frame.pack(fill='x', pady=(10, 0))
        
        self.selection_label = ttk.Label(self.selection_frame, text="No product selected", 
                                        font=("Helvetica", 10), foreground="#6c757d")
        self.selection_label.pack(anchor='w')

        # Right column - Products list
        right_column = ttk.Frame(main_container)
        right_column.grid(row=0, column=1, padx=(15, 0), sticky="nsew")

        # Products list card
        list_card = create_card_frame(right_column, "📦 Products Catalog")
        list_card.pack(fill='both', expand=True)

        # Search and filter frame
        search_frame = ttk.Frame(list_card)
        search_frame.pack(fill='x', padx=10, pady=(10, 5))
        
        ttk.Label(search_frame, text="Search:", font=("Helvetica", 10)).pack(side='left', padx=(0, 5))
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, 
                                font=("Helvetica", 10), width=25)
        search_entry.pack(side='left', padx=(0, 10))
        search_entry.insert(0, "Search products...")
        search_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(search_entry, "Search products..."))
        search_entry.bind("<FocusOut>", lambda e: self.set_placeholder(search_entry, "Search products..."))
        search_entry.bind("<KeyRelease>", self.search_products)
        
        # Category filter
        ttk.Label(search_frame, text="Category:", font=("Helvetica", 10)).pack(side='left', padx=(10, 5))
        self.filter_var = tk.StringVar()
        filter_combo = ttk.Combobox(search_frame, textvariable=self.filter_var, 
                                   values=["All", "Block", "Cement"], 
                                   state='readonly', width=10)
        filter_combo.pack(side='left')
        filter_combo.set("All")
        filter_combo.bind('<<ComboboxSelected>>', self.filter_products)

        # Enhanced treeview with modern styling
        tree_frame = ttk.Frame(list_card)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=10)

        columns = ('ID', 'Name', 'Category', 'Type', 'Price', 'Stock', 'Value')
        self.products_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', 
                                         height=20, selectmode='extended')
        
        # Configure column headings and widths
        column_configs = {
            'ID': {'width': 50, 'anchor': 'center'},
            'Name': {'width': 150, 'anchor': 'w'},
            'Category': {'width': 80, 'anchor': 'center'},
            'Type': {'width': 120, 'anchor': 'w'},
            'Price': {'width': 80, 'anchor': 'e'},
            'Stock': {'width': 60, 'anchor': 'center'},
            'Value': {'width': 100, 'anchor': 'e'}
        }
        
        for col, config in column_configs.items():
            self.products_tree.heading(col, text=col, anchor='center')
            self.products_tree.column(col, width=config['width'], anchor=config['anchor'])

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.products_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient='horizontal', command=self.products_tree.xview)
        self.products_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Grid layout for tree and scrollbars
        self.products_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')

        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # Configure main container row weight
        main_container.rowconfigure(0, weight=1)

        # Bind events
        self.products_tree.bind('<Double-1>', self.on_product_double_click)
        self.products_tree.bind('<<TreeviewSelect>>', self.on_product_select)

        # Initialize data
        self.refresh_products_display()
        logging.info("Modern products tab UI initialized")

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

    def animate_cards(self, cards):
        """Apply fade-in animation to cards"""
        try:
            for card in cards:
                card.configure(alpha=0)
                for i in range(0, 101, 10):
                    card.configure(alpha=i/100)
                    self.products_frame.winfo_toplevel().update()
                    self.products_frame.winfo_toplevel().after(20)
            logging.info("Animated products cards")
        except Exception as e:
            logging.error(f"Products card animation error: {str(e)}")

    def add_product(self):
        """Add a new product"""
        if not all([self.prod_name_var.get(), self.prod_category_var.get(), 
                   self.prod_type_var.get(), self.prod_price_var.get()]):
            messagebox.showerror("Error", "Please fill all fields")
            logging.warning("Add product failed: Missing fields")
            return
        
        if self.prod_name_var.get() == "Enter product name" or \
           self.prod_type_var.get() == "Enter product type" or \
           self.prod_price_var.get() == "Enter price":
            messagebox.showerror("Error", "Please enter valid values")
            logging.warning("Add product failed: Placeholder values detected")
            return
        
        try:
            price = float(self.prod_price_var.get())
            if price <= 0:
                messagebox.showerror("Error", "Price must be positive")
                logging.warning(f"Add product failed: Invalid price {self.prod_price_var.get()}")
                return
        except ValueError:
            messagebox.showerror("Error", "Invalid price")
            logging.warning(f"Add product failed: Non-numeric price {self.prod_price_var.get()}")
            return
        
        try:
            self.db.add_product(
                self.prod_name_var.get(), self.prod_category_var.get(), 
                self.prod_type_var.get(), price
            )
            messagebox.showinfo("Success", "Product added successfully")
            logging.info(f"Product added: {self.prod_name_var.get()}")
            self.clear_product_form()
            self.refresh_products_display()
            self.app.sales_manager.refresh_product_list()
            if hasattr(self.app, 'inventory_manager'):
                self.app.inventory_manager.refresh_product_list()
            if hasattr(self.app, 'inventory_details_manager'):
                self.app.inventory_details_manager.refresh_product_list()
            if hasattr(self.app, 'reports_manager'):
                self.app.reports_manager.refresh_reports()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add product: {str(e)}")
            logging.error(f"Add product error: {str(e)}")

    def update_product(self):
        """Update selected product"""
        if not self.selected_product_id:
            messagebox.showerror("Error", "Please select a product to update")
            logging.warning("Update product failed: No product selected")
            return
        
        if not all([self.prod_name_var.get(), self.prod_category_var.get(), 
                   self.prod_type_var.get(), self.prod_price_var.get()]):
            messagebox.showerror("Error", "Please fill all fields")
            logging.warning("Update product failed: Missing fields")
            return
        
        if self.prod_name_var.get() == "Enter product name" or \
           self.prod_type_var.get() == "Enter product type" or \
           self.prod_price_var.get() == "Enter price":
            messagebox.showerror("Error", "Please enter valid values")
            logging.warning("Update product failed: Placeholder values detected")
            return
        
        try:
            price = float(self.prod_price_var.get())
            if price <= 0:
                messagebox.showerror("Error", "Price must be positive")
                logging.warning(f"Update product failed: Invalid price {self.prod_price_var.get()}")
                return
        except ValueError:
            messagebox.showerror("Error", "Invalid price")
            logging.warning(f"Update product failed: Non-numeric price {self.prod_price_var.get()}")
            return
        
        try:
            self.db.update_product(
                self.selected_product_id, self.prod_name_var.get(), 
                self.prod_category_var.get(), self.prod_type_var.get(), price
            )
            messagebox.showinfo("Success", "Product updated successfully")
            logging.info(f"Product updated: ID {self.selected_product_id}")
            self.clear_product_form()
            self.refresh_products_display()
            self.app.sales_manager.refresh_product_list()
            if hasattr(self.app, 'inventory_manager'):
                self.app.inventory_manager.refresh_product_list()
            if hasattr(self.app, 'inventory_details_manager'):
                self.app.inventory_details_manager.refresh_product_list()
            if hasattr(self.app, 'reports_manager'):
                self.app.reports_manager.refresh_reports()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update product: {str(e)}")
            logging.error(f"Update product error: {str(e)}")

    def delete_product(self):
        """Delete selected product"""
        if not self.selected_product_id:
            messagebox.showerror("Error", "Please select a product to delete")
            logging.warning("Delete product failed: No product selected")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this product?"):
            try:
                self.db.delete_product(self.selected_product_id)
                messagebox.showinfo("Success", "Product deleted successfully")
                logging.info(f"Product deleted: ID {self.selected_product_id}")
                self.clear_product_form()
                self.refresh_products_display()
                self.app.sales_manager.refresh_product_list()
                if hasattr(self.app, 'inventory_manager'):
                    self.app.inventory_manager.refresh_product_list()
                if hasattr(self.app, 'inventory_details_manager'):
                    self.app.inventory_details_manager.refresh_product_list()
                if hasattr(self.app, 'reports_manager'):
                    self.app.reports_manager.refresh_reports()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete product: {str(e)}")
                logging.error(f"Delete product error: {str(e)}")

    def clear_product_form(self):
        """Clear product form"""
        self.prod_name_var.set("")
        self.prod_category_var.set("")
        self.prod_type_var.set("")
        self.prod_price_var.set("")
        self.set_placeholder(self.prod_name_entry, "Enter product name")
        self.set_placeholder(self.prod_type_entry, "Enter product type")
        self.set_placeholder(self.prod_price_entry, "Enter price")
        self.selected_product_id = None
        self.selection_label.configure(text="No product selected")
        logging.info("Product form cleared")

    def on_product_double_click(self, event):
        """Handle double-click on product"""
        item = self.products_tree.selection()[0] if self.products_tree.selection() else None
        if not item:
            return
        
        values = self.products_tree.item(item, 'values')
        self.selected_product_id = int(values[0])
        self.prod_name_var.set(values[1])
        self.prod_category_var.set(values[2])
        self.prod_type_var.set(values[3])
        self.prod_price_var.set(values[4].replace("GH₵", ""))
        self.clear_placeholder(self.prod_name_entry, "Enter product name")
        self.clear_placeholder(self.prod_type_entry, "Enter product type")
        self.clear_placeholder(self.prod_price_entry, "Enter price")
        logging.info(f"Selected product for edit: ID {self.selected_product_id}")

    def on_product_select(self, event=None):
        """Handle product selection"""
        item = self.products_tree.selection()[0] if self.products_tree.selection() else None
        if item:
            values = self.products_tree.item(item, 'values')
            self.selection_label.configure(text=f"Selected: {values[1]} (ID: {values[0]})")
        else:
            self.selection_label.configure(text="No product selected")

    def search_products(self, event=None):
        """Search products in real-time"""
        self.refresh_products_display()

    def filter_products(self, event=None):
        """Filter products by category"""
        self.refresh_products_display()

    def refresh_products_display(self):
        """Refresh products display with filtering and search"""
        try:
            for item in self.products_tree.get_children():
                self.products_tree.delete(item)
            
            # Get filter and search criteria
            filter_category = getattr(self, 'filter_var', tk.StringVar()).get() or "All"
            search_term = getattr(self, 'search_var', tk.StringVar()).get() or ""
            if search_term == "Search products...":
                search_term = ""
            
            for row in self.db.get_all_products():
                product_id, name, category, ptype, price, stock = row
                
                # Apply search filter
                if search_term and search_term.lower() not in name.lower():
                    continue
                
                # Apply category filter
                if filter_category != "All" and category != filter_category:
                    continue
                
                # Calculate total value
                total_value = price * stock
                
                self.products_tree.insert("", "end", values=(
                    product_id, name, category, ptype, f"GH₵{price:.2f}", stock, f"GH₵{total_value:.2f}"
                ))
            logging.info("Products display refreshed with filters")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh products: {str(e)}")
            logging.error(f"Error refreshing products display: {str(e)}")
            