"""

24063400 - Rayyan Tahir

GUI Component Tests for PAMS Login Window

Test Coverage:
  - TC-AUTH-01: Successful login flow
  - TC-AUTH-02: Empty username validation
  - TC-AUTH-03: Empty password validation
  - TC-AUTH-04: Invalid credentials counter
  - TC-AUTH-05: Three attempts warning
  - TC-AUTH-06: Account lockout at five attempts
  - TC-AUTH-07: Reset functionality
  - TC-AUTH-08: Signup success banner
  - TC-AUTH-09: Location dropdown fallback
  - TC-AUTH-10: Login success signal emission

Run with:
    pytest tests/gui/test_login_window.py -v
    pytest tests/gui/test_login_window.py -v --cov=src/gui/login_window.py
23010646 - Hasaan Ahmad
"""

import importlib.util
import pathlib
import pytest
from unittest.mock import patch
from PyQt6.QtCore import Qt


def load_login_module():
    """Load login_window.py dynamically without modifying project structure."""
    file_path = pathlib.Path("src/gui/login_window.py").resolve()
    spec = importlib.util.spec_from_file_location("login_window", file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def login_module():
    return load_login_module()


@pytest.fixture
def login_window(qtbot, login_module):
    """Create the LoginWindow instance for testing."""
    window = login_module.LoginWindow()
    qtbot.addWidget(window)
    return window
def test_empty_username_shows_error(qtbot, login_window):
    login_window._username_field.input_field.setText("")
    login_window._password_field.input_field.setText("password")

    login_window._on_login_clicked()

    assert login_window._error_label.isVisibleTo(login_window)
    assert "Please enter your username" in login_window._error_label.text()


def test_empty_password_shows_error(qtbot, login_window):
    login_window._username_field.input_field.setText("admin")
    login_window._password_field.input_field.setText("")

    login_window._on_login_clicked()

    assert login_window._error_label.isVisibleTo(login_window)
    assert "Please enter your password" in login_window._error_label.text()
def test_invalid_credentials_increments_attempts(qtbot, login_window):
    """Failed login increments _attempts and shows an error."""
    import builtins, types
    real_import = builtins.__import__
    def fake_import(name, *args, **kwargs):
        if name == "models":
            m = types.ModuleType("models")
            m.login = lambda u, p: None
            return m
        return real_import(name, *args, **kwargs)
    login_window._username_field.input_field.setText("wronguser")
    login_window._password_field.input_field.setText("wrongpass")
    with patch("builtins.__import__", side_effect=fake_import):
        login_window._on_login_clicked()
    assert login_window._attempts == 1
    assert login_window._error_label.isVisibleTo(login_window)


def test_attempts_warning_at_three(qtbot, login_window):
    """After 3 failed attempts the error message mentions 'attempts remaining'."""
    login_window._attempts = 2  # prime to 2; next click takes it to 3
    import builtins, types
    real_import = builtins.__import__
    def fake_import(name, *args, **kwargs):
        if name == "models":
            m = types.ModuleType("models")
            m.login = lambda u, p: None
            return m
        return real_import(name, *args, **kwargs)
    login_window._username_field.input_field.setText("user")
    login_window._password_field.input_field.setText("pass")
    with patch("builtins.__import__", side_effect=fake_import):
        login_window._on_login_clicked()
    assert login_window._attempts == 3
    assert "attempts remaining" in login_window._error_label.text()


def test_lockout_at_five_attempts(qtbot, login_window):
    """After 5 failed attempts the login button is disabled."""
    login_window._attempts = 4  # prime to 4; next click takes it to 5
    import builtins, types
    real_import = builtins.__import__
    def fake_import(name, *args, **kwargs):
        if name == "models":
            m = types.ModuleType("models")
            m.login = lambda u, p: None
            return m
        return real_import(name, *args, **kwargs)
    login_window._username_field.input_field.setText("user")
    login_window._password_field.input_field.setText("pass")
    with patch("builtins.__import__", side_effect=fake_import):
        login_window._on_login_clicked()
    assert login_window._attempts == 5
    assert not login_window._login_btn.isEnabled()
    assert "locked" in login_window._error_label.text().lower()
def test_reset_clears_fields_and_state(qtbot, login_window):
    """reset() clears inputs, re-enables the button, and zeroes _attempts."""
    login_window._username_field.input_field.setText("testuser")
    login_window._password_field.input_field.setText("testpass")
    login_window._attempts = 3
    login_window._login_btn.setEnabled(False)
    login_window._error_label.setVisible(True)

    login_window.reset()

    assert login_window._username_field.input_field.text() == ""
    assert login_window._password_field.input_field.text() == ""
    assert login_window._attempts == 0
    assert login_window._login_btn.isEnabled()
    assert login_window._login_btn.text() == "Sign In"
    assert not login_window._error_label.isVisibleTo(login_window)
def test_show_signup_success_displays_banner(qtbot, login_window):
    """show_signup_success() makes success label visible and hides error label."""
    login_window._error_label.setVisible(True)

    login_window.show_signup_success("Account created successfully! Please sign in.")

    assert login_window._success_label.isVisibleTo(login_window)
    assert "Account created" in login_window._success_label.text()
    assert not login_window._error_label.isVisibleTo(login_window)
def test_login_window_has_no_location_dropdown(qtbot, login_window):
    """Location dropdown was removed; location is now auto-resolved from DB."""
    assert not hasattr(login_window, '_location_combo')
    assert not hasattr(login_window, '_populate_locations')
def test_successful_login_disables_button_and_updates_text(qtbot, login_window):
    """
    TC-AUTH-01: When the DB returns a valid user, the login button is immediately
    disabled and its text changes to 'Signing in…'.
    Mirrors _on_login_clicked() success branch.
    """
    import builtins, types
    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "models":
            m = types.ModuleType("models")
            m.login = lambda u, p: {
                "name": "Haso", "role": "Administrator", "user_id": 1,
                "location_id": None, "location_name": None,
            }
            return m
        return real_import(name, *args, **kwargs)

    login_window._username_field.input_field.setText("haso_admin")
    login_window._password_field.input_field.setText("Admin1234!")

    with patch("builtins.__import__", side_effect=fake_import):
        login_window._on_login_clicked()
    assert not login_window._login_btn.isEnabled()
    assert "Signing in" in login_window._login_btn.text()
    assert not login_window._error_label.isVisibleTo(login_window)
def test_complete_login_emits_signal(qtbot, login_window):
    """_complete_login emits login_success with the correct 5 arguments (name, role, location_name, user_id, location_id)."""
    received = []
    login_window.login_success.connect(
        lambda name, role, loc, uid, lid: received.append((name, role, loc, uid, lid))
    )

    login_window._complete_login("Alice", "Tenant", "Bristol", 42, 1)

    assert len(received) == 1
    assert received[0] == ("Alice", "Tenant", "Bristol", 42, 1)


def test_complete_login_emits_none_location_for_admin(qtbot, login_window):
    """Admin/Manager login emits location_id=None."""
    received = []
    login_window.login_success.connect(
        lambda name, role, loc, uid, lid: received.append((name, role, loc, uid, lid))
    )

    login_window._complete_login("Haso", "Administrator", "All Locations", 1, None)

    assert len(received) == 1
    assert received[0] == ("Haso", "Administrator", "All Locations", 1, None)
