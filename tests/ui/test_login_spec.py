import pytest

from pages.Login_Page.login_page import LoginPage


# =============================================================================
# TC01 – TC05 | Login Page UI
# =============================================================================

@pytest.mark.regression
class TestLoginPageUIElements:

    @pytest.fixture(autouse=True)
    def navigate_before_each(self, driver):
        """
        Open Login page before every UI test.
        """
        self.login_page = LoginPage(driver)
        self.login_page.navigate()

    # =========================================================================
    # TC01-P | Smoke + Regression
    # =========================================================================

    @pytest.mark.smoke
    def test_tc01_p_page_loads_with_all_elements_visible(self):
        """
        Verify all critical login page elements are displayed.
        """

        login_page = self.login_page  #-----lp -> LoginPage instance

        assert login_page.is_login_page()

        assert login_page.is_username_visible()
        assert login_page.is_password_visible()
        assert login_page.is_sign_in_visible()
        assert login_page.is_remember_me_visible()
        assert login_page.is_forgot_password_visible()

        print(
            "✅ TC01-P PASSED - "
            "Login page loaded with all elements visible"
        )

    # =========================================================================
    # TC01-N | Regression
    # =========================================================================

    @pytest.mark.negative
    def test_tc01_n_no_dashboard_elements_when_not_logged_in(self):
        """
        Verify dashboard elements are not accessible before authentication.
        """

        login_page = self.login_page  #-----lp -> LoginPage instance

        assert login_page.is_login_page()

        assert login_page.is_dashboard_element_visible() is False

        assert login_page.is_sign_in_visible()

        print(
            "✅ TC01-N PASSED - "
            "Dashboard elements are not visible before login"
        )

    # =========================================================================
    # TC02-P | Smoke + Regression
    # =========================================================================

    @pytest.mark.smoke
    def test_tc02_p_fields_empty_by_default(self):
        """
        Verify email and password fields are empty on a fresh login page.
        """

        login_page = self.login_page

        assert login_page.get_email_field_value() == ""
        assert login_page.get_password_field_value() == ""

        print(
            "✅ TC02-P PASSED - "
            "Email and password fields are empty by default"
        )

    # =========================================================================
    # TC02-N | Regression
    # =========================================================================

    def test_tc02_n_fields_do_not_autofill_on_fresh_session(self):
        """
        Verify credentials are not automatically populated.
        """

        login_page = self.login_page

        assert login_page.get_email_field_value() == ""
        assert login_page.get_password_field_value() == ""

        print(
            "✅ TC02-N PASSED - "
            "Credentials are not autofilled"
        )

    # =========================================================================
    # TC03-P | Smoke + Regression
    # =========================================================================

    @pytest.mark.smoke
    def test_tc03_p_remember_me_unchecked_by_default(self):
        """
        Verify Remember Me is unchecked by default.
        """

        login_page = self.login_page

        assert login_page.is_remember_me_visible()
        assert login_page.is_remember_me_checked() is False

        print(
            "✅ TC03-P PASSED - "
            "Remember Me is unchecked by default"
        )

    # =========================================================================
    # TC03-N | Regression
    # =========================================================================

    def test_tc03_n_remember_me_does_not_persist_across_fresh_load(
        self,
        driver
    ):
        """
        Verify Remember Me does not remain selected after refresh.
        """

        login_page = self.login_page

        assert login_page.is_remember_me_checked() is False

        driver.refresh()

        login_page.wait_for_login_page()

        assert login_page.is_remember_me_checked() is False

        print(
            "✅ TC03-N PASSED - "
            "Remember Me does not persist after refresh"
        )

    # =========================================================================
    # TC04-P | Regression
    # =========================================================================

    def test_tc04_p_password_field_masks_input(self):
        """
        Verify password field uses type=password.
        """

        login_page = self.login_page

        assert login_page.get_password_input_type() == "password"
        assert login_page.is_password_field_enabled()

        print(
            "✅ TC04-P PASSED - "
            "Password field is masked"
        )

    # =========================================================================
    # TC04-N | Security + Regression
    # =========================================================================

    @pytest.mark.security
    def test_tc04_n_password_field_does_not_expose_typed_text(self):
        """
        Verify password input remains type=password after typing.
        """

        login_page = self.login_page

        login_page.enter_password(
            "MySecretPass123"
        )

        assert login_page.get_password_input_type() == "password"

        assert (
            login_page.get_password_field_value()
            == "MySecretPass123"
        )

        print(
            "✅ TC04-N PASSED - "
            "Password field remains masked after typing"
        )

    # =========================================================================
    # TC05-P | Smoke + Regression
    # =========================================================================

    @pytest.mark.smoke
    def test_tc05_p_email_field_accepts_email_type_input(self):
        """
        Verify email input is rendered as type=email.
        """

        login_page = self.login_page

        assert login_page.get_email_input_type() == "email"
        assert login_page.is_email_field_enabled()

        print(
            "✅ TC05-P PASSED - "
            "Email field has type=email"
        )

    # =========================================================================
    # TC05-N | Negative + Regression
    # =========================================================================

    @pytest.mark.negative
    def test_tc05_n_email_field_rejects_invalid_format_via_html5(
        self,
        valid_password
    ):
        """
        Verify browser HTML5 validation rejects invalid email.
        """

        login_page = self.login_page

        login_page.fill_credentials(
            "notanemail",
            valid_password
        )

        login_page.click_sign_in()

        assert login_page.is_login_page()

        validation_message = (
            login_page.get_email_validation_message()
        )

        assert validation_message != ""

        print(
            "✅ TC05-N PASSED - "
            "Invalid email format is rejected"
        )


# =============================================================================
# TC06 – TC10 | Login Functional Tests
# =============================================================================

@pytest.mark.regression
class TestLoginFunctional:

    @pytest.fixture(autouse=True)
    def navigate_before_each(self, driver):
        """
        Open Login page before every functional test.
        """
        self.login_page = LoginPage(driver)
        self.login_page.navigate()

    # =========================================================================
    # TC06-P | Smoke + Regression
    # =========================================================================

    @pytest.mark.smoke
    def test_tc06_p_valid_credentials_navigate_away_from_login(
        self,
        valid_email,
        valid_password
    ):
        """
        Verify valid credentials successfully authenticate the user.
        """

        login_page = self.login_page

        login_page.login(
            valid_email,
            valid_password
        )

        login_page.wait_until_logged_in()

        assert login_page.is_logged_in()

        assert login_page.is_username_visible() is False
        assert login_page.is_password_visible() is False

        login_page.take_screenshot(
            "TC06-P-login-success"
        )

        print(
            "✅ TC06-P PASSED - "
            "Valid credentials logged in successfully"
        )

    # =========================================================================
    # TC06-N | Negative + Regression
    # =========================================================================

    @pytest.mark.negative
    def test_tc06_n_wrong_case_password_fails(
        self,
        valid_email,
        valid_password
    ):
        """
        Verify passwords are case-sensitive.
        """

        login_page = self.login_page

        wrong_case = "".join(
            c.lower()
            if c.isupper()
            else c.upper()
            for c in valid_password
        )

        login_page.login(
            valid_email,
            wrong_case
        )

        login_page.wait_for_error_message()

        assert login_page.is_login_page()
        assert login_page.is_username_visible()

        login_page.take_screenshot(
            "TC06-N-wrong-case-password"
        )

        print(
            "✅ TC06-N PASSED - "
            "Wrong-case password failed"
        )

    # =========================================================================
    # TC07-P | Negative + Regression
    # =========================================================================

    @pytest.mark.negative
    def test_tc07_p_invalid_email_and_password_stays_on_login(
        self,
        invalid_email,
        invalid_password
    ):
        """
        Verify invalid credentials do not authenticate the user.
        """

        login_page = self.login_page

        login_page.login(
            invalid_email,
            invalid_password
        )

        login_page.wait_for_error_message()

        assert login_page.is_login_page()

        assert login_page.is_username_visible()
        assert login_page.is_password_visible()

        login_page.take_screenshot(
            "TC07-P-invalid-credentials"
        )

        print(
            "✅ TC07-P PASSED - "
            "Invalid credentials stayed on login page"
        )

    # =========================================================================
    # TC07-N | Smoke + Regression
    # =========================================================================

    @pytest.mark.smoke
    @pytest.mark.negative
    def test_tc07_n_error_message_shown_on_failed_login(
        self,
        invalid_email,
        invalid_password
    ):
        """
        Verify appropriate error is displayed after failed login.
        """

        login_page = self.login_page

        login_page.login(
            invalid_email,
            invalid_password
        )

        login_page.wait_for_error_message()

        assert login_page.is_login_page()
        assert login_page.is_error_message_visible()

        login_page.take_screenshot(
            "TC07-N-error-message-shown"
        )

        print(
            "✅ TC07-N PASSED - "
            "Error message displayed after failed login"
        )

    # =========================================================================
    # TC08-P | Regression
    # =========================================================================

    @pytest.mark.negative
    def test_tc08_p_valid_email_wrong_password_stays_on_login(
        self,
        valid_email,
        invalid_password
    ):
        """
        Verify valid email with invalid password cannot login.
        """

        login_page = self.login_page

        login_page.login(
            valid_email,
            invalid_password
        )

        login_page.wait_for_error_message()

        assert login_page.is_login_page()

        assert login_page.is_username_visible()

        login_page.take_screenshot(
            "TC08-P-wrong-password"
        )

        print(
            "✅ TC08-P PASSED - "
            "Wrong password stayed on login page"
        )

    # =========================================================================
    # TC08-N | Regression
    # =========================================================================

    @pytest.mark.negative
    def test_tc08_n_password_not_cleared_after_failed_login(
        self,
        valid_email,
        invalid_password
    ):
        """
        Verify password remains available after failed login.
        """

        login_page = self.login_page

        login_page.login(
            valid_email,
            invalid_password
        )

        login_page.wait_for_error_message()

        assert login_page.is_login_page()
        assert login_page.is_error_message_visible()

        error_text = (
            login_page.get_error_message_text()
        )

        assert len(error_text) > 0

        assert (
            login_page.get_password_field_value()
            == invalid_password
        )

        login_page.take_screenshot(
            "TC08-N-error-popup"
        )

        print(
            "✅ TC08-N PASSED - "
            "Password remained after failed login"
        )

    # =========================================================================
    # TC09-P | Regression
    # =========================================================================

    @pytest.mark.negative
    def test_tc09_p_wrong_email_valid_password_stays_on_login(
        self,
        invalid_email,
        valid_password
    ):
        """
        Verify invalid email cannot authenticate.
        """

        login_page = self.login_page

        login_page.login(
            invalid_email,
            valid_password
        )

        login_page.wait_for_error_message()

        assert login_page.is_login_page()
        assert login_page.is_sign_in_visible()

        login_page.take_screenshot(
            "TC09-P-wrong-email"
        )

        print(
            "✅ TC09-P PASSED - "
            "Wrong email stayed on login page"
        )

    # =========================================================================
    # TC09-N | Security + Regression
    # =========================================================================

    @pytest.mark.security
    @pytest.mark.negative
    def test_tc09_n_error_does_not_reveal_email_existence(
        self,
        invalid_password
    ):
        """
        Verify login errors do not disclose whether email exists.
        """

        login_page = self.login_page

        login_page.login(
            "unknown@notexist.com",
            invalid_password
        )

        login_page.wait_for_error_message()

        assert login_page.is_login_page()

        error_text = (
            login_page.get_error_message_text()
            .lower()
        )

        assert "email not found" not in error_text
        assert "user not found" not in error_text
        assert "no account" not in error_text
        assert "does not exist" not in error_text

        login_page.take_screenshot(
            "TC09-N-no-user-enumeration"
        )

        print(
            "✅ TC09-N PASSED - "
            "Error does not reveal email existence"
        )

    # =========================================================================
    # TC10-P | Smoke + Regression
    # =========================================================================

    @pytest.mark.smoke
    @pytest.mark.negative
    def test_tc10_p_both_fields_empty_stays_on_login(self):
        """
        Verify login cannot be submitted with both fields empty.
        """

        login_page = self.login_page

        login_page.login(
            "",
            ""
        )

        assert login_page.is_login_page()

        assert (
            login_page.get_email_field_value()
            == ""
        )

        assert (
            login_page.get_password_field_value()
            == ""
        )

        assert (
            login_page.is_sign_in_enabled()
            is False
        )

        login_page.take_screenshot(
            "TC10-P-empty-fields"
        )

        print(
            "✅ TC10-P PASSED - "
            "Empty credentials cannot login"
        )

    # =========================================================================
    # TC10-N | Smoke + Regression
    # =========================================================================

    @pytest.mark.smoke
    @pytest.mark.negative
    def test_tc10_n_sign_in_disabled_when_only_email_filled(
        self,
        valid_email
    ):
        """
        Verify Sign In remains disabled when only email is entered.
        """

        login_page = self.login_page

        login_page.enter_username(
            valid_email
        )

        assert (
            login_page.get_password_field_value()
            == ""
        )

        assert (
            login_page.is_sign_in_enabled()
            is False
        )

        login_page.take_screenshot(
            "TC10-N-only-email"
        )

        print(
            "✅ TC10-N PASSED - "
            "Sign In is disabled when only email is filled"
        )
