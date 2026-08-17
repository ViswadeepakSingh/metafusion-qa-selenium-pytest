"""
Selenium locators for Statistics > Dashboards manage view (#/stats).
"""

from selenium.webdriver.common.by import By


def _xpath_str(value):
    """Safely quote a string for XPath (handles embedded quotes)."""
    if "'" not in value:
        return f"'{value}'"

    if '"' not in value:
        return f'"{value}"'

    parts = value.split("'")
    return "concat(" + ", \"'\", ".join(f"'{p}'" for p in parts) + ")"


class DashboardsLocators:

    _SELECTORS = {

        # ================================================================
        # Dashboard heading and subtitle
        # ================================================================

        "heading": (
            By.XPATH,
            "//div[@class='root_heading' and normalize-space()='Dashboards']"
        ),

        "subtitle": (
            By.XPATH,
            "//*[contains("
            "normalize-space(text()), "
            "'Manage and switch between your saved dashboards.'"
            ")]"
        ),

        "card_level": (
            By.XPATH,
            "//div[contains(@class, 'layout-name')]"
        ),
        # ================================================================
        # Create / Rename form
        # ================================================================

        "dashboard_name_input": (
            By.XPATH,
            "//input[@placeholder='Dashboard Name']"
        ),

        "save_button": (
            By.XPATH,
            "//button[normalize-space()='Save']"
        ),

        "cancel_button": (
            By.XPATH,
            "//button[normalize-space()='Cancel']"
        ),

        # ================================================================
        # Empty-state + Add Dashboard
        # ================================================================

        "add_dashboard_card": (
            By.XPATH,
            "//*[self::div or self::button]"
            "[@aria-label='Add' "
            "or @aria-label='Add Dashboard' "
            "or @title='Add' "
            "or @title='Add Dashboard' "
            "or normalize-space()='+' "
            "or .//img[contains(@src,'plus') "
            "or contains(@src,'add')]]"
        ),

        # ================================================================
        # Page chrome
        # ================================================================

        "dashboard_header": (
            By.XPATH,
            "//*[normalize-space()='DASHBOARDS']"
        ),

        # ================================================================
        # Saved dashboard card
        # ================================================================

        "card_label": (
            By.XPATH,
            "//*[normalize-space()='DASHBOARD']"
        ),

        "updated_on": (
            By.XPATH,
            "//*[contains(normalize-space(),'Updated on')]"
        ),

        "widgets_badge": (
            By.XPATH,
            "//*[contains(normalize-space(),'Widget')]"
        ),
    }

    # ====================================================================
    # Generic locator getter
    # ====================================================================

    def get(self, key):
        try:
            return self._SELECTORS[key]

        except KeyError as exc:
            raise KeyError(
                f"Unknown Dashboards locator '{key}'. "
                f"Known: {sorted(self._SELECTORS)}"
            ) from exc

    # ====================================================================
    # Dynamic locators
    # ====================================================================

    @staticmethod
    def card_name(name):
        return (
            By.XPATH,
            f"//*[normalize-space(text())={_xpath_str(name)}]"
        )

    @staticmethod
    def widgets_badge_for(name):
        return (
            By.XPATH,
            f"//*[normalize-space(text())={_xpath_str(name)}]"
            f"/ancestor::*[.//*[contains(normalize-space(),'Widget')]][1]"
            f"//*[contains(normalize-space(),'Widget')]"
        )

    @staticmethod
    def button_by_text(text):
        return (
            By.XPATH,
            f"//button[normalize-space()={_xpath_str(text)}]"
        )

    # ====================================================================
    # Text configuration
    # ====================================================================

    dashboards_header_text = "DASHBOARDS"

    dashboards_subtitle_text = (
        "Manage and switch between your saved dashboards."
    )

    save_name = "Save"

    cancel_name = "Cancel"

    # Context menu options
    menu_item_labels = [
        "Open",
        "Rename",
        "Delete",
        "Set as Default",
    ]