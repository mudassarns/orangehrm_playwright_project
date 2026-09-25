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

    response = orangehrm_api.get_employees(
        employee_id=employee_data["employee_id"]
    )

    assert response.ok

    data = response.json()

    assert len(data["data"]) == 1

    employee = data["data"][0]

    assert employee["employeeId"] == employee_data["employee_id"]

    emp_number = employee["empNumber"]

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

    authenticated_page.reload()
    expect(employee_list.employee_information_heading).to_be_visible()

    result_count = employee_list.search_employee_by_id(
        employee_data["employee_id"]
    )
    
    assert result_count == 1

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

    response = orangehrm_api.get_employees(
        employee_id=employee_data["employee_id"]
    )

    assert response.ok

    data = response.json()

    assert len(data["data"]) == 1

    employee = data["data"][0]

    assert employee["employeeId"] == employee_data["employee_id"]

    emp_number = employee["empNumber"]

    employee_list = employee_details.go_to_employee_list()

    employee_list.search_employee_by_id(
        employee_data["employee_id"]
    )

    expect(employee_list.employee_result_rows).to_have_count(1)

    employee_list.delete_employee(
        employee_data["employee_id"]
    )

    employee_list.search_employee_by_id(
        employee_data["employee_id"]
    )

    expect(employee_list.employee_result_rows).to_have_count(0)

    response = orangehrm_api.get_employee(emp_number)

    assert response.status == 422
