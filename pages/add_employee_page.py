from playwright.sync_api import Page, expect

from pages.employee_details_page import EmployeeDetailsPage


class AddEmployeePage:

    def __init__(self, page: Page):
        self.page = page

        self.add_employee_heading = page.get_by_role(
            "heading", name="Add Employee"
        )

        self.first_name = page.get_by_role("textbox", name="First Name")
        self.middle_name = page.get_by_role("textbox", name="Middle Name")
        self.last_name = page.get_by_role("textbox", name="Last Name")

        self.employee_id = page.locator(".oxd-input-group").filter(
            has=page.locator("label", has_text="Employee Id")
        ).locator("input")

        self.save_button = page.get_by_role(
            "button", name="Save"
        )

        self.success_toast = page.locator(
            ".oxd-toast--success"
        )

    def enter_first_name(self, first_name):
        self.first_name.fill(first_name)

    def enter_middle_name(self, middle_name):
        self.middle_name.fill(middle_name)

    def enter_last_name(self, last_name):
        self.last_name.fill(last_name)

    def enter_employee_id(self, employee_id):
        self.employee_id.fill(employee_id)

    def save(self):
        with self.page.expect_response(
            lambda response:
            "/web/index.php/api/v2/pim/employees" in response.url
            and response.request.method == "POST"
        ):
            self.save_button.click()

        expect(self.success_toast).to_be_visible()

        employee_details = EmployeeDetailsPage(self.page)
        expect(employee_details.personal_details_tab).to_be_visible()

        return employee_details
