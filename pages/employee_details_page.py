from playwright.sync_api import Page, expect


class EmployeeDetailsPage:

    def __init__(self, page: Page):
        self.page = page

        self.personal_details_tab = page.get_by_role(
            "link", name="Personal Details"
        )

        self.employee_list_link = page.get_by_role(
            "link", name="Employee List"
        )

        self.first_name = page.get_by_role(
            "textbox", name="First Name"
        )

        self.middle_name = page.get_by_role(
            "textbox", name="Middle Name"
        )

        self.last_name = page.get_by_role(
            "textbox", name="Last Name"
        )

        self.save_button = page.get_by_role(
            "button", name="Save"
        )

        self.success_toast = page.locator(".oxd-toast--success")

    def enter_first_name(self, first_name):
        self.first_name.click()
        self.first_name.fill(first_name)

    def enter_middle_name(self, middle_name):
        self.first_name.click()
        self.middle_name.fill(middle_name)

    def enter_last_name(self, last_name):
        self.first_name.click()
        self.last_name.fill(last_name)

    def save(self):
        with self.page.expect_response(
            lambda response:
            "/web/index.php/api/v2/pim/employees/" in response.url
            and "/personal-details" in response.url
            and response.request.method == "PUT"
        ):
            self.save_button.click()

        expect(self.success_toast).to_be_visible()
        expect(self.employee_list_link).to_be_visible()

        return EmployeeDetailsPage(self.page)

    def go_to_employee_list(self):
        self.employee_list_link.click()

        from pages.employee_list_page import EmployeeListPage

        return EmployeeListPage(self.page)
