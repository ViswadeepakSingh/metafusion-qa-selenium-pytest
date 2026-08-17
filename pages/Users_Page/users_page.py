from PageObject.base_page import BasePage


class UsersPage(BasePage):
    # Locators
    USERS_TABLE      = "[data-testid='users-table']"
    ADD_USER_BTN     = "button:has-text('Add User')"
    USER_ROW         = "[data-testid='user-row']"
    DELETE_USER_BTN  = "button:has-text('Delete')"
    EDIT_USER_BTN    = "button:has-text('Edit')"
    CONFIRM_DELETE   = "button:has-text('Confirm')"
    USER_NAME_INPUT  = "[data-testid='user-name']"
    USER_EMAIL_INPUT = "[data-testid='user-email']"
    USER_ROLE_DD     = "[data-testid='user-role']"
    SAVE_USER_BTN    = "button:has-text('Save')"

    def __init__(self, page):
        super().__init__(page)

    def get_user_count(self) -> int:
        return self.count_elements(self.USER_ROW)

    def click_add_user(self):
        self.click(self.ADD_USER_BTN)

    def fill_user_details(self, name: str, email: str, role: str):
        self.fill(self.USER_NAME_INPUT, name)
        self.fill(self.USER_EMAIL_INPUT, email)
        self.select_option(self.USER_ROLE_DD, role)

    def save_user(self):
        self.click(self.SAVE_USER_BTN)

    def is_users_table_visible(self) -> bool:
        return self.is_visible(self.USERS_TABLE)
