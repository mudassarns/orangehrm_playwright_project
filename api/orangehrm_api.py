from playwright.sync_api import APIRequestContext


class OrangeHRMApi:
    EMPLOYEES_ENDPOINT = "/web/index.php/api/v2/pim/employees"

    def __init__(self, request: APIRequestContext, base_url: str):
        self.request = request
        self.base_url = base_url

    def get_employees(self, limit=None, offset=None):
        params = {}

        if limit is not None:
            params["limit"] = limit

        if offset is not None:
            params["offset"] = offset

        return self.request.get(
            f"{self.base_url}{self.EMPLOYEES_ENDPOINT}",
            params=params,
        )

    def get_employee(self, emp_number):
        return self.request.get(
            f"{self.base_url}{self.EMPLOYEES_ENDPOINT}/{emp_number}"
        )

    def create_employee(self, employee_data):
        payload = {
            "firstName": employee_data["first_name"],
            "middleName": employee_data["middle_name"],
            "lastName": employee_data["last_name"],
            "empPicture": None,
            "employeeId": employee_data["employee_id"],
        }

        return self.request.post(
            f"{self.base_url}{self.EMPLOYEES_ENDPOINT}",
            data=payload,
        )

    def delete_employee(self, emp_number):
        payload = {
            "ids": [emp_number]
        }

        return self.request.delete(
            f"{self.base_url}{self.EMPLOYEES_ENDPOINT}",
            data=payload,
        )

    def update_employee(self, emp_number, employee_id, first_name, middle_name, last_name):
        payload = {
            "firstName": first_name,
            "middleName": middle_name,
            "lastName": last_name,
            "employeeId": employee_id,
        }

        return self.request.put(
            f"{self.base_url}{self.EMPLOYEES_ENDPOINT}/{emp_number}/personal-details",
            data=payload,
        )
