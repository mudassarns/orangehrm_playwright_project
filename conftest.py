import pytest
from playwright.sync_api import expect
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from utils.test_data import generate_employee_data
from api.orangehrm_api import OrangeHRMApi
from db.database_client import DatabaseClient
from config import Config
from utils.screenshot import attach_failure_screenshot
import logging

logger = logging.getLogger(__name__)


def pytest_addoption(parser):
    parser.addoption(
        "--env",
        action="store",
        default="qa",
        help="Environment to run tests against",
    )

@pytest.fixture(scope="session", autouse=True)
def set_environment(request):
    Config.environment = request.config.getoption("--env")

@pytest.fixture(scope="session")
def auth_state(browser):
    context = browser.new_context()
    page = context.new_page()

    page.goto(Config.get("ORANGEHRM_BASE_URL"))

    login_page = LoginPage(page)
    dashboard = login_page.login(
        Config.get("ORANGEHRM_USERNAME"),
        Config.get("ORANGEHRM_PASSWORD")
    )

    expect(dashboard.dashboard_header).to_be_visible()
    logger.info("AUTH LOGIN | success")

    state = context.storage_state()

    context.close()

    return state


@pytest.fixture
def authenticated_page(browser, auth_state, request):
    context = browser.new_context(storage_state=auth_state)
    page = context.new_page()

    request.node._playwright_page = page

    page.goto(Config.get("ORANGEHRM_BASE_URL"))

    if "/auth/login" in page.url:
        context.close()

        refresh_auth_state(browser, auth_state)

        context = browser.new_context(storage_state=auth_state)
        page = context.new_page()

        request.node._playwright_page = page

        page.goto(Config.get("ORANGEHRM_BASE_URL"))

        if "/auth/login" in page.url:
            context.close()
            raise AssertionError(
                "Authentication refresh failed: application redirected to login page"
            )

    yield page

    context.close()


def refresh_auth_state(browser, auth_state):
    context = browser.new_context()
    page = context.new_page()

    page.goto(Config.get("ORANGEHRM_BASE_URL"))

    login_page = LoginPage(page)
    dashboard = login_page.login(
        Config.get("ORANGEHRM_USERNAME"),
        Config.get("ORANGEHRM_PASSWORD"),
    )

    expect(dashboard.dashboard_header).to_be_visible()

    logger.info("AUTH REFRESH | UI | success")
    new_state = context.storage_state()

    context.close()

    auth_state.clear()
    auth_state.update(new_state)


@pytest.fixture
def create_employee(authenticated_page):
    employee_data = generate_employee_data()

    dashboard = DashboardPage(authenticated_page)
    employee_list = dashboard.go_to_pim()
    add_employee = employee_list.go_to_add_employee()

    add_employee.enter_first_name(employee_data["first_name"])
    add_employee.enter_middle_name(employee_data["middle_name"])
    add_employee.enter_last_name(employee_data["last_name"])
    add_employee.enter_employee_id(employee_data["employee_id"])

    employee_details = add_employee.save()
    logger.info(
    "UI CREATE | employee_id=%s",
    employee_data["employee_id"],
)

    yield employee_data, employee_details

    employee_list = employee_details.go_to_employee_list()
    employee_list.search_employee_by_id(employee_data["employee_id"])

    result_count = employee_list.employee_result_rows.count()

    if result_count == 1:
        employee_list.delete_employee()

        employee_list.search_employee_by_id(
            employee_data["employee_id"]
        )

        result_count = employee_list.employee_result_rows.count()

        if result_count == 0:
            logger.info(
                f"CLEANUP SUCCESS: Employee "
                f"{employee_data['employee_id']} deleted"
            )
        else:
            logger.error(
                f"CLEANUP FAILED: Employee "
                f"{employee_data['employee_id']} still exists"
            )

    else:
        logger.warning(
            f"CLEANUP NOT REQUIRED: Employee "
            f"{employee_data['employee_id']} not found"
        )


@pytest.fixture
def orangehrm_api(playwright, browser, auth_state):
    request = playwright.request.new_context(
        storage_state=auth_state
    )

    def refresh_request():
        refresh_auth_state(browser, auth_state)

        return playwright.request.new_context(
            storage_state=auth_state
        )

    api = OrangeHRMApi(
        request=request,
        base_url=Config.get("ORANGEHRM_BASE_URL"),
        refresh_request=refresh_request,
    )

    yield api

    api.request.dispose()

@pytest.fixture
def create_employee_api(orangehrm_api):
    employee_data = generate_employee_data()

    create_response = orangehrm_api.create_employee(employee_data)

    assert create_response.status == 200

    employee_details = create_response.json()
    emp_number = employee_details["data"]["empNumber"]

    yield employee_data, employee_details

    get_response = orangehrm_api.get_employee(emp_number)

    if get_response.status == 200:
        delete_response = orangehrm_api.delete_employee(emp_number)

        if delete_response.status == 200:
            logger.info(f"CLEANUP SUCCESS: Employee {emp_number} deleted")
        else:
            logger.error(
                f"CLEANUP FAILED: Employee {emp_number} "
                f"could not be deleted. Status: {delete_response.status}"
            )
    else:
        logger.warning(f"CLEANUP NOT REQUIRED: Employee {emp_number} not found")

@pytest.fixture
def db():
    database = DatabaseClient()
    yield database
    database.close()

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when not in ("setup", "call") or not report.failed:
        return

    page = getattr(item, "_playwright_page", None)

    if page is not None:
        attach_failure_screenshot(report, page)
