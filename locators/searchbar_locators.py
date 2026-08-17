"""
Locators for the Search page (#/search/search-filter).

-> place at Locators/search_locators.py

Access pattern:
    LOC.get("search_input")
"""

class SearchLocators:

    _SELECTORS = {

        # Search input textbox
        # TC-SB01, TC-SB06, TC-SB07, TC-SB08, TC-SB09
        #
        # Actual DOM exposes this as a textbox.
        # Use Playwright role locator in Page Object.
        "search_input": "role=textbox",

        # Locators/search_locators.py

        "search_placeholder_text": "Search with label, source or location",

        # Search result card label
        # TC-SB10, TC-SB14, TC-SB17
        "result_card_label":
            "//*[contains(normalize-space(),'Person Collapse')]",


        # Result cards container
        # TC-SB15, TC-SB16
        "result_cards":
            "//*[contains(@class,'card') or contains(@class,'result')]",

        "filter_panel": ':text-is("FILTERS")',
        "filter_panel_label": "//*[contains(normalize-space(),'FILTERS')]",
    }


    def get(self, key):

        try:
            return self._SELECTORS[key]

        except KeyError as exc:
            raise KeyError(
                f"Unknown Search locator '{key}'. "
                f"Known: {sorted(self._SELECTORS)}"
            ) from exc


    # ==========================================================
    # Page Header
    # TC-SB01 - Search page loads
    # ==========================================================

    search_header_text = "Search"
    search_header_exact = True
    search_header_role = "heading"


    # ==========================================================
    # Placeholder
    # TC-SB02 - Placeholder text visible
    # ==========================================================

    search_placeholder = (
        "Search with label, source or location"
    )

    search_placeholder_text = (
        "Search with label, source or"
    )


    # ==========================================================
    # Search Toolbar
    # TC-SB03 - Image search icon visible
    # TC-SB04 - Filter icon visible
    # TC-SB23 - Image search opens
    # TC-SB24 - Filter panel opens
    # ==========================================================

    image_search_role = "img"
    image_search_name = "imageSearchIcon"

    close_icon_role = "img"
    close_icon_name = "close icon"

    filter_role = "button"
    filter_name = "filter icon"


    # ==========================================================
    # Results
    # TC-SB05 - Result count visible
    # TC-SB09 - Search result count
    # ==========================================================

    results_count_text = (
        "search result"
    )


    # ==========================================================
    # Tabs
    # TC-SB25 - Default tab
    # TC-SB26 - Tab switching
    # ==========================================================

    tab_all = "ALL"
    tab_saved = "SAVED"
    tab_forwarded = "FORWARDED"
