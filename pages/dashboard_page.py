from playwright.sync_api import Page
from pages.employee_list_page import EmployeeListPage


class DashboardPage:

    def __init__(self, page: Page):
        self.page = page

        self.dashboard_header = page.get_by_role(
            "heading", name="Dashboard"
        )
        self.pim_menu = page.get_by_role(
            "link", name="PIM"
        )

    def go_to_pim(self):
        self.pim_menu.click()

        return EmployeeListPage(self.page)
