"""
Selenium locators for Statistics > Dashboards manage view (#/stats).
"""

from selenium.webdriver.common.by import By


def _xpath_str(value):
    """Safely quote a string for XPath."""
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

        
        # ================================================================
        # Dashboard cards
        # ================================================================

        "card_level": (
            By.XPATH,
            "//div[contains(@class, 'layout-card') and contains(@class, 'view')]"
        ),

        "card_title": (
            By.XPATH,
            ".//div[contains(@class, 'layout-name')]"
        ),

        "card_label": (
            By.XPATH,
            ".//div[contains(@class, 'layout-name')]/span[normalize-space()='DASHBOARD']"
        ),

        "card_updated_on": (
            By.XPATH,
            ".//div[contains(@class, 'layout-footer')]//*[contains(normalize-space(), 'Updated on')]"
        ),

        "card_widgets_badge": (
            By.XPATH,
            ".//div[contains(@class, 'widget-count') and contains(normalize-space(), 'Widget')]"
        ),

        "card_default_badge": (
            By.XPATH,
            ".//*[normalize-space()='Default']"
        ),

        "card_menu_trigger": (
            By.XPATH,
            ".//div[contains(@class, 'layout-top')]//button"
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
        # Validation
        # ================================================================

        "validation_error": (
            By.XPATH,
            "//*[contains(@class, 'error') "
            "or contains(@class, 'invalid') "
            "or @role='alert']"
        ),

        # ================================================================
        # Add Dashboard
        # ================================================================

        "add_dashboard_card": (
            By.XPATH,
            "//*[self::div or self::button]"
            "[@aria-label='Add' "
            "or @aria-label='Add Dashboard' "
            "or @title='Add' "
            "or @title='Add Dashboard' "
            "or normalize-space()='+']"
        ),

        # ================================================================
        # Context Menu
        # ================================================================

        "context_menu": (
            By.XPATH,
            "//div[contains(@class, 'layout-modal')]"
        ),

        "context_menu_items": (
            By.XPATH,
            "//div[contains(@class, 'layout-modal')]//li"
        ),

        # ================================================================
        # Delete Confirmation Dialog
        # ================================================================

        "confirm_dialog": (
            By.XPATH,
            "//*[@role='dialog']"
        ),

        "confirm_dialog_confirm": (
            By.XPATH,
            "//*[@role='dialog']//button[normalize-space()='Delete']"
        ),

        "confirm_dialog_cancel": (
            By.XPATH,
            "//*[@role='dialog']//button[normalize-space()='Cancel']"
        ),

        # ================================================================
        # Page chrome
        # ================================================================

        "dashboard_header": (
            By.XPATH,
            "//*[normalize-space()='DASHBOARDS']"
        ),

        # Backward-compatible names
        "updated_on": (
            By.XPATH,
            "//*[contains(normalize-space(), 'Updated on')]"
        ),

        "widgets_badge": (
            By.XPATH,
            "//*[contains(normalize-space(), 'Widget')]"
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

    @staticmethod
    def menu_item_by_text(text):
        return (
            By.XPATH,
            "//div[contains(@class, 'layout-modal')]"
            f"//li[contains(normalize-space(), {_xpath_str(text)})]"
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

    menu_item_labels = [
        "Open",
        "Rename",
        "Delete",
        "Set as Default",
    ]