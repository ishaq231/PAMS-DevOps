# Authentication Test Evidence Pack

## TC Mapping

| Test Case ID | Automated Test Name | Source File |
|---|---|---|
| TC-AUTH-01 | `test_successful_login_disables_button_and_updates_text` | `tests/gui/test_login_window.py` |
| TC-AUTH-02 | `test_invalid_credentials_increments_attempts` | `tests/gui/test_login_window.py` |
| TC-AUTH-03 | `test_lockout_at_five_attempts` | `tests/gui/test_login_window.py` |
| TC-AUTH-04 | `TestTenantRegistrationSuccess::test_success_message_visible` | `tests/gui/test_signup_window.py` |
| TC-AUTH-05 | `TestStaffInvalidCode::test_invalid_staff_code_shows_error` | `tests/gui/test_signup_window.py` |
| TC-AUTH-06 | `TestDuplicateUserDetection::test_duplicate_shows_error` | `tests/gui/test_signup_window.py` |
| TC-AUTH-07 | `TestRoleNavItems::test_tenant_personal_keys` + `test_tenant_no_admin_keys` | `tests/gui/test_main_window.py` |

---

## Pytest Output (from `docs/auth_test_evidence.txt`)

```text
============================= test session starts ==============================
platform darwin -- Python 3.14.0, pytest-9.0.2, pluggy-1.6.0 -- /Users/rayantahyr/Desktop/advance-software-dev/UFCF8S-30-2-Advanced-Software-Development-Project/venv/bin/python3.14
cachedir: .pytest_cache
PyQt6 6.10.2 -- Qt runtime 6.10.2 -- Qt compiled 6.10.0
rootdir: /Users/rayantahyr/Desktop/advance-software-dev/UFCF8S-30-2-Advanced-Software-Development-Project
plugins: qt-4.5.0
collecting ... collected 8 items

tests/gui/test_login_window.py::test_successful_login_disables_button_and_updates_text PASSED [ 12%]
tests/gui/test_login_window.py::test_invalid_credentials_increments_attempts PASSED [ 25%]
tests/gui/test_login_window.py::test_lockout_at_five_attempts PASSED     [ 37%]
tests/gui/test_signup_window.py::TestTenantRegistrationSuccess::test_success_message_visible PASSED [ 50%]
tests/gui/test_signup_window.py::TestStaffInvalidCode::test_invalid_staff_code_shows_error PASSED [ 62%]
tests/gui/test_signup_window.py::TestDuplicateUserDetection::test_duplicate_shows_error PASSED [ 75%]
tests/gui/test_main_window.py::TestRoleNavItems::test_tenant_personal_keys PASSED [ 87%]
tests/gui/test_main_window.py::TestRoleNavItems::test_tenant_no_admin_keys PASSED [100%]

============================== 8 passed in 1.41s ===============================
```
