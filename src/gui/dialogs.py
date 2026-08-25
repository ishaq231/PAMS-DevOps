"""

23010646 - Hasaan Ahmad 
220367921 - Royden Dias

PAMS - Paragon Apartment Management System
Shared UI Components — reusable tables, dialogs, badges, and form helpers.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QDialog, QLineEdit, QComboBox, QTextEdit, QDateEdit,
    QMessageBox, QSpinBox, QDoubleSpinBox, QScrollArea,
    QFormLayout, QGraphicsDropShadowEffect, QSizePolicy,
    QAbstractItemView
)
from PyQt6.QtCore import Qt, QSize, QDate
from PyQt6.QtGui import QFont, QColor, QCursor, QIcon

try:
    from main_window import PAMSTheme
except ImportError:
    class PAMSTheme:
        BG_DARKEST = "#0F1923"; BG_DARK = "#15202E"; BG_SIDEBAR = "#1A2736"
        BG_CARD = "#1E2D3D"; BG_HOVER = "#253647"; BG_SURFACE = "#F0F4F8"
        BG_WHITE = "#FFFFFF"; ACCENT = "#00D4AA"; ACCENT_HOVER = "#00E8BB"
        ACCENT_DIM = "#00B894"; ACCENT_GLOW = "rgba(0, 212, 170, 0.15)"
        SUCCESS = "#2ECC71"; WARNING = "#F39C12"; DANGER = "#E74C3C"
        INFO = "#3498DB"; TEXT_PRIMARY = "#FFFFFF"; TEXT_SECONDARY = "#8899AA"
        TEXT_MUTED = "#7E92A5"; TEXT_DARK = "#1A2736"; TEXT_BODY = "#4A5568"
        BORDER_SUBTLE = "rgba(255, 255, 255, 0.06)"; BORDER_LIGHT = "#E2E8F0"
        SHADOW = "rgba(0, 0, 0, 0.25)"; FONT_FAMILY = "Segoe UI"
        CARD_RADIUS = 14; BTN_RADIUS = 10



# Reusable Styled Table

class PAMSTableWidget(QTableWidget):
    """A consistently styled table widget for all PAMS panels."""

    def __init__(self, headers: list[str], parent=None):
        super().__init__(parent)
        T = PAMSTheme
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.setSortingEnabled(True)

        self.setStyleSheet(f"""
            QTableWidget {{
                background-color: {T.BG_WHITE};
                border: 1px solid {T.BORDER_LIGHT};
                border-radius: 8px;
                gridline-color: {T.BORDER_LIGHT};
                font-size: 13px;
                color: {T.TEXT_DARK};
            }}
            QTableWidget::item {{
                padding: 8px 12px;
                border-bottom: 1px solid #F0F4F8;
            }}
            QTableWidget::item:selected {{
                background-color: {T.ACCENT_GLOW};
                color: {T.TEXT_DARK};
            }}
            QTableWidget::item:alternate {{
                background-color: #FAFCFE;
            }}
            QHeaderView::section {{
                background-color: {T.BG_SURFACE};
                color: {T.TEXT_BODY};
                font-weight: 600;
                font-size: 11px;
                padding: 10px 12px;
                border: none;
                border-bottom: 2px solid {T.BORDER_LIGHT};
            }}
        """)

    def populate(self, rows: list[list[str]]):
        """Fill the table with rows of string data."""
        self.setRowCount(0)
        for row_data in rows:
            row_idx = self.rowCount()
            self.insertRow(row_idx)
            for col_idx, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                self.setItem(row_idx, col_idx, item)
        self.resizeRowsToContents()


# Status Badge

class StatusBadge(QLabel):
    """A small coloured badge for status indicators."""

    STATUS_COLORS = {
        # Title-case (display values)
        "Active": PAMSTheme.SUCCESS, "Paid": PAMSTheme.SUCCESS,
        "Resolved": PAMSTheme.SUCCESS, "Available": PAMSTheme.SUCCESS,
        "Pending": PAMSTheme.WARNING, "In Progress": PAMSTheme.WARNING,
        "InProgress": PAMSTheme.WARNING, "Expiring Soon": PAMSTheme.WARNING,
        "Open": PAMSTheme.INFO, "Under Review": PAMSTheme.WARNING,
        "Occupied": PAMSTheme.INFO, "Overdue": PAMSTheme.DANGER,
        "Urgent": PAMSTheme.DANGER, "Under Maintenance": PAMSTheme.DANGER,
        "Inactive": PAMSTheme.DANGER, "Expired": PAMSTheme.DANGER,
        "Terminated": PAMSTheme.DANGER,
        "High": PAMSTheme.DANGER, "Medium": PAMSTheme.WARNING,
        "Low": PAMSTheme.INFO,
        # Uppercase DB enum values
        "ACTIVE": PAMSTheme.SUCCESS, "PAID": PAMSTheme.SUCCESS,
        "PENDING": PAMSTheme.WARNING, "OVERDUE": PAMSTheme.DANGER,
        "EXPIRED": PAMSTheme.DANGER, "TERMINATED": PAMSTheme.DANGER,
    }

    def __init__(self, status: str, parent=None):
        super().__init__(status, parent)
        color = self.STATUS_COLORS.get(status, PAMSTheme.TEXT_MUTED)
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {color}22;
                color: {color};
                font-size: 11px;
                font-weight: 600;
                padding: 4px 10px;
                border-radius: 10px;
                border: 1px solid {color}44;
            }}
        """)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedHeight(24)


# Action Button Factory

def make_action_button(text: str, color: str = PAMSTheme.ACCENT,
                       icon_text: str = "", width: int = 0) -> QPushButton:
    """Create a styled action button for panel toolbars."""
    T = PAMSTheme
    btn = QPushButton(f"{icon_text}  {text}" if icon_text else text)
    btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
    btn.setFixedHeight(36)
    if width:
        btn.setFixedWidth(width)
    btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {color};
            color: white;
            border: none;
            border-radius: {T.BTN_RADIUS}px;
            padding: 0 18px;
            font-size: 13px;
            font-weight: 600;
        }}
        QPushButton:hover {{
            background-color: {color}DD;
        }}
        QPushButton:pressed {{
            background-color: {color}BB;
        }}
    """)
    return btn


def make_outline_button(text: str, color: str = PAMSTheme.ACCENT) -> QPushButton:
    """Create a styled outline button."""
    T = PAMSTheme
    btn = QPushButton(text)
    btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
    btn.setFixedHeight(36)
    btn.setStyleSheet(f"""
        QPushButton {{
            background-color: transparent;
            color: {color};
            border: 1.5px solid {color};
            border-radius: {T.BTN_RADIUS}px;
            padding: 0 18px;
            font-size: 13px;
            font-weight: 500;
        }}
        QPushButton:hover {{
            background-color: {color}15;
        }}
    """)
    return btn


# Panel Header Builder

def make_panel_header(title: str, subtitle: str = "") -> QWidget:
    """Create a consistent panel header with title and subtitle."""
    T = PAMSTheme
    header = QWidget()
    header.setStyleSheet("background: transparent;")
    layout = QVBoxLayout(header)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(4)

    lbl_title = QLabel(title)
    lbl_title.setStyleSheet(f"""
        color: {T.ACCENT};
        font-size: 22px;
        font-weight: 700;
        background: transparent;
    """)
    layout.addWidget(lbl_title)

    if subtitle:
        lbl_sub = QLabel(subtitle)
        lbl_sub.setStyleSheet(f"""
            color: {T.TEXT_SECONDARY};
            font-size: 13px;
            background: transparent;
        """)
        layout.addWidget(lbl_sub)

    return header


# Section Card Wrapper

class SectionCard(QFrame):
    """A white card container for grouping related content."""

    def __init__(self, parent=None):
        super().__init__(parent)
        T = PAMSTheme
        self.setStyleSheet(f"""
            SectionCard {{
                background-color: {T.BG_WHITE};
                border: 1px solid {T.BORDER_LIGHT};
                border-radius: 10px;
            }}
        """)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(12)
        shadow.setOffset(0, 2)
        shadow.setColor(QColor(0, 0, 0, 12))
        self.setGraphicsEffect(shadow)


# Generic Form Dialog

class PAMSFormDialog(QDialog):
    """
    A generic form dialog that accepts a list of field definitions and
    builds a styled form.  Field spec:
        {"key": "fname", "label": "First Name", "type": "text", "value": ""}
        {"key": "role", "label": "Role", "type": "combo",
         "options": ["Admin", "Tenant"], "value": "Tenant"}
        {"key": "notes", "label": "Notes", "type": "textarea", "value": ""}
        {"key": "date", "label": "Date", "type": "date", "value": "2026-01-01"}
        {"key": "amount", "label": "Amount (£)", "type": "double", "value": 0.0}
        {"key": "count", "label": "Count", "type": "int", "value": 0}
    """

    def __init__(self, title: str, fields: list[dict], parent=None):
        super().__init__(parent)
        T = PAMSTheme
        self.setWindowTitle(title)
        self.setMinimumWidth(480)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {T.BG_SURFACE};
            }}
        """)

        self._fields = fields
        self._widgets: dict[str, QWidget] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 20)
        layout.setSpacing(16)

        # Title
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet(f"""
            color: {T.ACCENT};
            font-size: 18px;
            font-weight: 700;
        """)
        layout.addWidget(lbl_title)

        # Scrollable form
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")

        form_container = QWidget()
        form_container.setStyleSheet("background: transparent;")
        form_layout = QFormLayout(form_container)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(12)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        input_style = f"""
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit {{
                background-color: {T.BG_WHITE};
                border: 1.5px solid {T.BORDER_LIGHT};
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
                color: {T.TEXT_DARK};
                min-height: 22px;
            }}
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus,
            QDoubleSpinBox:focus, QDateEdit:focus {{
                border: 1.5px solid {T.ACCENT};
            }}
            QTextEdit {{
                background-color: {T.BG_WHITE};
                border: 1.5px solid {T.BORDER_LIGHT};
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
                color: {T.TEXT_DARK};
            }}
            QTextEdit:focus {{
                border: 1.5px solid {T.ACCENT};
            }}
            QComboBox::drop-down {{
                border: none;
                padding-right: 8px;
            }}
        """
        form_container.setStyleSheet(input_style)

        label_style = f"color: {T.TEXT_DARK}; font-size: 13px; font-weight: 600;"

        for field in fields:
            label = QLabel(field["label"])
            label.setStyleSheet(label_style)

            ftype = field.get("type", "text")
            widget = None

            if ftype == "text":
                widget = QLineEdit()
                widget.setText(str(field.get("value", "")))
                widget.setPlaceholderText(field.get("placeholder", ""))
            elif ftype == "password":
                widget = QLineEdit()
                widget.setEchoMode(QLineEdit.EchoMode.Password)
                widget.setPlaceholderText(field.get("placeholder", ""))
            elif ftype == "combo":
                widget = QComboBox()
                options = field.get("options", [])
                widget.addItems([str(opt) for opt in options])
                val = field.get("value", "")
                idx = widget.findText(str(val))
                if idx >= 0:
                    widget.setCurrentIndex(idx)
            elif ftype == "textarea":
                widget = QTextEdit()
                widget.setPlainText(str(field.get("value", "")))
                widget.setMaximumHeight(100)
            elif ftype == "date":
                widget = QDateEdit()
                widget.setCalendarPopup(True)
                val = field.get("value", "")
                if val:
                    widget.setDate(QDate.fromString(str(val), "yyyy-MM-dd"))
                else:
                    widget.setDate(QDate.currentDate())
            elif ftype == "double":
                widget = QDoubleSpinBox()
                widget.setMaximum(999999.99)
                widget.setDecimals(2)
                widget.setPrefix("£")
                widget.setValue(float(field.get("value", 0)))
            elif ftype == "int":
                widget = QSpinBox()
                widget.setMaximum(999999)
                widget.setValue(int(field.get("value", 0)))
            elif ftype == "readonly":
                widget = QLineEdit()
                widget.setText(str(field.get("value", "")))
                widget.setReadOnly(True)
                widget.setStyleSheet(widget.styleSheet() + "background-color: #E8ECF0;")
            else:
                widget = QLineEdit()
                widget.setText(str(field.get("value", "")))

            if widget:
                self._widgets[field["key"]] = widget
                form_layout.addRow(label, widget)

        scroll.setWidget(form_container)
        layout.addWidget(scroll)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        cancel_btn = make_outline_button("Cancel", T.TEXT_BODY)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        save_btn = make_action_button("Save", T.ACCENT)
        save_btn.clicked.connect(self.accept)
        btn_row.addWidget(save_btn)

        layout.addLayout(btn_row)

    def get_values(self) -> dict:
        """Return a dict of key → value from all form fields."""
        result = {}
        for key, widget in self._widgets.items():
            if isinstance(widget, QLineEdit):
                result[key] = widget.text().strip()
            elif isinstance(widget, QComboBox):
                result[key] = widget.currentText()
            elif isinstance(widget, QTextEdit):
                result[key] = widget.toPlainText().strip()
            elif isinstance(widget, QDateEdit):
                result[key] = widget.date().toString("yyyy-MM-dd")
            elif isinstance(widget, QDoubleSpinBox):
                result[key] = widget.value()
            elif isinstance(widget, QSpinBox):
                result[key] = widget.value()
        return result


# Detail View Dialog

class PAMSDetailDialog(QDialog):
    """A read-only detail dialog showing key–value pairs."""

    def __init__(self, title: str, details: list[tuple[str, str]], parent=None):
        super().__init__(parent)
        T = PAMSTheme
        self.setWindowTitle(title)
        self.setMinimumWidth(500)
        self.setStyleSheet(f"QDialog {{ background-color: {T.BG_SURFACE}; }}")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 20)
        layout.setSpacing(16)

        lbl_title = QLabel(title)
        lbl_title.setStyleSheet(f"""
            color: {T.ACCENT}; font-size: 18px; font-weight: 700;
        """)
        layout.addWidget(lbl_title)

        card = SectionCard()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 16, 20, 16)
        card_layout.setSpacing(10)

        for label_text, value_text in details:
            row = QHBoxLayout()
            lbl = QLabel(label_text)
            lbl.setStyleSheet(f"color: {T.TEXT_BODY}; font-size: 12px; font-weight: 600;")
            lbl.setFixedWidth(180)
            val = QLabel(str(value_text))
            val.setStyleSheet(f"color: {T.TEXT_DARK}; font-size: 13px;")
            val.setWordWrap(True)
            row.addWidget(lbl)
            row.addWidget(val, 1)
            card_layout.addLayout(row)

        layout.addWidget(card)

        close_btn = make_action_button("Close", T.ACCENT)
        close_btn.clicked.connect(self.accept)
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)


# Confirmation Dialog

def _show_styled_message(parent, title: str, message: str,
                         color: str, btn_text: str = "OK"):
    """Internal: show a custom styled message dialog with readable colours."""
    T = PAMSTheme
    dlg = QDialog(parent)
    dlg.setWindowTitle(title)
    dlg.setMinimumWidth(420)
    dlg.setStyleSheet(f"QDialog {{ background-color: {T.BG_SURFACE}; }}")

    layout = QVBoxLayout(dlg)
    layout.setContentsMargins(28, 24, 28, 20)
    layout.setSpacing(16)

    lbl_title = QLabel(title)
    lbl_title.setStyleSheet(f"color: {color}; font-size: 18px; font-weight: 700;")
    layout.addWidget(lbl_title)

    lbl_msg = QLabel(message)
    lbl_msg.setWordWrap(True)
    lbl_msg.setStyleSheet(f"color: {T.TEXT_DARK}; font-size: 14px;")
    layout.addWidget(lbl_msg)

    btn = QPushButton(btn_text)
    btn.setFixedHeight(36)
    btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
    btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {color};
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0 24px;
            font-size: 13px;
            font-weight: 600;
        }}
        QPushButton:hover {{ background-color: {color}DD; }}
    """)
    btn.clicked.connect(dlg.accept)
    btn_row = QHBoxLayout()
    btn_row.addStretch()
    btn_row.addWidget(btn)
    layout.addLayout(btn_row)

    dlg.exec()


def confirm_action(parent, title: str, message: str) -> bool:
    """Show a styled yes/no confirmation dialog."""
    T = PAMSTheme
    dlg = QDialog(parent)
    dlg.setWindowTitle(title)
    dlg.setMinimumWidth(440)
    dlg.setStyleSheet(f"QDialog {{ background-color: {T.BG_SURFACE}; }}")

    layout = QVBoxLayout(dlg)
    layout.setContentsMargins(28, 24, 28, 20)
    layout.setSpacing(16)

    lbl_title = QLabel(title)
    lbl_title.setStyleSheet(f"color: {T.WARNING}; font-size: 18px; font-weight: 700;")
    layout.addWidget(lbl_title)

    lbl_msg = QLabel(message)
    lbl_msg.setWordWrap(True)
    lbl_msg.setStyleSheet(f"color: {T.TEXT_DARK}; font-size: 14px;")
    layout.addWidget(lbl_msg)

    btn_row = QHBoxLayout()
    btn_row.addStretch()

    no_btn = QPushButton("No")
    no_btn.setFixedHeight(36)
    no_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
    no_btn.setStyleSheet(f"""
        QPushButton {{
            background-color: transparent;
            color: {T.TEXT_BODY};
            border: 1.5px solid {T.BORDER_LIGHT};
            border-radius: 8px;
            padding: 0 24px;
            font-size: 13px;
            font-weight: 500;
        }}
        QPushButton:hover {{ background-color: {T.BG_WHITE}; }}
    """)
    no_btn.clicked.connect(dlg.reject)

    yes_btn = QPushButton("Yes")
    yes_btn.setFixedHeight(36)
    yes_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
    yes_btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {T.ACCENT};
            color: {T.BG_DARKEST};
            border: none;
            border-radius: 8px;
            padding: 0 24px;
            font-size: 13px;
            font-weight: 600;
        }}
        QPushButton:hover {{ background-color: {T.ACCENT_HOVER}; }}
    """)
    yes_btn.clicked.connect(dlg.accept)

    btn_row.addWidget(no_btn)
    btn_row.addSpacing(8)
    btn_row.addWidget(yes_btn)
    layout.addLayout(btn_row)

    return dlg.exec() == QDialog.DialogCode.Accepted


def show_success(parent, message: str):
    """Show a styled success dialog."""
    _show_styled_message(parent, "Success", message, PAMSTheme.SUCCESS)


def show_error(parent, message: str):
    """Show a styled error dialog."""
    _show_styled_message(parent, "Error", message, PAMSTheme.DANGER)


# Base Panel Class

class BasePanel(QWidget):
    """Base class for all PAMS panels with scroll area and consistent styling."""

    def __init__(self, parent=None):
        super().__init__(parent)
        T = PAMSTheme
        self.setStyleSheet(f"background-color: {T.BG_SURFACE};")

        self._scroll = QScrollArea(self)
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll.setStyleSheet("background: transparent; border: none;")

        self._container = QWidget()
        self._container.setStyleSheet("background: transparent;")
        self._main_layout = QVBoxLayout(self._container)
        self._main_layout.setContentsMargins(32, 28, 32, 28)
        self._main_layout.setSpacing(20)

        self._scroll.setWidget(self._container)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self._scroll)
