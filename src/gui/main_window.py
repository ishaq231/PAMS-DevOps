"""

23010646 - Hasaan Ahmad 
220367921 - Royden Dias

PAMS - Paragon Apartment Management System
Main Window with role-based navigation and modern UI
"""

import sys
import os as _os
_sys_db_path = _os.path.join(_os.path.dirname(__file__), '..', 'database')
if _sys_db_path not in sys.path:
    sys.path.insert(0, _sys_db_path)
try:
    from models import (
        get_all_apartments as _get_all_apartments,
        get_all_invoices as _get_all_invoices,
        get_all_maintenance_requests as _get_all_maintenance_requests,
        get_apartment_count as _get_apartment_count,
        get_all_leases as _get_all_leases,
        get_leases_for_user as _get_leases_for_user,
        get_invoices_for_tenant as _get_invoices_for_tenant,
        get_maintenance_for_tenant as _get_maintenance_for_tenant,
        get_maintenance_for_staff as _get_maintenance_for_staff,
    )
    _MODELS_OK = True
except Exception:
    _MODELS_OK = False
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QStackedWidget, QFrame, QGraphicsDropShadowEffect,
    QSizePolicy, QSpacerItem, QScrollArea, QGridLayout, QProgressBar,
    QGraphicsOpacityEffect, QToolTip
)
from PyQt6.QtCore import (
    Qt, QSize, QPropertyAnimation, QEasingCurve, QTimer,
    pyqtProperty, QRect, QPoint, pyqtSignal, QParallelAnimationGroup
)
from PyQt6.QtGui import (
    QFont, QFontDatabase, QIcon, QPainter, QColor, QPen, QBrush,
    QLinearGradient, QPainterPath, QPixmap, QPalette, QCursor
)

# PAMS Design System — Colour Palette & Tokens

class PAMSTheme:
    """Centralised design tokens for the entire PAMS application."""

    # Core palette
    BG_DARKEST    = "#0F1923"
    BG_DARK       = "#15202E"
    BG_SIDEBAR    = "#1A2736"
    BG_CARD       = "#1E2D3D"
    BG_HOVER      = "#253647"
    BG_SURFACE    = "#F0F4F8"
    BG_WHITE      = "#FFFFFF"

    # Accent colours
    ACCENT        = "#00D4AA"   # Teal/mint — primary action
    ACCENT_HOVER  = "#00E8BB"
    ACCENT_DIM    = "#00B894"
    ACCENT_GLOW   = "rgba(0, 212, 170, 0.15)"

    # Semantic colours
    SUCCESS       = "#2ECC71"
    WARNING       = "#F39C12"
    DANGER        = "#E74C3C"
    INFO          = "#3498DB"

    # Text colours
    TEXT_PRIMARY   = "#FFFFFF"
    TEXT_SECONDARY = "#8899AA"
    TEXT_MUTED     = "#7E92A5"
    TEXT_DARK      = "#1A2736"
    TEXT_BODY      = "#4A5568"

    # Border / Misc
    BORDER_SUBTLE  = "rgba(255, 255, 255, 0.06)"
    BORDER_LIGHT   = "#E2E8F0"
    SHADOW         = "rgba(0, 0, 0, 0.25)"

    # Typography
    FONT_FAMILY    = "Segoe UI"
    FONT_HEADING   = "Segoe UI Semibold"

    # Spacing
    SIDEBAR_WIDTH       = 260
    SIDEBAR_COLLAPSED   = 72
    HEADER_HEIGHT       = 64
    CARD_RADIUS         = 14
    BTN_RADIUS          = 10

    @classmethod
    def global_stylesheet(cls) -> str:
        """Return the master QSS stylesheet for the application."""
        return f"""
            /* Global reset */
            * {{
                font-family: "{cls.FONT_FAMILY}";
            }}
            QToolTip {{
                background-color: {cls.BG_CARD};
                color: {cls.TEXT_PRIMARY};
                border: 1px solid {cls.BORDER_SUBTLE};
                padding: 6px 10px;
                border-radius: 6px;
                font-size: 12px;
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 6px;
                margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background: {cls.TEXT_MUTED};
                border-radius: 3px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {cls.TEXT_SECONDARY};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
                height: 0px;
            }}
            QScrollBar:horizontal {{
                background: transparent;
                height: 6px;
            }}
            QScrollBar::handle:horizontal {{
                background: {cls.TEXT_MUTED};
                border-radius: 3px;
                min-width: 30px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {cls.BG_WHITE};
                border: 1px solid {cls.BORDER_LIGHT};
                border-radius: 6px;
                padding: 4px;
                selection-background-color: {cls.ACCENT_GLOW};
                selection-color: {cls.TEXT_DARK};
                color: {cls.TEXT_DARK};
                outline: none;
            }}
            QComboBox QAbstractItemView::item {{
                padding: 8px 12px;
                min-height: 32px;
                color: {cls.TEXT_DARK};
            }}
        """


# Custom SVG-free icon painter (no external assets needed)

class IconPainter:
    """Draws simple geometric icons using QPainter — no image files required."""

    @staticmethod
    def _make_pixmap(size: int, draw_fn, color: str) -> QPixmap:
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        p = QPainter(pixmap)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor(color))
        pen.setWidthF(1.8)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        p.setPen(pen)
        draw_fn(p, size)
        p.end()
        return pixmap

    @staticmethod
    def dashboard(size=22, color="#8899AA"):
        def draw(p: QPainter, s):
            m = 3
            w = (s - 2*m - 2) / 2
            r = 3
            p.drawRoundedRect(int(m), int(m), int(w), int(w), r, r)
            p.drawRoundedRect(int(m + w + 2), int(m), int(w), int(w), r, r)
            p.drawRoundedRect(int(m), int(m + w + 2), int(w), int(w), r, r)
            p.drawRoundedRect(int(m + w + 2), int(m + w + 2), int(w), int(w), r, r)
        return QIcon(IconPainter._make_pixmap(size, draw, color))

    @staticmethod
    def users(size=22, color="#8899AA"):
        def draw(p: QPainter, s):
            cx, cy = s // 2, s // 2 - 2
            p.drawEllipse(QPoint(cx, cy - 1), 4, 4)
            path = QPainterPath()
            path.moveTo(cx - 7, s - 4)
            path.quadTo(cx - 7, cy + 5, cx, cy + 5)
            path.quadTo(cx + 7, cy + 5, cx + 7, s - 4)
            p.drawPath(path)
        return QIcon(IconPainter._make_pixmap(size, draw, color))

    @staticmethod
    def building(size=22, color="#8899AA"):
        def draw(p: QPainter, s):
            m = 4
            p.drawRect(m, m + 2, s - 2*m, s - m - 4)
            # windows
            for row in range(3):
                for col in range(2):
                    x = m + 3 + col * 7
                    y = m + 5 + row * 4
                    p.drawRect(x, y, 3, 2)
        return QIcon(IconPainter._make_pixmap(size, draw, color))

    @staticmethod
    def wallet(size=22, color="#8899AA"):
        def draw(p: QPainter, s):
            m = 3
            p.drawRoundedRect(m, m + 3, s - 2*m, s - 2*m - 3, 3, 3)
            p.drawLine(m, m + 7, s - m, m + 7)
            p.setBrush(QBrush(QColor(color)))
            p.drawEllipse(s - m - 6, s//2 - 1, 4, 4)
        return QIcon(IconPainter._make_pixmap(size, draw, color))

    @staticmethod
    def wrench(size=22, color="#8899AA"):
        def draw(p: QPainter, s):
            p.drawLine(5, s - 5, s - 7, 7)
            p.drawEllipse(s - 10, 3, 8, 8)
        return QIcon(IconPainter._make_pixmap(size, draw, color))

    @staticmethod
    def chart(size=22, color="#8899AA"):
        def draw(p: QPainter, s):
            m = 4
            p.drawLine(m, s - m, m, m)
            p.drawLine(m, s - m, s - m, s - m)
            # bars
            bw = 3
            heights = [6, 10, 8, 13]
            for i, h in enumerate(heights):
                x = m + 3 + i * 4
                p.drawRect(x, s - m - h, bw, h)
        return QIcon(IconPainter._make_pixmap(size, draw, color))

    @staticmethod
    def lease(size=22, color="#8899AA"):
        def draw(p: QPainter, s):
            m = 4
            p.drawRoundedRect(m, m, s - 2*m, s - 2*m, 2, 2)
            for i in range(4):
                y = m + 4 + i * 3
                p.drawLine(m + 3, y, s - m - 3, y)
        return QIcon(IconPainter._make_pixmap(size, draw, color))

    @staticmethod
    def bell(size=22, color="#8899AA"):
        def draw(p: QPainter, s):
            cx = s // 2
            path = QPainterPath()
            path.moveTo(cx - 6, s - 6)
            path.quadTo(cx - 6, 4, cx, 4)
            path.quadTo(cx + 6, 4, cx + 6, s - 6)
            path.lineTo(cx - 6, s - 6)
            p.drawPath(path)
            p.drawLine(cx - 2, s - 4, cx + 2, s - 4)
            p.drawLine(cx, 4, cx, 2)
        return QIcon(IconPainter._make_pixmap(size, draw, color))

    @staticmethod
    def settings(size=22, color="#8899AA"):
        def draw(p: QPainter, s):
            cx, cy = s // 2, s // 2
            p.drawEllipse(QPoint(cx, cy), 4, 4)
            for angle in range(0, 360, 45):
                import math
                rad = math.radians(angle)
                x1 = cx + int(6 * math.cos(rad))
                y1 = cy + int(6 * math.sin(rad))
                x2 = cx + int(8 * math.cos(rad))
                y2 = cy + int(8 * math.sin(rad))
                p.drawLine(x1, y1, x2, y2)
        return QIcon(IconPainter._make_pixmap(size, draw, color))

    @staticmethod
    def logout(size=22, color="#8899AA"):
        def draw(p: QPainter, s):
            m = 4
            p.drawLine(m, m, m, s - m)
            p.drawLine(m, m, s // 2, m)
            p.drawLine(m, s - m, s // 2, s - m)
            # arrow
            cy = s // 2
            p.drawLine(s // 2 - 2, cy, s - m, cy)
            p.drawLine(s - m - 3, cy - 3, s - m, cy)
            p.drawLine(s - m - 3, cy + 3, s - m, cy)
        return QIcon(IconPainter._make_pixmap(size, draw, color))

    @staticmethod
    def expand(size=22, color="#8899AA"):
        def draw(p: QPainter, s):
            cx = s // 2
            p.drawLine(cx - 5, cx - 2, cx, cx + 3)
            p.drawLine(cx, cx + 3, cx + 5, cx - 2)
        return QIcon(IconPainter._make_pixmap(size, draw, color))

    @staticmethod
    def home(size=22, color="#8899AA"):
        def draw(p: QPainter, s):
            cx = s // 2
            # roof
            p.drawLine(3, cx + 1, cx, 3)
            p.drawLine(cx, 3, s - 3, cx + 1)
            # walls
            p.drawRect(5, cx + 1, s - 10, s - cx - 4)
        return QIcon(IconPainter._make_pixmap(size, draw, color))


# Animated sidebar nav button

class NavButton(QPushButton):
    """Sidebar navigation button with hover animation and active indicator."""

    def __init__(self, icon: QIcon, text: str, parent=None):
        super().__init__(parent)
        self.setText(text)
        self.setIcon(icon)
        self.setIconSize(QSize(20, 20))
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setCheckable(True)
        self.setFixedHeight(44)
        self._active = False
        self._apply_style(False)

    def _apply_style(self, active: bool):
        T = PAMSTheme
        if active:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {T.ACCENT_GLOW};
                    color: {T.ACCENT};
                    border: none;
                    border-left: 3px solid {T.ACCENT};
                    border-radius: 0px;
                    text-align: left;
                    padding-left: 20px;
                    font-size: 13px;
                    font-weight: 600;
                    letter-spacing: 0.3px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {T.TEXT_SECONDARY};
                    border: none;
                    border-left: 3px solid transparent;
                    border-radius: 0px;
                    text-align: left;
                    padding-left: 20px;
                    font-size: 13px;
                    font-weight: 400;
                }}
                QPushButton:hover {{
                    background-color: {T.BG_HOVER};
                    color: {T.TEXT_PRIMARY};
                }}
            """)

    def set_active(self, active: bool):
        self._active = active
        self.setChecked(active)
        self._apply_style(active)


# Stat card widget for dashboard

class StatCard(QFrame):
    """A rounded card that displays a KPI with icon accent strip."""

    def __init__(self, title: str, value: str, subtitle: str = "",
                 accent: str = PAMSTheme.ACCENT, parent=None):
        super().__init__(parent)
        T = PAMSTheme
        self.setFixedHeight(130)
        self.setMinimumWidth(200)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setStyleSheet(f"""
            StatCard {{
                background-color: {T.BG_WHITE};
                border-radius: 4px;
                border: 1px solid {T.BORDER_LIGHT};
            }}
        """)

        # Shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 18))
        self.setGraphicsEffect(shadow)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 18, 0)
        layout.setSpacing(0)

        # Accent strip — flush against the left edge
        strip = QFrame()
        strip.setFixedWidth(5)
        strip.setStyleSheet(f"""
            background-color: {accent};
            border-top-left-radius: 4px;
            border-bottom-left-radius: 4px;
        """)
        layout.addWidget(strip)

        # Text content
        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(18, 16, 0, 16)
        text_layout.setSpacing(4)

        lbl_title = QLabel(title)
        lbl_title.setStyleSheet(f"""
            color: {T.TEXT_BODY};
            font-size: 12px;
            font-weight: 500;
            letter-spacing: 0.6px;
            text-transform: uppercase;
        """)

        lbl_value = QLabel(value)
        lbl_value.setStyleSheet(f"""
            color: {T.TEXT_DARK};
            font-size: 28px;
            font-weight: 700;
        """)

        lbl_sub = QLabel(subtitle)
        lbl_sub.setStyleSheet(f"""
            color: {T.TEXT_BODY};
            font-size: 11px;
        """)

        text_layout.addWidget(lbl_title)
        text_layout.addWidget(lbl_value)
        if subtitle:
            text_layout.addWidget(lbl_sub)
        text_layout.addStretch()

        layout.addLayout(text_layout)
        layout.addStretch()


# Quick-action card

class ActionCard(QPushButton):
    """A clickable card for quick-actions on the dashboard."""

    def __init__(self, title: str, description: str,
                 accent: str = PAMSTheme.ACCENT, parent=None):
        super().__init__(parent)
        T = PAMSTheme
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setFixedHeight(90)
        self.setMinimumWidth(180)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {T.BG_WHITE};
                border: 1px solid {T.BORDER_LIGHT};
                border-radius: {T.CARD_RADIUS}px;
                text-align: left;
                padding: 18px 24px;
            }}
            QPushButton:hover {{
                border: 1px solid {accent};
                background-color: #FAFCFF;
            }}
            QPushButton:pressed {{
                background-color: #F0F4F8;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(4)

        lbl_title = QLabel(title, self)
        lbl_title.setStyleSheet(f"""
            color: {T.TEXT_DARK};
            font-size: 14px;
            font-weight: 600;
            background: transparent;
            border: none;
            padding-left: 0px;
        """)
        lbl_title.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        lbl_desc = QLabel(description, self)
        lbl_desc.setStyleSheet(f"""
            color: {T.TEXT_BODY};
            font-size: 11px;
            background: transparent;
            border: none;
            padding-left: 0px;
        """)
        lbl_desc.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        lbl_desc.setWordWrap(True)

        layout.addWidget(lbl_title)
        layout.addWidget(lbl_desc)
        layout.addStretch()


# Dashboard panel (default landing page per role)

class DashboardPanel(QWidget):
    """Role-aware overview dashboard with KPI cards and quick actions."""

    nav_requested = pyqtSignal(str)

    def __init__(self, role: str = "Administrator", user_name: str = "Admin",
                 user_id: int = 0, location_name: str = None,
                 location_id=None, parent=None):
        super().__init__(parent)
        self._user_id = user_id
        self._location_name = location_name
        self._location_id = location_id
        self._role = role
        T = PAMSTheme
        self.setStyleSheet(f"background-color: {T.BG_SURFACE};")

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(32, 28, 32, 28)
        main_layout.setSpacing(24)

        # Greeting
        greeting = QLabel(f"Welcome back, {user_name}")
        greeting.setStyleSheet(f"""
            color: {T.ACCENT};
            font-size: 26px;
            font-weight: 700;
            background: transparent;
        """)
        sub_greeting = QLabel("Here's what's happening across your properties today.")
        sub_greeting.setStyleSheet(f"""
            color: {T.TEXT_SECONDARY};
            font-size: 14px;
            background: transparent;
        """)
        main_layout.addWidget(greeting)
        main_layout.addWidget(sub_greeting)
        main_layout.addSpacing(8)

        # KPI cards
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(16)

        stats = self._get_stats_for_role(role)
        for s in stats:
            card = StatCard(s["title"], s["value"], s["sub"], s.get("accent", T.ACCENT))
            cards_layout.addWidget(card)

        main_layout.addLayout(cards_layout)

        # Section header
        actions_header = QLabel("Quick Actions")
        actions_header.setStyleSheet(f"""
            color: {T.ACCENT};
            font-size: 18px;
            font-weight: 600;
            background: transparent;
        """)
        main_layout.addSpacing(8)
        main_layout.addWidget(actions_header)

        # Quick-action cards
        actions_layout = QGridLayout()
        actions_layout.setSpacing(14)

        actions = self._get_actions_for_role(role)
        for idx, a in enumerate(actions):
            card = ActionCard(a["title"], a["desc"], a.get("accent", T.ACCENT))
            nav_key = a.get("nav")
            if nav_key:
                card.clicked.connect(
                    (lambda k: lambda: self.nav_requested.emit(k))(nav_key))
            actions_layout.addWidget(card, idx // 3, idx % 3)

        main_layout.addLayout(actions_layout)
        main_layout.addStretch()

        scroll.setWidget(container)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def _get_stats_for_role(self, role: str) -> list:
        from datetime import date as _date
        T = PAMSTheme

        # ── helpers ──────────────────────────────────────────────────
        def _safe_float(v):
            try:
                return float(v or 0)
            except (TypeError, ValueError):
                return 0.0

        def _days_between(d1_str, d2_str):
            """Return (d2 - d1).days from 'YYYY-MM-DD' strings, or None."""
            try:
                from datetime import datetime as _dt
                fmt = "%Y-%m-%d"
                return (_dt.strptime(d2_str[:10], fmt) - _dt.strptime(d1_str[:10], fmt)).days
            except Exception:
                return None

        # ── fetch shared data ─────────────────────────────────────────
        apartments = _get_all_apartments() if _MODELS_OK else []
        invoices   = _get_all_invoices()   if _MODELS_OK else []
        requests   = _get_all_maintenance_requests() if _MODELS_OK else []

        # Filter by location for non-admin/manager roles
        if self._location_name and self._role not in ('Administrator', 'Manager'):
            apartments = [a for a in apartments if a.get('location') == self._location_name]
            invoices   = [i for i in invoices if i.get('location') == self._location_name]
            requests   = [r for r in requests if r.get('location') == self._location_name]

        # ── aggregate: apartments ─────────────────────────────────────
        total_apts = len(apartments)
        occupied   = sum(1 for a in apartments if a.get('occupation_status') == 'Occupied')
        locations  = len({a.get('location', '') for a in apartments if a.get('location')})
        occ_pct    = round(occupied / total_apts * 100) if total_apts else 0

        # ── aggregate: invoices ───────────────────────────────────────
        pending_amt  = sum(_safe_float(i.get('amount')) for i in invoices
                           if i.get('status') in ('Pending', 'Overdue'))
        overdue_cnt  = sum(1 for i in invoices if i.get('status') == 'Overdue')
        paid_amt     = sum(_safe_float(i.get('amount')) for i in invoices
                           if i.get('status') == 'Paid')

        # ── aggregate: maintenance requests ──────────────────────────
        open_reqs    = sum(1 for r in requests if r.get('status') in ('Open', 'In Progress'))
        high_pri     = sum(1 for r in requests if r.get('status') in ('Open', 'In Progress')
                           and r.get('priority') == 'High')
        maint_costs  = sum(_safe_float(r.get('cost')) for r in requests)

        # ── base stats (Admin / Manager / Front Desk) ─────────────────
        base = [
            {
                "title":  "Total Apartments",
                "value":  str(total_apts),
                "sub":    f"Across {locations} location{'s' if locations != 1 else ''}",
                "accent": T.ACCENT,
            },
            {
                "title":  "Occupancy Rate",
                "value":  f"{occ_pct}%",
                "sub":    f"{occupied} of {total_apts} occupied",
                "accent": T.SUCCESS,
            },
            {
                "title":  "Pending Payments",
                "value":  f"\u00a3{pending_amt:,.0f}",
                "sub":    f"{overdue_cnt} invoice{'s' if overdue_cnt != 1 else ''} overdue",
                "accent": T.WARNING,
            },
            {
                "title":  "Open Requests",
                "value":  str(open_reqs),
                "sub":    f"{high_pri} high priority",
                "accent": T.DANGER,
            },
        ]

        # ── Tenant ────────────────────────────────────────────────────
        if role == "Tenant":
            next_pay_val = "—"
            next_pay_sub = "No pending invoices"
            lease_val    = "—"
            lease_sub    = "No active lease"
            maint_val    = "—"
            maint_sub    = ""

            if _MODELS_OK and self._user_id:
                today = _date.today()

                # Next payment
                t_invoices = _get_invoices_for_tenant(self._user_id)
                upcoming = [i for i in t_invoices
                            if i.get('status') in ('Pending', 'Overdue')]
                if upcoming:
                    upcoming.sort(key=lambda i: i.get('due_date') or '')
                    nxt = upcoming[0]
                    next_pay_val = f"\u00a3{_safe_float(nxt.get('amount')):,.0f}"
                    next_pay_sub = f"Due {nxt.get('due_date', '')}"

                # Lease days remaining
                leases = _get_leases_for_user(self._user_id)
                active = next((l for l in leases if l.get('status') == 'ACTIVE'), None)
                if active and active.get('end_date'):
                    diff = _days_between(str(today), active['end_date'])
                    if diff is not None and diff >= 0:
                        lease_val = f"{diff} days"
                        lease_sub = f"Ends {active['end_date'][:10]}"
                    elif diff is not None:
                        lease_val = "Expired"
                        lease_sub = f"Ended {active['end_date'][:10]}"

                # Maintenance requests
                t_reqs = _get_maintenance_for_tenant(self._user_id)
                open_t = [r for r in t_reqs if r.get('status') in ('Open', 'In Progress')]
                maint_val = f"{len(open_t)} Open"
                if open_t:
                    top = open_t[0]
                    maint_sub = f"{top.get('description', '')[:30]} — {top.get('status', '')}"
                else:
                    maint_sub = "No open requests"

            return [
                {"title": "Next Payment",  "value": next_pay_val, "sub": next_pay_sub, "accent": T.ACCENT},
                {"title": "Lease Ends",    "value": lease_val,    "sub": lease_sub,    "accent": T.INFO},
                {"title": "Maintenance",   "value": maint_val,    "sub": maint_sub,    "accent": T.WARNING},
            ]

        # ── Finance Manager ───────────────────────────────────────────
        if role == "Finance Manager":
            net_rev = paid_amt - maint_costs
            return [
                {
                    "title":  "Collected",
                    "value":  f"\u00a3{paid_amt:,.0f}",
                    "sub":    f"{sum(1 for i in invoices if i.get('status') == 'Paid')} paid invoices",
                    "accent": T.SUCCESS,
                },
                {
                    "title":  "Outstanding",
                    "value":  f"\u00a3{pending_amt:,.0f}",
                    "sub":    f"{overdue_cnt} overdue",
                    "accent": T.WARNING,
                },
                {
                    "title":  "Overdue Invoices",
                    "value":  str(overdue_cnt),
                    "sub":    "Require follow-up",
                    "accent": T.DANGER,
                },
                {
                    "title":  "Net Revenue",
                    "value":  f"\u00a3{max(net_rev, 0):,.0f}",
                    "sub":    "After maintenance costs",
                    "accent": T.ACCENT,
                },
            ]

        # ── Maintenance Staff ─────────────────────────────────────────
        if role == "Maintenance Staff":
            assigned_val  = str(open_reqs)
            assigned_sub  = f"{high_pri} urgent"
            avg_val       = "—"
            avg_sub       = "No resolved requests"
            completed_val = "0"
            completed_sub = ""

            if _MODELS_OK and self._user_id:
                s_reqs     = _get_maintenance_for_staff(self._user_id)
                s_open     = [r for r in s_reqs if r.get('status') in ('Open', 'In Progress')]
                s_urgent   = sum(1 for r in s_open if r.get('priority') == 'High')
                s_done     = [r for r in s_reqs if r.get('status') in ('Resolved', 'Closed')]
                assigned_val = str(len(s_open))
                assigned_sub = f"{s_urgent} urgent"
                completed_val = str(len(s_done))
                if s_done:
                    s_cost = sum(_safe_float(r.get('cost')) for r in s_done)
                    completed_sub = f"\u00a3{s_cost:,.0f} in costs"
                durations = []
                for r in s_done:
                    if r.get('report_date') and r.get('resolved_date'):
                        d = _days_between(r['report_date'], r['resolved_date'])
                        if d is not None and d >= 0:
                            durations.append(d)
                if durations:
                    avg_days = sum(durations) / len(durations)
                    avg_val  = f"{avg_days:.1f} days"
                    avg_sub  = "Target: 3 days"

            return [
                {"title": "Assigned To You",       "value": assigned_val,  "sub": assigned_sub,  "accent": T.DANGER},
                {"title": "Avg Resolution",         "value": avg_val,       "sub": avg_sub,        "accent": T.SUCCESS},
                {"title": "Completed",              "value": completed_val, "sub": completed_sub,  "accent": T.ACCENT},
            ]

        return base  # Admin / Manager / Front Desk

    def _get_actions_for_role(self, role: str) -> list:
        T = PAMSTheme
        if role == "Administrator":
            return [
                {"title": "Register Apartment", "desc": "Add a new property to the system", "accent": T.ACCENT, "nav": "apartments"},
                {"title": "Manage Users", "desc": "Add, edit or deactivate staff accounts", "accent": T.INFO, "nav": "users"},
                {"title": "Track Leases", "desc": "View upcoming lease expirations", "accent": T.WARNING, "nav": "leases"},
                {"title": "Generate Report", "desc": "Occupancy & financial reports", "accent": T.SUCCESS, "nav": "reports"},
                {"title": "Assign Apartment", "desc": "Link a tenant to a property", "accent": T.ACCENT, "nav": "apartments"},
                {"title": "View Complaints", "desc": "Review tenant feedback", "accent": T.DANGER, "nav": "complaints"},
            ]
        if role == "Manager":
            return [
                {"title": "Performance Reports", "desc": "City-by-city occupancy & revenue", "accent": T.ACCENT, "nav": "reports"},
                {"title": "Expand Business", "desc": "Add a new city or location", "accent": T.SUCCESS, "nav": "expand"},
                {"title": "Occupancy Overview", "desc": "Monitor all apartment statuses", "accent": T.INFO, "nav": "occupancy"},
                {"title": "Manage Users", "desc": "Full access to user accounts", "accent": T.INFO, "nav": "users"},
                {"title": "View Invoices", "desc": "Financial overview", "accent": T.WARNING, "nav": "invoices"},
                {"title": "Maintenance Requests", "desc": "View all open requests", "accent": T.DANGER, "nav": "requests"},
            ]
        if role == "Front Desk Staff":
            return [
                {"title": "Register Tenant", "desc": "New tenant registration form", "accent": T.ACCENT, "nav": "register"},
                {"title": "Handle Enquiry", "desc": "Search and assist tenants", "accent": T.INFO, "nav": "tenants"},
                {"title": "Log Complaint", "desc": "Record a maintenance request", "accent": T.WARNING, "nav": "complaints"},
            ]
        if role == "Finance Manager":
            return [
                {"title": "Generate Invoice", "desc": "Create billing for a tenant", "accent": T.ACCENT, "nav": "invoices"},
                {"title": "Record Payment", "desc": "Mark invoice as paid", "accent": T.SUCCESS, "nav": "payments"},
                {"title": "Late Payment Alerts", "desc": "Send overdue notifications", "accent": T.DANGER, "nav": "late"},
                {"title": "Financial Summary", "desc": "Collected vs pending report", "accent": T.INFO, "nav": "fin_reports"},
            ]
        if role == "Maintenance Staff":
            return [
                {"title": "View My Requests", "desc": "Requests assigned to you", "accent": T.ACCENT, "nav": "requests"},
                {"title": "Log Resolution", "desc": "Record completed work", "accent": T.SUCCESS, "nav": "log"},
                {"title": "Update Priority", "desc": "Re-prioritise a request", "accent": T.WARNING, "nav": "requests"},
            ]
        if role == "Tenant":
            return [
                {"title": "Submit Request", "desc": "Report a maintenance issue", "accent": T.ACCENT, "nav": "my_maint"},
                {"title": "View Invoices", "desc": "Check billing history", "accent": T.INFO, "nav": "my_payments"},
                {"title": "Lease Details", "desc": "View your lease agreement", "accent": T.SUCCESS, "nav": "my_lease"},
                {"title": "Early Termination", "desc": "Request to leave early", "accent": T.DANGER, "nav": "my_lease"},
            ]
        return []


# Placeholder panel for sections not yet built

class PlaceholderPanel(QWidget):
    """Temporary placeholder for panels under construction."""

    def __init__(self, section_name: str, parent=None):
        super().__init__(parent)
        T = PAMSTheme
        self.setStyleSheet(f"background-color: {T.BG_SURFACE};")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_lbl = QLabel("🏗")
        icon_lbl.setStyleSheet("font-size: 48px; background: transparent;")
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel(section_name)
        title.setStyleSheet(f"""
            color: {T.ACCENT};
            font-size: 22px;
            font-weight: 700;
            background: transparent;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("This panel is under development.\nConnect your backend logic here.")
        subtitle.setStyleSheet(f"""
            color: {T.TEXT_SECONDARY};
            font-size: 13px;
            background: transparent;
        """)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(icon_lbl)
        layout.addSpacing(8)
        layout.addWidget(title)
        layout.addSpacing(4)
        layout.addWidget(subtitle)


# Header bar

class HeaderBar(QFrame):
    """Top header with breadcrumb, search and user controls."""

    logout_requested = pyqtSignal()
    bell_clicked = pyqtSignal()

    def __init__(self, user_name: str = "Admin", role: str = "Administrator", location: str = "", parent=None):
        super().__init__(parent)
        T = PAMSTheme
        self.setFixedHeight(T.HEADER_HEIGHT)
        self.setStyleSheet(f"""
            HeaderBar {{
                background-color: {T.BG_WHITE};
                border-bottom: 1px solid {T.BORDER_LIGHT};
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 0, 24, 0)

        # Breadcrumb / page title
        self.page_label = QLabel("Dashboard")
        self.page_label.setStyleSheet(f"""
            color: {T.TEXT_DARK};
            font-size: 16px;
            font-weight: 600;
        """)
        layout.addWidget(self.page_label)
        layout.addStretch()

        # Notification bell
        bell_btn = QPushButton()
        bell_btn.setIcon(IconPainter.bell(22, T.TEXT_BODY))
        bell_btn.setIconSize(QSize(20, 20))
        bell_btn.setFixedSize(38, 38)
        bell_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        bell_btn.setToolTip("Notifications")
        bell_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {T.BG_SURFACE};
                border: 1px solid {T.BORDER_LIGHT};
                border-radius: 19px;
            }}
            QPushButton:hover {{
                background-color: #E2E8F0;
            }}
        """)
        bell_btn.clicked.connect(self.bell_clicked.emit)
        layout.addWidget(bell_btn)
        layout.addSpacing(8)

        # Avatar circle
        avatar = QLabel(user_name[0].upper())
        avatar.setFixedSize(36, 36)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet(f"""
            background-color: {T.ACCENT};
            color: {T.BG_DARKEST};
            font-size: 15px;
            font-weight: 700;
            border-radius: 18px;
        """)
        layout.addWidget(avatar)
        layout.addSpacing(8)

        # User info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(0)
        name_lbl = QLabel(user_name)
        name_lbl.setStyleSheet(f"color: {T.TEXT_DARK}; font-size: 13px; font-weight: 600;")
        role_loc_text = f"{role} — {location}" if location else role
        role_lbl = QLabel(role_loc_text)
        role_lbl.setStyleSheet(f"color: {T.TEXT_BODY}; font-size: 11px;")
        info_layout.addWidget(name_lbl)
        info_layout.addWidget(role_lbl)
        layout.addLayout(info_layout)
        layout.addSpacing(12)

        # Logout button
        logout_btn = QPushButton(" Logout")
        logout_btn.setIcon(IconPainter.logout(20, T.DANGER))
        logout_btn.setIconSize(QSize(18, 18))
        logout_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        logout_btn.setFixedHeight(34)
        logout_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {T.DANGER};
                border: 1px solid {T.DANGER};
                border-radius: 8px;
                padding: 0 14px;
                font-size: 12px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {T.DANGER};
                color: white;
            }}
        """)
        logout_btn.clicked.connect(self.logout_requested.emit)
        layout.addWidget(logout_btn)

    def set_page_title(self, title: str):
        self.page_label.setText(title)


# Sidebar

class Sidebar(QFrame):
    """Collapsible sidebar with role-based navigation."""

    nav_clicked = pyqtSignal(str)  # emits the page key

    def __init__(self, role: str = "Administrator", parent=None):
        super().__init__(parent)
        T = PAMSTheme
        self.setFixedWidth(T.SIDEBAR_WIDTH)
        self.setStyleSheet(f"""
            Sidebar {{
                background-color: {T.BG_SIDEBAR};
                border-right: 1px solid {T.BORDER_SUBTLE};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 16)
        layout.setSpacing(0)

        # Logo / Branding
        brand_frame = QWidget()
        brand_frame.setFixedHeight(72)
        brand_frame.setStyleSheet("background: transparent;")
        brand_layout = QHBoxLayout(brand_frame)
        brand_layout.setContentsMargins(20, 0, 20, 0)

        # Paragon "P" logo
        logo_label = QLabel("P")
        logo_label.setFixedSize(38, 38)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {T.ACCENT}, stop:1 {T.ACCENT_DIM});
            color: {T.BG_DARKEST};
            font-size: 20px;
            font-weight: 800;
            border-radius: 10px;
        """)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(0)
        title_lbl = QLabel("PARAGON")
        title_lbl.setStyleSheet(f"""
            color: {T.TEXT_PRIMARY};
            font-size: 15px;
            font-weight: 700;
            letter-spacing: 1.5px;
        """)
        subtitle_lbl = QLabel("Apartment Management")
        subtitle_lbl.setStyleSheet(f"""
            color: {T.TEXT_MUTED};
            font-size: 10px;
            letter-spacing: 0.5px;
        """)
        title_layout.addWidget(title_lbl)
        title_layout.addWidget(subtitle_lbl)

        brand_layout.addWidget(logo_label)
        brand_layout.addSpacing(12)
        brand_layout.addLayout(title_layout)
        brand_layout.addStretch()

        layout.addWidget(brand_frame)

        # Separator
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background-color: {T.BORDER_SUBTLE};")
        layout.addWidget(sep)
        layout.addSpacing(12)

        # Section label
        section_lbl = QLabel("   NAVIGATION")
        section_lbl.setStyleSheet(f"""
            color: {T.TEXT_MUTED};
            font-size: 10px;
            font-weight: 600;
            letter-spacing: 1.2px;
            padding-left: 20px;
        """)
        layout.addWidget(section_lbl)
        layout.addSpacing(6)

        # Nav items based on role
        self._buttons: dict[str, NavButton] = {}
        nav_items = self._get_nav_items(role)

        for key, icon, label in nav_items:
            btn = NavButton(icon, f"  {label}")
            btn.clicked.connect(lambda checked, k=key: self._on_nav_click(k))
            layout.addWidget(btn)
            self._buttons[key] = btn

        layout.addStretch()

        # Footer: location selector
        sep2 = QFrame()
        sep2.setFixedHeight(1)
        sep2.setStyleSheet(f"background-color: {T.BORDER_SUBTLE};")
        layout.addWidget(sep2)

        footer = QWidget()
        footer.setStyleSheet("background: transparent;")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(20, 12, 20, 0)

        loc_indicator = QLabel("*")
        loc_indicator.setStyleSheet(f"color: {T.SUCCESS}; font-size: 10px;")

        loc_label = QLabel("Bristol Office")
        loc_label.setStyleSheet(f"color: {T.TEXT_SECONDARY}; font-size: 12px;")

        footer_layout.addWidget(loc_indicator)
        footer_layout.addSpacing(6)
        footer_layout.addWidget(loc_label)
        footer_layout.addStretch()
        layout.addWidget(footer)

    def _get_nav_items(self, role: str) -> list:
        """Return [(key, icon, label), ...] based on user role."""
        IP = IconPainter
        T = PAMSTheme

        common = [("dashboard", IP.dashboard(20, T.TEXT_SECONDARY), "Dashboard")]

        role_map = {
            "Administrator": [
                ("users",        IP.users(20, T.TEXT_SECONDARY),    "User Management"),
                ("apartments",   IP.building(20, T.TEXT_SECONDARY), "Apartments"),
                ("tenants",      IP.users(20, T.TEXT_SECONDARY),    "Tenants"),
                ("staff",        IP.wrench(20, T.TEXT_SECONDARY),   "Staff Members"),
                ("leases",       IP.lease(20, T.TEXT_SECONDARY),    "Lease Tracking"),
                ("reports",      IP.chart(20, T.TEXT_SECONDARY),    "Reports"),
                ("settings",     IP.settings(20, T.TEXT_SECONDARY), "Settings"),
            ],
            "Manager": [
                # Manager-specific
                ("occupancy",    IP.building(20, T.TEXT_SECONDARY), "Occupancy"),
                ("expand",       IP.expand(20, T.TEXT_SECONDARY),   "Expand Business"),
                ("locations",    IP.home(20, T.TEXT_SECONDARY),     "Locations"),
                # Inherited from Administrator
                ("users",        IP.users(20, T.TEXT_SECONDARY),    "User Management"),
                ("apartments",   IP.building(20, T.TEXT_SECONDARY), "Apartments"),
                ("tenants",      IP.users(20, T.TEXT_SECONDARY),    "Tenants"),
                ("leases",       IP.lease(20, T.TEXT_SECONDARY),    "Lease Tracking"),
                ("reports",      IP.chart(20, T.TEXT_SECONDARY),    "Reports"),
                # Inherited from Front Desk
                ("register",     IP.users(20, T.TEXT_SECONDARY),    "Register Tenant"),
                ("maintenance",  IP.wrench(20, T.TEXT_SECONDARY),   "Maintenance"),
                ("complaints",   IP.lease(20, T.TEXT_SECONDARY),    "Complaints"),
                # Inherited from Finance
                ("invoices",     IP.wallet(20, T.TEXT_SECONDARY),   "Invoices"),
                ("payments",     IP.wallet(20, T.TEXT_SECONDARY),   "Payments"),
                ("late",         IP.bell(20, T.TEXT_SECONDARY),     "Late Payments"),
                ("fin_reports",  IP.chart(20, T.TEXT_SECONDARY),    "Financial Reports"),
                # Inherited from Maintenance Staff
                ("requests",     IP.wrench(20, T.TEXT_SECONDARY),   "Maint. Requests"),
                ("log",          IP.lease(20, T.TEXT_SECONDARY),    "Log Resolution"),
                ("schedule",     IP.chart(20, T.TEXT_SECONDARY),    "Schedule"),
                # Settings
                ("settings",     IP.settings(20, T.TEXT_SECONDARY), "Settings"),
            ],
            "Front Desk Staff": [
                ("register",     IP.users(20, T.TEXT_SECONDARY),    "Register Tenant"),
                ("tenants",      IP.users(20, T.TEXT_SECONDARY),    "Tenant Info"),
                ("maintenance",  IP.wrench(20, T.TEXT_SECONDARY),   "Maintenance"),
                ("complaints",   IP.lease(20, T.TEXT_SECONDARY),    "Complaints"),
            ],
            "Finance Manager": [
                ("invoices",     IP.wallet(20, T.TEXT_SECONDARY),   "Invoices"),
                ("payments",     IP.wallet(20, T.TEXT_SECONDARY),   "Payments"),
                ("late",         IP.bell(20, T.TEXT_SECONDARY),     "Late Payments"),
                ("fin_reports",  IP.chart(20, T.TEXT_SECONDARY),    "Financial Reports"),
            ],
            "Maintenance Staff": [
                ("requests",     IP.wrench(20, T.TEXT_SECONDARY),   "My Requests"),
                ("log",          IP.lease(20, T.TEXT_SECONDARY),    "Log Resolution"),
                ("schedule",     IP.chart(20, T.TEXT_SECONDARY),    "Schedule"),
            ],
            "Tenant": [
                ("my_lease",     IP.lease(20, T.TEXT_SECONDARY),    "My Lease"),
                ("my_payments",  IP.wallet(20, T.TEXT_SECONDARY),   "Payments"),
                ("my_maint",     IP.wrench(20, T.TEXT_SECONDARY),   "Maintenance"),
                ("my_profile",   IP.users(20, T.TEXT_SECONDARY),    "Profile"),
                ("notifications",IP.bell(20, T.TEXT_SECONDARY),     "Notifications"),
            ],
        }

        return common + role_map.get(role, [])

    def _on_nav_click(self, key: str):
        for k, btn in self._buttons.items():
            btn.set_active(k == key)
        self.nav_clicked.emit(key)

    def set_active(self, key: str):
        """Visually highlight the given key without emitting nav_clicked."""
        for k, btn in self._buttons.items():
            btn.set_active(k == key)


# Main Window

class MainWindow(QMainWindow):
    """
    The primary application window for PAMS.
    Receives user credentials from the LoginWindow and builds
    a role-aware layout with sidebar navigation, header, and
    a stacked content area.
    """

    logout_requested = pyqtSignal()

    def __init__(self, user_name: str = "Admin User", role: str = "Administrator",
                 location: str = "Bristol", user_id: int = 0, location_id=None, parent=None):
        super().__init__(parent)
        self._user_name = user_name
        self._role = role
        self._location = location
        self._location_id = location_id
        self._user_id = user_id

        self._setup_window()
        self._build_ui()
        self.sidebar.set_active("dashboard")

    # Window chrome

    def _setup_window(self):
        self.setWindowTitle("PAMS — Paragon Apartment Management System")
        self.setMinimumSize(1200, 750)
        self.setStyleSheet(PAMSTheme.global_stylesheet())
        self.showMaximized()

    # UI construction

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Sidebar
        self.sidebar = Sidebar(role=self._role)
        self.sidebar.nav_clicked.connect(self._navigate)
        root_layout.addWidget(self.sidebar)

        # Right-hand area (header + content)
        right = QVBoxLayout()
        right.setContentsMargins(0, 0, 0, 0)
        right.setSpacing(0)

        self.header = HeaderBar(user_name=self._user_name, role=self._role, location=self._location)
        self.header.logout_requested.connect(self.logout_requested.emit)
        # Notification bell: navigate to notifications panel (Tenant) or dashboard
        self.header.bell_clicked.connect(self._on_bell_clicked)
        right.addWidget(self.header)

        # Stacked content
        self.stack = QStackedWidget()
        self._pages: dict[str, int] = {}
        self._register_pages()
        right.addWidget(self.stack)

        root_layout.addLayout(right)

    def _register_pages(self):
        """
        Create real panels for every nav key based on the user's role.
        Dashboard gets its own rich panel; role-specific pages are
        imported from admin_panel, finance_panel, maintenance_panel, frontdesk_panel.
        """
        # Lazy imports (fault-tolerant)
        try:
            from admin_panel import (
                UserManagementPanel, ApartmentManagementPanel,
                TenantManagementPanel, LeaseTrackingPanel,
                ReportsPanel, SettingsPanel, OccupancyOverviewPanel,
                LocationManagementPanel, ExpandBusinessPanel,
                PerformanceReportsPanel, StaffManagementPanel,
            )
        except Exception:
            UserManagementPanel = ApartmentManagementPanel = None
            TenantManagementPanel = LeaseTrackingPanel = None
            ReportsPanel = SettingsPanel = OccupancyOverviewPanel = None
            LocationManagementPanel = ExpandBusinessPanel = None
            PerformanceReportsPanel = StaffManagementPanel = None

        try:
            from finance_panel import (
                InvoiceManagementPanel, PaymentManagementPanel,
                LatePaymentPanel, FinancialReportsPanel,
            )
        except Exception:
            InvoiceManagementPanel = PaymentManagementPanel = None
            LatePaymentPanel = FinancialReportsPanel = None

        try:
            from maintenance_panel import (
                MaintenanceRequestsPanel, LogResolutionPanel, SchedulePanel,
            )
        except Exception:
            MaintenanceRequestsPanel = LogResolutionPanel = SchedulePanel = None

        try:
            from frontdesk_panel import (
                RegisterTenantPanel, TenantInfoPanel,
                MaintenanceRegistrationPanel, ComplaintsPanel,
            )
        except Exception:
            RegisterTenantPanel = TenantInfoPanel = None
            MaintenanceRegistrationPanel = ComplaintsPanel = None

        try:
            from tenant_panel import (
                MyLeasePanel, MyPaymentsPanel, MyMaintenancePanel,
                MyProfilePanel, NotificationsPanel,
            )
        except Exception:
            MyLeasePanel = MyPaymentsPanel = MyMaintenancePanel = None
            MyProfilePanel = NotificationsPanel = None

        # Dashboard (all roles)
        dashboard = DashboardPanel(role=self._role, user_name=self._user_name,
                                   user_id=self._user_id,
                                   location_name=self._location,
                                   location_id=self._location_id)
        dashboard.nav_requested.connect(self._navigate)
        self._add_page("dashboard", dashboard)

        # Page-title map (used by _navigate)
        self._page_titles = {
            "dashboard": "Dashboard",
            "users": "User Management",
            "apartments": "Apartment Management",
            "tenants": "Tenant Management" if self._role == "Administrator" else "Tenant Information",
            "leases": "Lease Tracking",
            "staff": "Staff Management",
            "reports": "Reports" if self._role == "Administrator" else "Performance Reports",
            "settings": "Settings",
            "occupancy": "Occupancy Overview",
            "locations": "Location Management",
            "expand": "Expand Business",
            "register": "Register Tenant",
            "maintenance": "Maintenance Requests",
            "complaints": "Complaints & Feedback",
            "invoices": "Invoice Management",
            "payments": "Payment Management",
            "late": "Late Payment Alerts",
            "fin_reports": "Financial Reports",
            "requests": "My Maintenance Requests",
            "log": "Log Resolution",
            "schedule": "Schedule & Availability",
            "my_lease": "My Lease Agreement",
            "my_payments": "My Payments",
            "my_maint": "My Maintenance Requests",
            "my_profile": "My Profile",
            "notifications": "Notifications",
        }

        # Role → panel mapping
        role_panels = {
            "Administrator": {
                "users":       UserManagementPanel,
                "apartments":  ApartmentManagementPanel,
                "tenants":     TenantManagementPanel,
                "staff":       StaffManagementPanel,
                "leases":      LeaseTrackingPanel,
                "reports":     ReportsPanel,
                "settings":    (lambda uid: lambda: SettingsPanel(user_id=uid))(self._user_id),
            },
            "Manager": {
                # Manager-specific
                "occupancy":  OccupancyOverviewPanel,
                "reports":    PerformanceReportsPanel,
                "locations":  LocationManagementPanel,
                "expand":     ExpandBusinessPanel,
                # Inherited from Administrator
                "users":       UserManagementPanel,
                "apartments":  ApartmentManagementPanel,
                "tenants":     TenantManagementPanel,
                "leases":      LeaseTrackingPanel,
                "settings":    (lambda uid: lambda: SettingsPanel(user_id=uid))(self._user_id),
                # Inherited from Front Desk
                "register":    RegisterTenantPanel,
                "maintenance": MaintenanceRegistrationPanel,
                "complaints":  ComplaintsPanel,
                # Inherited from Finance
                "invoices":    InvoiceManagementPanel,
                "payments":    PaymentManagementPanel,
                "late":        LatePaymentPanel,
                "fin_reports": FinancialReportsPanel,
                # Inherited from Maintenance Staff
                "requests":    MaintenanceRequestsPanel,
                "log":         LogResolutionPanel,
                "schedule":    SchedulePanel,
            },
            "Front Desk Staff": {
                "register":    (lambda ln: lambda: RegisterTenantPanel(location_name=ln))(self._location),
                "tenants":     (lambda ln: lambda: TenantInfoPanel(location_name=ln))(self._location),
                "maintenance": (lambda ln: lambda: MaintenanceRegistrationPanel(location_name=ln))(self._location),
                "complaints":  (lambda ln: lambda: ComplaintsPanel(location_name=ln))(self._location),
            },
            "Finance Manager": {
                "invoices":     (lambda ln: lambda: InvoiceManagementPanel(location_name=ln))(self._location),
                "payments":     (lambda ln: lambda: PaymentManagementPanel(location_name=ln))(self._location),
                "late":         (lambda ln: lambda: LatePaymentPanel(location_name=ln))(self._location),
                "fin_reports":  (lambda ln: lambda: FinancialReportsPanel(location_name=ln))(self._location),
            },
            "Maintenance Staff": {
                "requests":  (lambda ln: lambda: MaintenanceRequestsPanel(location_name=ln))(self._location),
                "log":       (lambda ln: lambda: LogResolutionPanel(location_name=ln))(self._location),
                "schedule":  (lambda ln: lambda: SchedulePanel(location_name=ln))(self._location),
            },
            "Tenant": {
                "my_lease":      (lambda uid: lambda: MyLeasePanel(user_id=uid))(self._user_id),
                "my_payments":   (lambda uid: lambda: MyPaymentsPanel(user_id=uid))(self._user_id),
                "my_maint":      (lambda uid: lambda: MyMaintenancePanel(user_id=uid))(self._user_id),
                "my_profile":    (lambda uid: lambda: MyProfilePanel(user_id=uid))(self._user_id),
                "notifications": (lambda uid: lambda: NotificationsPanel(user_id=uid))(self._user_id),
            },
        }

        # Create panels for the current role (skip None classes from failed imports)
        panels = role_panels.get(self._role, {})
        for key, PanelClass in panels.items():
            if PanelClass is not None:
                try:
                    self._add_page(key, PanelClass())
                except Exception:
                    self._add_page(key, PlaceholderPanel(
                        self._page_titles.get(key, key.replace("_", " ").title())
                    ))

        # Any remaining nav keys that don't have a page yet get placeholders
        all_nav_keys = list(self._page_titles.keys())
        for key in all_nav_keys:
            if key not in self._pages:
                self._add_page(key, PlaceholderPanel(self._page_titles[key]))

    def _add_page(self, key: str, widget: QWidget):
        idx = self.stack.addWidget(widget)
        self._pages[key] = idx

    # Navigation

    def _navigate(self, key: str):
        """Switch the stacked widget and update the header breadcrumb."""
        if key in self._pages:
            self.stack.setCurrentIndex(self._pages[key])
            title = getattr(self, "_page_titles", {}).get(
                key, key.replace("_", " ").title()
            )
            self.header.set_page_title(title)
            self.sidebar.set_active(key)  # visual-only, no signal

    def _on_bell_clicked(self):
        """Navigate to notifications for Tenants, or show dashboard for other roles."""
        if self._role == "Tenant" and "notifications" in self._pages:
            self._navigate("notifications")
        else:
            self._navigate("dashboard")

    # Public API for panel swapping

    def replace_page(self, key: str, widget: QWidget):
        """
        Swap a placeholder with a real panel.
        Usage:
            main_window.replace_page("tenants", TenantPanel())
        """
        if key in self._pages:
            old_idx = self._pages[key]
            old_widget = self.stack.widget(old_idx)
            self.stack.removeWidget(old_widget)
            old_widget.deleteLater()
        idx = self.stack.addWidget(widget)
        self._pages[key] = idx


# Entry point (standalone demo)

def main():
    app = QApplication(sys.argv)

    # Load system font (Segoe UI ships with Windows; falls back gracefully)
    app.setStyle("Fusion")

    # Demo: launch as Administrator
    window = MainWindow(
        user_name="Haso",
        role="Administrator",
        location="Bristol"
    )
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()