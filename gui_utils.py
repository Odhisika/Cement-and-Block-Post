import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import logging

# Design System Constants
class DesignSystem:
    """Centralized design system for consistent UI across the application"""
    
    # Color Palette
    COLORS = {
        'primary': '#007bff',
        'primary_dark': '#0056b3',
        'primary_light': '#66b3ff',
        'secondary': '#6c757d',
        'success': '#28a745',
        'warning': '#ffc107',
        'danger': '#dc3545',
        'info': '#17a2b8',
        'light': '#f8f9fa',
        'dark': '#343a40',
        'white': '#ffffff',
        'background': '#f5f6fa',
        'card_bg': '#ffffff',
        'border': '#dee2e6',
        'text_primary': '#212529',
        'text_secondary': '#6c757d',
        'text_muted': '#868e96'
    }
    
    # Typography
    FONTS = {
        'heading_large': ('Helvetica', 24, 'bold'),
        'heading_medium': ('Helvetica', 18, 'bold'),
        'heading_small': ('Helvetica', 14, 'bold'),
        'body_large': ('Helvetica', 12),
        'body_medium': ('Helvetica', 11),
        'body_small': ('Helvetica', 10),
        'caption': ('Helvetica', 9),
        'button': ('Helvetica', 11, 'bold'),
        'monospace': ('Consolas', 10)
    }
    
    # Spacing
    SPACING = {
        'xs': 4,
        'sm': 8,
        'md': 12,
        'lg': 16,
        'xl': 20,
        'xxl': 24
    }
    
    # Component Sizes
    SIZES = {
        'button_height': 35,
        'input_height': 32,
        'card_padding': 15,
        'border_radius': 6,
        'border_width': 1
    }

# Fallback ToolTip implementation when the external 'tooltip' package is not available.
# This provides a minimal tooltip behavior used by create_labeled_entry.
class ToolTip:
    def __init__(self, widget, text=''):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        # Bind enter/leave to show/hide tooltip
        try:
            self.widget.bind("<Enter>", self.show)
            self.widget.bind("<Leave>", self.hide)
        except Exception:
            # Some widgets may not support bind in the same way; ignore binding errors.
            pass

    def show(self, event=None):
        if self.tipwindow or not self.text:
            return
        # Calculate position just below the widget
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 10
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, background="#FFFFE0", relief='solid', borderwidth=1)
        label.pack()

    def hide(self, event=None):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

# Configure logging
logging.basicConfig(filename='pos.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def create_labeled_entry(parent, label_text, var, row=None, column=None, width=20, readonly=False, font=("Helvetica", 12)):
    """Create a labeled entry with modern styling using pack"""
    frame = ttk.Frame(parent, padding=5)
    frame.pack(fill='x', pady=5)
    
    ttk.Label(frame, text=label_text, font=("Helvetica", 12)).pack(side='left', padx=5)
    entry = ttk.Entry(frame, textvariable=var, width=width, font=font)
    entry.pack(side='left', fill='x', expand=True, padx=5)
    
    if readonly:
        entry.configure(state='readonly')
    
    # Use custom tooltip (no bootstyle param)
    ToolTip(entry, text=label_text)
    
    logging.info(f"Created labeled entry: {label_text}")
    return entry

def create_button_frame(parent, row=None, column=None, columnspan=1):
    """Create a frame for buttons with modern styling using pack"""
    frame = ttk.Frame(parent, padding=10, bootstyle="light")
    frame.pack(fill='x', pady=5)
    logging.info("Created button frame")
    return frame

def create_card_frame(parent, title, padding=10):
    """Create a card-style frame with shadow and rounded corners"""
    card = ttk.Frame(parent, bootstyle="light", padding=padding, relief="flat")
    card.configure(style="Card.TFrame")
    title_label = ttk.Label(card, text=title, font=("Helvetica", 14, "bold"), bootstyle="primary")
    title_label.pack(anchor='w', pady=5)
    separator = ttk.Separator(card, bootstyle="primary")
    separator.pack(fill='x', pady=5)
    
    # Store the title label as an attribute of the card frame for easy access
    card.title_label = title_label
    
    logging.info(f"Created card frame: {title}")
    return card

def create_modern_button(parent, text, command=None, style="primary", width=None, **kwargs):
    """Create a modern styled button with consistent design"""
    ds = DesignSystem()
    
    style_configs = {
        'primary': {'bootstyle': 'primary', 'bg': ds.COLORS['primary']},
        'secondary': {'bootstyle': 'secondary', 'bg': ds.COLORS['secondary']},
        'success': {'bootstyle': 'success', 'bg': ds.COLORS['success']},
        'warning': {'bootstyle': 'warning', 'bg': ds.COLORS['warning']},
        'danger': {'bootstyle': 'danger', 'bg': ds.COLORS['danger']},
        'outline-primary': {'bootstyle': 'outline-primary'},
        'outline-secondary': {'bootstyle': 'outline-secondary'}
    }
    
    config = style_configs.get(style, style_configs['primary'])
    
    button = ttk.Button(parent, text=text, command=command, 
                       bootstyle=config['bootstyle'],
                       width=width, **kwargs)
    
    logging.info(f"Created modern button: {text}")
    return button

def create_metric_card(parent, title, value, subtitle="", color="primary"):
    """Create a metric card with consistent styling"""
    ds = DesignSystem()
    
    card = ttk.Frame(parent, padding=ds.SIZES['card_padding'], 
                    relief="solid", borderwidth=ds.SIZES['border_width'])
    
    # Title
    title_label = ttk.Label(card, text=title, font=ds.FONTS['body_small'], 
                           foreground=ds.COLORS['text_secondary'])
    title_label.pack(anchor='w')
    
    # Value
    color_map = {
        'primary': ds.COLORS['primary'],
        'success': ds.COLORS['success'],
        'warning': ds.COLORS['warning'],
        'danger': ds.COLORS['danger'],
        'info': ds.COLORS['info']
    }
    
    value_color = color_map.get(color, ds.COLORS['primary'])
    value_label = ttk.Label(card, text=str(value), font=ds.FONTS['heading_medium'], 
                           foreground=value_color)
    value_label.pack(anchor='w')
    
    # Subtitle
    if subtitle:
        subtitle_label = ttk.Label(card, text=subtitle, font=ds.FONTS['caption'], 
                                  foreground=ds.COLORS['text_muted'])
        subtitle_label.pack(anchor='w')
    
    logging.info(f"Created metric card: {title}")
    return card

def create_section_header(parent, title, subtitle=""):
    """Create a consistent section header"""
    ds = DesignSystem()
    
    header_frame = ttk.Frame(parent)
    header_frame.pack(fill='x', pady=(0, ds.SPACING['lg']))
    
    title_label = ttk.Label(header_frame, text=title, font=ds.FONTS['heading_large'], 
                           foreground=ds.COLORS['primary'])
    title_label.pack(side='left')
    
    if subtitle:
        subtitle_label = ttk.Label(header_frame, text=subtitle, font=ds.FONTS['body_medium'], 
                                  foreground=ds.COLORS['text_secondary'])
        subtitle_label.pack(side='right')
    
    logging.info(f"Created section header: {title}")
    return header_frame

def create_data_table(parent, columns, data=None, height=15):
    """Create a modern data table with consistent styling"""
    ds = DesignSystem()
    
    # Container frame
    table_frame = ttk.Frame(parent)
    table_frame.pack(fill='both', expand=True, padx=ds.SPACING['md'], pady=ds.SPACING['md'])
    
    # Treeview
    tree = ttk.Treeview(table_frame, columns=columns, show='headings', 
                       height=height, selectmode='extended')
    
    # Configure columns
    for col in columns:
        tree.heading(col, text=col, anchor='center')
        tree.column(col, width=150, anchor='center')
    
    # Scrollbars
    v_scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=tree.yview)
    h_scrollbar = ttk.Scrollbar(table_frame, orient='horizontal', command=tree.xview)
    tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
    
    # Grid layout
    tree.grid(row=0, column=0, sticky='nsew')
    v_scrollbar.grid(row=0, column=1, sticky='ns')
    h_scrollbar.grid(row=1, column=0, sticky='ew')
    
    table_frame.grid_rowconfigure(0, weight=1)
    table_frame.grid_columnconfigure(0, weight=1)
    
    # Add data if provided
    if data:
        for row in data:
            tree.insert("", "end", values=row)
    
    logging.info(f"Created data table with {len(columns)} columns")
    return tree, table_frame

def configure_styles():
    """Configure comprehensive modern styles for the application"""
    ds = DesignSystem()
    style = ttk.Style()
    
    # Card styles
    style.configure("Card.TFrame", 
                   borderwidth=ds.SIZES['border_width'], 
                   relief="solid", 
                   padding=ds.SIZES['card_padding'], 
                   background=ds.COLORS['card_bg'])
    
    # Button styles
    style.configure("Modern.TButton",
                   font=ds.FONTS['button'],
                   padding=(ds.SPACING['md'], ds.SPACING['sm']))
    
    style.map("Modern.TButton",
              background=[("active", ds.COLORS['primary_dark']), 
                         ("!active", ds.COLORS['primary'])],
              foreground=[("active", ds.COLORS['white']), 
                         ("!active", ds.COLORS['white'])])
    
    # Entry styles
    style.configure("Modern.TEntry",
                   fieldbackground=ds.COLORS['white'],
                   borderwidth=ds.SIZES['border_width'],
                   relief="solid")
    
    # Combobox styles
    style.configure("Modern.TCombobox", 
                   padding=ds.SPACING['sm'],
                   fieldbackground=ds.COLORS['white'])
    
    # Treeview styles
    style.configure("Modern.Treeview", 
                   rowheight=35,
                   font=ds.FONTS['body_medium'],
                   background=ds.COLORS['white'],
                   fieldbackground=ds.COLORS['white'])
    
    style.configure("Modern.Treeview.Heading",
                   font=ds.FONTS['heading_small'],
                   background=ds.COLORS['light'],
                   foreground=ds.COLORS['text_primary'])
    
    # Label styles
    style.configure("Heading.TLabel",
                   font=ds.FONTS['heading_large'],
                   foreground=ds.COLORS['primary'])
    
    style.configure("Subheading.TLabel",
                   font=ds.FONTS['heading_medium'],
                   foreground=ds.COLORS['text_primary'])
    
    style.configure("Body.TLabel",
                   font=ds.FONTS['body_medium'],
                   foreground=ds.COLORS['text_primary'])
    
    style.configure("Caption.TLabel",
                   font=ds.FONTS['caption'],
                   foreground=ds.COLORS['text_secondary'])
    
    # Frame styles
    style.configure("Container.TFrame",
                   background=ds.COLORS['background'],
                   padding=ds.SPACING['lg'])
    
    logging.info("Comprehensive modern styles configured")