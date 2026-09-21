from pages.dashboard_page import DashboardPage


class LoginPage:

    def __init__(self, page):
        self.page = page

        self.username = page.get_by_role("textbox", name="Username")
        self.password = page.get_by_role("textbox", name="Password")
        self.login_button = page.get_by_role("button", name="Login")

    def login(self, username, password):
        self.username.fill(username)
        self.password.fill(password)
        self.login_button.click()

        return DashboardPage(self.page)
