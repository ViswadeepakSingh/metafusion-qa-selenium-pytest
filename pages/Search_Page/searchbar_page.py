import re
import logging
from urllib.parse import urlparse

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException
)

from config.config import Config
from locators.searchbar_locators import SearchLocators
from pages.base_page import BasePage


logger = logging.getLogger(__name__)


class SearchPage(BasePage):

    # ======================================================================
    # Initialization
    # ======================================================================

    def __init__(self, driver):
        super().__init__(driver)

        self.locators = SearchLocators

        logger.info("Initialized SearchPage")

    # ======================================================================
    # Navigation
    # ======================================================================

    def _search_url(self):
        """
        Build Search page URL from configured BASE_URL.
        """

        parsed = urlparse(
            Config().BASE_URL
        )

        return (
            f"{parsed.scheme}://"
            f"{parsed.netloc}"
            f"/#/search/search-filter"
        )

    def navigate(self, url=None):
        """
        Navigate to Search page.
        """

        search_url = url or self._search_url()

        self.driver.get(search_url)

        self._wait().until(
            lambda d:
            "#/search/search-filter"
            in d.current_url
        )

        # Wait until search input is actually rendered.
        self._visible(
            "search_input"
        )

        logger.info(
            "Navigated to Search page: %s",
            self.driver.current_url
        )

        return self

    def is_search_page(self):
        """
        Verify current page is Search page.
        """

        return (
            "#/search/search-filter"
            in self.driver.current_url
        )

    # ======================================================================
    # TC-SB01-05: Page Rendering
    # ======================================================================

    def verify_loaded(self):
        """Verify Search page heading and search input are visible."""

        logger.info(
            "Verifying Search page is loaded: %s",
            self.driver.current_url
        )

        assert self.is_search_page(), (
            f"Expected Search page, "
            f"but current URL is {self.driver.current_url}"
        )

        header = self._find(
            "search_header"
        ).text

        logger.info(
            "Search Header: %s",
            header
        )

        assert header == "Search", (
            f"Expected search header 'Search', "
            f"got '{header}'"
        )

        search_input = self._find(
            "search_input"
        )

        assert search_input.is_displayed(), (
            "Search input is not visible"
        )

        return self


    def verify_placeholder(self):
        """
        Verify search input placeholder text.
        """

        search_input = self._visible(
            "search_input"
        )

        placeholder = search_input.get_attribute(
            "placeholder"
        )

        assert placeholder is not None, (
            "Search input does not have placeholder"
        )

        assert (
            self.locators.search_placeholder_text
            in placeholder
        ), (
            f"Expected placeholder containing "
            f"'{self.locators.search_placeholder_text}', "
            f"got '{placeholder}'"
        )

        return self

    # ======================================================================
    # TC-SB06-09: Search Input
    # ======================================================================

    def _focus_search_input(self):
        """
        Focus search input.

        If the application expands the search box when its
        parent is clicked, click the parent first.
        """

        search_input = self._visible(
            "search_input"
        )

        try:
            parent = search_input.find_element(
                By.XPATH,
                ".."
            )

            parent.click()

        except Exception:
            # If parent cannot be clicked, click input itself.
            search_input.click()

        return search_input

    def enter_query(self, text):
        """
        TC-SB07:
        Enter text into search box.
        """

        search_input = self._focus_search_input()

        search_input.clear()

        search_input.send_keys(
            text
        )

        logger.info(
            "Entered search query: %s",
            text
        )

        return self

    def clear_query(self):
        """
        TC-SB08:
        Clear search box.
        """

        search_input = self._focus_search_input()

        search_input.clear()

        logger.info(
            "Search query cleared"
        )

        return self

    def submit(self):
        """
        TC-SB09:
        Press Enter to execute search.
        """

        search_input = self._focus_search_input()

        search_input.send_keys(
            Keys.ENTER
        )

        # Wait for result count to render.
        self._visible(
            "results_count",
            timeout=15
        )

        logger.info(
            "Search submitted"
        )

        return self

    def search(self, text):
        """
        Shortcut:
        enter query + submit.
        """

        return (
            self
            .enter_query(text)
            .submit()
        )

    def get_query_value(self):
        """
        Return current search input value.
        """

        search_input = self._visible(
            "search_input"
        )

        return search_input.get_attribute(
            "value"
        )

    def verify_query_value(self, expected):
        """
        TC-SB06 / TC-SB08:
        Verify search box contains expected value.
        """

        actual = self.get_query_value()

        assert actual == expected, (
            f"Expected search value "
            f"'{expected}', got '{actual}'"
        )

        return self

    # ======================================================================
    # TC-SB10-16: Search Results
    # ======================================================================

    def get_results_count(self):
        """
        Return numeric result count.

        Returns -1 if result count cannot be found.
        """

        try:

            element = self._visible(
                "results_count"
            )

            text = element.text

            match = re.search(
                r"[\d,]+",
                text
            )

            if match:
                return int(
                    match.group().replace(
                        ",",
                        ""
                    )
                )

        except (
            TimeoutException,
            NoSuchElementException
        ):
            pass

        return -1

    def verify_results_count_visible(self):
        """
        TC-SB09 / TC-SB10:
        Verify result count is visible.
        """

        assert self._is_visible(
            "results_count"
        ), (
            "Search results count is not visible"
        )

        return self

    def verify_has_results(self):
        """
        Verify at least one result card is visible.
        """

        try:

            element = self._visible(
                "result_card_label",
                timeout=10
            )

            assert element.is_displayed()

        except (
            TimeoutException,
            NoSuchElementException
        ):

            self.take_screenshot(
                "verify_has_results_failed"
            )

            raise AssertionError(
                "No search result card is visible"
            )

        return self

    def verify_no_results(self):
        """
        Verify result count is 0.
        """

        element = self._visible(
            "results_count"
        )

        text = element.text

        match = re.search(
            r"\b0\b",
            text
        )

        assert match is not None, (
            f"Expected result count 0, "
            f"but got: '{text}'"
        )

        return self

    # ======================================================================
    # TC-SB17-22: Edge Case / Negative Input
    # ======================================================================

    def verify_still_on_search(self):
        """
        Verify application remains on Search page
        after unusual input.
        """

        current_url = self.driver.current_url

        assert "search" in current_url.lower(), (
            f"Expected to remain on Search page, "
            f"but current URL is: {current_url}"
        )

        return self

    # ======================================================================
    # TC-SB23-24: Toolbar
    # ======================================================================

    def click_image_search(self):
        """
        TC-SB23:
        Open Image Search panel.
        """

        button = self._clickable(
            "image_search_button"
        )

        button.click()

        logger.info(
            "Clicked Image Search"
        )

        return self

    def close_image_search(self):
        """
        Close Image Search panel.
        """

        button = self._clickable(
            "close_image_search_button"
        )

        button.click()

        logger.info(
            "Closed Image Search"
        )

        return self

    def verify_image_search_opened(self):
        """
        Verify Image Search panel is open.
        """

        assert self._is_visible(
            "close_image_search_button"
        ), (
            "Image Search panel is not open"
        )

        return self

    def verify_image_icon_visible(self):
        """
        Verify Image Search icon is visible.
        """

        assert self._is_visible(
            "image_search_button"
        ), (
            "Image Search icon is not visible"
        )

        return self

    def click_filter(self):
        """
        TC-SB24:
        Open filter panel.
        """

        button = self._clickable(
            "filter_button"
        )

        button.click()

        logger.info(
            "Clicked Filter"
        )

        return self

    def verify_filter_panel_visible(self):
        """
        Verify filter panel is visible.
        """

        assert self._is_visible(
            "filter_panel"
        ), (
            "Filter panel is not visible"
        )

        return self

    def verify_filter_icon_visible(self):
        """
        Verify filter icon is visible.
        """

        assert self._is_visible(
            "filter_button"
        ), (
            "Filter icon is not visible"
        )

        return self

    # ======================================================================
    # TC-SB25-26: Tabs
    # ======================================================================

    def verify_tab_visible_and_clickable(
        self,
        tab_name
    ):
        """
        TC-SB25 / TC-SB26:
        Verify tab is visible and enabled.
        """

        tab = self._find_tab(
            tab_name
        )

        assert tab.is_displayed(), (
            f"Tab '{tab_name}' is not visible"
        )

        assert tab.is_enabled(), (
            f"Tab '{tab_name}' is not enabled"
        )

        return self

    def _find_tab(self, tab_name):
        """
        Find tab by visible text.

        Uses XPath so the test can dynamically provide
        the tab name.
        """

        xpath = (
            f"//*[contains("
            f"normalize-space(text()), "
            f"'{tab_name}'"
            f")]"
        )

        return self._wait().until(
            EC.visibility_of_element_located(
                (
                    By.XPATH,
                    xpath
                )
            )
        )

    def select_tab(self, tab_name):
        """
        Select a tab by its visible name.
        """

        tab = self._find_tab(
            tab_name
        )

        tab.click()

        logger.info(
            "Selected tab: %s",
            tab_name
        )

        return self

    def verify_tab_selected(self, tab_name):
        """
        Verify requested tab is selected.

        Supports common implementations:
        - aria-selected=true
        - class contains active
        - class contains selected
        """

        tab = self._find_tab(
            tab_name
        )

        aria_selected = tab.get_attribute(
            "aria-selected"
        )

        class_name = (
            tab.get_attribute("class")
            or ""
        ).lower()

        is_selected = (
            aria_selected == "true"
            or "active" in class_name
            or "selected" in class_name
        )

        assert is_selected, (
            f"Tab '{tab_name}' is not selected. "
            f"aria-selected='{aria_selected}', "
            f"class='{class_name}'"
        )

        return self
