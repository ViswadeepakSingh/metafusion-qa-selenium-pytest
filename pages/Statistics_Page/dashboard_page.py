from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from locators.dashboard_locators import DashboardsLocators


DEFAULT_TIMEOUT = 15


class DashboardPage:

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, DEFAULT_TIMEOUT)
        self.locators = DashboardsLocators()

    # ====================================================================
    # Heading
    # ====================================================================

    def heading_is_visible(self) -> bool:
        return self.wait.until(
            EC.visibility_of_element_located(
                self.locators.get("heading")
            )
        ).is_displayed()

    def is_heading_present(self) -> bool:
        return len(
            self.driver.find_elements(
                *self.locators.get("heading")
            )
        ) > 0

    def get_heading(self) -> str:
        return self.wait.until(
            EC.visibility_of_element_located(
                self.locators.get("heading")
            )
        ).text

    # ====================================================================
    # Subtitle
    # ====================================================================

    def subtitle_is_visible(self) -> bool:
        return self.wait.until(
            EC.visibility_of_element_located(
                self.locators.get("subtitle")
            )
        ).is_displayed()

    def get_subtitle_text(self) -> str:
        return self.wait.until(
            EC.visibility_of_element_located(
                self.locators.get("subtitle")
            )
        ).text

    # ====================================================================
    # Dashboard Cards
    # ====================================================================

    def is_dashboard_card_present(self) -> bool:
        cards = self.driver.find_elements(
            *self.locators.get("card_level")
        )

        return len(cards) > 0
    
    def get_dashboard_card_level(self) -> str:
        return self.wait.until(
            EC.visibility_of_element_located(
                self.locators.get("card_level")
            )
        ).text.strip()

    def dashboard_is_visible(self, name: str) -> bool:
        return self.wait.until(
            EC.visibility_of_element_located(
                self.locators.card_name(name)
            )
        ).is_displayed()

    def get_dashboard_name(self, name: str) -> str:
        return self.wait.until(
            EC.visibility_of_element_located(
                self.locators.card_name(name)
            )
        ).text

    # ====================================================================
    # Create Dashboard
    # ====================================================================

    def click_add_dashboard(self):
        self.wait.until(
            EC.element_to_be_clickable(
                self.locators.get("add_dashboard_card")
            )
        ).click()

    def enter_dashboard_name(self, name: str):
        element = self.wait.until(
            EC.visibility_of_element_located(
                self.locators.get("dashboard_name_input")
            )
        )

        element.clear()
        element.send_keys(name)

    def click_save(self):
        self.wait.until(
            EC.element_to_be_clickable(
                self.locators.get("save_button")
            )
        ).click()

    def click_cancel(self):
        self.wait.until(
            EC.element_to_be_clickable(
                self.locators.get("cancel_button")
            )
        ).click()

    # ====================================================================
    # Generic Button
    # ====================================================================

    def click_button(self, text: str):
        self.wait.until(
            EC.element_to_be_clickable(
                self.locators.button_by_text(text)
            )
        ).click()