from playwright.sync_api import expect
from pages.dashboard_page import DashboardPage
import pytest

pytestmark = pytest.mark.hybrid


def test_api_created_employee_visible_in_ui(
    authenticated_page,
    create_employee_api,
):
    employee_data, _ = create_employee_api

    dashboard = DashboardPage(authenticated_page)
    employee_list = dashboard.go_to_pim()

    employee_list.search_employee_by_id(
        employee_data["employee_id"]
    )

    expect(employee_list.employee_result_rows).to_have_count(1)


def test_ui_created_employee_visible_in_api(
    create_employee,
    orangehrm_api,
):
    employee_data, _ = create_employee

    response = orangehrm_api.get_employees(limit=100)

    assert response.ok

    data = response.json()

    matching_employees = [
        employee
        for employee in data["data"]
        if employee["employeeId"] == employee_data["employee_id"]
    ]

    assert len(matching_employees) == 1

    emp_number = matching_employees[0]["empNumber"]

    response = orangehrm_api.get_employee(emp_number)

    assert response.ok
    assert response.json()["data"]["employeeId"] == employee_data["employee_id"]


def test_api_updated_employee_visible_in_ui(
    authenticated_page,
    orangehrm_api,
    create_employee_api,
):
    employee_data, employee_details = create_employee_api

    emp_number = employee_details["data"]["empNumber"]

    response = orangehrm_api.update_employee(
        emp_number,
        employee_data["employee_id"],
        "UpdatedName",
        "UpdatedMiddle",
        "UpdatedLast",
    )

    assert response.ok

    dashboard = DashboardPage(authenticated_page)
    employee_list = dashboard.go_to_pim()

    employee_list.search_employee_by_id(
        employee_data["employee_id"]
    )

    expect(employee_list.employee_result_rows).to_have_count(1)

    row_text = employee_list.employee_result_rows.first.inner_text()

    assert "UpdatedName" in row_text
    assert "UpdatedMiddle" in row_text
    assert "UpdatedLast" in row_text
    assert employee_data["employee_id"] in row_text


def test_ui_deleted_employee_not_found_in_api(
    create_employee,
    orangehrm_api,
):
    employee_data, employee_details = create_employee

    response = orangehrm_api.get_employees(limit=100)

    assert response.ok

    data = response.json()

    matching_employees = [
        employee
        for employee in data["data"]
        if employee["employeeId"] == employee_data["employee_id"]
    ]

    assert len(matching_employees) == 1

    emp_number = matching_employees[0]["empNumber"]

    employee_list = employee_details.go_to_employee_list()

    employee_list.search_employee_by_id(
        employee_data["employee_id"]
    )

    expect(employee_list.employee_result_rows).to_have_count(1)

    employee_list.delete_employee()

    employee_list.search_employee_by_id(
        employee_data["employee_id"]
    )

    expect(employee_list.employee_result_rows).to_have_count(0)

    response = orangehrm_api.get_employee(emp_number)

    assert response.status == 422
