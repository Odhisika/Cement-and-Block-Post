import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import ToolTip
from tkinter import messagebox
from datetime import datetime, timedelta
from gui_utils import create_card_frame
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

class InventoryDetailsManager:
    def __init__(self, app, parent, db):
        self.app = app
        self.db = db
        self.inv_details_frame = ttk.Frame(parent, padding=10)
        self.create_inventory_details_tab()

    def create_inventory_details_tab(self):
        """Create the inventory history interface with modern styling"""
        # Header section
        header_frame = ttk.Frame(self.inv_details_frame)
        header_frame.pack(fill='x', pady=(0, 20))
        
        title = ttk.Label(header_frame, text="Inventory History & Analytics", 
                         font=("Helvetica", 24, "bold"), foreground="#007bff")
        title.pack(side='left')
        
        # Quick stats in header
        stats_frame = ttk.Frame(header_frame)
        stats_frame.pack(side='right')
        
        try:
            logs = self.db.get_inventory_logs()
            total_adjustments = len(logs)
            recent_adjustments = 0
            for log in logs:
                if len(log) >= 5:
                    try:
                        if (datetime.now() - datetime.fromisoformat(log[4])).days <= 7:
                            recent_adjustments += 1
                    except:
                        continue
            
            stats_text = f"Total Adjustments: {total_adjustments} | This Week: {recent_adjustments}"
            stats_label = ttk.Label(stats_frame, text=stats_text, 
                                   font=("Helvetica", 12), foreground="#6c757d")
            stats_label.pack()
        except Exception as e:
            logging.error(f"Error in header stats: {str(e)}")
            pass

        # Main container
        main_container = ttk.Frame(self.inv_details_frame)
        main_container.pack(fill='both', expand=True)

        # Summary cards row
        summary_frame = ttk.Frame(main_container)
        summary_frame.pack(fill='x', pady=(0, 20))
        summary_frame.columnconfigure(0, weight=1)
        summary_frame.columnconfigure(1, weight=1)
        summary_frame.columnconfigure(2, weight=1)

        # Recent Adjustments card
        recent_card = ttk.Frame(summary_frame, padding=15, relief="solid", borderwidth=1)
        recent_card.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        
        ttk.Label(recent_card, text="Recent Adjustments", font=("Helvetica", 10), 
                 foreground="#6c757d").pack(anchor='w')
        
        try:
            logs = self.db.get_inventory_logs()
            recent_count = 0
            for log in logs:
                if len(log) >= 5:
                    try:
                        if (datetime.now() - datetime.fromisoformat(log[4])).days <= 7:
                            recent_count += 1
                    except:
                        continue
            recent_label = ttk.Label(recent_card, text=str(recent_count), 
                                    font=("Helvetica", 20, "bold"), foreground="#17a2b8")
            recent_label.pack(anchor='w')
            ttk.Label(recent_card, text="This Week", font=("Helvetica", 9), 
                     foreground="#6c757d").pack(anchor='w')
        except:
            ttk.Label(recent_card, text="0", font=("Helvetica", 20, "bold"), 
                     foreground="#17a2b8").pack(anchor='w')

        # Total Value Adjusted card
        value_card = ttk.Frame(summary_frame, padding=15, relief="solid", borderwidth=1)
        value_card.grid(row=0, column=1, padx=(5, 5), sticky="ew")
        
        ttk.Label(value_card, text="Adjustments Today", font=("Helvetica", 10), 
                 foreground="#6c757d").pack(anchor='w')
        
        try:
            logs = self.db.get_inventory_logs()
            today_count = 0
            for log in logs:
                if len(log) >= 5:
                    try:
                        if datetime.fromisoformat(log[4]).date() == datetime.now().date():
                            today_count += 1
                    except:
                        continue
            today_label = ttk.Label(value_card, text=str(today_count), 
                                   font=("Helvetica", 20, "bold"), foreground="#28a745")
            today_label.pack(anchor='w')
            ttk.Label(value_card, text="Today", font=("Helvetica", 9), 
                     foreground="#6c757d").pack(anchor='w')
        except:
            ttk.Label(value_card, text="0", font=("Helvetica", 20, "bold"), 
                     foreground="#28a745").pack(anchor='w')

        # Most Adjusted Product card
        product_card = ttk.Frame(summary_frame, padding=15, relief="solid", borderwidth=1)
        product_card.grid(row=0, column=2, padx=(10, 0), sticky="ew")
        
        ttk.Label(product_card, text="Most Adjusted", font=("Helvetica", 10), 
                 foreground="#6c757d").pack(anchor='w')
        
        try:
            # Get most frequently adjusted product
            product_counts = {}
            for log in self.db.get_inventory_logs():
                product = log[1]
                product_counts[product] = product_counts.get(product, 0) + 1
            
            if product_counts:
                most_adjusted = max(product_counts, key=product_counts.get)
                # Truncate long product names
                display_name = most_adjusted[:15] + "..." if len(most_adjusted) > 15 else most_adjusted
                product_label = ttk.Label(product_card, text=display_name, 
                                         font=("Helvetica", 12, "bold"), foreground="#dc3545")
                product_label.pack(anchor='w')
                ttk.Label(product_card, text=f"{product_counts[most_adjusted]} times", 
                         font=("Helvetica", 9), foreground="#6c757d").pack(anchor='w')
            else:
                ttk.Label(product_card, text="None", font=("Helvetica", 12, "bold"), 
                         foreground="#dc3545").pack(anchor='w')
        except:
            ttk.Label(product_card, text="None", font=("Helvetica", 12, "bold"), 
                     foreground="#dc3545").pack(anchor='w')

        # History table card
        history_card = create_card_frame(main_container, "📋 Adjustment History")
        history_card.pack(fill='both', expand=True)

        # Filter and search frame
        filter_frame = ttk.Frame(history_card)
        filter_frame.pack(fill='x', padx=10, pady=(10, 5))
        
        # Time filter
        ttk.Label(filter_frame, text="Filter:", font=("Helvetica", 10)).pack(side='left', padx=(0, 5))
        
        self.time_filter_var = tk.StringVar()
        time_filter = ttk.Combobox(filter_frame, textvariable=self.time_filter_var, 
                                  values=["All Time", "Today", "This Week", "This Month"], 
                                  state='readonly', width=12)
        time_filter.pack(side='left', padx=(0, 10))
        time_filter.set("All Time")
        time_filter.bind('<<ComboboxSelected>>', self.filter_history)
        
        # Product search
        ttk.Label(filter_frame, text="Search:", font=("Helvetica", 10)).pack(side='left', padx=(10, 5))
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_var, 
                                font=("Helvetica", 10), width=20)
        search_entry.pack(side='left', padx=(0, 10))
        search_entry.insert(0, "Search products...")
        search_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(search_entry, "Search products..."))
        search_entry.bind("<FocusOut>", lambda e: self.set_placeholder(search_entry, "Search products..."))
        search_entry.bind("<KeyRelease>", self.search_history)

        # Refresh button
        refresh_btn = ttk.Button(filter_frame, text="🔄 Refresh", 
                                bootstyle="outline-primary", command=self.refresh_history)
        refresh_btn.pack(side='right')

        # Enhanced treeview with modern styling
        tree_frame = ttk.Frame(history_card)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=10)

        columns = ('ID', 'Product', 'Change', 'Note', 'Date & Time')
        self.history_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', 
                                        height=20, selectmode='extended')
        
        # Configure column headings and widths
        column_configs = {
            'ID': {'width': 50, 'anchor': 'center'},
            'Product': {'width': 200, 'anchor': 'w'},
            'Change': {'width': 80, 'anchor': 'center'},
            'Note': {'width': 250, 'anchor': 'w'},
            'Date & Time': {'width': 150, 'anchor': 'center'}
        }
        
        for col, config in column_configs.items():
            self.history_tree.heading(col, text=col, anchor='center')
            self.history_tree.column(col, width=config['width'], anchor=config['anchor'])

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.history_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient='horizontal', command=self.history_tree.xview)
        self.history_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Grid layout for tree and scrollbars
        self.history_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')

        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # Initialize data
        self.refresh_history()
        logging.info("Modern inventory details tab UI initialized")

    def animate_cards(self, cards):
        """Apply fade-in animation to cards"""
        try:
            for card in cards:
                card.configure(alpha=0)
                for i in range(0, 101, 10):
                    card.configure(alpha=i/100)
                    self.inv_details_frame.winfo_toplevel().update()
                    self.inv_details_frame.winfo_toplevel().after(20)
            logging.info("Animated inventory details cards")
        except Exception as e:
            logging.error(f"Inventory details card animation error: {str(e)}")

    def refresh_history(self):
        """Refresh inventory history display with enhanced formatting"""
        try:
            for item in self.history_tree.get_children():
                self.history_tree.delete(item)
            
            logs = self.db.get_inventory_logs()
            logging.info(f"Retrieved {len(logs)} logs from database")
            
            # Debug: Check the structure of the first log entry
            if logs:
                logging.info(f"Sample log entry: {logs[0]}, Length: {len(logs[0])}")
            
            filtered_logs = self.apply_filters(logs)
            
            for row in filtered_logs:
                try:
                    # Ensure we have exactly 5 elements: id, product_name, change_qty, note, log_date
                    if len(row) != 5:
                        logging.error(f"Invalid row structure: {row}, Length: {len(row)}")
                        continue
                        
                    log_id, product_name, change_qty, note, log_date = row
                    
                    # Format datetime
                    try:
                        dt = datetime.fromisoformat(log_date)
                        formatted_datetime = dt.strftime("%Y-%m-%d %H:%M:%S")
                    except:
                        formatted_datetime = str(log_date)
                    
                    # Color code quantity changes
                    change_display = f"+{change_qty}" if change_qty > 0 else str(change_qty)
                    
                    self.history_tree.insert("", "end", values=(
                        log_id, product_name, change_display, note or "No note", 
                        formatted_datetime
                    ))
                except Exception as row_error:
                    logging.error(f"Error processing row {row}: {str(row_error)}")
                    continue
            
            logging.info("Enhanced inventory history display refreshed")
        except Exception as e:
            error_msg = f"Failed to refresh inventory history: {str(e)}"
            messagebox.showerror("Error", error_msg)
            logging.error(f"Error refreshing inventory history: {str(e)}")
            import traceback
            logging.error(f"Full traceback: {traceback.format_exc()}")

    def apply_filters(self, logs):
        """Apply time and search filters to logs"""
        if not logs:
            return logs
            
        filtered_logs = logs
        
        try:
            # Apply time filter
            time_filter = getattr(self, 'time_filter_var', None)
            if time_filter and time_filter.get() != "All Time":
                now = datetime.now()
                temp_filtered = []
                
                for log in filtered_logs:
                    try:
                        if len(log) < 5:
                            continue
                        log_date = log[4]  # This is the 5th element (index 4)
                        
                        if time_filter.get() == "Today":
                            if datetime.fromisoformat(log_date).date() == now.date():
                                temp_filtered.append(log)
                        elif time_filter.get() == "This Week":
                            week_start = now - timedelta(days=now.weekday())
                            if datetime.fromisoformat(log_date) >= week_start:
                                temp_filtered.append(log)
                        elif time_filter.get() == "This Month":
                            month_start = now.replace(day=1)
                            if datetime.fromisoformat(log_date) >= month_start:
                                temp_filtered.append(log)
                    except Exception as e:
                        logging.error(f"Error filtering log by time {log}: {str(e)}")
                        continue
                        
                filtered_logs = temp_filtered
            
            # Apply search filter
            search_var = getattr(self, 'search_var', None)
            if search_var and search_var.get() and search_var.get() != "Search products...":
                search_term = search_var.get().lower()
                temp_filtered = []
                
                for log in filtered_logs:
                    try:
                        if len(log) < 4:
                            continue
                        product_name = log[1]  # 2nd element (index 1)
                        note = log[3] or ""    # 4th element (index 3)
                        
                        if (search_term in product_name.lower() or 
                            search_term in note.lower()):
                            temp_filtered.append(log)
                    except Exception as e:
                        logging.error(f"Error filtering log by search {log}: {str(e)}")
                        continue
                        
                filtered_logs = temp_filtered
                
        except Exception as e:
            logging.error(f"Error in apply_filters: {str(e)}")
            return logs  # Return original logs if filtering fails
        
        return filtered_logs

    def filter_history(self, event=None):
        """Handle time filter changes"""
        self.refresh_history()

    def search_history(self, event=None):
        """Handle search input changes"""
        self.refresh_history()

    def clear_placeholder(self, entry, placeholder):
        """Clear placeholder text on focus"""
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            entry.configure(foreground='black')

    def set_placeholder(self, entry, placeholder):
        """Set placeholder text when entry loses focus"""
        if not entry.get():
            entry.insert(0, placeholder)
            entry.configure(foreground='gray')

    def refresh_product_list(self):
        """Refresh product list (called by other tabs if needed)"""
        logging.info("Inventory details product list refresh called (no-op)")
        # No product dropdown in this tab, but included for consistency