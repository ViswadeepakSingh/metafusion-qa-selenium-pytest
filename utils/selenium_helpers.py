from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException
)


class SeleniumHelper:

    @staticmethod
    def wait(driver, timeout=20):
        """
        Return WebDriverWait instance.
        """

        return WebDriverWait(
            driver,
            timeout
        )

    @staticmethod
    def find(driver, locator):
        """
        Find a single element.
        """

        return driver.find_element(
            *locator
        )

    @staticmethod
    def find_all(driver, locator):
        """
        Find all matching elements.
        """

        return driver.find_elements(
            *locator
        )

    @staticmethod
    def wait_visible(
        driver,
        locator,
        timeout=20
    ):
        """
        Wait until an element is visible.
        """

        return WebDriverWait(
            driver,
            timeout
        ).until(
            EC.visibility_of_element_located(
                locator
            )
        )

    @staticmethod
    def wait_clickable(
        driver,
        locator,
        timeout=20
    ):
        """
        Wait until an element is clickable.
        """

        return WebDriverWait(
            driver,
            timeout
        ).until(
            EC.element_to_be_clickable(
                locator
            )
        )

    @staticmethod
    def is_visible(driver, locator):
        """
        Return True if element exists and is visible.
        """

        try:
            element = driver.find_element(
                *locator
            )

            return element.is_displayed()

        except (
            NoSuchElementException,
            TimeoutException
        ):
            return False
