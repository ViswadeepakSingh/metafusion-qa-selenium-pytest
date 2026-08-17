"""
Selenium + pytest test suite for the Search Bar feature.

Test specification coverage:
    TC-SB01 through TC-SB26

Page Object:
    pages/Search_Page/search_page.py

Authentication:
    Uses an authenticated Selenium driver fixture.

Test groups:
    TestSearchRendering  - TC-SB01 - TC-SB05
    TestSearchInput      - TC-SB06 - TC-SB09
    TestSearchResults    - TC-SB10 - TC-SB16
    TestSearchNegative   - TC-SB17 - TC-SB22
    TestSearchToolbar    - TC-SB23 - TC-SB24
    TestSearchTabs       - TC-SB25 - TC-SB26
"""

import re

import pytest

from pages.Search_Page.searchbar_page import SearchPage


# ==========================================================
# Test Data
# ==========================================================

KNOWN_LABEL = "person collapse"

SEARCH_DESCRIPTION = "collapse"

DASHBOARD_NAME = "Dashboard Name"

NO_MATCH = "zzzzznomatch123"

SQL_PAYLOAD = "' OR '1'='1"

LONG_QUERY = "a" * 200

UNICODE_QUERY = "😀 person náme"


# ==========================================================
# Shared Fixture
# ==========================================================

@pytest.fixture
def search_page(driver):
    """
    Create SearchPage and navigate to Search page.

    `driver` comes from conftest.py.
    """

    page = SearchPage(driver)

    page.navigate()

    return page


# ==========================================================
# TC-SB01 - TC-SB05
# Search Page Rendering
# ==========================================================

@pytest.mark.regression
class TestSearchRendering:
    """
    Static UI checks confirming Search page renders correctly.
    """

    @pytest.mark.smoke
    def test_tc_sb01_p_search_page_loads(self, search_page):
        """
        TC-SB01:
        Search page loads with heading and search bar visible.
        """

        search_page.verify_loaded()

        print(
            "✅ TC-SB01-P PASSED - "
            "Search page loaded successfully"
        )

    @pytest.mark.smoke
    def test_tc_sb02_p_placeholder_text(self, search_page):
        """
        TC-SB02:
        Search input displays expected placeholder.
        """

        search_page.verify_placeholder()

        print(
            "✅ TC-SB02-P PASSED - "
            "Search placeholder is visible"
        )

    @pytest.mark.smoke
    def test_tc_sb03_p_image_search_icon_visible(
        self,
        search_page
    ):
        """
        TC-SB03:
        Image search icon is visible.
        """

        search_page.verify_image_icon_visible()

        print(
            "✅ TC-SB03-P PASSED - "
            "Image search icon is visible"
        )

    @pytest.mark.smoke
    def test_tc_sb04_p_filter_icon_visible(
        self,
        search_page
    ):
        """
        TC-SB04:
        Filter icon is visible.
        """

        search_page.verify_filter_icon_visible()

        print(
            "✅ TC-SB04-P PASSED - "
            "Filter icon is visible"
        )

    @pytest.mark.smoke
    def test_tc_sb05_p_result_count_visible(
        self,
        search_page
    ):
        """
        TC-SB05:
        Result count is visible.
        """

        search_page.verify_results_count_visible()

        print(
            "✅ TC-SB05-P PASSED - "
            "Result count is visible"
        )


# ==========================================================
# TC-SB06 - TC-SB09
# Search Input Behaviour
# ==========================================================

@pytest.mark.regression
class TestSearchInput:
    """
    Tests covering typing, clearing and submitting search input.
    """

    @pytest.mark.smoke
    def test_tc_sb06_p_input_starts_empty(
        self,
        search_page
    ):
        """
        TC-SB06:
        Search input is empty on initial page load.
        """

        search_page.verify_query_value("")

        print(
            "✅ TC-SB06-P PASSED - "
            "Search input starts empty"
        )

    @pytest.mark.smoke
    def test_tc_sb07_p_typing_updates_input(
        self,
        search_page
    ):
        """
        TC-SB07:
        Typing updates search input.
        """

        (
            search_page
            .enter_query(KNOWN_LABEL)
            .verify_query_value(KNOWN_LABEL)
        )

        print(
            "✅ TC-SB07-P PASSED - "
            "Typing updates search input"
        )

    @pytest.mark.smoke
    def test_tc_sb08_p_field_can_be_cleared(
        self,
        search_page
    ):
        """
        TC-SB08:
        Search input can be cleared.
        """

        (
            search_page
            .enter_query(KNOWN_LABEL)
            .clear_query()
            .verify_query_value("")
        )

        print(
            "✅ TC-SB08-P PASSED - "
            "Search input can be cleared"
        )

    @pytest.mark.smoke
    def test_tc_sb09_p_enter_triggers_search(
        self,
        search_page
    ):
        """
        TC-SB09:
        Pressing Enter submits search and renders results.
        """

        (
            search_page
            .search(KNOWN_LABEL)
            .verify_results_count_visible()
        )

        print(
            "✅ TC-SB09-P PASSED - "
            "Enter triggers search"
        )


# ==========================================================
# TC-SB10 - TC-SB16
# Search Results Behaviour
# ==========================================================

@pytest.mark.regression
class TestSearchResults:
    """
    Tests confirming search returns relevant results.
    """

    def test_tc_sb10_p_search_by_label_returns_results(
        self,
        search_page
    ):
        """
        TC-SB10:
        Searching by known label returns results.
        """

        (
            search_page
            .search(KNOWN_LABEL)
            .verify_has_results()
            .take_screenshot(
                "TC-SB10-P-label-results"
            )
        )

        print(
            "✅ TC-SB10-P PASSED - "
            "Search by label returned results"
        )

    def test_tc_sb11_p_search_by_source_name(
        self,
        search_page
    ):
        """
        TC-SB11:
        Searching by source name returns results.
        """

        search_page.search(
            "sanjay fall"
        )

        try:

            search_page.verify_has_results()

        except AssertionError:

            search_page.take_screenshot(
                "TC-SB11-zero-results"
            )

            raise

        print(
            "✅ TC-SB11-P PASSED - "
            "Search by source name returned results"
        )

    def test_tc_sb12_p_search_by_location(
        self,
        search_page
    ):
        """
        TC-SB12:
        Searching by location/description returns results.
        """

        (
            search_page
            .search(SEARCH_DESCRIPTION)
            .verify_has_results()
        )

        print(
            "✅ TC-SB12-P PASSED - "
            "Search by location returned results"
        )

    def test_tc_sb13_p_search_is_case_insensitive(
        self,
        search_page
    ):
        """
        TC-SB13:
        Search is case insensitive.
        """

        # Uppercase search
        search_page.search(
            KNOWN_LABEL.upper()
        )

        upper_count = (
            search_page.get_results_count()
        )

        # Clear previous search
        search_page.clear_query()
        search_page.submit()

        # Lowercase search
        search_page.search(
            KNOWN_LABEL.lower()
        )

        lower_count = (
            search_page.get_results_count()
        )

        assert upper_count == lower_count, (
            "Case insensitive search failed: "
            f"{upper_count} != {lower_count}"
        )

        print(
            "✅ TC-SB13-P PASSED - "
            "Search is case insensitive"
        )

    def test_tc_sb14_p_substring_match_returns_results(
        self,
        search_page
    ):
        """
        TC-SB14:
        Partial keyword returns results.
        """

        (
            search_page
            .search("collapse")
            .verify_has_results()
        )

        print(
            "✅ TC-SB14-P PASSED - "
            "Substring search returned results"
        )

    def test_tc_sb15_p_clear_restores_full_results(
        self,
        search_page
    ):
        """
        TC-SB15:
        Clearing active search restores full results.
        """

        full_count = (
            search_page.get_results_count()
        )

        search_page.search(
            KNOWN_LABEL
        )

        filtered_count = (
            search_page.get_results_count()
        )

        search_page.clear_query()
        search_page.submit()

        restored_count = (
            search_page.get_results_count()
        )

        assert restored_count == full_count, (
            "Clear search did not restore results. "
            f"Full={full_count}, "
            f"Filtered={filtered_count}, "
            f"Restored={restored_count}"
        )

        print(
            "✅ TC-SB15-P PASSED - "
            "Clearing search restored full results"
        )

    def test_tc_sb16_p_leading_trailing_spaces_trimmed(
        self,
        search_page
    ):
        """
        TC-SB16:
        Leading/trailing whitespace is ignored.
        """

        search_page.search(
            f"  {KNOWN_LABEL}  "
        )

        padded_count = (
            search_page.get_results_count()
        )

        search_page.clear_query()
        search_page.submit()

        search_page.search(
            KNOWN_LABEL
        )

        normal_count = (
            search_page.get_results_count()
        )

        assert padded_count == normal_count, (
            "Search result mismatch after "
            "trimming spaces"
        )

        print(
            "✅ TC-SB16-P PASSED - "
            "Leading/trailing spaces handled correctly"
        )


# ==========================================================
# TC-SB17 - TC-SB22
# Negative / Edge Cases
# ==========================================================

@pytest.mark.regression
class TestSearchNegative:
    """
    Tests confirming search handles invalid or unusual input safely.
    """

    @pytest.mark.negative
    def test_tc_sb17_n_no_match_shows_zero_results(
        self,
        search_page
    ):
        """
        TC-SB17:
        Query with no match shows zero results.
        """

        (
            search_page
            .search(NO_MATCH)
            .verify_no_results()
            .take_screenshot(
                "TC-SB17-N-no-results"
            )
        )

        print(
            "✅ TC-SB17-N PASSED - "
            "No-match query returned zero results"
        )

    @pytest.mark.negative
    def test_tc_sb18_n_special_characters_do_not_crash(
        self,
        search_page
    ):
        """
        TC-SB18:
        Special characters do not crash the page.
        """

        (
            search_page
            .search("!@#$%^&*()")
            .verify_still_on_search()
        )

        print(
            "✅ TC-SB18-N PASSED - "
            "Special characters handled safely"
        )

    @pytest.mark.security
    @pytest.mark.negative
    def test_tc_sb19_n_sql_injection_handled_safely(
        self,
        search_page
    ):
        """
        TC-SB19:
        SQL-injection-style input does not expose
        backend/database errors.
        """

        (
            search_page
            .search(SQL_PAYLOAD)
            .verify_still_on_search()
        )

        body = (
            search_page
            .get_page_text()
            .lower()
        )

        assert not re.search(
            r"sql|syntax error|stack trace|exception",
            body
        ), (
            "Possible server/database error exposed"
        )

        search_page.take_screenshot(
            "TC-SB19-N-sql-safe"
        )

        print(
            "✅ TC-SB19-N PASSED - "
            "SQL injection payload handled safely"
        )

    @pytest.mark.negative
    def test_tc_sb20_n_long_query_does_not_crash(
        self,
        search_page
    ):
        """
        TC-SB20:
        Long query does not crash the application.
        """

        (
            search_page
            .search(LONG_QUERY)
            .verify_still_on_search()
        )

        print(
            "✅ TC-SB20-N PASSED - "
            "Long query handled safely"
        )

    @pytest.mark.negative
    def test_tc_sb21_n_unicode_emoji_handled(
        self,
        search_page
    ):
        """
        TC-SB21:
        Unicode and emoji are handled correctly.
        """

        (
            search_page
            .search(UNICODE_QUERY)
            .verify_still_on_search()
        )

        print(
            "✅ TC-SB21-N PASSED - "
            "Unicode and emoji handled safely"
        )

    @pytest.mark.negative
    def test_tc_sb22_n_whitespace_only_query(
        self,
        search_page
    ):
        """
        TC-SB22:
        Whitespace-only query does not break page.
        """

        (
            search_page
            .search("   ")
            .verify_still_on_search()
        )

        print(
            "✅ TC-SB22-N PASSED - "
            "Whitespace-only query handled safely"
        )


# ==========================================================
# TC-SB23 - TC-SB24
# Search Toolbar
# ==========================================================

@pytest.mark.regression
class TestSearchToolbar:
    """
    Tests covering image search and filter toolbar.
    """

    def test_tc_sb23_p_image_search_icon_opens(
        self,
        search_page
    ):
        """
        TC-SB23:
        Image search panel opens and can be closed.
        """

        (
            search_page
            .click_image_search()
            .verify_image_search_opened()
            .take_screenshot(
                "TC-SB23-P-image-search"
            )
            .close_image_search()
        )

        print(
            "✅ TC-SB23-P PASSED - "
            "Image search panel opened and closed"
        )

    def test_tc_sb24_p_filter_panel_opens(
        self,
        search_page
    ):
        """
        TC-SB24:
        Filter panel opens and is visible.
        """

        (
            search_page
            .click_filter()
            .verify_filter_panel_visible()
            .take_screenshot(
                "TC-SB24-P-filter-panel"
            )
        )

        print(
            "✅ TC-SB24-P PASSED - "
            "Filter panel opened successfully"
        )


# ==========================================================
# TC-SB25 - TC-SB26
# Search Tabs
# ==========================================================

@pytest.mark.regression
class TestSearchTabs:
    """
    Tests covering ALL / SAVED / FORWARDED tabs.
    """

    def test_tc_sb25_p_all_tab_default(
        self,
        search_page
    ):
        """
        TC-SB25:
        ALL tab is selected by default.
        """

        search_page.verify_tab_selected(
            "ALL"
        )

        print(
            "✅ TC-SB25-P PASSED - "
            "ALL tab is selected by default"
        )

    def test_tc_sb26_p_switching_tabs_updates_results(
        self,
        search_page
    ):
        """
        TC-SB26:
        Switching between SAVED, FORWARDED
        and ALL updates selected tab.
        """

        # SAVED
        (
            search_page
            .verify_tab_visible_and_clickable(
                "SAVED"
            )
            .select_tab("SAVED")
            .verify_tab_selected("SAVED")
        )

        # FORWARDED
        (
            search_page
            .verify_tab_visible_and_clickable(
                "FORWARDED"
            )
            .select_tab("FORWARDED")
            .verify_tab_selected("FORWARDED")
        )

        # ALL
        (
            search_page
            .verify_tab_visible_and_clickable(
                "ALL"
            )
            .select_tab("ALL")
            .verify_tab_selected("ALL")
        )

        print(
            "✅ TC-SB26-P PASSED - "
            "Search tabs switched successfully"
        )
