import logging
from pathlib import Path

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from locators.login_locators import LoginPageLocators


logger = logging.getLogger(__name__)


class LoginPage:

    URL = "https://sentry.metafusion.ai/#/auth/login"

    def __init__(self, driver):
        self.driver = driver
        self.locators = LoginPageLocators

    # ======================================================================
    # Internal helpers
    # ======================================================================

    def _wait(self, timeout=15):
        return WebDriverWait(self.driver, timeout)

    def _find(self, key):
        return self.driver.find_element(
            *self.locators.get(key)
        )

    def _visible(self, key, timeout=15):
        return self._wait(timeout).until(
            EC.visibility_of_element_located(
                self.locators.get(key)
            )
        )

    def _exists(self, key):
        try:
            self._find(key)
            return True
        except Exception:
            return False

    # ======================================================================
    # Navigation
    # ======================================================================

    def open(self):
        """Open the login page and wait until login route is loaded."""
        self.driver.get(self.URL)

        self._wait().until(
            lambda d: "login" in d.current_url.lower()
        )

        logger.info(
            "Opened Login page: %s",
            self.driver.current_url
        )

    def goto(self):
        self.open()

    def navigate(self):
        self.open()

    def is_login_page(self):
        """Return True if current URL is the login route."""
        return "login" in self.driver.current_url.lower()

    def wait_for_login_page(self, timeout=15):
        """Wait until current URL contains login."""
        self._wait(timeout).until(
            lambda d: "login" in d.current_url.lower()
        )

    def wait_until_logged_in(self, timeout=10):
        """Wait until the login route is no longer displayed."""
        self._wait(timeout).until(
            lambda d: "login" not in d.current_url.lower()
        )

    def is_logged_in(self):
        """Return True when current URL is no longer login."""
        return "login" not in self.driver.current_url.lower()

    # ======================================================================
    # Page elements - visibility
    # ======================================================================

    def is_username_visible(self):
        return self._visible(
            "username_input"
        ).is_displayed()

    def is_password_visible(self):
        return self._visible(
            "password_input"
        ).is_displayed()

    def is_sign_in_visible(self):
        return self._visible(
            "SignIn_button"
        ).is_displayed()

    def is_remember_me_visible(self):
        return self._visible(
            "remember_me_container"
        ).is_displayed()

    def is_forgot_password_visible(self):
        return self._visible(
            "forgot_password_link"
        ).is_displayed()

    # ======================================================================
    # Dashboard / Login page state
    # ======================================================================

    def is_dashboard_element_visible(self):
        dashboard_locators = [
            ("nav", "nav"),
            ("sidebar", '[class*="sidebar"]'),
            ("dashboard", '[class*="dashboard"]'),
        ]

        for _, selector in dashboard_locators:
            try:
                element = self.driver.find_element(
                    "css selector" if selector != "nav" else "tag name",
                    selector
                )

                if element.is_displayed():
                    return True

            except Exception:
                continue

        return False

    def are_login_fields_visible(self):
        return (
            self.is_username_visible()
            and self.is_password_visible()
        )

    # ======================================================================
    # Credentials
    # ======================================================================

    def enter_username(self, username):
        field = self._visible(
            "username_input"
        )

        field.clear()

        if username:
            field.send_keys(username)

    def enter_password(self, password):
        field = self._visible(
            "password_input"
        )

        field.clear()

        if password:
            field.send_keys(password)

    def enter_username_and_password(
        self,
        username,
        password
    ):
        self.enter_username(username)
        self.enter_password(password)

        logger.info("Credentials entered")

    def fill_credentials(
        self,
        email,
        password
    ):
        self.enter_username_and_password(
            email,
            password
        )

    # ======================================================================
    # Field values
    # ======================================================================

    def get_email_field_value(self):
        return self._find(
            "username_input"
        ).get_attribute("value")

    def get_password_field_value(self):
        return self._find(
            "password_input"
        ).get_attribute("value")

    def get_email_input_type(self):
        return self._find(
            "username_input"
        ).get_attribute("type")

    def get_password_input_type(self):
        return self._find(
            "password_input"
        ).get_attribute("type")

    def is_email_field_enabled(self):
        return self._find(
            "username_input"
        ).is_enabled()

    def is_password_field_enabled(self):
        return self._find(
            "password_input"
        ).is_enabled()

    # ======================================================================
    # Sign In
    # ======================================================================

    def is_sign_in_enabled(self):
        return self._find(
            "SignIn_button"
        ).is_enabled()

    def click_sign_in(self):
        button = self._visible(
            "SignIn_button"
        )

        button.click()

        logger.info("Clicked Sign In")

    def click_SignIn_button(self):
        # Backward compatibility if other tests use this name.
        self.click_sign_in()

    # ======================================================================
    # Login
    # ======================================================================

    def login(
        self,
        email,
        password
    ):
        self.enter_username_and_password(
            email,
            password
        )

        # Do not click if credentials are intentionally empty.
        if not email or not password or not password.strip():
            logger.info(
                "Sign In skipped because credentials are empty"
            )
            return

        self.click_sign_in()

    # ======================================================================
    # Remember Me
    # ======================================================================

    def check_remember_me(self):
        checkbox = self._visible(
            "remember_me_input"
        )

        if not checkbox.is_selected():
            checkbox.click()

    def uncheck_remember_me(self):
        checkbox = self._visible(
            "remember_me_input"
        )

        if checkbox.is_selected():
            checkbox.click()

    def is_remember_me_checked(self):
        return self._find(
            "remember_me_input"
        ).is_selected()

    # ======================================================================
    # Error handling
    # ======================================================================

    def is_error_message_visible(self):
        for key in (
            "error_message",
            "Toast_Error_Msg"
        ):
            try:
                element = self._find(key)

                if element.is_displayed():
                    return True

            except Exception:
                continue

        return False

    def wait_for_error_message(self, timeout=10):
        self._wait(timeout).until(
            lambda d: self.is_error_message_visible()
        )

    def get_error_message_text(self):
        for key in (
            "error_message",
            "Toast_Error_Msg"
        ):
            try:
                element = self._find(key)

                if element.is_displayed():
                    text = element.text.strip()

                    if text:
                        return text

            except Exception:
                continue

        return ""

    # ======================================================================
    # HTML5 validation
    # ======================================================================

    def get_email_validation_message(self):
        email = self._find(
            "username_input"
        )

        return self.driver.execute_script(
            "return arguments[0].validationMessage;",
            email
        )

    # ======================================================================
    # Forgot password
    # ======================================================================

    def click_forgot_password(self):
        self._visible(
            "forgot_password_link"
        ).click()

    # ======================================================================
    # Login verification
    # ======================================================================

    def verify_login_successful(self):
        try:
            toast = self._visible(
                "success_popup",
                timeout=10
            )

            message = toast.text.strip()

            return "Login Successful" in message

        except TimeoutException:
            return self._redirected_to_dashboard()

    def _redirected_to_dashboard(self):
        try:
            self._wait(10).until(
                lambda d: "/stats" in d.current_url.lower()
            )

            return True

        except TimeoutException:
            return False

    def verify_dashboard_page(self):
        self._wait(15).until(
            lambda d: "/stats" in d.current_url.lower()
        )

        return "/stats" in self.driver.current_url.lower()

    # ======================================================================
    # Logout
    # ======================================================================

    def click_logout_button(self):
        self._visible(
            "logout_button"
        ).click()

    def confirm_logout(self):
        self._visible(
            "confirm_logout_button"
        ).click()

    # ======================================================================
    # Screenshot
    # ======================================================================

    def save_screenshot(self, name):
        try:
            directory = Path("screenshots")
            directory.mkdir(
                parents=True,
                exist_ok=True
            )

            path = directory / f"{name}.png"

            self.driver.save_screenshot(
                str(path)
            )

            logger.info(
                "Screenshot saved: %s",
                path
            )

        except Exception:
            logger.exception(
                "Screenshot failed"
            )

    def take_screenshot(self, name):
        self.save_screenshot(name)
