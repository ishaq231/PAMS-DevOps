"""

23010646 - Hasaan Ahmad 
220367921 - Royden Dias

PAMS - Paragon Apartment Management System
Login Window — split-panel design with branding + credentials form
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'database'))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QFrame,
    QGraphicsDropShadowEffect, QCheckBox, QSizePolicy, QSpacerItem
)
from PyQt6.QtCore import (
    Qt, QSize, pyqtSignal, QTimer, QPropertyAnimation,
    QEasingCurve, QPoint, QRect
)
from PyQt6.QtGui import (
    QFont, QIcon, QPainter, QColor, QPen, QBrush,
    QLinearGradient, QPainterPath, QPixmap, QCursor, QPaintEvent
)

# Import the shared design tokens
try:
    from main_window import PAMSTheme, MainWindow
except ImportError:
    # Fallback: duplicate the essential tokens so login_window.py
    # can run standalone during development
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
    MainWindow = None


# Decorative cityscape painter for the branding panel

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

        # Semi-transparent building colour
        building_color = QColor(255, 255, 255, 18)
        window_color = QColor(0, 212, 170, 40)

        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(building_color))

        # Building definitions: (x_fraction, width_fraction, height_fraction)
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

            # Tiny windows
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

        # Label
        self._label = QLabel(label)
        self._label.setStyleSheet(f"""
            color: {T.TEXT_DARK};
            font-size: 13px;
            font-weight: 600;
        """)
        layout.addWidget(self._label)

        # Input row (field + optional eye toggle)
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

        # Password visibility toggle
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


# Login Window

class LoginWindow(QMainWindow):
    """
    Split-panel login screen.
    Left: dark branding panel with logo, tagline, and cityscape.
    Right: clean form with username, password, location selector.

    Emits `login_success(str, str, str, int)` → (user_name, role, location, user_id)
    when credentials are accepted.
    """

    login_success = pyqtSignal(str, str, str, int, object)  # user_name, role, location_name, user_id, location_id
    switch_to_signup = pyqtSignal()  # emitted when user clicks "Sign Up"

    def __init__(self, parent=None):
        super().__init__(parent)
        self._attempts = 0
        self._setup_window()
        self._build_ui()

    # Window setup

    def _setup_window(self):
        self.setWindowTitle("PAMS — Login")
        self.setFixedSize(960, 600)
        try:
            self.setStyleSheet(PAMSTheme.global_stylesheet())
        except Exception:
            # Keep window functional even if theme setup fails in CI/headless mode.
            pass

        # Centre on screen when geometry is available (may not be in headless CI).
        try:
            screen = QApplication.primaryScreen()
            if screen:
                geo = screen.availableGeometry()
                self.move(
                    (geo.width() - self.width()) // 2,
                    (geo.height() - self.height()) // 2
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

        #  LEFT — Dark branding panel
        left = QFrame()
        left.setFixedWidth(400)
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
        accent_line.setStyleSheet(f"background-color: {T.ACCENT}; border-radius: 1px;")
        left_layout.addWidget(accent_line)
        left_layout.addSpacing(24)

        # Tagline
        tagline = QLabel(
            "Streamlined property management\n"
            "across Bristol, Cardiff, London\n"
            "and Manchester."
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
            ("Role-based secure access", T.ACCENT),
            ("Multi-location support", T.ACCENT),
            ("Real-time reporting", T.ACCENT),
        ]
        for text, color in features:
            feat = QLabel(text)
            feat.setStyleSheet(f"""
                color: {T.TEXT_SECONDARY};
                font-size: 12px;
                padding: 3px 0px;
            """)
            left_layout.addWidget(feat)

        left_layout.addStretch()

        # Cityscape decoration at the bottom
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

        #  RIGHT — Login form panel
        right = QFrame()
        right.setStyleSheet(f"background-color: {T.BG_WHITE};")

        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(60, 0, 60, 0)
        right_layout.setSpacing(0)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        # Form header
        form_title = QLabel("Welcome back")
        form_title.setStyleSheet(f"""
            color: {T.TEXT_DARK};
            font-size: 26px;
            font-weight: 700;
        """)
        right_layout.addWidget(form_title)
        right_layout.addSpacing(6)

        form_sub = QLabel("Sign in to access your dashboard")
        form_sub.setStyleSheet(f"""
            color: {T.TEXT_BODY};
            font-size: 14px;
        """)
        right_layout.addWidget(form_sub)
        right_layout.addSpacing(32)

        # Username field
        self._username_field = PAMSInput("Username", "Enter your username")
        right_layout.addWidget(self._username_field)
        right_layout.addSpacing(18)

        # Password field
        self._password_field = PAMSInput("Password", "Enter your password", is_password=True)
        right_layout.addWidget(self._password_field)
        right_layout.addSpacing(18)

        right_layout.addSpacing(10)

        # Remember me row
        remember_row = QHBoxLayout()
        self._remember_cb = QCheckBox("Remember me")
        self._remember_cb.setStyleSheet(f"""
            QCheckBox {{
                color: {T.TEXT_BODY};
                font-size: 12px;
                spacing: 6px;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 1.5px solid {T.BORDER_LIGHT};
                border-radius: 4px;
                background-color: {T.BG_WHITE};
            }}
            QCheckBox::indicator:checked {{
                background-color: {T.ACCENT};
                border-color: {T.ACCENT};
            }}
        """)
        remember_row.addWidget(self._remember_cb)
        remember_row.addStretch()
        right_layout.addLayout(remember_row)
        right_layout.addSpacing(24)

        # Error message (hidden by default)
        self._error_label = QLabel("")
        self._error_label.setStyleSheet(f"""
            color: {T.DANGER};
            font-size: 12px;
            font-weight: 500;
            background-color: rgba(231, 76, 60, 0.08);
            border: 1px solid rgba(231, 76, 60, 0.25);
            border-radius: 6px;
            padding: 10px 14px;
        """)
        self._error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._error_label.setVisible(False)
        right_layout.addWidget(self._error_label)
        right_layout.addSpacing(4)

        # Success message (hidden by default)
        self._success_label = QLabel("")
        self._success_label.setStyleSheet(f"""
            color: {T.SUCCESS};
            font-size: 12px;
            font-weight: 500;
            background-color: rgba(46, 204, 113, 0.08);
            border: 1px solid rgba(46, 204, 113, 0.25);
            border-radius: 6px;
            padding: 10px 14px;
        """)
        self._success_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._success_label.setVisible(False)
        right_layout.addWidget(self._success_label)
        right_layout.addSpacing(8)

        # Login button
        self._login_btn = QPushButton("Sign In")
        self._login_btn.setFixedHeight(48)
        self._login_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._login_btn.setStyleSheet(f"""
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
        self._login_btn.clicked.connect(self._on_login_clicked)
        right_layout.addWidget(self._login_btn)
        right_layout.addSpacing(20)

        # Sign Up link row
        signup_row = QHBoxLayout()
        signup_row.setAlignment(Qt.AlignmentFlag.AlignCenter)

        no_account_label = QLabel("Don't have an account?")
        no_account_label.setStyleSheet(f"""
            color: {T.TEXT_BODY};
            font-size: 13px;
        """)
        signup_row.addWidget(no_account_label)

        signup_link = QPushButton("Sign Up")
        signup_link.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        signup_link.setStyleSheet(f"""
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
        signup_link.clicked.connect(self._on_switch_to_signup)
        signup_row.addWidget(signup_link)

        right_layout.addLayout(signup_row)

        root.addWidget(right)

        # Keyboard shortcut: Enter to login
        self._username_field.input_field.returnPressed.connect(self._on_login_clicked)
        self._password_field.input_field.returnPressed.connect(self._on_login_clicked)

        # Focus username on open
        QTimer.singleShot(100, self._username_field.input_field.setFocus)

    # Location loading


    # Authentication logic

    def _on_login_clicked(self):
        T = PAMSTheme
        username = self._username_field.text().lower()
        password = self._password_field.text()

        # Reset error/success styling
        self._username_field.set_error(False)
        self._password_field.set_error(False)
        self._error_label.setVisible(False)
        self._success_label.setVisible(False)

        # Validation
        if not username:
            self._show_error("Please enter your username.")
            self._username_field.set_error(True)
            return

        if not password:
            self._show_error("Please enter your password.")
            self._password_field.set_error(True)
            return

        # Authenticate against database
        db_result = None
        try:
            import sys as _sys, os as _os
            _sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), '..', 'database'))
            from models import login as db_login
            db_result = db_login(username, password)
        except Exception:
            db_result = None

        if db_result:
            location_name = db_result.get("location_name") or "All Locations"
            location_id = db_result.get("location_id")
            self._login_btn.setEnabled(False)
            self._login_btn.setText("Signing in…")
            _uid = int(db_result.get("user_id") or 0)
            QTimer.singleShot(400, lambda: self._complete_login(
                db_result["name"], db_result["role"], location_name, _uid, location_id
            ))
        else:
            self._attempts += 1
            if self._attempts >= 3:
                self._show_error(
                    f"Invalid credentials. {5 - self._attempts} attempts remaining."
                )
                if self._attempts >= 5:
                    self._login_btn.setEnabled(False)
                    self._show_error("Account locked. Please contact an administrator.")
            else:
                self._show_error("Invalid username or password.")
            self._username_field.set_error(True)
            self._password_field.set_error(True)

    def _complete_login(self, name: str, role: str, location_name: str, user_id: int = 0, location_id=None):
        self.login_success.emit(name, role, location_name, user_id, location_id)

    def _show_error(self, message: str):
        self._success_label.setVisible(False)
        self._error_label.setText(message)
        self._error_label.setVisible(True)

    def show_signup_success(self, message: str = "Account created successfully! Please sign in."):
        """Show a green notification bar after successful signup."""
        self._error_label.setVisible(False)
        self._success_label.setText(message)
        self._success_label.setVisible(True)

    def _on_switch_to_signup(self):
        self.switch_to_signup.emit()

    # Public API

    def reset(self):
        """Reset form state (useful when logging out and returning here)."""
        self._username_field.input_field.clear()
        self._password_field.input_field.clear()
        self._username_field.set_error(False)
        self._password_field.set_error(False)
        self._error_label.setVisible(False)
        self._success_label.setVisible(False)
        self._login_btn.setEnabled(True)
        self._login_btn.setText("Sign In")
        self._attempts = 0
        QTimer.singleShot(100, self._username_field.input_field.setFocus)


# Application controller — wires Login → MainWindow → Logout

class PAMSApplication:
    """
    Top-level controller that manages the login/main-window/signup lifecycle.
    Usage:
        app = QApplication(sys.argv)
        pams = PAMSApplication()
        pams.start()
        sys.exit(app.exec())
    """

    def __init__(self):
        self._login_window = LoginWindow()
        self._signup_window = None
        self._main_window = None

        self._login_window.login_success.connect(self._on_login_success)
        self._login_window.switch_to_signup.connect(self._on_switch_to_signup)

    def start(self):
        self._login_window.show()

    # Signup navigation

    def _on_switch_to_signup(self):
        self._login_window.hide()
        if self._signup_window is None:
            from signup_window import SignupWindow
            self._signup_window = SignupWindow()
            self._signup_window.switch_to_login.connect(self._on_switch_to_login)
            self._signup_window.signup_success.connect(self._on_signup_success)
        else:
            self._signup_window.reset()
        self._signup_window.show()

    def _on_switch_to_login(self):
        if self._signup_window:
            self._signup_window.hide()
        self._login_window.reset()
        self._login_window.show()

    def _on_signup_success(self):
        if self._signup_window:
            self._signup_window.hide()
        self._login_window.reset()
        self._login_window.show_signup_success()
        self._login_window.show()

    def _on_login_success(self, name: str, role: str, location: str, user_id: int = 0, location_id=None):
        self._login_window.hide()

        # Import MainWindow (may already be imported at top)
        if MainWindow is not None:
            self._main_window = MainWindow(
                user_name=name, role=role, location=location, user_id=user_id,
                location_id=location_id
            )
            self._main_window.logout_requested.connect(self._on_logout)
            self._main_window.show()
        else:
            # Standalone mode — just print and close
            print(f"Login OK → {name} ({role}) @ {location}")
            print("MainWindow not available — run from project root.")
            self._login_window.show()

    def _on_logout(self):
        if self._main_window:
            self._main_window.close()
            self._main_window = None
        self._login_window.reset()
        self._login_window.show()


# Entry point

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    pams = PAMSApplication()
    pams.start()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()