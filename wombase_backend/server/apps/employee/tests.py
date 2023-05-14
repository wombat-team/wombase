from .models import EmployeeRole
from ..core.models import Employee
from .serializers import EmployeeDetailsSerializer, EmployeeListSerializer
from ..core.tests import (
    AbstractTestMixin,
    AbstractRetrieveUpdateDestroyViewTest,
    AbstractListViewTestMixin, authenticated,
)


class EmployeeCreationTest(AbstractTestMixin):
    model = Employee

    def setUp(self):
        EmployeeRole.objects.get_or_create(
            name="Worker",
        )
        EmployeeRole.objects.get_or_create(
            name="Manager",
        )

    def test_employee_creation(self):
        """Non-admin users must have all fields except email (email is optional).
        Also, these fields must match pre- and post-creation, while password must differ.
        Created user password must be encrypted"""
        phone_number = "+380981234567"
        password = "example_test_password"
        first_name = "John"
        last_name = "Smith"
        role_name = "Worker"
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
        for field, field_value in self.to_narrowed_dict(
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

    def test_employee_with_no_email_creation(self):
        """Users may register with no email. Test is successful if email is blank"""
        employee = Employee.objects.create_user(
            phone_number="+380990987654",
            password="test test",
            role_name="Manager",
            first_name="Yura",
            last_name="Khoma",
        )
        self.assertIsNone(
            email := employee.email, f"Field email must be None, actual: {email}"
        )


@authenticated
class EmployeeTestMixin(AbstractTestMixin):
    url = "/employee/"

    def setUp(self):
        EmployeeRole.objects.get_or_create(name="Worker")
        EmployeeRole.objects.get_or_create(name="Manager")
        for index in range(1, 3):
            Employee.objects.create_user(
                phone_number=f"+38063{index}234567",
                password=f"testPass{index}",
                role_name="Worker",
                first_name=f"TestName{index}",
                last_name=f"TestSurname{index}",
                email=f"test{index}@example.com",
            )

    def tearDown(self):
        Employee.objects.all().delete()


class TestEmployeeListView(EmployeeTestMixin, AbstractListViewTestMixin):
    serializer = EmployeeListSerializer

    def test_list(self):
        return self.basic_list_functionality_test()


class TestEmployeeRetrieveUpdateDestroyAPIView(
    EmployeeTestMixin, AbstractRetrieveUpdateDestroyViewTest
):
    serializer = EmployeeDetailsSerializer
    update_data = {
        "first_name": "Olena",
        "last_name": "Kulish",
        "phone_number": "+380971234567",
        "role": "Manager",
        "password": "hashMeIAmInsecure",
    }

    def test_request_to_unexisting_id(self):
        self.request_by_unexisting_id()

    def test_retrieve_employee(self):
        self.basic_retrieve_functionality_test()

    def test_basic_update_employee(self):
        self.basic_update_functionality_test()

    def test_delete_employee(self):
        self.basic_delete_functionality_test()

    def test_update_no_change_to_blank_email(self):
        available_id = self.available_object_pk
        pre_change_email = self.model.objects.get(id=available_id).email
        self.client.put(self.get_url(), data=self.update_data)
        after_change_email = self.model.objects.get(id=available_id).email
        self.assertEquals(
            pre_change_email,
            after_change_email,
            "Email must not be changed if not included in request",
        )

    def test_update_password_is_hashed(self):
        self.client.put(self.get_url(), data=self.update_data)
        employee_in_db = self.model.objects.get(id=self.available_object_pk)
        self.assertNotEquals(
            self.update_data.get("password"),
            employee_in_db.password,
            "Password must be hashed.",
        )
