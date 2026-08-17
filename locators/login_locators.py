from selenium.webdriver.common.by import By


class LoginPageLocators:

    locators = {

        "username_input": (
            By.XPATH,
            "//input[@placeholder='Email address']"
        ),

        "password_input": (
            By.XPATH,
            "//input[@placeholder='Password']"
        ),

        "SignIn_button": (
            By.XPATH,
            "//button[normalize-space()='Sign In']"
        ),

        "logout_button": (
            By.CSS_SELECTOR,
            "#logout"
        ),

        "confirm_logout_button": (
            By.XPATH,
            "//span[normalize-space()='Yes']"
        ),

        "success_popup": (
            By.CSS_SELECTOR,
            "#toast-container"
        ),

        "Toast_Error_Msg": (
            By.CSS_SELECTOR,
            "#toast-container"
        ),

        "Dashboard_header": (
            By.XPATH,
            "//div[@class='root_heading']"
        ),

        "error_message": (
            By.XPATH,
            "//span[@class='text-danger ng-star-inserted']"
        ),

        "remember_me_container": (
            By.CSS_SELECTOR,
            "span.checkmark"
        ),

        "remember_me_input": (
            By.CSS_SELECTOR,
            "input[type='checkbox']"
        ),

        "forgot_password_link": (
            By.XPATH,
            "//a[normalize-space()='Forgot password?']"
        ),
    }

    @classmethod
    def get(cls, key: str):
        return cls.locators[key]
