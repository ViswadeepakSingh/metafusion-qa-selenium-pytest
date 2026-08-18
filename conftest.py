"""
Shared pytest fixtures for Selenium + pytest.

Project:
    Metafusion Sentry Platform

Fixtures
--------
config
    Application configuration.

driver
    Bare Chrome driver without authentication.

auth_state
    Logs in once per pytest session and caches cookies +
    localStorage in .auth/state.json.

authenticated_driver
    Fresh Chrome driver with cached authentication.
    Navigates to #/stats and waits for Dashboards page.

fresh_login_driver
    Fresh authenticated Chrome driver.
    Does NOT automatically navigate to #/stats.
    Useful for authentication/session tests.

manage_view
    Returns DashboardPage for the Statistics > Dashboards page.

analytics_dashboard
    Returns an existing dashboard card.
    The dashboard name is also exposed to test_dashboard.py as
    EXISTING_DASHBOARD.

disposable_dashboard
    Creates a temporary dashboard for tests and deletes it
    automatically during fixture teardown.
"""

# =============================================================================
# Imports
# =============================================================================

import json
import logging
import sys
import time
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

PROJECT_ROOT = Path(__file__).resolve().parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# =============================================================================
# Config
# =============================================================================

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
# Global configuration compatibility
# =============================================================================
#
# Some existing tests use:
#
#     from conftest import BASE_URL
#
# Keep this available for backward compatibility.
# =============================================================================

_BASE_CONFIG = Config()

BASE_URL = _BASE_CONFIG.BASE_URL


# =============================================================================
# Paths
# =============================================================================

STORAGE_STATE = (
    PROJECT_ROOT
    / ".auth"
    / "state.json"
)

SCREENSHOT_DIR = (
    PROJECT_ROOT
    / "screenshots"
)


# =============================================================================
# Helper functions
# =============================================================================

def app_origin(base_url):
    """
    Return application origin.

    Example:
        https://sentry.metafusion.ai
    """

    parsed = urlparse(base_url)

    return (
        f"{parsed.scheme}://"
        f"{parsed.netloc}"
    )


def stats_url(base_url):
    parsed = urlparse(base_url)

    return (
        f"{parsed.scheme}://"
        f"{parsed.netloc}"
        f"/#/stats"
    )

STATS_URL = stats_url(
    BASE_URL
)



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

    # Helpful for CI / Windows environments.
    options.add_argument("--disable-dev-shm-usage")

    drv = webdriver.Chrome(
        options=options
    )

    try:
        drv.maximize_window()
    except Exception:
        pass

    drv.set_page_load_timeout(60)

    return drv


# =============================================================================
# Authentication state
# =============================================================================

def _dump_state(driver):
    """
    Capture cookies and localStorage from the current application origin.
    """

    cookies = driver.get_cookies()

    local_storage = driver.execute_script(
        """
        var storage = {};

        for (
            var i = 0;
            i < window.localStorage.length;
            i++
        ) {
            var key = window.localStorage.key(i);

            storage[key] =
                window.localStorage.getItem(key);
        }

        return storage;
        """
    )

    return {
        "cookies": cookies,
        "localStorage": local_storage,
    }


def _load_state(driver, state, origin):
    """
    Load cached cookies and localStorage.

    Browser must first visit the application origin.
    """

    driver.get(origin)

    # -------------------------------------------------------------------------
    # Cookies
    # -------------------------------------------------------------------------

    for cookie in state.get("cookies", []):

        current_cookie = dict(cookie)

        # Selenium can reject some attributes.
        current_cookie.pop(
            "sameSite",
            None
        )

        # Selenium sometimes has problems with leading-dot domains.
        domain = current_cookie.get(
            "domain",
            ""
        )

        if domain.startswith("."):
            current_cookie["domain"] = (
                domain.lstrip(".")
            )

        # Some cookie exports may contain unsupported fields.
        current_cookie.pop(
            "storeId",
            None
        )

        try:

            driver.add_cookie(
                current_cookie
            )

        except Exception as error:

            logger.warning(
                "Could not load cookie '%s': %s",
                current_cookie.get("name"),
                error,
            )

    # -------------------------------------------------------------------------
    # Local Storage
    # -------------------------------------------------------------------------

    for key, value in state.get(
        "localStorage",
        {}
    ).items():

        try:

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

        except Exception as error:

            logger.warning(
                "Could not load localStorage key '%s': %s",
                key,
                error,
            )


# =============================================================================
# Dashboard module loader
# =============================================================================

def _load_dashboard_page():
    """
    Import DashboardPage dynamically.

    Supports both:
        pages/Statistics_Page/dashboard_page.py
        pages/Statistics_Page/Dashboard_Page.py
    """

    import importlib.util

    candidates = [
        PROJECT_ROOT
        / "pages"
        / "Statistics_Page"
        / "dashboard_page.py",

        PROJECT_ROOT
        / "pages"
        / "Statistics_Page"
        / "Dashboard_Page.py",
    ]

    for candidate in candidates:

        if not candidate.exists():
            continue

        spec = importlib.util.spec_from_file_location(
            "dashboard_page_fixture_module",
            candidate,
        )

        if spec is None or spec.loader is None:
            continue

        module = importlib.util.module_from_spec(
            spec
        )

        spec.loader.exec_module(
            module
        )

        return module

    raise ModuleNotFoundError(
        "Could not find dashboard_page.py "
        "or Dashboard_Page.py"
    )


# =============================================================================
# Dashboard Page Objects
# =============================================================================

_dashboard_module = _load_dashboard_page()

DashboardPage = (
    _dashboard_module.DashboardPage
)

DashboardForm = (
    _dashboard_module.DashboardForm
)

DashboardCard = (
    _dashboard_module.DashboardCard
)

ContextMenu = (
    _dashboard_module.ContextMenu
)

ConfirmDialog = (
    _dashboard_module.ConfirmDialog
)


# =============================================================================
# Config fixture
# =============================================================================

@pytest.fixture(scope="session")
def config():
    """
    Return application configuration.
    """

    return Config()


# =============================================================================
# Credential fixtures
# =============================================================================

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
# Authentication fixture
# =============================================================================

@pytest.fixture(scope="session")
def auth_state(config):
    """
    Login once per pytest session.

    Captures:
        - Cookies
        - localStorage

    Saves:
        .auth/state.json

    Returns:
        Authentication state dictionary.
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
        max(
            1,
            int(config.TIMEOUT / 1000)
        ),
    )

    try:

        logger.info(
            "Starting automatic login..."
        )

        # ---------------------------------------------------------------------
        # Open login page
        # ---------------------------------------------------------------------

        driver.get(
            config.BASE_URL
        )

        # ---------------------------------------------------------------------
        # Email
        # ---------------------------------------------------------------------

        email_field = wait.until(
            EC.visibility_of_element_located(
                (
                    By.XPATH,
                    "//input[@placeholder='Email address']",
                )
            )
        )

        email_field.clear()

        email_field.send_keys(
            config.USERNAME
        )

        # ---------------------------------------------------------------------
        # Password
        # ---------------------------------------------------------------------

        password_field = wait.until(
            EC.visibility_of_element_located(
                (
                    By.XPATH,
                    "//input[@placeholder='Password']",
                )
            )
        )

        password_field.clear()

        password_field.send_keys(
            config.PASSWORD
        )

        # ---------------------------------------------------------------------
        # Sign In
        # ---------------------------------------------------------------------

        sign_in_button = wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//button[normalize-space()='Sign In']",
                )
            )
        )

        sign_in_button.click()

        # ---------------------------------------------------------------------
        # Wait for Statistics route
        # ---------------------------------------------------------------------

        try:

            wait.until(
                EC.url_contains(
                    "#/stats"
                )
            )

        except Exception:

            wait.until(
                lambda d:
                "/stats"
                in d.current_url.lower()
            )

        # ---------------------------------------------------------------------
        # Make sure we are not still on login
        # ---------------------------------------------------------------------

        wait.until(
            lambda d:
            "/auth/login"
            not in d.current_url.lower()
        )

        logger.info(
            "Login successful: %s",
            driver.current_url,
        )

        # ---------------------------------------------------------------------
        # Save authentication state
        # ---------------------------------------------------------------------

        state = _dump_state(
            driver
        )

        STORAGE_STATE.write_text(
            json.dumps(
                state,
                indent=2
            ),
            encoding="utf-8",
        )

        logger.info(
            "Authentication state saved: %s",
            STORAGE_STATE,
        )

        return state

    except Exception as error:

        logger.error(
            "Automatic login failed: %s",
            error,
        )

        # ---------------------------------------------------------------------
        # Failure screenshot
        # ---------------------------------------------------------------------

        SCREENSHOT_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        try:

            driver.save_screenshot(
                str(
                    SCREENSHOT_DIR
                    / "login_failed.png"
                )
            )

        except Exception:
            pass

        # ---------------------------------------------------------------------
        # Failure HTML
        # ---------------------------------------------------------------------

        try:

            (
                SCREENSHOT_DIR
                / "login_failed_page.html"
            ).write_text(
                driver.page_source,
                encoding="utf-8",
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

    No authentication.

    Used for:
        - Login tests
        - Negative login tests
        - Unauthenticated access tests
    """

    drv = _build_driver(
        config.HEADLESS
    )

    try:

        yield drv

    finally:

        drv.quit()


# =============================================================================
# Fresh authenticated driver
# =============================================================================

@pytest.fixture(scope="function")
def fresh_login_driver(
    config,
    auth_state,
):
    """
    Fresh authenticated browser.

    IMPORTANT:
        This fixture loads the cached authentication state,
        but does NOT navigate automatically to #/stats.

    This is useful for authentication/session tests such as:

        test_TC_DB16_P_session_reuse_lands_directly_on_stats
    """

    drv = _build_driver(
        config.HEADLESS
    )

    try:

        _load_state(
            drv,
            auth_state,
            app_origin(
                config.BASE_URL
            ),
        )

        logger.info(
            "Fresh authenticated driver created."
        )

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
        6. Return driver
    """

    drv = _build_driver(
        config.HEADLESS
    )

    timeout = max(
        1,
        int(config.TIMEOUT / 1000)
    )

    wait = WebDriverWait(
        drv,
        timeout,
    )

    try:

        # ---------------------------------------------------------------------
        # Load cached authentication
        # ---------------------------------------------------------------------

        _load_state(
            drv,
            auth_state,
            app_origin(
                config.BASE_URL
            ),
        )

        # ---------------------------------------------------------------------
        # Navigate to Statistics / Dashboards
        # ---------------------------------------------------------------------

        drv.get(
            stats_url(
                config.BASE_URL
            )
        )

        # ---------------------------------------------------------------------
        # Wait for stats URL
        # ---------------------------------------------------------------------

        try:

            wait.until(
                EC.url_contains(
                    "#/stats"
                )
            )

        except Exception:

            wait.until(
                lambda d:
                "/stats"
                in d.current_url.lower()
            )

        # ---------------------------------------------------------------------
        # Authentication check
        # ---------------------------------------------------------------------

        if "/auth/login" in (
            drv.current_url.lower()
        ):

            SCREENSHOT_DIR.mkdir(
                parents=True,
                exist_ok=True,
            )

            drv.save_screenshot(
                str(
                    SCREENSHOT_DIR
                    / "auth_expired.png"
                )
            )

            pytest.fail(
                "Authentication expired. "
                f"URL: {drv.current_url}"
            )

        # ---------------------------------------------------------------------
        # Wait for Dashboards heading
        # ---------------------------------------------------------------------

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

        yield drv

    finally:

        drv.quit()


# =============================================================================
# Dashboard Manage View
# =============================================================================

@pytest.fixture(scope="function")
def manage_view(
    authenticated_driver,
):
    """
    Return DashboardPage for Statistics > Dashboards.

    The authenticated_driver fixture already:
        - loads authentication
        - navigates to #/stats
        - waits for Dashboards heading
    """

    page = DashboardPage(
        authenticated_driver
    )

    # Additional safety wait.
    page.heading_is_visible()

    return page


# =============================================================================
# Existing dashboard
# =============================================================================

@pytest.fixture(scope="function")
def analytics_dashboard(
    manage_view,
    request,
):
    """
    Return an existing saved dashboard card.

    The test suite currently refers to the dashboard name through:

        EXISTING_DASHBOARD

    Instead of hardcoding a dashboard name in conftest.py, we dynamically
    select the first available dashboard card.

    We also expose its name to the test module:

        request.module.EXISTING_DASHBOARD
    """

    cards = manage_view.get_all_cards()

    if not cards:

        pytest.fail(
            "No saved dashboard cards were found. "
            "analytics_dashboard requires at least one dashboard."
        )

    # -------------------------------------------------------------------------
    # Select first available dashboard.
    # -------------------------------------------------------------------------

    selected_card = None

    for card in cards:

        try:

            title = card.title.strip()

            if title:
                selected_card = card
                break

        except Exception as error:

            logger.warning(
                "Could not read dashboard card: %s",
                error,
            )

    if selected_card is None:

        pytest.fail(
            "Dashboard cards exist, but no usable dashboard title "
            "could be read."
        )

    dashboard_name = selected_card.title.strip()

    # -------------------------------------------------------------------------
    # Make EXISTING_DASHBOARD available to test_dashboard.py.
    #
    # This fixes tests such as:
    #
    #     assert card.title == EXISTING_DASHBOARD
    #
    # without hardcoding the dashboard name here.
    # -------------------------------------------------------------------------

    request.module.EXISTING_DASHBOARD = (
        dashboard_name
    )

    logger.info(
        "Using existing dashboard: %s",
        dashboard_name,
    )

    return selected_card


# =============================================================================
# Disposable dashboard
# =============================================================================

@pytest.fixture(scope="function")
def disposable_dashboard(
    manage_view,
):
    """
    Create a temporary dashboard for a test.

    Example:

        def test_something(
            self,
            manage_view,
            disposable_dashboard
        ):
            card = manage_view.get_card_by_name(
                disposable_dashboard
            )

    The dashboard is automatically deleted after the test.
    """

    name = (
        f"AutoTest DB "
        f"{int(time.time() * 1000)}"
    )

    logger.info(
        "Creating disposable dashboard: %s",
        name,
    )

    # -------------------------------------------------------------------------
    # Create dashboard
    # -------------------------------------------------------------------------

    form = manage_view.click_add_card()

    form.wait_until_open()

    form.enter_name(
        name
    )

    form.save()

    form.wait_until_closed()

    # -------------------------------------------------------------------------
    # Wait until dashboard appears
    # -------------------------------------------------------------------------

    manage_view.wait_for_card_present(
        name
    )

    card = manage_view.get_card_by_name(
        name
    )

    if card is None:

        pytest.fail(
            f"Disposable dashboard '{name}' "
            "was not created."
        )

    try:

        yield name

    finally:

        # ---------------------------------------------------------------------
        # Cleanup dashboard
        # ---------------------------------------------------------------------

        try:

            # Refresh lookup because the card may have become stale.
            manage_view.wait_for_card_present(
                name
            )

            card = manage_view.get_card_by_name(
                name
            )

            if card is not None:

                menu = card.open_context_menu()

                dialog = menu.click_delete()

                dialog.confirm()

                manage_view.wait_for_card_absent(
                    name
                )

                logger.info(
                    "Disposable dashboard deleted: %s",
                    name,
                )

        except Exception as error:

            logger.warning(
                "Could not cleanup disposable dashboard '%s': %s",
                name,
                error,
            )


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
    Save screenshot when a test fails.
    """

    outcome = yield

    report = outcome.get_result()

    if report.when != "call":
        return

    if not report.failed:
        return

    # -------------------------------------------------------------------------
    # Find active Selenium driver.
    # -------------------------------------------------------------------------

    drv = (
        item.funcargs.get(
            "authenticated_driver"
        )
        or item.funcargs.get(
            "fresh_login_driver"
        )
        or item.funcargs.get(
            "driver"
        )
    )

    if not drv:
        return

    try:

        SCREENSHOT_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        screenshot_path = (
            SCREENSHOT_DIR
            / f"{item.name}.png"
        )

        drv.save_screenshot(
            str(screenshot_path)
        )

        logger.info(
            "Failure screenshot saved: %s",
            screenshot_path,
        )

    except Exception as error:

        logger.warning(
            "Could not save failure screenshot: %s",
            error,
        )


# =============================================================================
# Terminal status
# =============================================================================

def pytest_runtest_logreport(
    report
):
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