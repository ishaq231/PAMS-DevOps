"""

23010646 - Hasaan Ahmad 
220367921 - Royden Dias

PAMS - Paragon Apartment Management System
Signup Window — split-panel design with branding + registration form
Matches the login_window.py colour scheme and layout conventions.
"""

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QComboBox, QFrame,
    QGraphicsDropShadowEffect, QScrollArea, QSizePolicy, QSpacerItem,
    QDateEdit
)
from PyQt6.QtCore import (
    Qt, QSize, pyqtSignal, QTimer, QPropertyAnimation,
    QEasingCurve, QPoint, QRect, QDate
)
from PyQt6.QtGui import (
    QFont, QIcon, QPainter, QColor, QPen, QBrush,
    QLinearGradient, QPainterPath, QPixmap, QCursor, QPaintEvent
)

# Import shared design tokens
try:
    from main_window import PAMSTheme
except ImportError:
    try:
        from login_window import PAMSTheme
    except ImportError:
        class PAMSTheme:
            BG_DARKEST    = "#0F1923"
            BG_DARK       = "#15202E"
            BG_SIDEBAR    = "#1A2736"
            BG_CARD       = "#1E2D3D"
            BG_HOVER      = "#253647"
            BG_SURFACE    = "#F0F4F8"
            BG_WHITE      = "#FFFFFF"
            ACCENT        = "#00D4AA"
            ACCENT_HOVER  = "#00E8BB"
            ACCENT_DIM    = "#00B894"
            ACCENT_GLOW   = "rgba(0, 212, 170, 0.15)"
            SUCCESS       = "#2ECC71"
            WARNING       = "#F39C12"
            DANGER        = "#E74C3C"
            INFO          = "#3498DB"
            TEXT_PRIMARY   = "#FFFFFF"
            TEXT_SECONDARY = "#8899AA"
            TEXT_MUTED     = "#7E92A5"
            TEXT_DARK      = "#1A2736"
            TEXT_BODY      = "#4A5568"
            BORDER_SUBTLE  = "rgba(255, 255, 255, 0.06)"
            BORDER_LIGHT   = "#E2E8F0"
            SHADOW         = "rgba(0, 0, 0, 0.25)"
            FONT_FAMILY    = "Segoe UI"
            CARD_RADIUS    = 14
            BTN_RADIUS     = 10
            @classmethod
            def global_stylesheet(cls):
                return f'* {{ font-family: "{cls.FONT_FAMILY}"; }}'


# Decorative cityscape (reused from login_window)

class CityscapeWidget(QWidget):
    """Draws a subtle geometric cityscape silhouette at the bottom
    of the branding panel to reinforce the apartment/property theme."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(120)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def paintEvent(self, event: QPaintEvent):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        building_color = QColor(255, 255, 255, 18)
        window_color   = QColor(0, 212, 170, 40)

        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(building_color))

        buildings = [
            (0.02, 0.08, 0.70), (0.08, 0.06, 0.50), (0.13, 0.10, 0.85),
            (0.22, 0.07, 0.55), (0.28, 0.09, 0.75), (0.36, 0.06, 0.45),
            (0.41, 0.11, 0.90), (0.50, 0.07, 0.60), (0.56, 0.08, 0.70),
            (0.63, 0.10, 0.80), (0.72, 0.06, 0.50), (0.77, 0.09, 0.65),
            (0.85, 0.07, 0.75), (0.91, 0.08, 0.55),
        ]

        for xf, wf, hf in buildings:
            bx = int(w * xf)
            bw = int(w * wf)
            bh = int(h * hf)
            by = h - bh
            p.drawRect(bx, by, bw, bh)

            p.setBrush(QBrush(window_color))
            win_w, win_h = 3, 3
            cols = max(1, bw // 8)
            rows = max(1, bh // 12)
            for row in range(rows):
                for col in range(cols):
                    wx = bx + 4 + col * 8
                    wy = by + 6 + row * 10
                    if wx + win_w < bx + bw - 2 and wy + win_h < h - 4:
                        p.drawRect(wx, wy, win_w, win_h)
            p.setBrush(QBrush(building_color))

        p.end()


# Styled input field

class PAMSInput(QWidget):
    """A labelled text input with consistent PAMS styling."""

    def __init__(self, label: str, placeholder: str = "",
                 is_password: bool = False, parent=None):
        super().__init__(parent)
        T = PAMSTheme
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self._label = QLabel(label)
        self._label.setStyleSheet(f"""
            color: {T.TEXT_DARK};
            font-size: 13px;
            font-weight: 600;
        """)
        layout.addWidget(self._label)

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)

        self._input = QLineEdit()
        self._input.setPlaceholderText(placeholder)
        if is_password:
            self._input.setEchoMode(QLineEdit.EchoMode.Password)
        self._input.setFixedHeight(44)
        self._input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {T.BG_SURFACE};
                border: 1.5px solid {T.BORDER_LIGHT};
                border-radius: 8px;
                padding: 0 14px;
                font-size: 14px;
                color: {T.TEXT_DARK};
            }}
            QLineEdit:focus {{
                border: 1.5px solid {T.ACCENT};
                background-color: {T.BG_WHITE};
            }}
            QLineEdit::placeholder {{
                color: {T.TEXT_MUTED};
            }}
        """)
        row.addWidget(self._input)

        if is_password:
            self._toggle_btn = QPushButton("Show")
            self._toggle_btn.setFixedSize(44, 44)
            self._toggle_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            self._toggle_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {T.BG_SURFACE};
                    border: 1.5px solid {T.BORDER_LIGHT};
                    border-left: none;
                    border-top-right-radius: 8px;
                    border-bottom-right-radius: 8px;
                    font-size: 16px;
                    color: {T.TEXT_MUTED};
                }}
                QPushButton:hover {{
                    background-color: #E2E8F0;
                }}
            """)
            self._toggle_btn.clicked.connect(self._toggle_visibility)
            self._input.setStyleSheet(self._input.styleSheet().replace(
                "border-radius: 8px;",
                "border-top-left-radius: 8px; border-bottom-left-radius: 8px; "
                "border-top-right-radius: 0px; border-bottom-right-radius: 0px;"
            ))
            row.addWidget(self._toggle_btn)
            self._visible = False

        layout.addLayout(row)

    def _toggle_visibility(self):
        self._visible = not self._visible
        if self._visible:
            self._input.setEchoMode(QLineEdit.EchoMode.Normal)
            self._toggle_btn.setText("Hide")
        else:
            self._input.setEchoMode(QLineEdit.EchoMode.Password)
            self._toggle_btn.setText("Show")

    def text(self) -> str:
        return self._input.text().strip()

    def set_error(self, error: bool):
        T = PAMSTheme
        if error:
            self._input.setStyleSheet(self._input.styleSheet().replace(
                f"border: 1.5px solid {T.BORDER_LIGHT}",
                f"border: 1.5px solid {T.DANGER}"
            ))
        else:
            self._input.setStyleSheet(self._input.styleSheet().replace(
                f"border: 1.5px solid {T.DANGER}",
                f"border: 1.5px solid {T.BORDER_LIGHT}"
            ))

    @property
    def input_field(self) -> QLineEdit:
        return self._input


# Signup Window

class SignupWindow(QMainWindow):
    """
    Split-panel registration screen.
    Left:  dark branding panel with logo, tagline, and cityscape.
    Right: scrollable registration form matching the PAMS colour scheme.

    Emits `signup_success()` when a new user registers successfully.
    Emits `switch_to_login()` when the user clicks 'Back to Login'.
    """

    signup_success  = pyqtSignal()
    switch_to_login = pyqtSignal()

    ROLES = ["Tenant", "Staff"]
    # Staff codes are now stored in the staff_role DB table — no hardcoded code here

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_window()
        self._build_ui()

    # window chrome

    def _setup_window(self):
        self.setWindowTitle("PAMS — Create Account")
        self.setFixedSize(1020, 680)
        try:
            self.setStyleSheet(PAMSTheme.global_stylesheet())
        except Exception:
            # Keep window functional even if theme setup fails in CI/headless mode.
            pass

        try:
            screen = QApplication.primaryScreen()
            if screen:
                geo = screen.availableGeometry()
                self.move(
                    (geo.width()  - self.width())  // 2,
                    (geo.height() - self.height()) // 2,
                )
        except Exception:
            pass

    # UI construction

    def _build_ui(self):
        T = PAMSTheme
        central = QWidget()
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # LEFT — Dark branding panel
        left = QFrame()
        left.setFixedWidth(380)
        left.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0.3, y2:1,
                    stop:0 {T.BG_DARKEST}, stop:1 {T.BG_SIDEBAR});
            }}
        """)

        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(40, 48, 40, 0)
        left_layout.setSpacing(0)

        # Logo mark
        logo = QLabel("P")
        logo.setFixedSize(56, 56)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {T.ACCENT}, stop:1 {T.ACCENT_DIM});
            color: {T.BG_DARKEST};
            font-size: 28px;
            font-weight: 800;
            border-radius: 14px;
        """)
        left_layout.addWidget(logo)
        left_layout.addSpacing(24)

        # Title
        title = QLabel("PARAGON")
        title.setStyleSheet(f"""
            color: {T.TEXT_PRIMARY};
            font-size: 28px;
            font-weight: 700;
            letter-spacing: 3px;
        """)
        left_layout.addWidget(title)

        subtitle = QLabel("Apartment Management System")
        subtitle.setStyleSheet(f"""
            color: {T.TEXT_SECONDARY};
            font-size: 14px;
            letter-spacing: 0.5px;
        """)
        left_layout.addWidget(subtitle)
        left_layout.addSpacing(36)

        # Divider accent line
        accent_line = QFrame()
        accent_line.setFixedSize(48, 3)
        accent_line.setStyleSheet(
            f"background-color: {T.ACCENT}; border-radius: 1px;"
        )
        left_layout.addWidget(accent_line)
        left_layout.addSpacing(24)

        # Tagline
        tagline = QLabel(
            "Create your account to start\n"
            "managing your apartment\n"
            "experience with Paragon."
        )
        tagline.setStyleSheet(f"""
            color: {T.TEXT_MUTED};
            font-size: 14px;
            line-height: 1.6;
        """)
        tagline.setWordWrap(True)
        left_layout.addWidget(tagline)
        left_layout.addSpacing(32)

        # Feature bullets
        features = [
            "Quick & secure registration",
            "Role-based access control",
            "Start managing in minutes",
        ]
        for text in features:
            feat = QLabel(text)
            feat.setStyleSheet(f"""
                color: {T.TEXT_SECONDARY};
                font-size: 12px;
                padding: 3px 0px;
            """)
            left_layout.addWidget(feat)

        left_layout.addStretch()

        # Cityscape decoration
        cityscape = CityscapeWidget()
        left_layout.addWidget(cityscape)

        # Version footer
        version = QLabel("v1.0.0  ·  2025–26 Academic Project")
        version.setStyleSheet(f"""
            color: {T.TEXT_MUTED};
            font-size: 10px;
            padding-bottom: 16px;
        """)
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(version)

        root.addWidget(left)

        # RIGHT — Sign-up form panel
        right = QFrame()
        right.setStyleSheet(f"background-color: {T.BG_WHITE};")

        # Scrollable form so it works on smaller screens
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                background-color: {T.BG_WHITE};
                border: none;
            }}
            QScrollBar:vertical {{
                width: 6px;
                background: transparent;
            }}
            QScrollBar::handle:vertical {{
                background: {T.BORDER_LIGHT};
                border-radius: 3px;
                min-height: 30px;
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)

        form_container = QWidget()
        form_container.setStyleSheet(f"background-color: {T.BG_WHITE};")
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(50, 36, 50, 36)
        form_layout.setSpacing(0)

        # Form header
        form_title = QLabel("Create Account")
        form_title.setStyleSheet(f"""
            color: {T.TEXT_DARK};
            font-size: 26px;
            font-weight: 700;
        """)
        form_layout.addWidget(form_title)
        form_layout.addSpacing(6)

        form_sub = QLabel("Fill in your details to register")
        form_sub.setStyleSheet(f"""
            color: {T.TEXT_BODY};
            font-size: 14px;
        """)
        form_layout.addWidget(form_sub)
        form_layout.addSpacing(28)

        # Name row (first + last side-by-side)
        name_row = QHBoxLayout()
        name_row.setSpacing(16)

        self._fname_field = PAMSInput("First Name", "John")
        self._lname_field = PAMSInput("Last Name", "Doe")
        name_row.addWidget(self._fname_field)
        name_row.addWidget(self._lname_field)
        form_layout.addLayout(name_row)
        form_layout.addSpacing(14)

        # Email
        self._email_field = PAMSInput("Email Address", "you@example.com")
        form_layout.addWidget(self._email_field)
        form_layout.addSpacing(14)

        # Phone number
        self._phone_field = PAMSInput("Phone Number", "+44 7XXX XXXXXX")
        form_layout.addWidget(self._phone_field)
        form_layout.addSpacing(14)

        # Date of Birth
        dob_label = QLabel("Date of Birth")
        dob_label.setStyleSheet(f"""
            color: {T.TEXT_DARK};
            font-size: 13px;
            font-weight: 600;
        """)
        form_layout.addWidget(dob_label)
        form_layout.addSpacing(6)

        self._dob_edit = QDateEdit()
        self._dob_edit.setCalendarPopup(True)
        self._dob_edit.setDisplayFormat("dd/MM/yyyy")
        self._dob_edit.setDate(QDate(2000, 1, 1))
        self._dob_edit.setMaximumDate(QDate.currentDate())
        self._dob_edit.setFixedHeight(44)
        self._dob_edit.setStyleSheet(f"""
            QDateEdit {{
                background-color: {T.BG_SURFACE};
                border: 1.5px solid {T.BORDER_LIGHT};
                border-radius: 8px;
                padding: 0 14px;
                font-size: 14px;
                color: {T.TEXT_DARK};
            }}
            QDateEdit:focus {{
                border: 1.5px solid {T.ACCENT};
                background-color: {T.BG_WHITE};
            }}
            QDateEdit::drop-down {{
                border: none;
                width: 32px;
            }}
            QDateEdit::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {T.TEXT_MUTED};
                margin-right: 10px;
            }}
        """)
        form_layout.addWidget(self._dob_edit)
        form_layout.addSpacing(14)

        # Role dropdown
        role_label = QLabel("Role")
        role_label.setStyleSheet(f"""
            color: {T.TEXT_DARK};
            font-size: 13px;
            font-weight: 600;
        """)
        form_layout.addWidget(role_label)
        form_layout.addSpacing(6)

        self._role_combo = QComboBox()
        self._role_combo.addItems(self.ROLES)
        self._role_combo.setFixedHeight(44)
        self._role_combo.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._role_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {T.BG_SURFACE};
                border: 1.5px solid {T.BORDER_LIGHT};
                border-radius: 8px;
                padding: 0 14px;
                font-size: 14px;
                color: {T.TEXT_DARK};
            }}
            QComboBox:focus {{
                border: 1.5px solid {T.ACCENT};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 32px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {T.TEXT_MUTED};
                margin-right: 10px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {T.BG_WHITE};
                border: 1px solid {T.BORDER_LIGHT};
                border-radius: 6px;
                padding: 4px;
                selection-background-color: {T.ACCENT_GLOW};
                selection-color: {T.TEXT_DARK};
                outline: none;
            }}
            QComboBox QAbstractItemView::item {{
                padding: 8px 12px;
                min-height: 32px;
            }}
        """)
        form_layout.addWidget(self._role_combo)
        self._role_combo.currentTextChanged.connect(self._on_role_changed)
        form_layout.addSpacing(14)

        # Staff fields (hidden by default, shown when Staff is selected)
        self._staff_code_container = QWidget()
        staff_code_layout = QVBoxLayout(self._staff_code_container)
        staff_code_layout.setContentsMargins(0, 0, 0, 0)
        staff_code_layout.setSpacing(6)

        self._staff_code_field = PAMSInput("Staff Code", "Enter your staff authorisation code")

        staff_info = QLabel("A unique code is required to register as staff.")
        staff_info.setStyleSheet(f"""
            color: {T.WARNING};
            font-size: 11px;
            font-style: italic;
            padding: 2px 0;
        """)

        staff_code_layout.addWidget(self._staff_code_field)
        staff_code_layout.addWidget(staff_info)

        self._staff_code_container.setVisible(False)
        form_layout.addWidget(self._staff_code_container)
        form_layout.addSpacing(14)

        # Location dropdown (shown only for Tenant signup)
        self._location_container = QWidget()
        loc_layout = QVBoxLayout(self._location_container)
        loc_layout.setContentsMargins(0, 0, 0, 0)
        loc_layout.setSpacing(6)

        loc_label = QLabel("Preferred Location")
        loc_label.setStyleSheet(f"""
            color: {T.TEXT_DARK};
            font-size: 13px;
            font-weight: 600;
        """)
        loc_layout.addWidget(loc_label)

        self._location_combo = QComboBox()
        self._location_combo.setFixedHeight(44)
        self._location_combo.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._location_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {T.BG_SURFACE};
                border: 1.5px solid {T.BORDER_LIGHT};
                border-radius: 8px;
                padding: 0 14px;
                font-size: 14px;
                color: {T.TEXT_DARK};
            }}
            QComboBox:focus {{
                border: 1.5px solid {T.ACCENT};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 32px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {T.TEXT_MUTED};
                margin-right: 10px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {T.BG_WHITE};
                border: 1px solid {T.BORDER_LIGHT};
                border-radius: 6px;
                padding: 4px;
                selection-background-color: {T.ACCENT_GLOW};
                selection-color: {T.TEXT_DARK};
                outline: none;
            }}
            QComboBox QAbstractItemView::item {{
                padding: 8px 12px;
                min-height: 32px;
            }}
        """)
        self._populate_locations()
        loc_layout.addWidget(self._location_combo)

        self._location_container.setVisible(True)  # Visible by default (Tenant is default role)
        form_layout.addWidget(self._location_container)
        form_layout.addSpacing(14)

        # Username
        self._username_field = PAMSInput("Username", "Choose a username")
        form_layout.addWidget(self._username_field)
        form_layout.addSpacing(14)

        # Password + Confirm
        self._password_field = PAMSInput(
            "Password", "Min 8 characters", is_password=True
        )
        form_layout.addWidget(self._password_field)
        form_layout.addSpacing(14)

        self._confirm_password_field = PAMSInput(
            "Confirm Password", "Re-enter your password", is_password=True
        )
        form_layout.addWidget(self._confirm_password_field)
        form_layout.addSpacing(20)

        # Error / success message (hidden by default)
        self._message_label = QLabel("")
        self._message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._message_label.setVisible(False)
        form_layout.addWidget(self._message_label)
        form_layout.addSpacing(8)

        # Sign Up button
        self._signup_btn = QPushButton("Create Account")
        self._signup_btn.setFixedHeight(48)
        self._signup_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._signup_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {T.ACCENT}, stop:1 {T.ACCENT_DIM});
                color: {T.BG_DARKEST};
                border: none;
                border-radius: 10px;
                font-size: 15px;
                font-weight: 700;
                letter-spacing: 0.5px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {T.ACCENT_HOVER}, stop:1 {T.ACCENT});
            }}
            QPushButton:pressed {{
                background-color: {T.ACCENT_DIM};
            }}
            QPushButton:disabled {{
                background-color: {T.BORDER_LIGHT};
                color: {T.TEXT_MUTED};
            }}
        """)
        self._signup_btn.clicked.connect(self._on_signup_clicked)
        form_layout.addWidget(self._signup_btn)
        form_layout.addSpacing(20)

        # Back to login link
        login_row = QHBoxLayout()
        login_row.setAlignment(Qt.AlignmentFlag.AlignCenter)

        already_label = QLabel("Already have an account?")
        already_label.setStyleSheet(f"""
            color: {T.TEXT_BODY};
            font-size: 13px;
        """)
        login_row.addWidget(already_label)

        login_link = QPushButton("Sign In")
        login_link.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        login_link.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                color: {T.ACCENT};
                font-size: 13px;
                font-weight: 700;
                padding: 0 4px;
            }}
            QPushButton:hover {{
                color: {T.ACCENT_HOVER};
                text-decoration: underline;
            }}
        """)
        login_link.clicked.connect(self._on_switch_to_login)
        login_row.addWidget(login_link)

        form_layout.addLayout(login_row)
        form_layout.addStretch()

        scroll.setWidget(form_container)

        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.addWidget(scroll)

        root.addWidget(right)

        # Enter key triggers signup from any field
        for field in (
            self._fname_field, self._lname_field, self._email_field,
            self._phone_field, self._staff_code_field, self._username_field,
            self._password_field, self._confirm_password_field,
        ):
            field.input_field.returnPressed.connect(self._on_signup_clicked)

        # Focus first name on open
        QTimer.singleShot(100, self._fname_field.input_field.setFocus)

    # Role change handler

    def _populate_locations(self):
        """Load locations from the database and populate the combo box."""
        self._location_combo.clear()
        locations = []
        try:
            import os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'database'))
            from models import get_all_locations
            rows = get_all_locations()
            locations = [row["city"] for row in rows if row.get("city")]
        except Exception as e:
            print(f"[SignupWindow] Could not load locations from DB: {e}")
        if not locations:
            locations = ["Bristol", "Cardiff", "London", "Manchester"]
        self._location_combo.addItems(locations)

    def _on_role_changed(self, role: str):
        """Show or hide the staff code / location fields based on selected role."""
        is_staff = role == "Staff"
        self._staff_code_container.setVisible(is_staff)
        self._location_container.setVisible(not is_staff)
        if not is_staff:
            self._staff_code_field.input_field.clear()
            self._staff_code_field.set_error(False)

    # Validation & registration

    def _on_signup_clicked(self):
        # Reset all field errors
        for field in (
            self._fname_field, self._lname_field, self._email_field,
            self._phone_field, self._staff_code_field, self._username_field,
            self._password_field, self._confirm_password_field,
        ):
            field.set_error(False)
        self._message_label.setVisible(False)

        # Gather values
        fname    = self._fname_field.text()
        lname    = self._lname_field.text()
        email    = self._email_field.text()
        phone    = self._phone_field.text()
        dob      = self._dob_edit.date().toString("yyyy-MM-dd")
        role     = self._role_combo.currentText()
        username = self._username_field.text()
        password = self._password_field.text()
        confirm  = self._confirm_password_field.text()

        # Client-side validation
        if not fname:
            self._show_error("Please enter your first name.")
            self._fname_field.set_error(True)
            return

        if not lname:
            self._show_error("Please enter your last name.")
            self._lname_field.set_error(True)
            return

        if not email or "@" not in email:
            self._show_error("Please enter a valid email address.")
            self._email_field.set_error(True)
            return

        if not phone:
            self._show_error("Please enter your phone number.")
            self._phone_field.set_error(True)
            return

        if role == "Staff":
            staff_code = self._staff_code_field.text()
            if not staff_code:
                self._show_error("Please enter the staff authorisation code.")
                self._staff_code_field.set_error(True)
                return

        if not username or len(username) < 3:
            self._show_error("Username must be at least 3 characters.")
            self._username_field.set_error(True)
            return

        if not password or len(password) < 8:
            self._show_error("Password must be at least 8 characters.")
            self._password_field.set_error(True)
            return

        if password != confirm:
            self._show_error("Passwords do not match.")
            self._password_field.set_error(True)
            self._confirm_password_field.set_error(True)
            return

        # Attempt database registration
        self._signup_btn.setEnabled(False)
        self._signup_btn.setText("Creating Account…")

        try:
            import sys, os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'database'))
            from models import signup, does_user_exist, get_role_by_code

            # Validate staff code against DB and resolve the actual role name
            actual_role = role  # default for Tenant
            if role == "Staff":
                staff_code = self._staff_code_field.text()
                resolved_role = get_role_by_code(staff_code)
                if resolved_role is None:
                    self._show_error("Invalid staff code. Contact an administrator.")
                    self._staff_code_field.set_error(True)
                    self._signup_btn.setEnabled(True)
                    self._signup_btn.setText("Create Account")
                    return
                actual_role = resolved_role

            # Check if user/email already exists
            exists = does_user_exist(username, email)
            if exists:
                self._show_error("Username or email already exists.")
                self._username_field.set_error(True)
                self._email_field.set_error(True)
                self._signup_btn.setEnabled(True)
                self._signup_btn.setText("Create Account")
                return

            result = signup(fname, lname, email, phone, dob, actual_role, username, password)
            if result:
                self._show_success("Account created successfully! Redirecting to login…")
                QTimer.singleShot(1500, self._complete_signup)
            else:
                self._show_error("Registration failed. Please try again.")
                self._signup_btn.setEnabled(True)
                self._signup_btn.setText("Create Account")

        except Exception as e:
            self._show_error(f"Error: {e}")
            self._signup_btn.setEnabled(True)
            self._signup_btn.setText("Create Account")

    def _complete_signup(self):
        self.signup_success.emit()

    def _on_switch_to_login(self):
        self.switch_to_login.emit()

    # Message helpers

    def _show_error(self, message: str):
        T = PAMSTheme
        self._message_label.setText(message)
        self._message_label.setStyleSheet(f"""
            color: {T.DANGER};
            font-size: 12px;
            font-weight: 500;
            background-color: rgba(231, 76, 60, 0.08);
            border: 1px solid rgba(231, 76, 60, 0.25);
            border-radius: 6px;
            padding: 10px 14px;
        """)
        self._message_label.setVisible(True)

    def _show_success(self, message: str):
        T = PAMSTheme
        self._message_label.setText(message)
        self._message_label.setStyleSheet(f"""
            color: {T.SUCCESS};
            font-size: 12px;
            font-weight: 500;
            background-color: rgba(46, 204, 113, 0.08);
            border: 1px solid rgba(46, 204, 113, 0.25);
            border-radius: 6px;
            padding: 10px 14px;
        """)
        self._message_label.setVisible(True)

    # Public API

    def reset(self):
        """Clear all fields and reset the form."""
        for field in (
            self._fname_field, self._lname_field, self._email_field,
            self._phone_field, self._username_field,
            self._password_field, self._confirm_password_field,
        ):
            field.input_field.clear()
            field.set_error(False)
        self._dob_edit.setDate(QDate(2000, 1, 1))
        self._role_combo.setCurrentIndex(0)
        self._staff_code_field.input_field.clear()
        self._staff_code_field.set_error(False)
        self._staff_code_container.setVisible(False)
        self._message_label.setVisible(False)
        self._signup_btn.setEnabled(True)
        self._signup_btn.setText("Create Account")
        QTimer.singleShot(100, self._fname_field.input_field.setFocus)


# Standalone entry point

def main():
    """Standalone launcher with full login ↔ signup navigation."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    signup_window = SignupWindow()
    login_ref = [None]  # mutable container for non-local reference

    def _on_login_success(name, role, location, user_id=0):
        if login_ref[0]:
            login_ref[0].hide()
        try:
            from main_window import MainWindow
            main_win = MainWindow(user_name=name, role=role, location=location, user_id=user_id)
            main_win.logout_requested.connect(lambda: (
                main_win.close(),
                _switch_to_login(),
            ))
            main_win.show()
        except ImportError:
            print(f"Login OK → {name} ({role}) @ {location}")
            print("MainWindow not available — run from project root.")
            _switch_to_login()

    def _switch_to_login():
        signup_window.hide()
        try:
            from login_window import LoginWindow
            if login_ref[0] is None:
                login_ref[0] = LoginWindow()
                login_ref[0].switch_to_signup.connect(_switch_to_signup)
                login_ref[0].login_success.connect(_on_login_success)
            else:
                login_ref[0].reset()
            login_ref[0].show()
        except ImportError:
            signup_window.show()

    def _switch_to_signup():
        if login_ref[0]:
            login_ref[0].hide()
        signup_window.reset()
        signup_window.show()

    def _switch_to_login_after_signup():
        signup_window.hide()
        try:
            from login_window import LoginWindow
            if login_ref[0] is None:
                login_ref[0] = LoginWindow()
                login_ref[0].switch_to_signup.connect(_switch_to_signup)
                login_ref[0].login_success.connect(_on_login_success)
            else:
                login_ref[0].reset()
            login_ref[0].show_signup_success()
            login_ref[0].show()
        except ImportError:
            signup_window.show()

    signup_window.switch_to_login.connect(_switch_to_login)
    signup_window.signup_success.connect(_switch_to_login_after_signup)
    signup_window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
