from playwright.sync_api import expect
from pages.dashboard_page import DashboardPage
import pytest
from config import Config
from pages.login_page import LoginPage

pytestmark = pytest.mark.ui


def test_login(page):
    page.goto(Config.get("ORANGEHRM_BASE_URL"))

    login_page = LoginPage(page)
    dashboard = login_page.login(
        Config.get("ORANGEHRM_USERNAME"),
        Config.get("ORANGEHRM_PASSWORD"),
    )

    expect(dashboard.dashboard_header).to_be_visible()
    assert 1 == 2

def test_authenticated_page(authenticated_page):
    dashboard = DashboardPage(authenticated_page)

    expect(dashboard.dashboard_header).to_be_visible()


def test_search_employee_by_id(authenticated_page):
    dashboard = DashboardPage(authenticated_page)

    employee_list = dashboard.go_to_pim()

    employee_list.search_employee_by_id("0001")

    expect(employee_list.employee_result_rows).to_have_count(1)
    expect(employee_list.employee_result_rows.first).to_contain_text("0001")

    employee_details = employee_list.open_employee_details()

    expect(employee_details.personal_details_tab).to_be_visible()
    assert 1 == 2


def test_create_employee(create_employee):
    employee_data, employee_details = create_employee

    expect(employee_details.personal_details_tab).to_be_visible()

    employee_list = employee_details.go_to_employee_list()

    employee_list.search_employee_by_id(
        employee_data["employee_id"]
    )
    assert 1 == 2

    expect(employee_list.employee_result_rows).to_have_count(1)
    expect(
        employee_list.employee_result_rows.first
    ).to_contain_text(employee_data["employee_id"])


def test_edit_employee(create_employee):
    employee_data, employee_details = create_employee

    employee_list = employee_details.go_to_employee_list()
    employee_list.search_employee_by_id(employee_data["employee_id"])

    expect(employee_list.employee_result_rows).to_have_count(1)

    employee_details = employee_list.open_employee_details()

    employee_details.enter_first_name("Updated")
    expect(employee_details.first_name).to_have_value("Updated")

    employee_details.enter_middle_name("UpdatedMiddle")
    expect(employee_details.middle_name).to_have_value("UpdatedMiddle")

    employee_details.enter_last_name("UpdatedLast")
    expect(employee_details.last_name).to_have_value("UpdatedLast")

    employee_details.save()
    
    employee_list = employee_details.go_to_employee_list()
    employee_list.search_employee_by_id(employee_data["employee_id"])

    expect(employee_list.employee_result_rows).to_have_count(1)

    row = employee_list.employee_result_rows.first

    expect(row.get_by_role("cell").nth(1)).to_have_text(
    employee_data["employee_id"]
    )
    expect(row.get_by_role("cell").nth(2)).to_have_text(
        "Updated UpdatedMiddle"
    )
    expect(row.get_by_role("cell").nth(3)).to_have_text(
        "UpdatedLast"
    )


def test_delete_employee(create_employee):
    employee_data, employee_details = create_employee

    employee_list = employee_details.go_to_employee_list()
    employee_list.search_employee_by_id(employee_data["employee_id"])

    expect(employee_list.employee_result_rows).to_have_count(1)

    employee_list.delete_employee()

    employee_list.search_employee_by_id(employee_data["employee_id"])

    expect(employee_list.employee_result_rows).to_have_count(0)
