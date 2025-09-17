import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from login import LoginManager
from database import DatabaseHandler
import logging

# Configure logging
logging.basicConfig(filename='pos.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class BlockCementPOS:
    def __init__(self, root):
        self.root = root
        self.root.title("Block & Cement POS")
        self.root.geometry("1200x700")
        self.db = DatabaseHandler('blocks_cement.db')

        # Theme setup
        self.style = ttk.Style(theme='flatly')  # flatly, darkly, litera
        self.style.configure("TButton", font=("Helvetica", 12))
        self.style.configure("TLabel", font=("Helvetica", 12))
        self.style.configure("Treeview.Heading", font=("Helvetica", 12, "bold"))
        self.style.configure("Treeview", font=("Helvetica", 11), rowheight=25)

        # Initialize manager variables
        self.dashboard_manager = None
        self.sales_manager = None
        self.inventory_manager = None
        self.products_manager = None
        self.reports_manager = None
        self.inventory_details_manager = None

        self.create_login_screen()

    def create_login_screen(self):
        """Create login screen"""
        self.login_manager = LoginManager(self.root, self.db, self.create_main_app)
        logging.info("Login screen initialized")

    def create_main_app(self):
        """Create main application interface with sidebar"""
        for widget in self.root.winfo_children():
            widget.destroy()

        # Main container
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill='both', expand=True)

        # Sidebar
        self.sidebar = ttk.Frame(self.main_frame, bootstyle="primary")
        self.sidebar.pack(side='left', fill='y', padx=5, pady=5)

        # Sidebar buttons
        self.nav_buttons = {}
        tabs = [
            ("Dashboard", self.show_dashboard),
            ("Sales", self.show_sales),
            ("Inventory", self.show_inventory),
            ("Products", self.show_products),
            ("Reports", self.show_reports),
            ("Inventory History", self.show_inventory_details),
            ("Toggle Theme", self.toggle_theme),
            ("Logout", self.logout)
        ]

        for text, command in tabs:
            btn = ttk.Button(
                self.sidebar, text=text,
                command=command,
                bootstyle="primary-outline",
                width=20
            )
            btn.pack(pady=5, padx=10, fill='x')
            self.nav_buttons[text] = btn

        # Content area
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)

        # Initialize managers with error handling
        self.initialize_managers()

        # Safe hiding of tabs and show default
        self.hide_all_tabs()
        self.show_dashboard()  # Default tab
        logging.info("Main application interface initialized")

    def initialize_managers(self):
        """Initialize all manager classes with error handling"""
        try:
            # Try to import and create managers
            try:
                from dashboard import DashboardManager
                self.dashboard_manager = DashboardManager(self, self.content_frame, self.db)
                logging.info("Dashboard manager initialized")
            except ImportError:
                logging.warning("DashboardManager not found, creating placeholder")
                self.dashboard_manager = self.create_placeholder_manager("Dashboard")

            try:
                from sales import SalesManager
                self.sales_manager = SalesManager(self, self.content_frame, self.db)
                logging.info("Sales manager initialized")
            except ImportError:
                logging.warning("SalesManager not found, creating placeholder")
                self.sales_manager = self.create_placeholder_manager("Sales")

            try:
                from inventory import InventoryManager
                self.inventory_manager = InventoryManager(self, self.content_frame, self.db)
                logging.info("Inventory manager initialized")
            except ImportError:
                logging.warning("InventoryManager not found, creating placeholder")
                self.inventory_manager = self.create_placeholder_manager("Inventory")

            try:
                from products import ProductsManager
                self.products_manager = ProductsManager(self, self.content_frame, self.db)
                logging.info("Products manager initialized")
            except ImportError:
                logging.warning("ProductsManager not found, creating placeholder")
                self.products_manager = self.create_placeholder_manager("Products")

            try:
                from reports import ReportsManager
                self.reports_manager = ReportsManager(self, self.content_frame, self.db)
                logging.info("Reports manager initialized")
            except ImportError:
                logging.warning("ReportsManager not found, creating placeholder")
                self.reports_manager = self.create_placeholder_manager("Reports")

            try:
                from inventory_details import InventoryDetailsManager
                self.inventory_details_manager = InventoryDetailsManager(self, self.content_frame, self.db)
                logging.info("Inventory details manager initialized")
            except ImportError:
                logging.warning("InventoryDetailsManager not found, creating placeholder")
                self.inventory_details_manager = self.create_placeholder_manager("Inventory Details")

        except Exception as e:
            logging.error(f"Error initializing managers: {str(e)}")
            messagebox.showerror("Error", f"Error initializing application modules: {str(e)}")

    def create_placeholder_manager(self, name):
        """Create a placeholder manager when the actual manager is missing"""
        class PlaceholderManager:
            def __init__(self, parent_frame, name):
                self.frame_name = name.lower().replace(" ", "_") + "_frame"
                frame = ttk.Frame(parent_frame)
                setattr(self, self.frame_name, frame)
                
                # Create a simple placeholder content
                ttk.Label(frame, text=f"{name} Module", 
                         font=("Helvetica", 24, "bold")).pack(pady=50)
                ttk.Label(frame, text=f"The {name} module is not yet implemented.", 
                         font=("Helvetica", 14)).pack(pady=10)
                ttk.Label(frame, text="Please check that all required files are present.", 
                         font=("Helvetica", 12)).pack(pady=5)

        return PlaceholderManager(self.content_frame, name)

    def hide_all_tabs(self):
        """Hide all tab frames safely"""
        managers_and_frames = [
            (self.dashboard_manager, "dashboard_frame"),
            (self.sales_manager, "sales_frame"),
            (self.inventory_manager, "inventory_frame"),
            (self.products_manager, "products_frame"),
            (self.reports_manager, "reports_frame"),
            (self.inventory_details_manager, "inv_details_frame"),
        ]

        for manager, frame_attr in managers_and_frames:
            if manager and hasattr(manager, frame_attr):
                frame = getattr(manager, frame_attr)
                if frame and frame.winfo_exists():
                    frame.pack_forget()

    def show_dashboard(self):
        if self.dashboard_manager:
            self.hide_all_tabs()
            frame = getattr(self.dashboard_manager, 'dashboard_frame', None)
            if frame:
                frame.pack(fill='both', expand=True)
            self.set_active_button("Dashboard")
            self.animate_tab()
            # Refresh dashboard data when shown
            if hasattr(self.dashboard_manager, 'refresh_dashboard'):
                self.dashboard_manager.refresh_dashboard()
            logging.info("Dashboard tab displayed")
        else:
            messagebox.showerror("Error", "Dashboard module not available")

    def show_sales(self):
        if self.sales_manager:
            self.hide_all_tabs()
            frame = getattr(self.sales_manager, 'sales_frame', None)
            if frame:
                frame.pack(fill='both', expand=True)
            self.set_active_button("Sales")
            self.animate_tab()
            logging.info("Sales tab displayed")
        else:
            messagebox.showerror("Error", "Sales module not available")

    def show_inventory(self):
        if self.inventory_manager:
            self.hide_all_tabs()
            frame = getattr(self.inventory_manager, 'inventory_frame', None)
            if frame:
                frame.pack(fill='both', expand=True)
            self.set_active_button("Inventory")
            self.animate_tab()
            logging.info("Inventory tab displayed")
        else:
            messagebox.showerror("Error", "Inventory module not available")

    def show_products(self):
        if self.products_manager:
            self.hide_all_tabs()
            frame = getattr(self.products_manager, 'products_frame', None)
            if frame:
                frame.pack(fill='both', expand=True)
            self.set_active_button("Products")
            self.animate_tab()
            logging.info("Products tab displayed")
        else:
            messagebox.showerror("Error", "Products module not available")

    def show_reports(self):
        if self.reports_manager:
            self.hide_all_tabs()
            frame = getattr(self.reports_manager, 'reports_frame', None)
            if frame:
                frame.pack(fill='both', expand=True)
            self.set_active_button("Reports")
            self.animate_tab()
            logging.info("Reports tab displayed")
        else:
            messagebox.showerror("Error", "Reports module not available")

    def show_inventory_details(self):
        if self.inventory_details_manager:
            self.hide_all_tabs()
            frame = getattr(self.inventory_details_manager, 'inv_details_frame', None)
            if frame:
                frame.pack(fill='both', expand=True)
            self.set_active_button("Inventory History")
            self.animate_tab()
            logging.info("Inventory History tab displayed")
        else:
            messagebox.showerror("Error", "Inventory Details module not available")

    def animate_tab(self):
        """Smooth fade-in effect for the whole window"""
        try:
            self.root.attributes("-alpha", 0.8)  # slightly transparent
            for i in range(80, 101, 2):  # fade in steps
                self.root.attributes("-alpha", i / 100)
                self.root.update_idletasks()
                self.root.after(5)  # control speed
            self.root.attributes("-alpha", 1.0)  # ensure fully visible
            logging.info("Fade-in animation applied")
        except Exception as e:
            logging.error(f"Tab animation error: {str(e)}")

    def toggle_theme(self):
        """Toggle between flatly and darkly themes"""
        current_theme = self.style.theme_use()
        new_theme = "darkly" if current_theme == "flatly" else "flatly"
        self.style.theme_use(new_theme)
        logging.info(f"Switched to theme: {new_theme}")

    def set_active_button(self, active_text):
        """Highlight the active sidebar button"""
        for text, btn in self.nav_buttons.items():
            btn.configure(bootstyle="primary-outline" if text != active_text else "primary")

    def refresh_all_managers(self):
        """Refresh all manager displays after data changes"""
        try:
            if hasattr(self.dashboard_manager, 'refresh_dashboard'):
                self.dashboard_manager.refresh_dashboard()
            if hasattr(self.inventory_manager, 'refresh_current_stocks'):
                self.inventory_manager.refresh_current_stocks()
            if hasattr(self.inventory_manager, 'refresh_product_list'):
                self.inventory_manager.refresh_product_list()
            if hasattr(self.products_manager, 'refresh_products_display'):
                self.products_manager.refresh_products_display()
            if hasattr(self.inventory_details_manager, 'refresh_history'):
                self.inventory_details_manager.refresh_history()
            if hasattr(self.reports_manager, 'refresh_reports'):
                self.reports_manager.refresh_reports()
            if hasattr(self.sales_manager, 'refresh_recent_sales'):
                self.sales_manager.refresh_recent_sales()
            logging.info("All managers refreshed")
        except Exception as e:
            logging.error(f"Error refreshing managers: {str(e)}")

    def logout(self):
        """Log out and return to login screen"""
        self.main_frame.destroy()
        self.create_login_screen()
        logging.info("User logged out")


if __name__ == "__main__":
    root = ttk.Window()
    app = BlockCementPOS(root)
    root.mainloop()