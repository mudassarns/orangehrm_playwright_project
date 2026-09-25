from playwright.sync_api import APIRequestContext
import logging

logger = logging.getLogger(__name__)


class OrangeHRMApi:
    EMPLOYEES_ENDPOINT = "/web/index.php/api/v2/pim/employees"

    def __init__(
        self,
        request: APIRequestContext,
        base_url: str,
        refresh_request,
    ):
        self.request = request
        self.base_url = base_url
        self.refresh_request = refresh_request

    def _request(self, method, url, **kwargs):
        response = self.request.fetch(
            url,
            method=method,
            **kwargs,
        )

        logger.info(
            "API %s | %s | Status: %s",
            method,
            url,
            response.status,
        )

        if response.status in (401, 403):
            logger.warning(
                "API %s | Authentication failed with status %s | "
                "Refreshing authentication state",
                method,
                response.status,
            )

            self.request.dispose()
            self.request = self.refresh_request()

            response = self.request.fetch(
                url,
                method=method,
                **kwargs,
            )

            logger.info(
                "API %s | Retry status: %s",
                method,
                response.status,
            )

        return response

    def get_employees(self, limit=None, offset=None, employee_id=None):
        params = {}

        if limit is not None:
            params["limit"] = limit

        if offset is not None:
            params["offset"] = offset

        if employee_id is not None:
            params["employeeId"] = employee_id

        return self._request(
            "GET",
            f"{self.base_url}{self.EMPLOYEES_ENDPOINT}",
            params=params,
        )

    def get_employee(self, emp_number):
        return self._request(
            "GET",
            f"{self.base_url}{self.EMPLOYEES_ENDPOINT}/{emp_number}",
        )

    def create_employee(self, employee_data):
        payload = {
            "firstName": employee_data["first_name"],
            "middleName": employee_data["middle_name"],
            "lastName": employee_data["last_name"],
            "empPicture": None,
            "employeeId": employee_data["employee_id"],
        }

        return self._request(
            "POST",
            f"{self.base_url}{self.EMPLOYEES_ENDPOINT}",
            data=payload,
        )

    def delete_employee(self, emp_number):
        payload = {
            "ids": [emp_number]
        }

        return self._request(
            "DELETE",
            f"{self.base_url}{self.EMPLOYEES_ENDPOINT}",
            data=payload,
        )

    def update_employee(
        self,
        emp_number,
        employee_id,
        first_name,
        middle_name,
        last_name,
    ):
        payload = {
            "firstName": first_name,
            "middleName": middle_name,
            "lastName": last_name,
            "employeeId": employee_id,
        }

        return self._request(
            "PUT",
            f"{self.base_url}{self.EMPLOYEES_ENDPOINT}/{emp_number}/personal-details",
            data=payload,
        )
