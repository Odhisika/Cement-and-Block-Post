import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import bcrypt
import logging
from gui_utils import (create_labeled_entry, create_button_frame, create_card_frame, 
                      DesignSystem, create_modern_button, configure_styles)

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

class LoginManager:
    def __init__(self, root, db, callback):
        self.root = root
        self.db = db
        self.callback = callback
        self.login_in_progress = False  # Flag to prevent multiple login attempts
        self.create_login_frame()

    def create_login_frame(self):
        """Create a modern login interface with enhanced styling"""
        ds = DesignSystem()
        configure_styles()
        
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Background with gradient effect
        self.login_frame = ttk.Frame(self.root, padding=ds.SPACING['xxl'])
        self.login_frame.pack(fill='both', expand=True)
        self.login_frame.configure(style="Container.TFrame")

        # Center container
        center_frame = ttk.Frame(self.login_frame)
        center_frame.pack(expand=True)

        # App branding header
        brand_frame = ttk.Frame(center_frame)
        brand_frame.pack(pady=(0, ds.SPACING['xxl']))
        
        app_title = ttk.Label(brand_frame, text="Block & Cement", 
                             font=ds.FONTS['heading_large'], 
                             foreground=ds.COLORS['primary'])
        app_title.pack()
        
        app_subtitle = ttk.Label(brand_frame, text="Point of Sale System", 
                                font=ds.FONTS['body_large'], 
                                foreground=ds.COLORS['text_secondary'])
        app_subtitle.pack()

        # Login card with enhanced styling
        login_card = ttk.Frame(center_frame, padding=ds.SPACING['xxl'], 
                              relief="solid", borderwidth=2)
        login_card.pack(pady=ds.SPACING['lg'])
        login_card.configure(style="Card.TFrame")

        # Card header
        header_label = ttk.Label(login_card, text="🔐 Sign In", 
                                font=ds.FONTS['heading_medium'], 
                                foreground=ds.COLORS['text_primary'])
        header_label.pack(pady=(0, ds.SPACING['lg']))

        # Username field with icon
        username_frame = ttk.Frame(login_card)
        username_frame.pack(fill='x', pady=ds.SPACING['sm'])
        
        ttk.Label(username_frame, text="👤", font=ds.FONTS['body_large']).pack(side='left', padx=(0, ds.SPACING['sm']))
        username_label = ttk.Label(username_frame, text="Username", font=ds.FONTS['body_medium'])
        username_label.pack(anchor='w')
        
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(username_frame, textvariable=self.username_var, 
                                       font=ds.FONTS['body_medium'], width=25)
        self.username_entry.pack(fill='x', pady=(ds.SPACING['xs'], 0))
        self.username_entry.insert(0, "Enter your username")
        self.username_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(self.username_entry, "Enter your username"))
        self.username_entry.bind("<FocusOut>", lambda e: self.set_placeholder(self.username_entry, "Enter your username"))
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())

        # Password field with icon
        password_frame = ttk.Frame(login_card)
        password_frame.pack(fill='x', pady=ds.SPACING['sm'])
        
        ttk.Label(password_frame, text="🔒", font=ds.FONTS['body_large']).pack(side='left', padx=(0, ds.SPACING['sm']))
        password_label = ttk.Label(password_frame, text="Password", font=ds.FONTS['body_medium'])
        password_label.pack(anchor='w')
        
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(password_frame, textvariable=self.password_var, 
                                       font=ds.FONTS['body_medium'], width=25, show="*")
        self.password_entry.pack(fill='x', pady=(ds.SPACING['xs'], 0))
        self.password_entry.insert(0, "Enter your password")
        self.password_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(self.password_entry, "Enter your password", show="*"))
        self.password_entry.bind("<FocusOut>", lambda e: self.set_placeholder(self.password_entry, "Enter your password", show="*"))
        self.password_entry.bind("<Return>", lambda e: self.verify_login())

        # Button section
        button_frame = ttk.Frame(login_card)
        button_frame.pack(fill='x', pady=(ds.SPACING['lg'], ds.SPACING['sm']))
        
        self.login_btn = create_modern_button(button_frame, "🚀 Sign In", 
                                             command=self.verify_login, style="primary", width=20)
        self.login_btn.pack(side='left', padx=(0, ds.SPACING['sm']))
        
        clear_btn = create_modern_button(button_frame, "🗑️ Clear", 
                                        command=self.clear_form, style="outline-secondary", width=15)
        clear_btn.pack(side='left')

        # Status area
        self.status_frame = ttk.Frame(login_card)
        self.status_frame.pack(fill='x', pady=(ds.SPACING['sm'], 0))
        
        self.spinner = ttk.Label(self.status_frame, text="🔄 Authenticating...", 
                                font=ds.FONTS['body_medium'], foreground=ds.COLORS['info'])

        # Footer info
        footer_frame = ttk.Frame(center_frame)
        footer_frame.pack(pady=(ds.SPACING['lg'], 0))
        
        footer_text = ttk.Label(footer_frame, text="Secure • Fast • Reliable", 
                               font=ds.FONTS['caption'], foreground=ds.COLORS['text_muted'])
        footer_text.pack()

        # Focus on username field
        self.username_entry.focus()
        
        logging.info("Enhanced modern login frame initialized")

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

    def verify_login(self):
        """Verify login credentials"""
        if self.login_in_progress:
            return  # Prevent multiple login attempts

        username = self.username_var.get()
        password = self.password_var.get()
        
        if username == "Enter your username" or password == "Enter your password":
            messagebox.showerror("Error", "Please enter both username and password")
            logging.warning("Login attempt failed: Placeholder text detected")
            return

        try:
            self.login_in_progress = True
            self.login_btn.configure(state="disabled", text="Logging in...")
            self.spinner.pack(pady=10)
            self.root.config(cursor="wait")
            self.login_frame.configure(bootstyle="secondary")
            self.root.update()

            user = self.db.get_user(username)
            if user and bcrypt.checkpw(password.encode('utf-8'), user[1]):
                messagebox.showinfo("Success", f"Welcome, {username}!")
                logging.info(f"User {username} logged in successfully")
                # Reset UI elements before destroying frame
                self.login_btn.configure(state="normal", text="Login")
                self.spinner.pack_forget()
                self.root.config(cursor="")
                self.login_frame.configure(bootstyle="light")
                self.login_frame.destroy()
                self.callback()
            else:
                messagebox.showerror("Error", "Invalid username or password")
                logging.warning(f"Login attempt failed for user {username}: Invalid credentials")
        except Exception as e:
            messagebox.showerror("Error", f"Login failed: {str(e)}")
            logging.error(f"Login error for user {username}: {str(e)}")
        finally:
            self.login_in_progress = False
            # Ensure button and spinner are reset even on error
            try:
                self.login_btn.configure(state="normal", text="Login")
                self.spinner.pack_forget()
                self.root.config(cursor="")
                self.login_frame.configure(bootstyle="light")
            except tk.TclError:
                logging.warning("Login button already destroyed, skipping configure")

    def clear_form(self):
        """Clear the login form"""
        self.username_var.set("")
        self.password_var.set("")
        self.set_placeholder(self.username_entry, "Enter your username")
        self.set_placeholder(self.password_entry, "Enter your password", show="*")
        logging.info("Login form cleared")