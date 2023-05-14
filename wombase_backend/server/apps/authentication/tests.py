from rest_framework.authtoken.models import Token

from server.apps.authentication.serializers import (
    EmployeeRegistrationSerializer,
    EmployeeLoginSerializer,
)
from server.apps.core.models import Employee
from server.apps.core.tests import AbstractCreateViewTestMixin, AbstractTestMixin
from server.apps.employee.models import EmployeeRole


class InheritsEmployeeCreateData:
    create_data = {
        "phone_number": "+380970987654",
        "first_name": "Helen",
        "last_name": "Crain",
        "email": "helen.crain@example.com",
        "role": "Manager",
        "password": "somePassword123#(#(",
    }

    @classmethod
    def get_sample_data(cls):
        return cls.create_data.copy()


class TestEmployeeRegistrationAPIView(InheritsEmployeeCreateData, AbstractCreateViewTestMixin):
    serializer = EmployeeRegistrationSerializer
    url = "/employee/register/"

    def setUp(self) -> None:
        EmployeeRole.objects.get_or_create(name="Manager")

    def test_register(self):
        self.basic_create_functionality_test()
        employee = Employee.objects.get(phone_number="+380970987654")
        token = Token.objects.filter(user=employee).first()
        self.assertIsNotNone(token, f"Token is not in the DB after registration")


class TestEmployeeLoginAPIView(InheritsEmployeeCreateData, AbstractTestMixin):
    serializer = EmployeeLoginSerializer
    url = "/employee/login/"

    @property
    def login_data(self):
        return {key: self.create_data.get(key) for key in ("phone_number", "password")}

    def setUp(self) -> None:
        EmployeeRole.objects.create(name="Manager")
        serializer = EmployeeRegistrationSerializer()
        serializer.create(self.get_sample_data())

    def test_login(self):
        response = self.client.post(self.url, data=self.login_data)
        self.request_code_matches_expected_test(response, 200)
        expected_token = Token.objects.get(
            user__phone_number=self.create_data.get("phone_number")
        ).key
        actual_token = response.data.get("token")
        self.assertEquals(
            expected_token,
            actual_token,
            "Token acquired after registration and token acquired after login do not match",
        )
