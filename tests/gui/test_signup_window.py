"""

24063400 - Rayyan Tahir

Unit tests for PAMS SignupWindow — validation and registration logic.

DB calls (signup, does_user_exist, get_role_by_code) are mocked via
sys.modules so no live database connection is required.

Tests cover:
  TC-AUTH-04  Tenant Registration Success
      -> valid form data + mocked DB → success banner shown, button disabled
  TC-AUTH-05  Staff Registration — Invalid Staff Code (Edge Case)
      -> get_role_by_code returns None → error message shown, user not created
  TC-AUTH-06  Duplicate Username / Email Detection (Edge Case)
      -> does_user_exist returns True → error message shown

Additional validation edge-case tests:
  - Empty first name
  - Empty last name
  - Invalid / missing email (no '@')
  - Empty phone number
  - Username too short (< 3 chars)
  - Password too short (< 8 chars)
  - Mismatched passwords
  - Staff role with missing code

Run with:
    pytest tests/gui/test_signup_window.py -v
"""

import importlib.util
import pathlib
import sys
import types
import pytest

from unittest.mock import MagicMock, patch
from PyQt6.QtCore import QDate

def load_signup_module():
    """Load signup_window.py dynamically without modifying project structure."""
    file_path = pathlib.Path("src/gui/signup_window.py").resolve()
    spec = importlib.util.spec_from_file_location("signup_window", file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

@pytest.fixture(scope="module")
def signup_module():
    return load_signup_module()


@pytest.fixture
def signup_window(qtbot, signup_module):
    """Create a fresh SignupWindow for each test."""
    window = signup_module.SignupWindow()
    qtbot.addWidget(window)
    return window

def _fill_valid_tenant(window):
    """Populate every required field with valid tenant data."""
    window._fname_field.input_field.setText("Alice")
    window._lname_field.input_field.setText("Smith")
    window._email_field.input_field.setText("alice@example.com")
    window._phone_field.input_field.setText("+44 7700 000001")
    window._dob_edit.setDate(QDate(1995, 6, 15))
    window._role_combo.setCurrentText("Tenant")
    window._username_field.input_field.setText("alice123")
    window._password_field.input_field.setText("SecurePass1")
    window._confirm_password_field.input_field.setText("SecurePass1")


def _fill_valid_staff(window, code="VALIDCODE"):
    """Populate every required field with valid staff data."""
    _fill_valid_tenant(window)
    window._role_combo.setCurrentText("Staff")
    window._staff_code_field.input_field.setText(code)


def _make_mock_models(signup_result=True, user_exists=False, role_by_code="Front Desk Staff"):
    """Build a mock 'models' module with controllable return values."""
    m = types.ModuleType("models")
    m.signup = MagicMock(return_value=signup_result)
    m.does_user_exist = MagicMock(return_value=user_exists)
    m.get_role_by_code = MagicMock(return_value=role_by_code)
    return m

class TestTenantRegistrationSuccess:
    """TC-AUTH-04: All fields valid, DB accepts the new user."""

    def test_signup_button_disabled_on_submit(self, qtbot, signup_window):
        """
        TC-AUTH-04 step 3: After clicking submit with valid data and a mocked
        successful DB call, the 'Create Account' button is disabled while the
        1 500 ms success timer runs.
        """
        _fill_valid_tenant(signup_window)
        mock_models = _make_mock_models(signup_result=True, user_exists=False)

        with patch.dict(sys.modules, {"models": mock_models}):
            signup_window._on_signup_clicked()

        assert not signup_window._signup_btn.isEnabled()

    def test_success_message_visible(self, qtbot, signup_window):
        """
        TC-AUTH-04: A success message is visible after a valid registration.
        """
        _fill_valid_tenant(signup_window)
        mock_models = _make_mock_models(signup_result=True, user_exists=False)

        with patch.dict(sys.modules, {"models": mock_models}):
            signup_window._on_signup_clicked()

        assert signup_window._message_label.isVisibleTo(signup_window)
        text = signup_window._message_label.text()
        assert "successfully" in text.lower() or "created" in text.lower()

    def test_db_signup_called_with_tenant_role(self, qtbot, signup_window):
        """
        TC-AUTH-04: The underlying signup() DB call is invoked with role='Tenant'.
        """
        _fill_valid_tenant(signup_window)
        mock_models = _make_mock_models(signup_result=True, user_exists=False)

        with patch.dict(sys.modules, {"models": mock_models}):
            signup_window._on_signup_clicked()
        call_args = mock_models.signup.call_args
        assert call_args is not None, "signup() was never called"
        _, role_arg = call_args[0][0], call_args[0][5]
        assert role_arg == "Tenant"

class TestStaffInvalidCode:
    """TC-AUTH-05: Staff selected but get_role_by_code returns None."""

    def test_invalid_staff_code_shows_error(self, qtbot, signup_window):
        """
        TC-AUTH-05 step 3: An unrecognised staff code shows an error message.
        """
        _fill_valid_staff(signup_window, code="WRONG123")
        mock_models = _make_mock_models(role_by_code=None)

        with patch.dict(sys.modules, {"models": mock_models}):
            signup_window._on_signup_clicked()

        assert signup_window._message_label.isVisibleTo(signup_window)
        assert "invalid staff code" in signup_window._message_label.text().lower()

    def test_invalid_staff_code_does_not_call_signup(self, qtbot, signup_window):
        """
        TC-AUTH-05: signup() must NOT be called when the staff code is invalid.
        """
        _fill_valid_staff(signup_window, code="WRONG123")
        mock_models = _make_mock_models(role_by_code=None)

        with patch.dict(sys.modules, {"models": mock_models}):
            signup_window._on_signup_clicked()

        mock_models.signup.assert_not_called()

    def test_invalid_staff_code_button_re_enabled(self, qtbot, signup_window):
        """
        TC-AUTH-05: The button must be re-enabled so the user can correct the code.
        """
        _fill_valid_staff(signup_window, code="WRONG123")
        mock_models = _make_mock_models(role_by_code=None)

        with patch.dict(sys.modules, {"models": mock_models}):
            signup_window._on_signup_clicked()

        assert signup_window._signup_btn.isEnabled()

    def test_empty_staff_code_shows_error(self, qtbot, signup_window):
        """
        TC-AUTH-05 (edge): Leaving the staff code blank also shows an error
        before any DB call is made.
        """
        _fill_valid_staff(signup_window, code="")
        signup_window._staff_code_field.input_field.clear()

        signup_window._on_signup_clicked()

        assert signup_window._message_label.isVisibleTo(signup_window)
        assert "staff" in signup_window._message_label.text().lower()

class TestDuplicateUserDetection:
    """TC-AUTH-06: does_user_exist returns True → registration blocked."""

    def test_duplicate_shows_error(self, qtbot, signup_window):
        """
        TC-AUTH-06 step 2: Submitting with an already-registered email shows
        the duplicate-user error message.
        """
        _fill_valid_tenant(signup_window)
        mock_models = _make_mock_models(user_exists=True)

        with patch.dict(sys.modules, {"models": mock_models}):
            signup_window._on_signup_clicked()

        assert signup_window._message_label.isVisibleTo(signup_window)
        assert "already exists" in signup_window._message_label.text().lower()

    def test_duplicate_does_not_call_signup(self, qtbot, signup_window):
        """
        TC-AUTH-06: signup() must NOT be called when the user already exists.
        """
        _fill_valid_tenant(signup_window)
        mock_models = _make_mock_models(user_exists=True)

        with patch.dict(sys.modules, {"models": mock_models}):
            signup_window._on_signup_clicked()

        mock_models.signup.assert_not_called()

    def test_duplicate_button_re_enabled(self, qtbot, signup_window):
        """
        TC-AUTH-06: The button must be re-enabled so the user can change details.
        """
        _fill_valid_tenant(signup_window)
        mock_models = _make_mock_models(user_exists=True)

        with patch.dict(sys.modules, {"models": mock_models}):
            signup_window._on_signup_clicked()

        assert signup_window._signup_btn.isEnabled()

class TestClientSideValidation:
    """Validation errors raised before any DB call is made."""

    def test_empty_first_name(self, qtbot, signup_window):
        _fill_valid_tenant(signup_window)
        signup_window._fname_field.input_field.clear()
        signup_window._on_signup_clicked()
        assert "first name" in signup_window._message_label.text().lower()

    def test_empty_last_name(self, qtbot, signup_window):
        _fill_valid_tenant(signup_window)
        signup_window._lname_field.input_field.clear()
        signup_window._on_signup_clicked()
        assert "last name" in signup_window._message_label.text().lower()

    def test_invalid_email_no_at(self, qtbot, signup_window):
        _fill_valid_tenant(signup_window)
        signup_window._email_field.input_field.setText("notanemail")
        signup_window._on_signup_clicked()
        assert "email" in signup_window._message_label.text().lower()

    def test_empty_phone(self, qtbot, signup_window):
        _fill_valid_tenant(signup_window)
        signup_window._phone_field.input_field.clear()
        signup_window._on_signup_clicked()
        assert "phone" in signup_window._message_label.text().lower()

    def test_username_too_short(self, qtbot, signup_window):
        _fill_valid_tenant(signup_window)
        signup_window._username_field.input_field.setText("ab")
        signup_window._on_signup_clicked()
        assert "username" in signup_window._message_label.text().lower()

    def test_password_too_short(self, qtbot, signup_window):
        _fill_valid_tenant(signup_window)
        signup_window._password_field.input_field.setText("short")
        signup_window._confirm_password_field.input_field.setText("short")
        signup_window._on_signup_clicked()
        assert "password" in signup_window._message_label.text().lower()

    def test_password_mismatch(self, qtbot, signup_window):
        _fill_valid_tenant(signup_window)
        signup_window._confirm_password_field.input_field.setText("DifferentPass9")
        signup_window._on_signup_clicked()
        assert "match" in signup_window._message_label.text().lower()

    def test_validation_error_no_db_call(self, qtbot, signup_window):
        """Client-side validation must block the DB call entirely."""
        signup_window._fname_field.input_field.clear()
        mock_models = _make_mock_models()

        with patch.dict(sys.modules, {"models": mock_models}):
            signup_window._on_signup_clicked()

        mock_models.signup.assert_not_called()
        mock_models.does_user_exist.assert_not_called()

class TestReset:

    def test_reset_clears_fields(self, qtbot, signup_window):
        _fill_valid_tenant(signup_window)
        signup_window.reset()
        assert signup_window._fname_field.input_field.text() == ""
        assert signup_window._lname_field.input_field.text() == ""
        assert signup_window._email_field.input_field.text() == ""

    def test_reset_re_enables_button(self, qtbot, signup_window):
        signup_window._signup_btn.setEnabled(False)
        signup_window.reset()
        assert signup_window._signup_btn.isEnabled()

    def test_reset_hides_message(self, qtbot, signup_window):
        signup_window._message_label.setVisible(True)
        signup_window.reset()
        assert not signup_window._message_label.isVisibleTo(signup_window)
