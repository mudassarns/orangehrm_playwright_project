from playwright.sync_api import Page
from pages.employee_details_page import EmployeeDetailsPage
from pages.add_employee_page import AddEmployeePage


class EmployeeListPage:

    def __init__(self, page: Page):
        self.page = page

        self.employee_information_heading = page.get_by_role(
            "heading", name="Employee Information"
        )

        self.employee_id = page.locator(".oxd-input-group").filter(
            has=page.locator("label", has_text="Employee Id")
        ).locator("input")

        self.search_button = page.get_by_role(
            "button", name="Search"
        )

        self.employee_result_rows = page.locator(
            ".oxd-table-body .oxd-table-card"
        )

        self.add_employee_link = page.get_by_role(
            "link", name="Add Employee"
        )

        self.confirm_delete_button = page.get_by_role(
            "button", name="Yes, Delete"
        )


    def search_employee_by_id(self, employee_id):
        self.employee_id.fill(employee_id)
        self.search_button.click()

    def open_employee_details(self):
        self.employee_result_rows.first.click()
        return EmployeeDetailsPage(self.page)

    def go_to_add_employee(self):
        self.add_employee_link.click()
        return AddEmployeePage(self.page)

    def delete_employee(self):
        delete_button = self.employee_result_rows.first.get_by_role(
            "button"
        ).filter(
            has=self.page.locator("i.bi-trash")
        )

        delete_button.click()
        self.confirm_delete_button.click()
