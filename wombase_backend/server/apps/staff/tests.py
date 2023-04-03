from django.test import TestCase

from server.apps.staff.models import Employee, EmployeeRole


class EmployeeTestCase(TestCase):
    def setUp(self):
        EmployeeRole.objects.create(
            name='worker',
        )
        EmployeeRole.objects.create(
            name='manager',
        )

    def test_employee_creation(self):
        """Non-admin users must have all fields except email (email is optional).
        Also, these fields must match pre- and post-creation, while password must differ.
        Created user password must be encrypted"""
        phone_number = '+380981234567'
        password = 'example_test_password'
        first_name = 'John'
        last_name = 'Smith'
        role_name = 'worker'
        email = f'wolf@exmaple.com'
        employee = Employee.objects.create_user(
            phone_number=phone_number,
            password=password,
            role_name=role_name,
            first_name=first_name,
            last_name=last_name,
            email=email,
        )
        pre_creation_fields = locals()
        for field, field_value in employee.__dict__.items():
            if field in ('phone_number', 'first_name', 'last_name', 'email'):
                self.assertEqual(
                    pre_creation_fields.get(field),
                    field_value,
                    f"Field {field} must is not equal to {field_value}"
                )
        self.assertEqual(
            role := EmployeeRole.objects.get(name=role_name),
            employee.role,
            f"Role {role.name} must be equal to {role_name}"
        )
        self.assertNotEqual(password, employee.password, 'Password must be encrypted')

    def test_admin_creation(self):
        """Admin users must have only phone number and password, which must be encrypted.
        Role must be None, while rest of not mentioned fields must be ''"""
        phone_number = '+380630987654'
        password = 'example'
        admin = Employee.objects.create_superuser(
            phone_number=phone_number,
            password=password
        )
        for field, field_value in admin.__dict__.items():
            if field in ('first_name', 'last_name'):
                self.assertEquals(field_value, '', f"Field {field} must be blank, but its value is {field_value}")
            if field in ('email', 'role'):
                self.assertIsNone(email := admin.email, f"Field {field} must be blank, actual: {email}")
        self.assertNotEqual(password, admin.password, 'Password must be encrypted')

    def test_user_with_no_email_creation(self):
        """Users may register with no email. Test is successful if email is blank"""
        employee = Employee.objects.create_user(
            phone_number='+380990987654',
            password='test test',
            role_name='manager',
            first_name='Yura',
            last_name='Khoma'
        )
        self.assertIsNone(email := employee.email, f"Field email must be blank, actual: {email}")
