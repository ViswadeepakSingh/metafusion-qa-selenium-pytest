"""
Shared pytest fixtures for Selenium.

Place this file at the project root:

    conftest.py

Fixtures
--------
config
    Returns Config().

driver
    Bare Chrome driver without authentication.
    Useful for negative/authentication tests.

authenticated_driver
    Fresh Chrome driver with the cached authentication session.
    Navigates to #/stats and waits until the Dashboards page is rendered.

auth_state
    Logs in once per pytest session and caches cookies + localStorage
    in .auth/state.json.
"""

import json
import logging
import sys
from pathlib import Path
from urllib.parse import urlparse

import pytest

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# =============================================================================
# Project path
# =============================================================================

sys.path.insert(0, str(Path(__file__).parent))

from config.config import Config


# =============================================================================
# Logging
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


# =============================================================================
# Paths
# =============================================================================

STORAGE_STATE = (
    Path(__file__).parent
    / ".auth"
    / "state.json"
)

SCREENSHOT_DIR = Path("screenshots")


# =============================================================================
# Helper functions
# =============================================================================

def app_origin(base_url):
    """
    Return only the application origin.

    Example:
        https://sentry.metafusion.ai
    """

    parsed = urlparse(base_url)

    return f"{parsed.scheme}://{parsed.netloc}"


def stats_url(base_url):
    """
    Return Statistics / Dashboards URL.
    """

    return f"{app_origin(base_url)}/#/stats"


def _build_driver(headless):
    """
    Create and configure Chrome WebDriver.
    """

    options = Options()

    if headless:
        options.add_argument("--headless=new")

    options.add_argument("--start-maximized")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=options)

    driver.maximize_window()

    driver.set_page_load_timeout(60)

    return driver


# =============================================================================
# Authentication state helpers
# =============================================================================

def _dump_state(driver):
    """
    Capture cookies and localStorage from the current origin.
    """

    cookies = driver.get_cookies()

    local_storage = driver.execute_script(
        "var s = {};"

        "for (var i = 0; "
        "i < window.localStorage.length; "
        "i++) {"

        "  var k = window.localStorage.key(i);"

        "  s[k] = window.localStorage.getItem(k);"

        "}"

        "return s;"
    )

    return {
        "cookies": cookies,
        "localStorage": local_storage,
    }


def _load_state(driver, state, origin):
    """
    Inject cached cookies and localStorage.

    The browser must first visit the application origin
    before cookies/localStorage can be injected.
    """

    driver.get(origin)

    # -----------------------------------------------------------------
    # Cookies
    # -----------------------------------------------------------------

    for cookie in state.get("cookies", []):

        c = dict(cookie)

        # Selenium can reject some cookie attributes.
        c.pop("sameSite", None)

        # Remove leading dot from cookie domain.
        if c.get("domain", "").startswith("."):
            c["domain"] = c["domain"].lstrip(".")

        try:

            driver.add_cookie(c)

        except Exception as error:

            logger.warning(
                "Skipped cookie %s: %s",
                c.get("name"),
                error,
            )

    # -----------------------------------------------------------------
    # Local Storage
    # -----------------------------------------------------------------

    for key, value in state.get(
        "localStorage",
        {}
    ).items():

        driver.execute_script(
            """
            window.localStorage.setItem(
                arguments[0],
                arguments[1]
            );
            """,
            key,
            value,
        )


# =============================================================================
# Config / credentials
# =============================================================================

@pytest.fixture(scope="session")
def config():
    """
    Return application configuration.
    """

    return Config()


@pytest.fixture(scope="session")
def valid_email(config):
    """
    Valid login email.
    """

    return config.USERNAME


@pytest.fixture(scope="session")
def valid_password(config):
    """
    Valid login password.
    """

    return config.PASSWORD


@pytest.fixture(scope="session")
def invalid_email():
    """
    Invalid email for negative login tests.
    """

    return "invalid@test.com"


@pytest.fixture(scope="session")
def invalid_password():
    """
    Invalid password for negative login tests.
    """

    return "WrongPassword123"


# =============================================================================
# Login once and cache authentication state
# =============================================================================

@pytest.fixture(scope="session")
def auth_state(config):
    """
    Login once per pytest session.

    Captures:
        - Cookies
        - LocalStorage

    Saves them to:

        .auth/state.json
    """

    STORAGE_STATE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    driver = _build_driver(
        config.HEADLESS
    )

    wait = WebDriverWait(
        driver,
        int(config.TIMEOUT / 1000),
    )

    try:

        # -------------------------------------------------------------
        # Open login page
        # -------------------------------------------------------------

        driver.get(
            config.BASE_URL
        )

        # -------------------------------------------------------------
        # Email
        # -------------------------------------------------------------

        wait.until(
            EC.visibility_of_element_located(
                (
                    By.XPATH,
                    "//input[@placeholder='Email address']",
                )
            )
        ).send_keys(
            config.USERNAME
        )

        # -------------------------------------------------------------
        # Password
        # -------------------------------------------------------------

        driver.find_element(
            By.XPATH,
            "//input[@placeholder='Password']",
        ).send_keys(
            config.PASSWORD
        )

        # -------------------------------------------------------------
        # Sign In
        # -------------------------------------------------------------

        driver.find_element(
            By.XPATH,
            "//button[normalize-space()='Sign In']",
        ).click()

        # -------------------------------------------------------------
        # Wait for Statistics route
        # -------------------------------------------------------------

        try:

            wait.until(
                EC.url_contains("#/stats")
            )

        except Exception:

            wait.until(
                lambda d:
                "/stats"
                in d.current_url.lower()
            )

        # -------------------------------------------------------------
        # Make sure we are not still on login
        # -------------------------------------------------------------

        wait.until(
            lambda d:
            "/auth/login"
            not in d.current_url.lower()
        )

        # -------------------------------------------------------------
        # Save authentication state
        # -------------------------------------------------------------

        state = _dump_state(
            driver
        )

        STORAGE_STATE.write_text(
            json.dumps(state),
            encoding="utf-8",
        )

        logger.info(
            "Login OK — session cached at %s",
            STORAGE_STATE,
        )

        return state

    except Exception as error:

        logger.error(
            "Auto-login failed: %s",
            error,
        )

        # -------------------------------------------------------------
        # Save failure screenshot
        # -------------------------------------------------------------

        SCREENSHOT_DIR.mkdir(
            exist_ok=True
        )

        driver.save_screenshot(
            "screenshots/login_failed.png"
        )

        # -------------------------------------------------------------
        # Save page source
        # -------------------------------------------------------------

        try:

            with open(
                "screenshots/login_failed_page.html",
                "w",
                encoding="utf-8",
            ) as file:

                file.write(
                    driver.page_source
                )

        except Exception:
            pass

        raise

    finally:

        driver.quit()


# =============================================================================
# Bare driver
# =============================================================================

@pytest.fixture(scope="function")
def driver(config):
    """
    Bare Chrome driver.

    No authentication is loaded.

    Use this for:
        - Login negative tests
        - Unauthenticated access tests
        - Authentication tests
    """

    drv = _build_driver(
        config.HEADLESS
    )

    try:

        yield drv

    finally:

        drv.quit()


# =============================================================================
# Authenticated driver
# =============================================================================

@pytest.fixture(scope="function")
def authenticated_driver(
    config,
    auth_state,
):
    """
    Fresh Chrome driver with cached authentication.

    Flow:

        1. Start Chrome
        2. Load cookies/localStorage
        3. Navigate to #/stats
        4. Verify authentication
        5. Wait for Dashboards heading
        6. Return driver to test
    """

    drv = _build_driver(
        config.HEADLESS
    )

    wait = WebDriverWait(
        drv,
        int(config.TIMEOUT / 1000),
    )

    try:

        # -------------------------------------------------------------
        # Load cached authentication
        # -------------------------------------------------------------

        _load_state(
            drv,
            auth_state,
            app_origin(config.BASE_URL),
        )

        # -------------------------------------------------------------
        # Navigate to Statistics / Dashboards
        # -------------------------------------------------------------

        drv.get(
            stats_url(config.BASE_URL)
        )

        # -------------------------------------------------------------
        # Wait for #/stats
        # -------------------------------------------------------------

        try:

            wait.until(
                EC.url_contains("#/stats")
            )

        except Exception:

            wait.until(
                lambda d:
                "/stats"
                in d.current_url.lower()
            )

        # -------------------------------------------------------------
        # Verify authentication
        # -------------------------------------------------------------

        if "/auth/login" in drv.current_url.lower():

            SCREENSHOT_DIR.mkdir(
                exist_ok=True
            )

            drv.save_screenshot(
                "screenshots/auth_expired.png"
            )

            pytest.fail(
                "Authentication expired. "
                f"URL: {drv.current_url}"
            )

        # -------------------------------------------------------------
        # IMPORTANT:
        #
        # URL changing to #/stats does NOT necessarily mean
        # the Dashboards page has finished rendering.
        #
        # Wait for the actual Dashboards heading.
        # -------------------------------------------------------------

        wait.until(
            EC.visibility_of_element_located(
                (
                    By.XPATH,
                    "//div[@class='root_heading' "
                    "and normalize-space()='Dashboards']",
                )
            )
        )

        logger.info(
            "Authenticated session loaded: %s",
            drv.current_url,
        )

        # -------------------------------------------------------------
        # Give driver to test
        # -------------------------------------------------------------

        yield drv

    finally:

        drv.quit()


# =============================================================================
# Screenshot on test failure
# =============================================================================

@pytest.hookimpl(
    tryfirst=True,
    hookwrapper=True,
)
def pytest_runtest_makereport(
    item,
    call,
):
    """
    Automatically save screenshot when a test fails.
    """

    outcome = yield

    report = outcome.get_result()

    if report.when != "call":
        return

    if not report.failed:
        return

    # -------------------------------------------------------------
    # Find active Selenium driver
    # -------------------------------------------------------------

    drv = (
        item.funcargs.get(
            "authenticated_driver"
        )
        or item.funcargs.get(
            "driver"
        )
    )

    if drv:

        try:

            SCREENSHOT_DIR.mkdir(
                exist_ok=True
            )

            screenshot_path = (
                SCREENSHOT_DIR
                / f"{item.name}.png"
            )

            drv.save_screenshot(
                str(screenshot_path)
            )

            logger.info(
                "Failure screenshot saved for %s",
                item.name,
            )

        except Exception as error:

            logger.warning(
                "Could not save failure screenshot: %s",
                error,
            )


# =============================================================================
# Terminal status
# =============================================================================

def pytest_runtest_logreport(report):
    """
    Print simple PASS / FAIL / SKIP status.
    """

    if report.when != "call":
        return

    if report.passed:

        print(
            f"\n[PASS] {report.nodeid}"
        )

    elif report.failed:

        print(
            f"\n[FAIL] {report.nodeid}"
        )

    elif report.skipped:

        print(
            f"\n[SKIP] {report.nodeid}"
        )