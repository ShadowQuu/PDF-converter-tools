"""
Shared styles for PDF tool GUI components.
Provides consistent styling across all tabs and widgets.
"""

# Primary button style (green - for main actions like convert, split)
BUTTON_PRIMARY = """
    QPushButton {
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 4px;
        font-weight: bold;
        font-size: 14px;
        padding: 8px 16px;
        min-height: 24px;
    }
    QPushButton:hover {
        background-color: #45a049;
    }
    QPushButton:pressed {
        background-color: #3d8b40;
    }
    QPushButton:disabled {
        background-color: #cccccc;
        color: #666666;
    }
"""

# Secondary button style (blue - for actions like merge)
BUTTON_SECONDARY = """
    QPushButton {
        background-color: #2196F3;
        color: white;
        border: none;
        border-radius: 4px;
        font-weight: bold;
        font-size: 14px;
        padding: 8px 16px;
        min-height: 24px;
    }
    QPushButton:hover {
        background-color: #1976D2;
    }
    QPushButton:pressed {
        background-color: #0D47A1;
    }
    QPushButton:disabled {
        background-color: #cccccc;
        color: #666666;
    }
"""

# Toolbar button style (gray - for add, remove, clear, etc.)
BUTTON_TOOLBAR = """
    QPushButton {
        background-color: #f5f5f5;
        color: #333333;
        border: 1px solid #cccccc;
        border-radius: 4px;
        font-size: 13px;
        padding: 6px 12px;
        min-width: 70px;
    }
    QPushButton:hover {
        background-color: #e0e0e0;
        border-color: #999999;
    }
    QPushButton:pressed {
        background-color: #d5d5d5;
    }
    QPushButton:disabled {
        background-color: #f0f0f0;
        color: #999999;
        border-color: #dddddd;
    }
"""

# Group box style
GROUP_BOX = """
    QGroupBox {
        font-weight: bold;
        border: 1px solid #cccccc;
        border-radius: 6px;
        margin-top: 12px;
        padding-top: 12px;
        background-color: #fafafa;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 8px;
        color: #333333;
    }
"""

# Progress bar style
PROGRESS_BAR = """
    QProgressBar {
        border: 1px solid #cccccc;
        border-radius: 4px;
        text-align: center;
        background-color: #f5f5f5;
        height: 20px;
    }
    QProgressBar::chunk {
        background-color: #4CAF50;
        border-radius: 3px;
    }
"""

# Line edit style
LINE_EDIT = """
    QLineEdit {
        border: 1px solid #cccccc;
        border-radius: 4px;
        padding: 6px 10px;
        background-color: white;
    }
    QLineEdit:focus {
        border-color: #2196F3;
    }
    QLineEdit:disabled {
        background-color: #f5f5f5;
        color: #999999;
    }
"""

# Combo box style
COMBO_BOX = """
    QComboBox {
        border: 1px solid #cccccc;
        border-radius: 4px;
        padding: 6px 10px;
        background-color: white;
        min-width: 100px;
    }
    QComboBox:focus {
        border-color: #2196F3;
    }
    QComboBox::drop-down {
        border: none;
        width: 20px;
    }
    QComboBox::down-arrow {
        width: 12px;
        height: 12px;
    }
"""

# Check box style
CHECK_BOX = """
    QCheckBox {
        spacing: 8px;
    }
    QCheckBox::indicator {
        width: 18px;
        height: 18px;
        border: 1px solid #cccccc;
        border-radius: 3px;
        background-color: white;
    }
    QCheckBox::indicator:checked {
        background-color: #4CAF50;
        border-color: #4CAF50;
        image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMiIgaGVpZ2h0PSIxMiIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjMiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PHBvbHlsaW5lIHBvaW50cz0iMjAgNiA5IDE3IDQgMTIiPjwvcG9seWxpbmU+PC9zdmc+);
    }
    QCheckBox::indicator:hover {
        border-color: #999999;
    }
"""

# Radio button style
RADIO_BUTTON = """
    QRadioButton {
        spacing: 8px;
    }
    QRadioButton::indicator {
        width: 18px;
        height: 18px;
        border: 1px solid #cccccc;
        border-radius: 9px;
        background-color: white;
    }
    QRadioButton::indicator:checked {
        background-color: white;
        border: 5px solid #4CAF50;
    }
    QRadioButton::indicator:hover {
        border-color: #999999;
    }
"""

# List widget style
LIST_WIDGET = """
    QListWidget {
        border: 1px solid #cccccc;
        border-radius: 4px;
        background-color: white;
        alternate-background-color: #f9f9f9;
    }
    QListWidget::item {
        padding: 6px 10px;
        border-bottom: 1px solid #eeeeee;
    }
    QListWidget::item:selected {
        background-color: #e3f2fd;
        color: #333333;
    }
    QListWidget::item:hover {
        background-color: #f5f5f5;
    }
"""

# Scroll bar style
SCROLL_BAR = """
    QScrollBar:vertical {
        border: none;
        background-color: #f5f5f5;
        width: 10px;
        border-radius: 5px;
    }
    QScrollBar::handle:vertical {
        background-color: #cccccc;
        border-radius: 5px;
        min-height: 30px;
    }
    QScrollBar::handle:vertical:hover {
        background-color: #999999;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
"""

# Tab widget style
TAB_WIDGET = """
    QTabWidget::pane {
        border: 1px solid #cccccc;
        border-radius: 4px;
        background-color: white;
    }
    QTabBar::tab {
        background-color: #f5f5f5;
        border: 1px solid #cccccc;
        border-bottom: none;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
        padding: 8px 16px;
        margin-right: 2px;
    }
    QTabBar::tab:selected {
        background-color: white;
        border-bottom: 1px solid white;
    }
    QTabBar::tab:hover {
        background-color: #e0e0e0;
    }
"""

# Hint label style
HINT_LABEL = """
    color: #666666;
    font-size: 12px;
    font-style: italic;
"""

def apply_style(widget, style_name):
    """
    Apply a named style to a widget.
    
    Args:
        widget: The QWidget to apply the style to
        style_name: Name of the style (e.g., 'BUTTON_PRIMARY', 'GROUP_BOX')
    """
    style = globals().get(style_name)
    if style:
        widget.setStyleSheet(style)
    else:
        raise ValueError(f"Unknown style name: {style_name}")
