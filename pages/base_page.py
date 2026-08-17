from utils.selenium_helpers import SeleniumHelper


class BasePage:

    def __init__(self, driver):
        self.driver = driver
        self.locators = None

    def _wait(self, timeout=20):
        return SeleniumHelper.wait(
            self.driver,
            timeout
        )

    def _find(self, key):
        return SeleniumHelper.find(
            self.driver,
            self.locators.get(key)
        )

    def _find_all(self, key):
        return SeleniumHelper.find_all(
            self.driver,
            self.locators.get(key)
        )

    def _visible(self, key, timeout=20):
        return SeleniumHelper.wait_visible(
            self.driver,
            self.locators.get(key),
            timeout
        )

    def _clickable(self, key, timeout=20):
        return SeleniumHelper.wait_clickable(
            self.driver,
            self.locators.get(key),
            timeout
        )

    def _is_visible(self, key):
        return SeleniumHelper.is_visible(
            self.driver,
            self.locators.get(key)
        )
