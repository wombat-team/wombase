from django.test import TestCase
from rest_framework.test import APIClient

from ..core.models import Employee, EmployeeRole
from .serializers import EmployeeDetailsSerializer


def to_dict(
        employee: Employee | dict,
        fields: tuple = EmployeeDetailsSerializer.Meta.fields,
        excluded_fields: tuple = ("password",),
):
    employee_dict = {}
    necessary_fields = set(fields) - set(excluded_fields)
    foreign_keys = tuple(
        filter(lambda x: Employee._meta.get_field(x).is_relation, necessary_fields)
    )
    for field in necessary_fields:
        field_value = (
            employee.get(field)
            if isinstance(employee, dict)
            else getattr(employee, field)
        )
        employee_dict.update(
            {field: field_value if field not in foreign_keys else str(field_value)}
        )
    return employee_dict


class EmployeeTestCase(TestCase):
    def setUp(self):
        EmployeeRole.objects.get_or_create(
            name="worker",
        )
        EmployeeRole.objects.get_or_create(
            name="manager",
        )

    def test_employee_creation(self):
        """Non-admin users must have all fields except email (email is optional).
        Also, these fields must match pre- and post-creation, while password must differ.
        Created user password must be encrypted"""
        phone_number = "+380981234567"
        password = "example_test_password"
        first_name = "John"
        last_name = "Smith"
        role_name = "worker"
        email = f"wolf@exmaple.com"
        employee = Employee.objects.create_user(
            phone_number=phone_number,
            password=password,
            role_name=role_name,
            first_name=first_name,
            last_name=last_name,
            email=email,
        )
        pre_creation_fields = locals()
        for field, field_value in to_dict(
                employee, fields=("phone_number", "first_name", "last_name", "email")
        ).items():
            self.assertEqual(
                pre_creation_fields.get(field),
                field_value,
                f"Field {field} must is not equal to {field_value}",
            )
        self.assertEqual(
            role := EmployeeRole.objects.get(name=role_name),
            employee.role,
            f"Role {role.name} must be equal to {role_name}",
        )
        self.assertNotEqual(password, employee.password, "Password must be encrypted")
        self.assertTrue(employee.check_password(password))

    def test_admin_creation(self):
        """Admin users must have only phone number and password, which must be encrypted.
        Role must be None, while rest of not mentioned fields must be ''"""
        phone_number = "+380630987654"
        password = "example"
        admin = Employee.objects.create_superuser(
            phone_number=phone_number, password=password
        )
        for field, field_value in admin.__dict__.items():
            if field in ("first_name", "last_name"):
                self.assertEquals(
                    field_value,
                    "",
                    f"Field {field} must be blank, but its value is {field_value}",
                )
            if field in ("email", "role"):
                self.assertIsNone(
                    email := admin.email,
                    f"Field {field} must be blank, actual: {email}",
                )
        self.assertNotEqual(password, admin.password, "Password must be encrypted")

    def test_user_with_no_email_creation(self):
        """Users may register with no email. Test is successful if email is blank"""
        employee = Employee.objects.create_user(
            phone_number="+380990987654",
            password="test test",
            role_name="manager",
            first_name="Yura",
            last_name="Khoma",
        )
        self.assertIsNone(
            email := employee.email, f"Field email must be None, actual: {email}"
        )


class EmployeeTestMixin(TestCase):
    client_class = APIClient
    url = "/employee/"

    def setUp(self):
        Employee.objects.all().delete()
        EmployeeRole.objects.get_or_create(name="worker")
        EmployeeRole.objects.get_or_create(name="manager")
        for index in range(1, 3):
            Employee.objects.create_user(
                phone_number=f"+38063{index}234567",
                password=f"testPass{index}",
                role_name="worker",
                first_name=f"TestName{index}",
                last_name=f"TestSurname{index}",
                email=f"test{index}@example.com",
            )


class TestEmployeeListCreateView(EmployeeTestMixin):
    def test_list_employees(self):
        """Response list must contain all objects that were created and return 200 status code"""
        response = self.client.get(self.url)

        self.assertEqual(
            status_code := response.status_code,
            200,
            f"Status code should be 200, got {status_code}",
        )

        expected_objects = [to_dict(employee) for employee in Employee.objects.all()]
        actual_objects = [dict(employee) for employee in response.data]
        self.assertListEqual(
            expected_objects,
            actual_objects,
            "Objects of present db dataset must be equal to objects returned by get request",
        )

    def test_create_employee(self):
        """Post request must create new object in DB when data is valid, return 201 status code and created object"""
        data = {
            "phone_number": "+380970987654",
            "first_name": "Helen",
            "last_name": "Crain",
            "email": "helen.crain@example.com",
            "role": "manager",
            "password": "somePassword123#(#(",
        }
        response = self.client.post(self.url, data=data)
        self.assertEquals(
            201,
            response_code := response.status_code,
            f"Expected status code 201, got {response_code}",
        )
        response_data = response.data
        for field in data:
            if field == "password":
                continue
            self.assertEquals(
                exptected := data.get(field),
                actual := response_data.get(field),
                f"Field {field}: expected {exptected}, actual {actual}",
            )
        self.assertEquals(
            3, Employee.objects.count(), "Newly created object is not in the DB"
        )


class TestEmployeeRetrieveUpdateDestroyAPIVIew(EmployeeTestMixin):
    @property
    def available_object_id(self) -> int:
        return Employee.objects.first().id

    @property
    def url(self) -> str:
        return super(self.__class__, self).url + str(self.available_object_id)

    def test_request_to_unexisting_id(self):
        response = self.client.get(self.url + "1000")
        self.assertEquals(
            404,
            status_code := response.status_code,
            f"Expected status code 404, got {status_code}",
        )

    def test_retrieve_employee(self):
        """Get request must return employee from db and status code 200"""
        response = self.client.get(self.url)
        expected_employee = to_dict(Employee.objects.get(id=self.available_object_id),
                                    fields=EmployeeDetailsSerializer.Meta.fields)
        actual_employee = to_dict(response.data, fields=EmployeeDetailsSerializer.Meta.fields)
        self.assertEqual(
            200,
            actual_status_code := response.status_code,
            f"Reponse status code must be 200, got {actual_status_code}",
        )
        self.assertEqual(
            expected_employee,
            actual_employee,
            f"Expected {expected_employee}, got {actual_employee}",
        )

    def test_update_employee(self):
        """Put request must return changed employee data and changed password must be hashed. Status code 200"""
        employee_before_put = Employee.objects.get(id=self.available_object_id)
        data = {
            "first_name": "Olena",
            "last_name": "Kulish",
            "phone_number": "+380971234567",
            "role": "manager",
            "password": "hashMeIAmInsecure",
        }
        response = self.client.put(self.url, data=data)
        employee_in_db = Employee.objects.get(id=self.available_object_id)
        self.assertEquals(
            expected := to_dict(data, excluded_fields=("password", "email"), fields=EmployeeDetailsSerializer.Meta.fields),
            actual := to_dict(
                employee_in_db,
                excluded_fields=(
                    "password",
                    "email",
                ), fields=EmployeeDetailsSerializer.Meta.fields
            ),
            f"Employee in db is not the same as request by put. Expected {expected}, got {actual}",
        )
        self.assertEquals(
            "test1@example.com",
            employee_in_db.email,
            "Email must not be changed if not included in request",
        )
        self.assertEquals(
            to_dict(response.data, excluded_fields=("password",), fields=EmployeeDetailsSerializer.Meta.fields),
            actual := to_dict(employee_in_db, excluded_fields=("password",), fields=EmployeeDetailsSerializer.Meta.fields),
            f"Response data must match the data in db. Expected {expected}, got {actual}",
        )
        self.assertNotEquals(
            data.get("password"), employee_in_db.password, "Password must be hashed."
        )
        self.assertEquals(
            200,
            actual_status_code := response.status_code,
            f"Expecrted status code 200, got {actual_status_code}",
        )

    def test_delete_employee(self):
        """Employee must dissapear from db after deletion and status code must be 204"""
        response = self.client.delete(self.url)
        self.assertIsNone(
            Employee.objects.filter(id=self.available_object_id).first(),
            "Employee is still present in the db. It must be deleted",
        )
        self.assertEquals(
            204,
            actual_status_code := response.status_code,
            f"Expected status code 204, got {actual_status_code}",
        )
