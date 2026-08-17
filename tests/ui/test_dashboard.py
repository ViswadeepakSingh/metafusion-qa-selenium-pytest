"""
Selenium + pytest spec for Statistics > Dashboards.
-> place at tests/test_dashboards_spec.py

Mirrors the Playwright suite (manage view, card content, create/cancel,
navigation, context menu). Uses the authenticated_driver fixture from conftest.
"""
from urllib.parse import urlparse

import importlib.util
import pytest
import time
import logging
import re
import os
import sys
from pathlib import Path

from selenium.webdriver.common.by import By


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TESTS_ROOT = Path(__file__).resolve().parents[1]
for root in (str(PROJECT_ROOT), str(TESTS_ROOT)):
    if root not in sys.path:
        sys.path.insert(0, root)

from conftest import config, driver
from locators.dashboard_locators import DashboardsLocators

# Load page modules without relying on a repo-specific package path / case-sensitive folder names.
def _load_module(module_name, *candidates):
    for candidate in candidates:
        if candidate.exists():
            spec = importlib.util.spec_from_file_location(module_name, candidate)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                return module
    raise ModuleNotFoundError(f"Could not find {module_name} in the project layout")

DashboardPage = _load_module(
    "dashboard_page",
    PROJECT_ROOT / "pages" / "Statistics_Page" / "dashboard_page.py",
    PROJECT_ROOT / "pages" / "statistics_page" / "dashboard_page.py",
    TESTS_ROOT / "pages" / "Statistics_Page" / "dashboard_page.py",
    TESTS_ROOT / "pages" / "statistics_page" / "dashboard_page.py",
).DashboardPage

ContextMenu = _load_module(
    "context_menu",
    PROJECT_ROOT / "pages" / "Statistics_Page" / "context_menu.py",
    PROJECT_ROOT / "pages" / "statistics_page" / "context_menu.py",
    TESTS_ROOT / "pages" / "Statistics_Page" / "context_menu.py",
    TESTS_ROOT / "pages" / "statistics_page" / "context_menu.py",
).ContextMenu

DashboardForm = _load_module(
    "dashboard_form",
    PROJECT_ROOT / "pages" / "Statistics_Page" / "dashboard_form.py",
    PROJECT_ROOT / "pages" / "statistics_page" / "dashboard_form.py",
    TESTS_ROOT / "pages" / "Statistics_Page" / "dashboard_form.py",
    TESTS_ROOT / "pages" / "statistics_page" / "dashboard_form.py",
).DashboardForm

# Load test data without relying on a repo-specific package path.
for candidate in (
    PROJECT_ROOT / "utils" / "testdata.py",
    TESTS_ROOT / "utils" / "testdata.py",
    PROJECT_ROOT / "tests" / "utils" / "testdata.py",
):
    if candidate.exists():
        spec = importlib.util.spec_from_file_location("testdata", candidate)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            BOUNDARY_NAMES = module.BOUNDARY_NAMES
            break
else:
    raise ModuleNotFoundError("Could not find utils/testdata.py in the project layout")


LOC = DashboardsLocators()

# Existing dashboard visible in the manage view — change to match your data.
EXISTING_DASHBOARD = "Analytics"


def _stats_url(base_url):
    parsed = urlparse(base_url)
    return f"{parsed.scheme}://{parsed.netloc}/#/stats"


def _unique_name():
    return f"AutoTest DB {int(time.time() * 1000)}"


def contains_valid_date(value):
    """Return True if text contains a valid date-like value."""
    return bool(re.search(r"\b(?:\d{1,2}/\d{1,2}/\d{2,4}|\d{4}-\d{2}-\d{2})\b", value or ""))


def contains_todays_date(value):
    """Return True if text contains today's date in a common UI format."""
    if not value:
        return False

    today = time.strftime("%m/%d/%Y")
    return today in str(value) or time.strftime("%m/%d/%y") in str(value)


# --------------------------------------------------------------------
# TC-DB01-P | Manage View | Manage view loads with heading and subtitle
# Type: UI | Category: Positive | Priority: High | Tags: Smoke test
# Preconditions: User logged in (session reused); on #/stats
# Steps:
#   1. Land on #/stats
#   2. Observe header area
# Expected: DASHBOARDS heading and subtitle
#   'Manage and switch between your saved dashboards.' are visible
#---------------------------------------------------------------------
class TestDashboardsManageView:

    @pytest.mark.ui
    @pytest.mark.positive
    @pytest.mark.high
    @pytest.mark.smoke
    def test_TC_DB01_P_manage_view_loads_with_headings_subtitle(
        self,
        authenticated_driver
    ):
        """ TC-DB01-P Verify that the Dashboard manage view loads with: 
        - Dashboards heading - Dashboard subtitle """

        dashboard = DashboardPage(authenticated_driver)

        assert dashboard.heading_is_visible(), \
            "Expected 'DASHBOARDS' heading to be visible"

        assert dashboard.subtitle_is_visible(), \
            "Expected dashboard subtitle to be visible"

        assert dashboard.get_heading().strip() == "DASHBOARDS", \
            "Expected heading text to be 'DASHBOARDS'"

        assert (
            "Manage and switch between your saved dashboards."
            in dashboard.get_subtitle_text()
        ), \
            "Expected dashboard subtitle text to be displayed"

    
    @pytest.mark.ui
    @pytest.mark.negative
    @pytest.mark.high
    @pytest.mark.smoke
    def test_TC_DB01_N_manage_view_not_reachable_without_a_session(
        self,
        driver,
        config
    ):
        driver.get(_stats_url(config.BASE_URL))

        dashboard = DashboardPage(driver)

        assert not dashboard.is_heading_present(), \
            "Dashboard should not be visible without an authenticated session"

        

    @pytest.mark.ui
    @pytest.mark.positive
    @pytest.mark.high
    def test_TC_DB02_P_add_dashboard_card_is_visible(self, manage_view):
        """
        TC-DB02-P: Add-dashboard '+' card is visible.
        Preconditions: user logged in; on #/stats.
        Steps: observe the dashboards grid.
        Expected: the dashed '+' add-dashboard card is visible.
        """
        assert manage_view.add_card_is_visible()

    @pytest.mark.ui
    @pytest.mark.positive
    @pytest.mark.medium
    def test_TC_DB03_P_at_least_one_saved_dashboard_card_shown(
        self,
        authenticated_driver
    ):
        dashboard = DashboardPage(authenticated_driver)

        assert dashboard.is_dashboard_card_present(), \
            "Expected at least one saved dashboard card to be displayed"

        card_level = dashboard.get_dashboard_card_level()

        print("Dashboard card:", card_level)

        assert card_level != "", \
            "Expected dashboard card to contain text"

    @pytest.mark.ui
    @pytest.mark.positive
    @pytest.mark.high
    def test_TC_DB04_P_card_shows_name_label_date_and_widgets(analytics_dashboard):
        """
        TC-DB04-P: Card shows name, label, date and widgets.
        Preconditions: user logged in; 'Analytics' dashboard exists.
        Steps: locate the 'Analytics' card, inspect its contents.
        Expected: card shows title 'Analytics', 'DASHBOARD' label, an
        'Updated on' date and a widgets badge.
        """
        card = analytics_dashboard

        assert card.title == "Analytics"
        assert card.label == "DASHBOARD"
        assert card.updated_on_text  # non-empty
        assert card.widgets_badge_text  # non-empty


    @pytest.mark.ui
    @pytest.mark.positive
    @pytest.mark.low
    def test_TC_DB05_P_updated_on_shows_valid_date(analytics_dashboard):
        """
        TC-DB05-P: 'Updated on' shows a valid date.
        Preconditions: user logged in; a saved card exists.
        Steps: read the 'Updated on' text on a card.
        Expected: text contains a date in M/D/YYYY format (e.g. 2/11/2026).
        """
        assert contains_valid_date(analytics_dashboard.updated_on_text)


    @pytest.mark.functional
    @pytest.mark.positive
    @pytest.mark.medium
    def test_TC_DB06_P_widgets_badge_shows_a_count(analytics_dashboard):
        """
        TC-DB06-P: Widgets badge shows a count.
        Preconditions: user logged in; 'Analytics' dashboard exists.
        Steps: read the widgets badge on the 'Analytics' card.
        Expected: badge reads 'N Widgets' (e.g. '5 Widgets').
        """
        import re

        assert re.search(r"\d+\s*Widgets?", analytics_dashboard.widgets_badge_text)


    @pytest.mark.functional
    @pytest.mark.negative
    @pytest.mark.low
    def test_TC_DB07_N_widgets_count_is_non_negative_integer(analytics_dashboard):
        """
        TC-DB07-N: Widgets count is a non-negative integer (data-validity check).
        Preconditions: user logged in; 'Analytics' dashboard exists.
        Steps: parse the integer from the widgets badge.
        Expected: parsed value is an integer >= 0.
        """
        count = analytics_dashboard.widgets_count()
        assert isinstance(count, int)
        assert count >= 0, f"Widgets count parsed as {count}, expected >= 0"


    @pytest.mark.functional
    @pytest.mark.positive
    @pytest.mark.high
    def test_TC_DB08_P_add_card_opens_create_form(manage_view):
        """
        TC-DB08-P: Add card opens the create form.
        Preconditions: user logged in; on #/stats.
        Steps: click the '+' add card.
        Expected: 'Dashboard Name' input plus SAVE and CANCEL buttons are visible.
        """
        form = manage_view.click_add_card()

        assert form.is_open()
        assert manage_view.driver.find_elements(*form.save_locator)
        assert manage_view.driver.find_elements(*form.cancel_locator)

        form.cancel()  # leave no residual state for later tests


    @pytest.mark.ui
    @pytest.mark.positive
    @pytest.mark.high
    def test_TC_DB09_P_name_field_empty_on_fresh_form(manage_view):
        """
        TC-DB09-P: Name field empty on fresh form.
        Preconditions: user logged in; create form opened.
        Steps: open the create form, observe the name field.
        Expected: 'Dashboard Name' field value is '' (empty).
        """
        form = manage_view.click_add_card()
        assert form.get_name_value() == ""
        form.cancel()


    @pytest.mark.functional
    @pytest.mark.positive
    @pytest.mark.medium
    @pytest.mark.parametrize("name", BOUNDARY_NAMES)
    def test_TC_DB10_P_field_accepts_range_of_valid_names(manage_view, name):
        """
        TC-DB10-P: Field accepts a range of valid names (parametrized boundary + unicode).
        Preconditions: user logged in; create form open.
        Steps: enter each value, read back the field.
        Expected: each value is accepted exactly as typed:
        'A'; 'Q3 Metrics'; 'Dashboard-2026_v1'; 'Ünïcode Náme';
        ' Padded Name '; a 200+ char name.
        """
        form = manage_view.click_add_card()
        form.enter_name(name)
        assert form.get_name_value() == name
        form.cancel()


    @pytest.mark.functional
    @pytest.mark.positive
    @pytest.mark.high
    def test_TC_DB11_P_create_dashboard_end_to_end_adds_a_card(manage_view):
        """
        TC-DB11-P: Create dashboard end-to-end adds a card.
        Preconditions: user logged in; create form open.
        Steps: enter a unique name, click SAVE, return to manage view.
        Expected: form closes; a new card with that name appears; saved
        count increases by 1.
        Note: mutates data — this test creates and then deletes its own
        throwaway dashboard as teardown.
        """
        name = _unique_name("TC-DB11")
        before = manage_view.cards_count()

        form = manage_view.click_add_card()
        form.enter_name(name)
        form.save()
        form.wait_until_closed()

        manage_view.wait_for_card_present(name)
        assert manage_view.cards_count() == before + 1
        assert manage_view.get_card_by_name(name) is not None

        # Teardown: remove the dashboard this test created.
        card = manage_view.get_card_by_name(name)
        menu = card.open_context_menu()
        dialog = menu.click_delete()
        dialog.confirm()
        manage_view.wait_for_card_absent(name)


    @pytest.mark.functional
    @pytest.mark.negative
    @pytest.mark.high
    def test_TC_DB12_N_empty_name_rejected_on_save(manage_view):
        """
        TC-DB12-N: Empty name is rejected on Save.
        Preconditions: user logged in; create form open.
        Steps: leave name empty, click SAVE.
        Expected: Save is blocked; form stays open (name required).
        * Invert this assertion if your app intentionally allows empty names.
        """
        form = manage_view.click_add_card()
        form.clear_name()
        form.save()

        assert form.is_open(), "Expected the create form to stay open when name is empty"

    @pytest.mark.functional
    @pytest.mark.positive
    @pytest.mark.high
    def test_TC_DB13_P_cancel_closes_form_without_adding_card(manage_view):
        """
        TC-DB13-P: Cancel closes form without adding a card.
        Preconditions: user logged in; create form open.
        Steps: enter a name, click CANCEL, return to manage view.
        Expected: form closes; the discarded name does NOT appear as a card.
        """
        name = _unique_name("TC-DB13-discarded")
        before = manage_view.cards_count()

        form = manage_view.click_add_card()
        form.enter_name(name)
        form.cancel()
        form.wait_until_closed()

        assert manage_view.cards_count() == before
        assert manage_view.get_card_by_name(name) is None


    @pytest.mark.functional
    @pytest.mark.positive
    @pytest.mark.medium
    def test_TC_DB14_P_reopened_form_is_empty_after_cancel(manage_view):
        """
        TC-DB14-P: Reopened form is empty after Cancel (no leaked state).
        Preconditions: user logged in; create form open.
        Steps: enter a name, click CANCEL, reload and reopen the form.
        Expected: the freshly opened form shows an empty name field.
        """
        form = manage_view.click_add_card()
        form.enter_name(_unique_name("TC-DB14-leaked"))
        form.cancel()
        form.wait_until_closed()

        manage_view.driver.refresh()
        manage_view.wait.until(lambda d: manage_view.is_rendered())

        reopened = manage_view.click_add_card()
        assert reopened.get_name_value() == ""
        reopened.cancel()

    @pytest.mark.functional
    @pytest.mark.positive
    @pytest.mark.high
    def test_TC_DB15_P_clicking_saved_card_opens_dashboard(manage_view, analytics_dashboard):
        """
        TC-DB15-P: Clicking a saved card opens the dashboard.
        Preconditions: user logged in; 'Analytics' dashboard exists.
        Steps: click the 'Analytics' card.
        Expected: the dashboard opens/switches; the create form is not
        shown; still within stats.
        Note (from sheet): confirm the exact opened-state assertion against
        your app's real DOM/URL once the placeholder locators are filled in.
        """

        analytics_dashboard.click()
        driver = manage_view.driver

        # TODO: replace with a real assertion for "the Analytics dashboard is open",
        # e.g. a URL change to '#/stats/<id>' or a visible dashboard-content element.
        assert "#/stats" in driver.current_url

        assert len(driver.find_elements(*LOC.NAME_INPUT)) == 0, (
            "Create form should not be visible after opening a saved dashboard"
        )

    @pytest.mark.auth
    @pytest.mark.positive
    @pytest.mark.high
    def test_TC_DB16_P_session_reuse_lands_directly_on_stats(fresh_login_driver):
        """
        TC-DB16-P: Session reuse lands directly on stats.
        Preconditions: valid credentials configured (APP_USERNAME / APP_PASSWORD).
        Steps: log in once (storage_state cached), reuse session to open #/stats.
        Expected: the authenticated session lands directly on the
        stats/manage view.
        Note (from sheet): consider a storage_state strategy — e.g. Playwright's
        storage_state equivalent for Selenium is exporting/importing cookies
        via driver.get_cookies() / add_cookie() between sessions, so login
        only has to happen once per full suite run rather than per test.
        """
        from conftest import BASE_URL

        fresh_login_driver.get(f"{BASE_URL}/#/stats")
        page = DashboardPage(fresh_login_driver)

        assert page.is_rendered()
        assert "#/stats" in fresh_login_driver.current_url

    @pytest.mark.ui
    @pytest.mark.positive
    @pytest.mark.high
    def test_TC_DB17_P_three_dots_menu_opens_with_all_options(analytics_dashboard):
        """
        TC-DB17-P: Three-dots menu opens with all options.
        Preconditions: user logged in; a saved dashboard card exists.
        Steps: click the three-dots (⋮) icon on a card.
        Expected: menu opens showing exactly: Open, Rename, Delete, Set as Default.
        """
        menu = analytics_dashboard.open_context_menu()
        assert menu.is_open()
        assert menu.get_item_labels() == ContextMenu.EXPECTED_LABELS


    @pytest.mark.ui
    @pytest.mark.positive
    @pytest.mark.medium
    def test_TC_DB18_P_menu_items_show_correct_icons_and_labels(analytics_dashboard):
        """
        TC-DB18-P: Menu items show correct icons and labels.
        Preconditions: user logged in; three-dots menu open.
        Steps: open the three-dots menu, inspect each item.
        Expected: each item shows its label and icon: Open, Rename (pencil),
        Delete (trash), Set as Default (refresh).
        TODO: the icon check below assumes each menu item renders an
        `[data-testid='icon']` child — replace with your app's real markup
        (e.g. an <svg> or icon-font class) once known.
        """
        menu = analytics_dashboard.open_context_menu()
        items = menu.driver.find_elements(*ContextMenu.ALL_ITEMS)

        assert [i.text.strip() for i in items] == ContextMenu.EXPECTED_LABELS
        for item in items:
            icons = item.find_elements("css selector", "[data-testid='icon']")
            assert icons, f"Expected an icon inside menu item '{item.text.strip()}'"


    @pytest.mark.ui
    @pytest.mark.positive
    @pytest.mark.medium
    def test_TC_DB19_P_menu_closes_on_outside_click(analytics_dashboard):
        """
        TC-DB19-P: Menu closes on outside click.
        Preconditions: user logged in; three-dots menu open.
        Steps: open the menu, click anywhere outside the menu.
        Expected: menu closes; no action is triggered.
        """
        original_title = analytics_dashboard.title
        menu = analytics_dashboard.open_context_menu()

        menu.close_via_outside_click()
        menu.wait_until_closed()

        assert not menu.is_open()
        assert analytics_dashboard.title == original_title


    @pytest.mark.ui
    @pytest.mark.positive
    @pytest.mark.low
    def test_TC_DB20_P_menu_closes_on_esc_key(analytics_dashboard):
        """
        TC-DB20-P: Menu closes on Esc key.
        Preconditions: user logged in; three-dots menu open.
        Steps: open the menu, press Esc.
        Expected: menu closes; no action is triggered.
        """
        original_title = analytics_dashboard.title
        menu = analytics_dashboard.open_context_menu()

        menu.close_via_escape()
        menu.wait_until_closed()

        assert not menu.is_open()
        assert analytics_dashboard.title == original_title


    @pytest.mark.ui
    @pytest.mark.negative
    @pytest.mark.medium
    def test_TC_DB21_N_menu_not_visible_until_three_dots_clicked(manage_view, analytics_dashboard):
        """
        TC-DB21-N: Menu not visible until three-dots clicked.
        Preconditions: user logged in; on #/stats.
        Steps: observe a card without clicking the three-dots.
        Expected: Open/Rename/Delete/Set as Default items are not
        rendered/visible.
        """
        assert not analytics_dashboard.has_visible_menu_items()


    @pytest.mark.functional
    @pytest.mark.positive
    @pytest.mark.high
    def test_TC_DB22_P_menu_available_on_newly_created_dashboard(manage_view, disposable_dashboard):
        """
        TC-DB22-P: Menu available on a newly created dashboard.
        Preconditions: user logged in; just created a new dashboard.
        Steps: create a new dashboard, click its three-dots icon.
        Expected: menu opens with all four options on the new card.
        """
        card = manage_view.get_card_by_name(disposable_dashboard)
        assert card is not None

        menu = card.open_context_menu()
        assert menu.is_open()
        assert menu.get_item_labels() == ContextMenu.EXPECTED_LABELS


    @pytest.mark.ui
    @pytest.mark.positive
    @pytest.mark.low
    def test_TC_DB23_P_only_one_card_menu_open_at_a_time(
        manage_view, analytics_dashboard, disposable_dashboard
    ):
        """
        TC-DB23-P: Only one card menu open at a time.
        Preconditions: user logged in; >=2 dashboard cards exist.
        Steps: open card A menu, click card B three-dots.
        Expected: card A menu closes; only card B menu is open.
        """
        card_a = analytics_dashboard
        card_b = manage_view.get_card_by_name(disposable_dashboard)
        assert card_b is not None

        menu_a = card_a.open_context_menu()
        assert menu_a.is_open()

        menu_b = card_b.open_context_menu()
        assert menu_b.is_open()
        # A single global menu root implies opening B's closes A's automatically;
        # if your app renders one menu instance per card, replace this with a
        # per-card is_open() check instead.
        assert len(manage_view.driver.find_elements(*ContextMenu.ROOT)) == 1

    pytest.mark.functional
    @pytest.mark.positive
    @pytest.mark.high
    def test_TC_DB24_P_open_item_opens_the_dashboard(manage_view, analytics_dashboard):
        """
        TC-DB24-P: Open item opens the dashboard.
        Preconditions: user logged in; three-dots menu open on 'Analytics'.
        Steps: click 'Open'.
        Expected: the 'Analytics' dashboard opens/switches; menu closes.
        """
        menu = analytics_dashboard.open_context_menu()
        menu.click_open()
        menu.wait_until_closed()

        assert not menu.is_open()
        # TODO: add a stronger assertion once you know the real "dashboard is
        # open" signal, e.g. URL contains the dashboard id or a
        # dashboard-content container is visible.
        assert "#/stats" in manage_view.driver.current_url


    @pytest.mark.functional
    @pytest.mark.positive
    @pytest.mark.medium
    def test_TC_DB25_P_open_matches_clicking_the_card(manage_view, analytics_dashboard):
        """
        TC-DB25-P: Open matches clicking the card (consistency check).
        Preconditions: user logged in; 'Analytics' dashboard exists.
        Steps: note the state after clicking the card, repeat via menu 'Open'.
        Expected: both paths land on the same opened-dashboard state.
        """
        driver = manage_view.driver

        analytics_dashboard.click()
        url_via_click = driver.current_url
        form_open_via_click = len(driver.find_elements(*DashboardForm.NAME_INPUT)) > 0

        manage_view.driver.get(manage_view.driver.current_url.split("#")[0] + "#/stats")
        manage_view.wait_for_card_present("Analytics")
        card = manage_view.get_card_by_name("Analytics")

        menu = card.open_context_menu()
        menu.click_open()
        menu.wait_until_closed()
        url_via_menu = driver.current_url
        form_open_via_menu = len(driver.find_elements(*DashboardForm.NAME_INPUT)) > 0

        assert url_via_click == url_via_menu
        assert form_open_via_click == form_open_via_menu



    @pytest.mark.functional
    @pytest.mark.positive
    @pytest.mark.high
    def test_TC_DB26_P_rename_opens_editable_field_prefilled(analytics_dashboard):
        """
        TC-DB26-P: Rename opens an editable field prefilled.
        Preconditions: user logged in; three-dots menu open on 'Analytics'.
        Steps: click 'Rename'.
        Expected: a rename input appears prefilled with the current name 'Analytics'.
        """
        menu = analytics_dashboard.open_context_menu()
        rename_field = menu.click_rename()

        assert rename_field.is_open()
        assert rename_field.get_name_value() == "Analytics"
        rename_field.cancel()


    @pytest.mark.functional
    @pytest.mark.positive
    @pytest.mark.high
    def test_TC_DB27_P_rename_to_valid_new_name_updates_the_card(manage_view, analytics_dashboard):
        """
        TC-DB27-P: Rename to a valid new name updates the card.
        Preconditions: user logged in; rename field open.
        Steps: clear field, enter 'Analytics v2', confirm/save.
        Expected: card title updates to 'Analytics v2'; menu/field closes.
        Note: mutates data — renames back to 'Analytics' as teardown so
        later tests relying on the 'Analytics' fixture still find it.
        """
        menu = analytics_dashboard.open_context_menu()
        rename_field = menu.click_rename()
        rename_field.enter_name("Analytics v2")
        rename_field.save()
        rename_field.wait_until_closed()

        try:
            manage_view.wait_for_card_present("Analytics v2")
            renamed_card = manage_view.get_card_by_name("Analytics v2")
            assert renamed_card is not None
            assert renamed_card.title == "Analytics v2"
        finally:
            card = manage_view.get_card_by_name("Analytics v2")
            if card is not None:
                menu2 = card.open_context_menu()
                rename_back = menu2.click_rename()
                rename_back.enter_name("Analytics")
                rename_back.save()
                rename_back.wait_until_closed()


    @pytest.mark.functional
    @pytest.mark.negative
    @pytest.mark.high
    def test_TC_DB28_N_empty_name_rejected_on_rename(analytics_dashboard):
        """
        TC-DB28-N: Empty name rejected on rename.
        Preconditions: user logged in; rename field open.
        Steps: clear the field, confirm/save.
        Expected: rename blocked; original name retained; validation shown.
        * Invert this assertion if your app intentionally allows empty names.
        """
        original_title = analytics_dashboard.title
        menu = analytics_dashboard.open_context_menu()
        rename_field = menu.click_rename()

        rename_field.clear_name()
        rename_field.save()

        assert rename_field.is_open(), "Expected rename to stay open on empty name"
        assert analytics_dashboard.title == original_title
        rename_field.cancel()


    @pytest.mark.functional
    @pytest.mark.negative
    @pytest.mark.medium
    def test_TC_DB29_N_whitespace_only_name_rejected(analytics_dashboard):
        """
        TC-DB29-N: Whitespace-only name rejected.
        Preconditions: user logged in; rename field open.
        Steps: enter ' ' (spaces), confirm/save.
        Expected: rename blocked, or trimmed to empty and rejected.
        """
        original_title = analytics_dashboard.title
        menu = analytics_dashboard.open_context_menu()
        rename_field = menu.click_rename()

        rename_field.enter_name("   ")
        rename_field.save()

        assert rename_field.is_open() or analytics_dashboard.title == original_title
        rename_field.cancel()


    @pytest.mark.functional
    @pytest.mark.positive
    @pytest.mark.medium
    def test_TC_DB30_P_cancel_rename_keeps_original_name(analytics_dashboard):
        """
        TC-DB30-P: Cancel rename keeps original name.
        Preconditions: user logged in; rename field open.
        Steps: enter a new name, cancel / press Esc.
        Expected: card retains the original name; no change persisted.
        """
        original_title = analytics_dashboard.title
        menu = analytics_dashboard.open_context_menu()
        rename_field = menu.click_rename()

        rename_field.enter_name("Should Not Persist")
        rename_field.cancel()
        rename_field.wait_until_closed()

        assert analytics_dashboard.title == original_title


    @pytest.mark.functional
    @pytest.mark.positive
    @pytest.mark.low
    @pytest.mark.parametrize("name", BOUNDARY_NAMES)
    def test_TC_DB31_P_rename_accepts_unicode_and_boundary_names(
        manage_view, disposable_dashboard, name
    ):
        """
        TC-DB31-P: Rename accepts unicode and boundary names (parametrized).
        Preconditions: user logged in; rename field open.
        Steps: enter each value and save.
        Expected: accepts 'Ünïcode Náme', 'Dashboard-2026_v1', a 200+ char
        name, and the other boundary values.
        """
        card = manage_view.get_card_by_name(disposable_dashboard)
        menu = card.open_context_menu()
        rename_field = menu.click_rename()
        rename_field.enter_name(name)
        rename_field.save()
        rename_field.wait_until_closed()

        manage_view.wait_for_card_present(name)
        renamed = manage_view.get_card_by_name(name)
        assert renamed is not None
        assert renamed.title == name

        # Rename back so the `disposable_dashboard` fixture's teardown (which
        # looks the card up by its original name) can still find and delete it.
        menu2 = renamed.open_context_menu()
        rename_back = menu2.click_rename()
        rename_back.enter_name(disposable_dashboard)
        rename_back.save()
        rename_back.wait_until_closed()


    @pytest.mark.functional
    @pytest.mark.positive
    @pytest.mark.low
    def test_TC_DB32_P_rename_refreshes_updated_on_date(manage_view, disposable_dashboard):
        """
        TC-DB32-P: Rename refreshes 'Updated on' date.
        Preconditions: user logged in; card renamed successfully.
        Steps: rename a card, read its 'Updated on' value.
        Expected: 'Updated on' reflects today's date after rename.
        """
        card = manage_view.get_card_by_name(disposable_dashboard)
        new_name = f"{disposable_dashboard}-renamed"

        menu = card.open_context_menu()
        rename_field = menu.click_rename()
        rename_field.enter_name(new_name)
        rename_field.save()
        rename_field.wait_until_closed()

        manage_view.wait_for_card_present(new_name)
        renamed = manage_view.get_card_by_name(new_name)
        assert contains_todays_date(renamed.updated_on_text)

        # Rename back for the fixture's teardown.
        menu2 = renamed.open_context_menu()
        rename_back = menu2.click_rename()
        rename_back.enter_name(disposable_dashboard)
        rename_back.save()
        rename_back.wait_until_closed()


    @pytest.mark.skip(
        reason="Manual per test sheet - confirm product rule for duplicate names "
        "before automating"
    )
    @pytest.mark.functional
    @pytest.mark.negative
    @pytest.mark.medium
    def test_TC_DB33_N_duplicate_name_handling(manage_view, analytics_dashboard, disposable_dashboard):
        """
        TC-DB33-N: Duplicate name handling.
        Preconditions: user logged in; >=2 dashboards exist.
        Steps: rename card B to card A's exact name, save.
        Expected: duplicate rejected or disambiguated per spec (no silent collision).
        """
        card_b = manage_view.get_card_by_name(disposable_dashboard)
        menu = card_b.open_context_menu()
        rename_field = menu.click_rename()
        rename_field.enter_name(analytics_dashboard.title)
        rename_field.save()

        # TODO: assert your app's actual duplicate-name rule here once confirmed
        # (e.g. validation error shown, or auto-suffixed name like "Analytics (2)").
        assert rename_field.get_validation_error() is not None


    @pytest.mark.functional
    @pytest.mark.positive
    @pytest.mark.high
    def test_TC_DB34_P_delete_shows_a_confirmation_prompt(analytics_dashboard):
        """
        TC-DB34-P: Delete shows a confirmation prompt (guards accidental deletion).
        Preconditions: user logged in; three-dots menu open.
        Steps: click 'Delete'.
        Expected: a confirmation dialog/prompt appears before any removal.
        """
        menu = analytics_dashboard.open_context_menu()
        dialog = menu.click_delete()

        assert dialog.is_open()
        dialog.cancel()  # don't actually delete the shared 'Analytics' fixture card


    @pytest.mark.functional
    @pytest.mark.positive
    @pytest.mark.high
    def test_TC_DB35_P_confirm_delete_removes_the_card(manage_view, disposable_dashboard):
        """
        TC-DB35-P: Confirm delete removes the card.
        Preconditions: user logged in; a disposable dashboard exists.
        Steps: click 'Delete', confirm.
        Expected: card is removed; saved count decreases by 1.
        """
        before = manage_view.cards_count()
        card = manage_view.get_card_by_name(disposable_dashboard)

        menu = card.open_context_menu()
        dialog = menu.click_delete()
        dialog.confirm()

        manage_view.wait_for_card_absent(disposable_dashboard)
        assert manage_view.cards_count() == before - 1
        assert manage_view.get_card_by_name(disposable_dashboard) is None


    @pytest.mark.functional
    @pytest.mark.positive
    @pytest.mark.high
    def test_TC_DB36_P_cancel_delete_keeps_the_card(manage_view, disposable_dashboard):
        """
        TC-DB36-P: Cancel delete keeps the card.
        Preconditions: user logged in; delete confirmation shown.
        Steps: click 'Delete', cancel.
        Expected: dialog closes; card remains; count unchanged.
        """
        before = manage_view.cards_count()
        card = manage_view.get_card_by_name(disposable_dashboard)

        menu = card.open_context_menu()
        dialog = menu.click_delete()
        dialog.cancel()
        dialog.wait_until_closed()

        assert manage_view.cards_count() == before
        assert manage_view.get_card_by_name(disposable_dashboard) is not None


    @pytest.mark.functional
    @pytest.mark.positive
    @pytest.mark.medium
    def test_TC_DB37_P_deleted_dashboard_stays_gone_after_reload(manage_view, disposable_dashboard):
        """
        TC-DB37-P: Deleted dashboard stays gone after reload (persistence).
        Preconditions: user logged in; a card just deleted.
        Steps: delete and confirm, reload #/stats.
        Expected: the deleted card does not reappear.
        """
        card = manage_view.get_card_by_name(disposable_dashboard)
        menu = card.open_context_menu()
        dialog = menu.click_delete()
        dialog.confirm()
        manage_view.wait_for_card_absent(disposable_dashboard)

        manage_view.driver.refresh()
        manage_view.wait.until(lambda d: manage_view.is_rendered())

        assert manage_view.get_card_by_name(disposable_dashboard) is None


    @pytest.mark.skip(
        reason="Manual per test sheet - confirm product rule for deleting the "
        "default dashboard before automating"
    )
    @pytest.mark.functional
    @pytest.mark.negative
    @pytest.mark.high
    def test_TC_DB38_N_deleting_the_default_dashboard(manage_view, disposable_dashboard):
        """
        TC-DB38-N: Deleting the default dashboard.
        Preconditions: user logged in; target card has the 'Default' badge.
        Steps: delete the current default dashboard, confirm.
        Expected: handled per spec — blocked, or default reassigned to
        another card (no orphaned default).
        """
        card = manage_view.get_card_by_name(disposable_dashboard)
        menu = card.open_context_menu()
        menu.click_set_default()
        assert card.is_default()

        menu2 = card.open_context_menu()
        dialog = menu2.click_delete()
        dialog.confirm()

        # TODO: assert your app's real rule once confirmed — e.g. no card has
        # is_default() == True with zero dashboards left, or another card
        # automatically inherits the Default badge.


    @pytest.mark.skip(
        reason="Manual per test sheet - edge case, confirm behavior for an "
        "empty dashboard list before automating"
    )
    @pytest.mark.functional
    @pytest.mark.negative
    @pytest.mark.medium
    def test_TC_DB39_N_deleting_the_last_remaining_dashboard(manage_view):
        """
        TC-DB39-N: Deleting the last remaining dashboard.
        Preconditions: user logged in; exactly 1 dashboard exists.
        Steps: delete the only dashboard, confirm.
        Expected: handled gracefully — empty-state shown or deletion blocked
        per spec.
        Note: this test needs an environment seeded with exactly one
        dashboard; it is not safe to run against a shared environment as-is.
        """
        assert manage_view.cards_count() == 1, "Precondition not met: expected exactly 1 dashboard"
        card = manage_view.get_all_cards()[0]

        menu = card.open_context_menu()
        dialog = menu.click_delete()
        dialog.confirm()

        # TODO: assert your app's real empty-state behavior once confirmed.



    @pytest.mark.functional
    @pytest.mark.positive
    @pytest.mark.high
    def test_TC_DB40_P_set_as_default_marks_the_card_default(manage_view, disposable_dashboard):
        """
        TC-DB40-P: Set as Default marks the card default.
        Preconditions: user logged in; non-default card menu open.
        Steps: click 'Set as Default'.
        Expected: target card shows the 'Default' badge.
        """
        card = manage_view.get_card_by_name(disposable_dashboard)
        assert not card.is_default()

        menu = card.open_context_menu()
        menu.click_set_default()

        card = manage_view.get_card_by_name(disposable_dashboard)
        assert card.is_default()


    @pytest.mark.functional
    @pytest.mark.positive
    @pytest.mark.high
    def test_TC_DB41_P_only_one_default_at_a_time(manage_view, analytics_dashboard, disposable_dashboard):
        """
        TC-DB41-P: Only one default at a time (mutual exclusivity).
        Preconditions: user logged in; card A is currently default.
        Steps: set card B as default.
        Expected: card B gains 'Default' badge; card A loses it (exactly one default).
        """
        card_a = analytics_dashboard
        menu_a = card_a.open_context_menu()
        menu_a.click_set_default()
        card_a = manage_view.get_card_by_name("Analytics")
        assert card_a.is_default()

        card_b = manage_view.get_card_by_name(disposable_dashboard)
        menu_b = card_b.open_context_menu()
        menu_b.click_set_default()

        card_a = manage_view.get_card_by_name("Analytics")
        card_b = manage_view.get_card_by_name(disposable_dashboard)
        assert card_b.is_default()
        assert not card_a.is_default()


    @pytest.mark.functional
    @pytest.mark.positive
    @pytest.mark.medium
    def test_TC_DB42_P_default_persists_after_reload(manage_view, disposable_dashboard):
        """
        TC-DB42-P: Default persists after reload.
        Preconditions: user logged in; a new default just set.
        Steps: set a default, reload #/stats.
        Expected: the chosen card still shows 'Default'.
        """
        card = manage_view.get_card_by_name(disposable_dashboard)
        menu = card.open_context_menu()
        menu.click_set_default()

        manage_view.driver.refresh()
        manage_view.wait.until(lambda d: manage_view.is_rendered())

        card = manage_view.get_card_by_name(disposable_dashboard)
        assert card.is_default()


    @pytest.mark.functional
    @pytest.mark.negative
    @pytest.mark.medium
    def test_TC_DB43_N_set_as_default_on_already_default_card(manage_view, disposable_dashboard):
        """
        TC-DB43-N: Set as Default on already-default card.
        Preconditions: user logged in; menu open on the current default card.
        Steps: click 'Set as Default' on the default card.
        Expected: no-op / option disabled or hidden; single default preserved.
        """
        card = manage_view.get_card_by_name(disposable_dashboard)
        menu = card.open_context_menu()
        menu.click_set_default()
        card = manage_view.get_card_by_name(disposable_dashboard)
        assert card.is_default()

        menu2 = card.open_context_menu()
        # TODO: confirm expected UX — this assumes the option is still clickable
        # and simply a no-op. If your app disables/hides it instead, assert that
        # the 'Set as Default' item is absent or has a disabled attribute here.
        menu2.click_set_default()

        card = manage_view.get_card_by_name(disposable_dashboard)
        assert card.is_default()
        assert sum(1 for c in manage_view.get_all_cards() if c.is_default()) == 1


    @pytest.mark.skip(
        reason="Manual per test sheet - confirm default-dashboard-loads-first "
        "behavior against product spec before automating"
    )
    @pytest.mark.functional
    @pytest.mark.positive
    @pytest.mark.medium
    def test_TC_DB44_P_default_dashboard_loads_first_on_entry(manage_view, disposable_dashboard):
        """
        TC-DB44-P: Default dashboard loads first on entry.
        Preconditions: user logged in; a default is set.
        Steps: re-enter #/stats fresh.
        Expected: the default dashboard is the one presented/selected first.
        """
        card = manage_view.get_card_by_name(disposable_dashboard)
        menu = card.open_context_menu()
        menu.click_set_default()

        manage_view.driver.refresh()
        manage_view.wait.until(lambda d: manage_view.is_rendered())

        # TODO: assert your app's real "presented first" signal once confirmed,
        # e.g. the default dashboard's content is auto-opened/highlighted.
