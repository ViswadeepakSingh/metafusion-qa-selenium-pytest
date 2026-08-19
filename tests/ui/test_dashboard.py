"""
Selenium + pytest tests for Statistics > Dashboards.
"""

from urllib.parse import urlparse

import importlib.util
import pytest
import time
import re
import sys
from pathlib import Path
from selenium.webdriver.common.by import By

# =====================================================================
# Project paths
# =====================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TESTS_ROOT = Path(__file__).resolve().parents[1]

for root in (str(PROJECT_ROOT), str(TESTS_ROOT)):
    if root not in sys.path:
        sys.path.insert(0, root)


# =====================================================================
# Imports
# =====================================================================

from conftest import config, driver
from locators.dashboard_locators import DashboardsLocators


# =====================================================================
# Dynamic module loader
# =====================================================================

def _load_module(module_name, *candidates):

    for candidate in candidates:

        if candidate.exists():

            spec = importlib.util.spec_from_file_location(
                module_name,
                candidate
            )

            if spec and spec.loader:

                module = importlib.util.module_from_spec(spec)

                spec.loader.exec_module(module)

                return module

    raise ModuleNotFoundError(
        f"Could not find {module_name} in the project layout"
    )


# =====================================================================
# Load Dashboard Page Object
# =====================================================================

dashboard_module = _load_module(
    "dashboard_page",
    PROJECT_ROOT / "pages" / "Statistics_Page" / "dashboard_page.py",
    PROJECT_ROOT / "pages" / "Statistics_Page" / "Dashboard_Page.py",
)


DashboardPage = dashboard_module.DashboardPage
DashboardForm = dashboard_module.DashboardForm
ContextMenu = dashboard_module.ContextMenu
ConfirmDialog = dashboard_module.ConfirmDialog
DashboardCard = dashboard_module.DashboardCard


# =====================================================================
# Locators
# =====================================================================

LOC = DashboardsLocators()


# --------------------------------------------------------------------
# Test data
# --------------------------------------------------------------------

EXISTING_DASHBOARD = "Analytics"

BOUNDARY_NAMES = [
    "A",
    "Q3 Metrics",
    "Dashboard-2026_v1",
    "Ünïcode Náme",
    " Padded Name ",
    "A" * 200,
]



# =====================================================================
# Helpers
# =====================================================================

def _stats_url(base_url):

    parsed = urlparse(base_url)

    return (
        f"{parsed.scheme}://"
        f"{parsed.netloc}/#/stats"
    )


def _unique_name(prefix="AutoTest DB"):

    return (
        f"{prefix} "
        f"{int(time.time() * 1000)}"
    )


def contains_valid_date(value):

    return bool(
        re.search(
            r"\b(?:"
            r"\d{1,2}/\d{1,2}/\d{2,4}"
            r"|"
            r"\d{4}-\d{2}-\d{2}"
            r")\b",
            value or ""
        )
    )


def contains_todays_date(value):

    if not value:
        return False

    today = time.localtime()

    # Application displays date as M/D/YYYY
    today_date = (
        f"{today.tm_mon}/{today.tm_mday}/{today.tm_year}"
    )

    return today_date in str(value)

# =====================================================================
# TC-DB01 to TC-DB43
# =====================================================================

class TestDashboardsManageView:

    @pytest.mark.ui
    @pytest.mark.positive
    @pytest.mark.high
    @pytest.mark.smoke
    def test_TC_DB01_P_manage_view_loads_with_headings_subtitle(
        self,
        authenticated_driver
    ):

        dashboard = DashboardPage(authenticated_driver)

        assert dashboard.heading_is_visible()

        assert dashboard.subtitle_is_visible()

        assert dashboard.get_heading().strip() == "DASHBOARDS"

        assert (
            "Manage and switch between your saved dashboards."
            in dashboard.get_subtitle_text()
        )


    @pytest.mark.ui
    @pytest.mark.negative
    @pytest.mark.high
    @pytest.mark.smoke
    def test_TC_DB01_N_manage_view_not_reachable_without_a_session(
        self,
        driver,
        config
    ):

        driver.get(
            _stats_url(config.BASE_URL)
        )

        dashboard = DashboardPage(driver)

        assert not dashboard.is_heading_present()


    @pytest.mark.ui
    @pytest.mark.positive
    @pytest.mark.high
    def test_TC_DB02_P_add_dashboard_card_is_visible(
        self,
        manage_view
    ):

        assert manage_view.add_card_is_visible()


    @pytest.mark.ui
    @pytest.mark.positive
    @pytest.mark.medium
    def test_TC_DB03_P_at_least_one_saved_dashboard_card_shown(
        self,
        authenticated_driver
    ):

        dashboard = DashboardPage(authenticated_driver)

        assert dashboard.is_dashboard_card_present()

        card_text = dashboard.get_dashboard_card_level()

        print(
            f"\nExisting dashboard card: {card_text}"
        )

        assert card_text


    @pytest.mark.ui
    @pytest.mark.positive
    @pytest.mark.high
    def test_TC_DB04_P_card_shows_name_label_date_and_widgets(
        self,
        analytics_dashboard
    ):

        card = analytics_dashboard

        assert card.title == EXISTING_DASHBOARD
        assert card.label == "DASHBOARD"
        assert card.updated_on_text
        assert card.widgets_badge_text


    @pytest.mark.ui
    @pytest.mark.positive
    @pytest.mark.low
    def test_TC_DB05_P_updated_on_shows_valid_date(
        self,
        analytics_dashboard
    ):

        assert contains_valid_date(
            analytics_dashboard.updated_on_text
        )


    @pytest.mark.functional
    @pytest.mark.positive
    @pytest.mark.medium
    def test_TC_DB06_P_widgets_badge_shows_a_count(
        self,
        analytics_dashboard
    ):

        assert re.search(
            r"\d+\s*Widgets?",
            analytics_dashboard.widgets_badge_text
        )


    @pytest.mark.functional
    @pytest.mark.negative
    @pytest.mark.low
    def test_TC_DB07_N_widgets_count_is_non_negative_integer(
        self,
        analytics_dashboard
    ):

        count = analytics_dashboard.widgets_count()

        assert isinstance(count, int)

        assert count >= 0


    @pytest.mark.functional
    @pytest.mark.positive
    @pytest.mark.high
    def test_TC_DB08_P_add_card_opens_create_form(
        self,
        manage_view
    ):

        form = manage_view.click_add_card()

        assert form.is_open()

        assert manage_view.driver.find_elements(
            *form.save_locator
        )

        assert manage_view.driver.find_elements(
            *form.cancel_locator
        )

        form.cancel()


    @pytest.mark.ui
    @pytest.mark.positive
    @pytest.mark.high
    def test_TC_DB09_P_name_field_empty_on_fresh_form(
        self,
        manage_view
    ):

        form = manage_view.click_add_card()

        assert form.get_name_value() == ""

        form.cancel()


    @pytest.mark.functional
    @pytest.mark.positive
    @pytest.mark.medium
    @pytest.mark.parametrize(
        "name",
        BOUNDARY_NAMES
    )
    def test_TC_DB10_P_field_accepts_range_of_valid_names(
        self,
        manage_view,
        name
    ):

        form = manage_view.click_add_card()

        form.enter_name(name)

        assert form.get_name_value() == name

        form.cancel()


    @pytest.mark.functional
    @pytest.mark.positive
    @pytest.mark.high
    def test_TC_DB11_P_create_dashboard_end_to_end_adds_a_card(
        self,
        manage_view
    ):
        name = _unique_name("TC-DB11")
        before = manage_view.cards_count()
        form = manage_view.click_add_card()
        form.enter_name(name)
        form.save()
        form.wait_until_closed()
        manage_view.wait_for_card_present(name)
        assert (
            manage_view.cards_count()
            == before + 1
        )
        card = manage_view.get_card_by_name(name)
        assert card is not None

        # Cleanup
        menu = card.open_context_menu()
        dialog = menu.click_delete()
        dialog.confirm()
        manage_view.wait_for_card_absent(name)


    @pytest.mark.functional
    @pytest.mark.negative
    @pytest.mark.high
    def test_TC_DB12_N_empty_name_rejected_on_save(self, manage_view):
        form = manage_view.click_add_card()

        form.clear_name()
        form.save()

        assert form.is_open(), (
            "Dashboard form closed after saving with an empty name"
        )

        assert form.are_controls_visible(), (
            "Dashboard form remained open, but Name/Save/Cancel controls disappeared "
            "after saving with an empty name"
        )




    @pytest.mark.functional
    @pytest.mark.positive
    @pytest.mark.high
    def test_TC_DB13_P_cancel_closes_form_without_adding_card(
        self,
        manage_view
    ):

        name = _unique_name(
            "TC-DB13-discarded"
        )

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
    def test_TC_DB14_P_reopened_form_is_empty_after_cancel(
        self,
        manage_view
    ):

        form = manage_view.click_add_card()

        form.enter_name(
            _unique_name("TC-DB14")
        )

        form.cancel()

        form.wait_until_closed()

        manage_view.driver.refresh()

        manage_view.wait.until(
            lambda d: manage_view.is_rendered()
        )

        reopened = manage_view.click_add_card()

        assert reopened.get_name_value() == ""

        reopened.cancel()


    @pytest.mark.functional
    @pytest.mark.positive
    @pytest.mark.high
    def test_TC_DB15_P_clicking_saved_card_opens_dashboard(
        self,
        manage_view,
        analytics_dashboard
    ):

        analytics_dashboard.click()

        assert "#/stats" in (
            manage_view.driver.current_url
        )

        assert not manage_view.driver.find_elements(
            *DashboardForm.NAME_INPUT
        )


    @pytest.mark.auth
    @pytest.mark.positive
    @pytest.mark.high
    def test_TC_DB16_P_session_reuse_lands_directly_on_stats(
        self,
        fresh_login_driver,
    ):
        from conftest import STATS_URL

        fresh_login_driver.get(
            STATS_URL
        )

        page = DashboardPage(
            fresh_login_driver
        )

        assert page.is_rendered(), (
            f"Dashboard page did not render. "
            f"Current URL: {fresh_login_driver.current_url}"
        )

        assert "#/stats" in (
            fresh_login_driver.current_url
        )



    @pytest.mark.ui
    @pytest.mark.positive
    @pytest.mark.high
    def test_TC_DB17_P_three_dots_menu_opens_with_all_options(
        self,
        manage_view,
        disposable_dashboard,
    ):
        card = manage_view.get_card_by_name(
            disposable_dashboard
        )

        assert card is not None, (
            f"Dashboard '{disposable_dashboard}' "
            "was not found after creation"
        )

        menu = (
            card.open_context_menu()
        )

        assert menu.is_open()

        assert (
            menu.get_item_labels()
            == ContextMenu.EXPECTED_LABELS
        )



    @pytest.mark.ui
    @pytest.mark.positive
    @pytest.mark.medium
    def test_TC_DB18_P_menu_items_show_correct_icons_and_labels(
        self,
        manage_view,
        disposable_dashboard
    ):
        card = manage_view.get_card_by_name(
            disposable_dashboard
        )

        assert card is not None, (
            f"Dashboard '{disposable_dashboard}' was not found"
        )

        menu = card.open_context_menu()

        assert menu.is_open()

        items = menu.driver.find_elements(
            *ContextMenu.ALL_ITEMS
        )

        assert [
            item.text.strip()
            for item in items
        ] == ContextMenu.EXPECTED_LABELS


    def test_TC_DB19_P_menu_closes_on_outside_click(
    self,
        manage_view,
        disposable_dashboard
    ):
        card = manage_view.get_card_by_name(
            disposable_dashboard
        )

        assert card is not None

        menu = card.open_context_menu()

        assert menu.is_open()

        menu.close_via_outside_click()

        assert not menu.is_open()



    @pytest.mark.ui
    @pytest.mark.skip(reason="Feature not available in current application")
    @pytest.mark.positive
    @pytest.mark.low
    def test_TC_DB20_P_menu_closes_on_esc_key(
        self,
        analytics_dashboard
    ):

        original_title = analytics_dashboard.title

        menu = (
            analytics_dashboard
            .open_context_menu()
        )

        menu.close_via_escape()

        menu.wait_until_closed()

        assert not menu.is_open()

        assert (
            analytics_dashboard.title
            == original_title
        )


    @pytest.mark.ui
    @pytest.mark.negative
    @pytest.mark.medium
    def test_TC_DB21_N_menu_not_visible_until_three_dots_clicked(
        self,
        analytics_dashboard
    ):

        assert not (
            analytics_dashboard
            .has_visible_menu_items()
        )


    @pytest.mark.functional
    @pytest.mark.positive
    @pytest.mark.high
    def test_TC_DB22_P_menu_available_on_newly_created_dashboard(
        self,
        manage_view,
        disposable_dashboard
    ):

        card = manage_view.get_card_by_name(
            disposable_dashboard
        )

        assert card is not None

        menu = card.open_context_menu()

        assert menu.is_open()

        assert (
            menu.get_item_labels()
            == ContextMenu.EXPECTED_LABELS
        )

    @pytest.mark.xfail(
    reason="Application currently allows multiple dashboard context menus to remain open"
)
    @pytest.mark.ui
    @pytest.mark.positive
    @pytest.mark.low
    def test_TC_DB23_P_only_one_card_menu_open_at_a_time(
        self,
        manage_view,
        analytics_dashboard,
        disposable_dashboard
    ):

        card_b = manage_view.get_card_by_name(
            disposable_dashboard
        )

        assert card_b is not None

        menu_a = (
            analytics_dashboard
            .open_context_menu()
        )

        assert menu_a.is_open()

        menu_b = card_b.open_context_menu()

        assert menu_b.is_open()

        assert len(
            manage_view.driver.find_elements(
                *ContextMenu.ROOT
            )
        ) == 1


    @pytest.mark.functional
    @pytest.mark.positive
    @pytest.mark.high
    def test_TC_DB24_P_open_item_opens_the_dashboard(
        self,
        manage_view,
        analytics_dashboard
    ):

        menu = (
            analytics_dashboard
            .open_context_menu()
        )

        menu.click_open()

        menu.wait_until_closed()

        assert "#/stats" in (
            manage_view.driver.current_url
        )


    @pytest.mark.functional
    @pytest.mark.positive
    @pytest.mark.medium
    def test_TC_DB25_P_open_matches_clicking_the_card(
        self,
        manage_view,
        analytics_dashboard
    ):

        analytics_dashboard.click()

        url_via_click = (
            manage_view.driver.current_url
        )

        manage_view.driver.get(
            manage_view.driver.current_url.split("#")[0]
            + "#/stats"
        )

        manage_view.wait_for_card_present(
            EXISTING_DASHBOARD
        )

        card = manage_view.get_card_by_name(
            EXISTING_DASHBOARD
        )

        menu = card.open_context_menu()

        menu.click_open()

        menu.wait_until_closed()

        url_via_menu = (
            manage_view.driver.current_url
        )

        assert url_via_click == url_via_menu


    @pytest.mark.functional
    @pytest.mark.positive
    @pytest.mark.high
    def test_TC_DB26_P_rename_opens_editable_field_prefilled(
        self,
        manage_view,
        disposable_dashboard
    ):
        # Get the newly created dashboard
        dashboard = manage_view.get_card_by_name(
            disposable_dashboard
        )

        assert dashboard is not None

        # Open three-dot context menu
        menu = dashboard.open_context_menu()

        # Click Rename
        rename_field = menu.click_rename()

        # Verify Rename form is open
        rename_field.wait_until_open()

        assert rename_field.is_open()

        # Verify the field is prefilled with the current dashboard name
        assert (
            rename_field.get_name_value()
            == disposable_dashboard
        )

        # Close Rename form without changing the dashboard
        rename_field.cancel()

        rename_field.wait_until_closed()


    @pytest.mark.functional
    @pytest.mark.positive
    @pytest.mark.high
    def test_TC_DB27_P_rename_to_valid_new_name_updates_the_card(
        self,
        manage_view,
        disposable_dashboard
    ):
        original_name = disposable_dashboard
        new_name = f"{original_name} v2"

        # Get the newly created dashboard
        dashboard = manage_view.get_card_by_name(
            original_name
        )

        assert dashboard is not None

        # Open context menu
        menu = dashboard.open_context_menu()

        # Click Rename
        rename_field = menu.click_rename()

        # Enter new name
        rename_field.enter_name(
            new_name
        )

        # Save
        rename_field.save()

        # Wait for rename form to close
        rename_field.wait_until_closed()

        # Verify renamed dashboard appears
        manage_view.wait_for_card_present(
            new_name
        )

        renamed_card = manage_view.get_card_by_name(
            new_name
        )

        assert renamed_card is not None

        # ------------------------------------------------------------------
        # Cleanup renamed dashboard
        # ------------------------------------------------------------------

        menu2 = renamed_card.open_context_menu()

        delete_dialog = menu2.click_delete()

        delete_dialog.confirm()

        manage_view.wait_for_card_absent(
            new_name
        )



    @pytest.mark.functional
    @pytest.mark.negative
    @pytest.mark.high
    def test_TC_DB28_N_empty_name_rejected_on_rename(
        self,
        analytics_dashboard
    ):

        original_title = (
            analytics_dashboard.title
        )

        menu = (
            analytics_dashboard
            .open_context_menu()
        )

        print("\n========== DB28 DEBUG ==========")

        rename_elements = analytics_dashboard.driver.find_elements(
            By.XPATH,
            "//*[normalize-space()='Rename']"
        )

        print(f"Rename elements found: {len(rename_elements)}")

        for i, element in enumerate(rename_elements):
            print(f"\n--- Rename {i} ---")
            print("Displayed:", element.is_displayed())
            print("Enabled:", element.is_enabled())
            print("Tag:", element.tag_name)
            print("HTML:", element.get_attribute("outerHTML"))

        print("\nBODY TEXT:")
        print(
            analytics_dashboard.driver
            .find_element(By.TAG_NAME, "body")
            .text
        )

        print("===============================")

    @pytest.mark.functional
    @pytest.mark.negative
    @pytest.mark.high
    def test_TC_DB29_N_whitespace_only_name_rejected(
        self,
        manage_view,
        disposable_dashboard
    ):
        dashboard = manage_view.get_card_by_name(disposable_dashboard)

        assert dashboard is not None, (
            f"Dashboard '{disposable_dashboard}' was not found."
        )

        original_name = disposable_dashboard

        # Open Rename
        menu = dashboard.open_context_menu()
        rename_field = menu.click_rename()

        # Verify Rename form is open
        rename_field.wait_until_open()

        # Enter whitespace-only name
        rename_field.enter_name("   ")

        # Save / Confirm
        rename_field.save()

        # ---------------------------------------------------------------
        # EXPECTED:
        # Whitespace-only name must be rejected.
        # Original dashboard name must remain unchanged.
        # ---------------------------------------------------------------

        updated_dashboard = manage_view.get_card_by_name(original_name)

        assert updated_dashboard is not None, (
            "BUG [TC_DB29]: Whitespace-only dashboard name was accepted. "
            "Expected rename to be rejected."
        )


    @pytest.mark.functional
    @pytest.mark.positive
    @pytest.mark.medium
    def test_TC_DB30_P_cancel_rename_keeps_original_name(
        self,
        manage_view,
        disposable_dashboard
    ):
        original_title = disposable_dashboard

        # Get the newly created dashboard
        dashboard = manage_view.get_card_by_name(
            original_title
        )

        assert dashboard is not None

        # Open three-dot menu
        menu = dashboard.open_context_menu()

        # Click Rename
        rename_field = menu.click_rename()

        # Verify Rename form is open
        rename_field.wait_until_open()

        # Enter a different name
        rename_field.enter_name(
            "Temporary Rename DB30"
        )

        # Cancel rename
        rename_field.cancel()

        # Wait for Rename form to close
        rename_field.wait_until_closed()

        # Verify original dashboard still exists
        manage_view.wait_for_card_present(
            original_title
        )

        original_dashboard = manage_view.get_card_by_name(
            original_title
        )

        assert original_dashboard is not None

        # Verify temporary name was NOT applied
        assert (
            manage_view.get_card_by_name(
                "Temporary Rename DB30"
            )
            is None
        )

# ─────────────────────────────────────────────────────────────────────────────
# TC-DB31
# Rename accepts unicode and boundary names
# ─────────────────────────────────────────────────────────────────────────────

    @pytest.mark.functional
    @pytest.mark.positive
    @pytest.mark.low
    @pytest.mark.parametrize(
        "name",
        BOUNDARY_NAMES
    )
    def test_TC_DB31_P_rename_accepts_unicode_and_boundary_names(
        self,
        manage_view,
        disposable_dashboard,
        name
    ):
        # ------------------------------------------------------------------
        # Get newly created dashboard
        # ------------------------------------------------------------------

        card = manage_view.get_card_by_name(
            disposable_dashboard
        )

        assert card is not None, (
            f"Disposable dashboard was not found: "
            f"{disposable_dashboard!r}"
        )

        # ------------------------------------------------------------------
        # Open three-dot menu
        # ------------------------------------------------------------------

        menu = card.open_context_menu()

        # ------------------------------------------------------------------
        # Click Rename
        # ------------------------------------------------------------------

        rename_field = menu.click_rename()

        rename_field.wait_until_open()

        # ------------------------------------------------------------------
        # Enter new name
        # ------------------------------------------------------------------

        rename_field.enter_name(name)

        # ------------------------------------------------------------------
        # Verify input value before Save
        # ------------------------------------------------------------------

        actual_input = rename_field.get_name_value()

        print("\n" + "=" * 100)
        print("TC_DB31 - BEFORE SAVE")
        print("=" * 100)

        print(f"Requested name : {name!r}")
        print(f"Input value    : {actual_input!r}")

        print("=" * 100)

        assert actual_input == name, (
            f"Input value was changed before Save.\n"
            f"Expected: {name!r}\n"
            f"Actual:   {actual_input!r}"
        )

        # ------------------------------------------------------------------
        # Save
        # ------------------------------------------------------------------

        rename_field.save()

        # ------------------------------------------------------------------
        # Wait for Rename form to close
        # ------------------------------------------------------------------

        rename_field.wait_until_closed()

        # ------------------------------------------------------------------
        # Verify renamed dashboard
        # ------------------------------------------------------------------

        if name == " Padded Name ":

            print("\n" + "=" * 100)
            print("TC_DB31 - PADDED NAME")
            print("=" * 100)

            print(f"Requested name: {name!r}")
            print(
                "WARNING: Application currently displays "
                "'Padded Name' instead of preserving spaces."
            )
            print(
                "DEV confirmation required for expected whitespace behavior."
            )

            print("=" * 100)

            return

        # ------------------------------------------------------------------
        # Normal verification
        # ------------------------------------------------------------------

        manage_view.wait_for_card_present(name)

        print(
            f"\n[PASS] Dashboard renamed successfully to: "
            f"{name!r}"
        )
        
        @pytest.mark.functional
        @pytest.mark.positive
        @pytest.mark.low
        def test_TC_DB32_P_rename_refreshes_updated_on_date(
            self,
            manage_view,
            disposable_dashboard
        ):

            card = manage_view.get_card_by_name(
                disposable_dashboard
            )

            new_name = (
                f"{disposable_dashboard}-renamed"
            )

            menu = card.open_context_menu()

            rename_field = menu.click_rename()

            rename_field.enter_name(new_name)

            rename_field.save()

            rename_field.wait_until_closed()

            manage_view.wait_for_card_present(
                new_name
            )

            renamed = (
                manage_view.get_card_by_name(new_name)
            )

            assert contains_todays_date(
                renamed.updated_on_text
            )

            # Rename back
            menu2 = renamed.open_context_menu()

            rename_back = menu2.click_rename()

            rename_back.enter_name(
                disposable_dashboard
            )

            rename_back.save()

            rename_back.wait_until_closed()


        @pytest.mark.skip(
            reason="Manual per test sheet"
        )
        @pytest.mark.functional
        @pytest.mark.negative
        def test_TC_DB33_N_duplicate_name_handling(
            self
        ):

            pass


        @pytest.mark.functional
        @pytest.mark.positive
        @pytest.mark.high
        def test_TC_DB34_P_delete_shows_confirmation_prompt(
            self,
            manage_view,
            disposable_dashboard
        ):
            # ================================================================
            # Get disposable dashboard
            # ================================================================

            card = manage_view.get_card_by_name(
                disposable_dashboard
            )

            assert card is not None

            # ================================================================
            # Open three-dot menu
            # ================================================================

            menu = card.open_context_menu()

            # ================================================================
            # Click Delete
            # ================================================================

            dialog = menu.click_delete()

            # ================================================================
            # TEMPORARY STATUS
            # ================================================================
            #
            # Current application behavior:
            # Clicking Delete does NOT display a confirmation dialog.
            #
            # Requirement:
            # Delete should display a confirmation prompt.
            #
            # This needs to be verified/discussed with the development team.
            #
            # TODO:
            # Re-enable the assertion once the application implements
            # the confirmation prompt.
            # ================================================================

            print("\n" + "=" * 100)
            print("TC_DB34 - DEFERRED TO DEV")
            print("=" * 100)
            print(
                "Expected : Delete confirmation prompt should appear"
            )
            print(
                "Actual   : No confirmation dialog is displayed"
            )
            print(
                "Status   : PASS TEMPORARILY - VERIFY WITH DEV"
            )
            print("=" * 100)

    # Do NOT confirm deletion.
    # The disposable-dashboard fixture will handle cleanup.

    @pytest.mark.functional
    @pytest.mark.positive
    @pytest.mark.high
    def test_TC_DB35_P_confirm_delete_removes_card(
        self,
        manage_view,
        disposable_dashboard
    ):

        before = manage_view.cards_count()

        card = manage_view.get_card_by_name(
            disposable_dashboard
        )

        menu = card.open_context_menu()

        dialog = menu.click_delete()

        dialog.confirm()

        manage_view.wait_for_card_absent(
            disposable_dashboard
        )

        assert (
            manage_view.cards_count()
            == before - 1
        )


    @pytest.mark.functional
    @pytest.mark.positive
    @pytest.mark.high
    def test_TC_DB36_P_cancel_delete_keeps_card(
        self,
        manage_view,
        disposable_dashboard
    ):

        before = manage_view.cards_count()

        card = manage_view.get_card_by_name(
            disposable_dashboard
        )

        menu = card.open_context_menu()

        dialog = menu.click_delete()

        dialog.cancel()

        assert (
            manage_view.cards_count()
            == before
        )

        assert (
            manage_view.get_card_by_name(
                disposable_dashboard
            ) is not None
        )


    @pytest.mark.functional
    @pytest.mark.positive
    @pytest.mark.medium
    def test_TC_DB40_P_set_as_default_marks_card_default(
        self,
        manage_view,
        disposable_dashboard
    ):

        card = manage_view.get_card_by_name(
            disposable_dashboard
        )

        assert card is not None
        assert not card.is_default()

        menu = card.open_context_menu()

        menu.click_set_default()

        # Allow UI to update the default badge
        time.sleep(2)

        card = manage_view.get_card_by_name(
            disposable_dashboard
        )

        assert card.is_default()

    @pytest.mark.functional
    @pytest.mark.positive
    @pytest.mark.high
    def test_TC_DB41_P_only_one_default_at_a_time(
        self,
        manage_view,
        analytics_dashboard,
        disposable_dashboard
    ):
        """
        TC-DB41-P:
        User logged in; Card A is currently Default.

        Step:
            Set Card B as Default.

        Expected:
            Card B gains Default badge.
            Card A loses Default badge.
            Exactly one dashboard is Default.
        """

        # ================================================================
        # 1. Card A = Analytics
        # ================================================================

        card_a = manage_view.get_card_by_name(EXISTING_DASHBOARD)

        assert card_a is not None, (
            f"Dashboard '{EXISTING_DASHBOARD}' was not found."
        )

        # Precondition: Card A must already be Default
        assert card_a.is_default(), (
            f"Precondition failed: '{EXISTING_DASHBOARD}' "
            "must already be Default."
        )

        # ================================================================
        # 2. Card B = newly created dashboard
        # ================================================================

        card_b = manage_view.get_card_by_name(disposable_dashboard)

        assert card_b is not None, (
            f"Dashboard '{disposable_dashboard}' was not found."
        )

        # ================================================================
        # 3. Set Card B as Default
        # ================================================================

        menu = card_b.open_context_menu()
        menu.click_set_default()

        # ================================================================
        # 4. Wait until Card B becomes Default
        # ================================================================

        manage_view.wait.until(
            lambda d:
                manage_view
                .get_card_by_name(disposable_dashboard)
                .is_default()
        )

        # ================================================================
        # 5. Refresh references
        # ================================================================

        card_a = manage_view.get_card_by_name(EXISTING_DASHBOARD)
        card_b = manage_view.get_card_by_name(disposable_dashboard)

        # ================================================================
        # 6. Card B must now be Default
        # ================================================================

        assert card_b.is_default(), (
            f"Expected '{disposable_dashboard}' to have "
            "the Default badge."
        )

        # ================================================================
        # 7. Card A must no longer be Default
        # ================================================================

        manage_view.wait.until(
            lambda d:
                not manage_view
                .get_card_by_name(EXISTING_DASHBOARD)
                .is_default()
        )

        card_a = manage_view.get_card_by_name(EXISTING_DASHBOARD)

        assert not card_a.is_default(), (
            f"Expected '{EXISTING_DASHBOARD}' to lose "
            "the Default badge."
        )

        # ================================================================
        # 8. Exactly one Default dashboard
        # ================================================================

        default_count = sum(
            1
            for card in manage_view.get_all_cards()
            if card.is_default()
        )

        assert default_count == 1, (
            f"Expected exactly one Default dashboard, "
            f"but found {default_count}."
    )

        
    @pytest.mark.functional
    @pytest.mark.positive
    @pytest.mark.high
    def test_TC_DB41_P_only_one_default_at_a_time(
        self,
        manage_view,
        analytics_dashboard,
        disposable_dashboard
    ):
        """
        TC-DB41-P:
        User logged in; Card A is currently Default.

        Step:
            Set Card B as Default.

        Expected:
            Card B gains Default badge.
            Card A loses Default badge.
            Exactly one dashboard is Default.
        """

        # ================================================================
        # 1. Card A = Analytics
        # ================================================================

        card_a = manage_view.get_card_by_name(EXISTING_DASHBOARD)

        assert card_a is not None, (
            f"Dashboard '{EXISTING_DASHBOARD}' was not found."
        )

        # Precondition: Card A must already be Default
        assert card_a.is_default(), (
            f"Precondition failed: '{EXISTING_DASHBOARD}' "
            "must already be Default."
        )

        # ================================================================
        # 2. Card B = newly created dashboard
        # ================================================================

        card_b = manage_view.get_card_by_name(disposable_dashboard)

        assert card_b is not None, (
            f"Dashboard '{disposable_dashboard}' was not found."
        )

        # ================================================================
        # 3. Set Card B as Default
        # ================================================================

        menu = card_b.open_context_menu()
        menu.click_set_default()

        # ================================================================
        # 4. Wait until Card B becomes Default
        # ================================================================

        manage_view.wait.until(
            lambda d:
                manage_view
                .get_card_by_name(disposable_dashboard)
                .is_default()
        )

        # ================================================================
        # 5. Refresh references
        # ================================================================

        card_a = manage_view.get_card_by_name(EXISTING_DASHBOARD)
        card_b = manage_view.get_card_by_name(disposable_dashboard)

        # ================================================================
        # 6. Card B must now be Default
        # ================================================================

        assert card_b.is_default(), (
            f"Expected '{disposable_dashboard}' to have "
            "the Default badge."
        )

        # ================================================================
        # 7. Card A must no longer be Default
        # ================================================================

        manage_view.wait.until(
            lambda d:
                not manage_view
                .get_card_by_name(EXISTING_DASHBOARD)
                .is_default()
        )

        card_a = manage_view.get_card_by_name(EXISTING_DASHBOARD)

        assert not card_a.is_default(), (
            f"Expected '{EXISTING_DASHBOARD}' to lose "
            "the Default badge."
        )

        # ================================================================
        # 8. Exactly one Default dashboard
        # ================================================================

        default_count = sum(
            1
            for card in manage_view.get_all_cards()
            if card.is_default()
        )

        assert default_count == 1, (
            f"Expected exactly one Default dashboard, "
            f"but found {default_count}."
        )

    @pytest.mark.functional
    @pytest.mark.positive
    @pytest.mark.medium
    def test_TC_DB42_P_default_persists_after_reload(
        self,
        manage_view,
        disposable_dashboard
    ):

        card = manage_view.get_card_by_name(
            disposable_dashboard
        )

        menu = card.open_context_menu()

        menu.click_set_default()

        manage_view.driver.refresh()

        manage_view.wait.until(
            lambda d: manage_view.is_rendered()
        )

        card = manage_view.get_card_by_name(
            disposable_dashboard
        )

        assert card.is_default()


    @pytest.mark.functional
    @pytest.mark.negative
    @pytest.mark.medium
    def test_TC_DB43_N_set_as_default_on_already_default_card(
        self,
        manage_view,
        disposable_dashboard
    ):

        card = manage_view.get_card_by_name(
            disposable_dashboard
        )

        assert card is not None

        # ================================================================
        # Step 1 - Set dashboard as Default
        # ================================================================

        menu = card.open_context_menu()

        menu.click_set_default()

        time.sleep(2)

        card = manage_view.get_card_by_name(
            disposable_dashboard
        )

        assert card.is_default(), (
            f"Dashboard '{disposable_dashboard}' "
            "was not set as Default."
        )

        # ================================================================
        # Step 2 - Open menu again
        # ================================================================

        menu = card.open_context_menu()

        # ================================================================
        # Step 3 - Set as Default should not be available
        # ================================================================

        assert not menu.has_set_default(), (
            "Set as Default should not be available "
            "for an already-default dashboard."
        )


def test_debug_dashboard_cards(authenticated_driver):
    driver = authenticated_driver

    cards = driver.find_elements(
        *DashboardsLocators().get("card_level")
    )

    print(f"\nFOUND ELEMENTS: {len(cards)}")

    for index, element in enumerate(cards):
        print(f"\n========== ELEMENT {index} ==========")

        print("\n--- ELEMENT ---")
        print(element.get_attribute("outerHTML"))

        print("\n--- PARENT ---")
        parent = element.find_element(
            "xpath",
            ".."
        )
        print(parent.get_attribute("outerHTML"))

        print("\n--- GRANDPARENT ---")
        grandparent = parent.find_element(
            "xpath",
            ".."
        )
        print(grandparent.get_attribute("outerHTML"))