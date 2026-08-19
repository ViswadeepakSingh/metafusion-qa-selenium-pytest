"""
Selenium Page Objects for Statistics > Dashboards.

Classes:
    DashboardForm
    ConfirmDialog
    ContextMenu
    DashboardCard
    DashboardPage
"""

import re

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from locators.dashboard_locators import DashboardsLocators


DEFAULT_TIMEOUT = 15
LOC = DashboardsLocators()
  

# ===========================================================================
# Dashboard Create / Rename Form
# ===========================================================================

class DashboardForm:
    """Create/Rename dashboard form."""

    NAME_INPUT = LOC.get("dashboard_name_input")
    SAVE_BUTTON = LOC.get("save_button")
    CANCEL_BUTTON = LOC.get("cancel_button")
    VALIDATION_ERROR = None

    save_locator = SAVE_BUTTON
    cancel_locator = CANCEL_BUTTON

    def __init__(self, driver, locators=None, timeout=DEFAULT_TIMEOUT):
        self.driver = driver
        self.locators = locators or LOC
        self.wait = WebDriverWait(driver, timeout)

    # TC-DB08, TC-DB09, TC-DB10, TC-DB12, TC-DB13, TC-DB14
    def is_open(self):
        try:
            return self.driver.find_element(*self.NAME_INPUT).is_displayed()
        except NoSuchElementException:
            return False

    # TC-DB08, TC-DB09, TC-DB10, TC-DB12, TC-DB13, TC-DB14
    def wait_until_open(self):
        self.wait.until(EC.visibility_of_element_located(self.NAME_INPUT))
        return self

    # TC-DB11, TC-DB13, TC-DB14, TC-DB27, TC-DB30, TC-DB31, TC-DB32
    def wait_until_closed(self):
        self.wait.until_not(
            lambda d: self.is_open()
        )
        return self

    # TC-DB09, TC-DB10, TC-DB14, TC-DB26
    def get_name_value(self):
        field = self.wait.until(
            EC.visibility_of_element_located(self.NAME_INPUT)
        )
        return field.get_attribute("value") or ""

    # TC-DB10, TC-DB11, TC-DB13, TC-DB14, TC-DB27, TC-DB29, TC-DB30, TC-DB31, TC-DB32
    def enter_name(self, name):
        field = self.wait.until(
            EC.visibility_of_element_located(self.NAME_INPUT)
        )
        field.clear()
        field.send_keys(name)
        return self

    # TC-DB12, TC-DB28
    def clear_name(self):
        self.wait.until(
            EC.visibility_of_element_located(self.NAME_INPUT)
        ).clear()
        return self

    # TC-DB33
    def get_validation_error(self):
        try:
            element = self.driver.find_element(*self.VALIDATION_ERROR)
            return element.text.strip() if element.is_displayed() else None
        except NoSuchElementException:
            return None

    # TC-DB11, TC-DB12, TC-DB27, TC-DB28, TC-DB29, TC-DB31, TC-DB32
    def save(self):
        save_locator = self.locators.get("save_button")

        save_button = self.wait.until(
            EC.presence_of_element_located(save_locator)
        )

        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            save_button
        )

        try:
            self.wait.until(
                EC.element_to_be_clickable(save_locator)
            ).click()

        except (
            TimeoutException,
            ElementClickInterceptedException,
        ):
            save_button = self.wait.until(
                EC.visibility_of_element_located(save_locator)
            )

            self.driver.execute_script(
                "arguments[0].click();",
                save_button
            )

        self.wait.until(
            EC.invisibility_of_element_located(save_locator)
        )

    # TC-DB08, TC-DB09, TC-DB10, TC-DB13, TC-DB14, TC-DB26, TC-DB28, TC-DB29, TC-DB30
    # pages/Statistics_Page/dashboard_page.py

    # pages/Statistics_Page/dashboard_page.py

    def cancel(self):
        def click_visible_cancel(driver):
            try:
                buttons = driver.find_elements(*self.CANCEL_BUTTON)

                for button in buttons:
                    try:
                        if button.is_displayed():
                            driver.execute_script(
                                "arguments[0].click();",
                                button
                            )
                            return True
                    except StaleElementReferenceException:
                        continue

                return False

            except Exception:
                return False

        self.wait.until(click_visible_cancel)

        self.wait.until_not(lambda d: self.is_open())

        return self




    # Only to check that btns are visible or not
    def are_controls_visible(self):
        try:
            name_input = self.driver.find_element(*self.NAME_INPUT)
            save_btn = self.driver.find_element(*self.SAVE_BUTTON)
            cancel_btn = self.driver.find_element(*self.CANCEL_BUTTON)

            return (
                name_input.is_displayed()
                and save_btn.is_displayed()
                and cancel_btn.is_displayed()
            )
        except NoSuchElementException:
            return False




# ===========================================================================
# Delete Confirmation Dialog
# ===========================================================================

class ConfirmDialog:
    """Delete confirmation dialog."""

    ROOT = LOC.get("confirm_dialog")
    CONFIRM_BUTTON = LOC.get("confirm_dialog_confirm")
    CANCEL_BUTTON = LOC.get("confirm_dialog_cancel")

    def __init__(self, driver, locators=None, timeout=DEFAULT_TIMEOUT):
        self.driver = driver
        self.locators = locators or LOC
        self.wait = WebDriverWait(driver, timeout)

    # TC-DB34, TC-DB35, TC-DB36, TC-DB37
    def is_open(self):
        try:
            return self.driver.find_element(*self.ROOT).is_displayed()
        except NoSuchElementException:
            return False

    # TC-DB34, TC-DB35, TC-DB36, TC-DB37
    def wait_until_open(self):
        self.wait.until(
            EC.visibility_of_element_located(self.ROOT)
        )
        return self

    # TC-DB35, TC-DB36, TC-DB37
    def wait_until_closed(self):
        self.wait.until_not(lambda d: self.is_open())
        return self

    # TC-DB35, TC-DB37
    def confirm(self):
        if not self.is_open():
            # The live app deletes immediately from the context menu
            # with no confirmation prompt; nothing left to confirm.
            return self

        self.wait.until(
            EC.element_to_be_clickable(self.CONFIRM_BUTTON)
        ).click()
        self.wait_until_closed()
        return self

    # TC-DB34, TC-DB36
    def cancel(self):
        if not self.is_open():
            return self

        self.wait.until(
            EC.element_to_be_clickable(self.CANCEL_BUTTON)
        ).click()
        self.wait_until_closed()
        return self


# ===========================================================================
# Dashboard Context Menu
# ===========================================================================

class ContextMenu:
    """Three-dot menu for a dashboard card."""

    ROOT = LOC.get("context_menu")
    ALL_ITEMS = LOC.get("context_menu_items")

    EXPECTED_LABELS = [
        "Open",
        "Rename",
        "Delete",
        "Set as Default",
    ]

    def __init__(self, driver, locators=None, timeout=DEFAULT_TIMEOUT):
        self.driver = driver
        self.locators = locators or LOC
        self.wait = WebDriverWait(driver, timeout)

    # TC-DB17, TC-DB22
    def is_open(self):
        try:
            return self.driver.find_element(*self.ROOT).is_displayed()
        except NoSuchElementException:
            return False

    # TC-DB17, TC-DB18, TC-DB22, TC-DB23
    def wait_until_open(self):
        self.wait.until(
            EC.visibility_of_element_located(self.ROOT)
        )
        return self

    # TC-DB19, TC-DB20, TC-DB24, TC-DB25
    def wait_until_closed(self):
        self.wait.until_not(lambda d: self.is_open())
        return self

    # TC-DB17, TC-DB18, TC-DB22
    def get_item_labels(self):
        return [
            item.text.strip()
            for item in self.driver.find_elements(*self.ALL_ITEMS)
        ]

    # TC-DB19
    def close_via_outside_click(self):
        """
        Close the context menu by clicking the backdrop/outside area.
        """

        backdrop = self.wait.until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "div.backdrop")
            )
        )

        backdrop.click()

        self.wait.until(
            EC.invisibility_of_element_located(
                (By.CSS_SELECTOR, "div.backdrop")
            )
        )


    # TC-DB20
    def close_via_escape(self):
        self.driver.find_element(
            *self.ROOT
        ).send_keys(Keys.ESCAPE)
        return self

    # TC-DB24, TC-DB25
    def click_open(self):
        self.wait.until(
            EC.element_to_be_clickable(
                self.locators.menu_item_by_text("Open")
            )
        ).click()
        return self

    # TC-DB26, TC-DB27, TC-DB28, TC-DB29, TC-DB30, TC-DB31, TC-DB32
    def click_rename(self):
        self.wait.until(
            EC.element_to_be_clickable(
                self.locators.menu_item_by_text("Rename")
            )
        ).click()

        form = DashboardForm(self.driver, self.locators)
        form.wait_until_open()
        return form

    # TC-DB34, TC-DB35, TC-DB36, TC-DB37
    def click_delete(self):
        self.wait.until(
            EC.element_to_be_clickable(
                self.locators.menu_item_by_text("Delete")
            )
        ).click()

        # The live app deletes the dashboard immediately; there is no
        # confirmation dialog to wait for.
        dialog = ConfirmDialog(self.driver, self.locators)
        return dialog

    # TC-DB40, TC-DB41, TC-DB42, TC-DB43
    def click_set_default(self):
        self.wait.until(
            EC.element_to_be_clickable(
                self.locators.menu_item_by_text("Set as Default")
            )
        ).click()

        self.wait_until_closed()
        return self
    
    def has_menu_item(self, label):
        try:
            element = self.element.find_element(
                By.XPATH,
                f".//li[normalize-space()='{label}']"
            )

            return element.is_displayed()

        except NoSuchElementException:
            return False

    def has_set_default(self):
        """
        Returns True if 'Set as Default' is visible in the context menu.
        """

        try:
            items = self.driver.find_elements(*self.ALL_ITEMS)

            return any(
                item.is_displayed()
                and item.text.strip() == "Set as Default"
                for item in items
            )

        except NoSuchElementException:
            return False

# ===========================================================================
# Dashboard Card
# ===========================================================================

class DashboardCard:
    """Represents one saved dashboard card."""

    def __init__(self, driver, element, locators, timeout=DEFAULT_TIMEOUT):
        self.driver = driver
        self.element = element
        self.locators = locators
        self.wait = WebDriverWait(driver, timeout)

    # TC-DB04, TC-DB15, TC-DB26, TC-DB27, TC-DB28, TC-DB30, TC-DB31, TC-DB32
    @property
    def title(self):
        """
        Return dashboard name only.

        DOM:
            <div class="layout-name">
                Analytics
                <span>DASHBOARD</span>
            </div>

        Returns:
            Analytics
        """

        element = self.element.find_element(
            *self.locators.get("card_title")
        )

        return self.driver.execute_script(
            """
            return Array.from(arguments[0].childNodes)
                .filter(node => node.nodeType === Node.TEXT_NODE)
                .map(node => node.textContent)
                .join('')
                .trim();
            """,
            element
        )

    # TC-DB04
    @property
    def label(self):
        return self.element.find_element(
            *self.locators.get("card_label")
        ).text.strip()

    # TC-DB04, TC-DB05, TC-DB32
    @property
    def updated_on_text(self):
        return self.element.find_element(
            *self.locators.get("card_updated_on")
        ).text.strip()

    # TC-DB04, TC-DB06, TC-DB07
    @property
    def widgets_badge_text(self):
        return self.element.find_element(
            *self.locators.get("card_widgets_badge")
        ).text.strip()

    # TC-DB06, TC-DB07
    def widgets_count(self):
        match = re.search(r"\d+", self.widgets_badge_text)
        return int(match.group()) if match else 0

    # TC-DB40, TC-DB41, TC-DB42, TC-DB43
    def is_default(self):
        try:
            return self.element.find_element(
                *self.locators.get("card_default_badge")
            ).is_displayed()
        except NoSuchElementException:
            return False

    # TC-DB15, TC-DB25
    def click(self):
        self.element.click()
        return self

    # TC-DB17, TC-DB18, TC-DB19, TC-DB20, TC-DB21, TC-DB22,
    # TC-DB23, TC-DB24, TC-DB25, TC-DB26, TC-DB27, TC-DB28, TC-DB29,
    # TC-DB30, TC-DB31, TC-DB32, TC-DB34, TC-DB35, TC-DB36,
    # TC-DB37, TC-DB40, TC-DB41, TC-DB42, TC-DB43
    def open_context_menu(self):

        locator = DashboardsLocators().get(
            "card_menu_trigger"
        )

        button = self.element.find_element(
            *locator
        )

        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            button
        )

        self.wait.until(
            lambda d: button.is_displayed()
            and button.is_enabled()
        )

        try:
            button.click()

        except Exception:
            self.driver.execute_script(
                "arguments[0].click();",
                button
            )

        menu = ContextMenu(self.driver)

        menu.wait_until_open()

        return menu

    # TC-DB21
    def has_visible_menu_items(self):
        items = self.driver.find_elements(*ContextMenu.ALL_ITEMS)
        return any(item.is_displayed() for item in items)


# ===========================================================================
# Dashboard Manage Page
# ===========================================================================

class DashboardPage:
    """Statistics > Dashboards manage page."""

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, DEFAULT_TIMEOUT)
        self.locators = DashboardsLocators()

    # -----------------------------------------------------------------------
    # Heading / Subtitle
    # -----------------------------------------------------------------------

    # TC-DB01-P
    def heading_is_visible(self):
        return self.wait.until(
            EC.visibility_of_element_located(
                self.locators.get("heading")
            )
        ).is_displayed()

    # TC-DB01-N
    def is_heading_present(self):
        try:
            self.wait.until(
                EC.visibility_of_element_located(
                    self.locators.get("heading")
                )
            )
            return True
        except TimeoutException:
            return False


    # TC-DB01-P
    def get_heading(self):
        return self.wait.until(
            EC.visibility_of_element_located(
                self.locators.get("heading")
            )
        ).text.strip()

    # TC-DB16-P
    def is_rendered(self):
        return self.is_heading_present()

    # TC-DB01-P
    def subtitle_is_visible(self):
        return self.wait.until(
            EC.visibility_of_element_located(
                self.locators.get("subtitle")
            )
        ).is_displayed()

    # TC-DB01-P
    def get_subtitle_text(self):
        return self.wait.until(
            EC.visibility_of_element_located(
                self.locators.get("subtitle")
            )
        ).text.strip()

    # -----------------------------------------------------------------------
    # Dashboard Cards
    # -----------------------------------------------------------------------

    # TC-DB03-P
    def is_dashboard_card_present(self):
        return bool(
            self.driver.find_elements(
                *self.locators.get("card_level")
            )
        )

    # TC-DB03-P
    def get_dashboard_card_level(self):
        """Return text of the first visible dashboard card."""
        return self.wait.until(
            EC.visibility_of_element_located(
                self.locators.get("card_level")
            )
        ).text.strip()

    # TC-DB04, TC-DB15
    def dashboard_is_visible(self, name):
        return self.wait.until(
            EC.visibility_of_element_located(
                self.locators.card_name(name)
            )
        ).is_displayed()

    # TC-DB04, TC-DB15
    def get_dashboard_name(self, name):
        return self.wait.until(
            EC.visibility_of_element_located(
                self.locators.card_name(name)
            )
        ).text.strip()

    # TC-DB11, TC-DB13, TC-DB35, TC-DB36
    def cards_count(self):
        return len(
            self.driver.find_elements(
                *self.locators.get("card_level")
            )
        )

    # TC-DB23, TC-DB31, TC-DB35, TC-DB36, TC-DB37, TC-DB40,
    # TC-DB41, TC-DB42, TC-DB43
    def get_all_cards(self):
        return [
            DashboardCard(self.driver, element, self.locators)
            for element in self.driver.find_elements(
                *self.locators.get("card_level")
            )
        ]

    # TC-DB04, TC-DB11, TC-DB15, TC-DB22, TC-DB27, TC-DB31,
    # TC-DB32, TC-DB35, TC-DB36, TC-DB37, TC-DB40, TC-DB41,
    # TC-DB42, TC-DB43
    def get_card_by_name(self, name):
        for card in self.get_all_cards():
            try:
                if card.title == name:
                    return card
            except StaleElementReferenceException:
                continue
        return None

    # TC-DB11, TC-DB27, TC-DB31, TC-DB32, TC-DB35
    def wait_for_card_present(self, name):
        self.wait.until(
            lambda d: self.get_card_by_name(name) is not None
        )
        return self

    # TC-DB11, TC-DB35, TC-DB37
    def wait_for_card_absent(self, name):
        self.wait.until(
            lambda d: self.get_card_by_name(name) is None
        )
        return self

    # -----------------------------------------------------------------------
    # Add Dashboard
    # -----------------------------------------------------------------------

    # TC-DB02-P
    def add_card_is_visible(self):
        return self.wait.until(
            EC.visibility_of_element_located(
                self.locators.get("add_dashboard_card")
            )
        ).is_displayed()

    # TC-DB08, TC-DB09, TC-DB10, TC-DB11, TC-DB12, TC-DB13, TC-DB14
    def click_add_card(self):
        locator = self.locators.get("add_dashboard_card")

        # Wait until the Add Dashboard control is present
        element = self.wait.until(
            EC.presence_of_element_located(locator)
        )

        # Scroll it into view
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            element
        )

        # Try normal click first
        try:
            self.wait.until(
                EC.element_to_be_clickable(locator)
            ).click()

        except Exception:
            # Fallback for elements that are present/visible
            # but Selenium considers not clickable
            self.driver.execute_script(
                "arguments[0].click();",
                element
            )

        form = DashboardForm(self.driver, self.locators)
        form.wait_until_open()

        return form

    # -----------------------------------------------------------------------
    # Generic Button
    # -----------------------------------------------------------------------

    def click_button(self, text):
        self.wait.until(
            EC.element_to_be_clickable(
                self.locators.button_by_text(text)
            )
        ).click()