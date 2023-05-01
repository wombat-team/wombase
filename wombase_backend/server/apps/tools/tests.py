from server.apps.core.models import Employee
from server.apps.core.tests import (
    AbstractTestMixin,
    AbstractListCreateViewTest,
    AbstractRetrieveUpdateDestroyViewTest,
    AbstractDetailsMixin,
)
from server.apps.tools.models import ToolCategory, Tool
from server.apps.tools.serializers import (
    ToolCategorySerializer,
    ToolDetailSerializer,
    ToolListCreateSerializer,
)


class ToolCategoryTestMixin(AbstractTestMixin):
    url = "/tools/category/"

    def setUp(self):
        ToolCategory.objects.all().delete()
        for category_name in ("Drill", "Screwdriver"):
            ToolCategory.objects.create(
                name=category_name, description=category_name * 2
            )


class TestToolCategoryListCreateAPIView(
    ToolCategoryTestMixin, AbstractListCreateViewTest
):
    serializer = ToolCategorySerializer
    create_data = {"name": "Saw", "description": "Saws"}

    def test_list_tool_category(self):
        self.basic_list_functionality_test()

    def test_create_tool_category(self):
        self.basic_create_functionality_test()


class TestToolCategoryRetrieveUpdateDestroyAPIView(
    ToolCategoryTestMixin, AbstractRetrieveUpdateDestroyViewTest
):
    serializer = ToolCategorySerializer
    update_data = {"name": "Rasp", "description": "Smoothes"}

    def test_request_by_unexisting_id(self):
        self.request_by_unexisting_id()

    def test_retrieve_tool_category(self):
        self.basic_retrieve_functionality_test()

    def test_update_tool_category(self):
        self.basic_update_functionality_test()

    def test_delete_tool_category(self):
        self.basic_delete_functionality_test()


class ToolTestMixin(AbstractTestMixin):
    url = "/tools/"
    employee_id = 0

    def setUp(self):
        Tool.objects.all().delete()
        ToolCategory.objects.create(name="Drill", description="Drills")
        screwdriver = ToolCategory.objects.create(
            name="Screwdriver", description="Screwdrives"
        )
        Employee.objects.all().delete()
        self.employee_id = Employee.objects.create(
            phone_number="+380630987654", password="test"
        ).id
        for index in range(1, 3):
            Tool.objects.create(
                name=f"Screwdriver {index}-B",
                identifier=f"S{index}",
                category=screwdriver,
                description="Screw it!",
                owner_id=self.employee_id,
                currently_at=None,
            )


class TestToolListCreateAPIView(ToolTestMixin, AbstractListCreateViewTest):
    serializer = ToolListCreateSerializer
    create_data = {
        "name": "Drill SD-491 Lviv",
        "identifier": "D-8182",
        "category": "Drill",
        "description": "It works. Kind of",
    }

    def get_create_data(self):
        return {**self.create_data, "owner": self.employee_id}

    def test_get_queryset(self):
        self.query_param_test_set(
            query_param="currently_at",
            param_value="service",
            exptected_queryset_length=0,
        )
        self.query_param_test_set(
            query_param="category",
            param_value="er",
            exptected_queryset_length=2,
        )
        self.query_param_test_set(
            query_param="identifier",
            param_value="1",
            exptected_queryset_length=1,
        )
        self.query_param_test_set(
            query_param="name",
            param_value="rewdriv",
            exptected_queryset_length=2,
        )

    def test_list_tools(self):
        self.basic_list_functionality_test()

    def test_create_tools(self):
        self.basic_create_functionality_test()


class TestToolRetrieveUpdateDestroyAPIView(
    ToolTestMixin, AbstractRetrieveUpdateDestroyViewTest
):
    serializer = ToolDetailSerializer
    update_data = {
        "name": "Drill SD-492 Kyiv",
        "identifier": "D-8182",
        "category": "Drill",
        "description": "It works. Surely",
    }

    def get_update_data(self):
        return {**self.update_data, "owner": self.employee_id}

    def get_update_excluded_fields(self):
        return ("currently_at",)

    def test_request_by_unexisting_id(self):
        self.request_by_unexisting_id()

    def test_retrieve_tool(self):
        self.basic_retrieve_functionality_test()

    def test_update_tool(self):
        self.basic_update_functionality_test()

    def test_delete_tool(self):
        self.basic_delete_functionality_test()


class TestToolTransferReturnMixin(ToolTestMixin, AbstractDetailsMixin):
    serializer = ToolDetailSerializer

    def setUp(self):
        screwdriver = ToolCategory.objects.create(
            name="Screwdriver", description="Screwdrives"
        )
        Employee.objects.all().delete()
        self.giver_employee_id = Employee.objects.create(
            phone_number="+380630987654", password="test"
        ).id
        self.receiver_employeee_id = Employee.objects.create(
            phone_number="+380631234567", password="test"
        ).id
        Tool.objects.create(
            name=f"Screwdriver 1-B",
            identifier=f"S1",
            category=screwdriver,
            description="Screw it!",
            owner_id=self.giver_employee_id,
            currently_at=None,
        )

    def get_url(self) -> str:
        return f"{self.url}{self.available_object_pk}"

    def begin_patch(self, patch_data: dict):
        response = self.client.patch(
            self.get_url(),
            data=patch_data,
        )
        self.request_code_matches_expected_test(
            response=response, expected_status_code=200
        )
        return self.get_available_object()

    def test_patched_tool_not_found(self):
        reponse = self.client.patch(self.get_url() + "1")
        self.request_code_matches_expected_test(
            response=reponse, expected_status_code=404
        )


class TestToolTransferAPIView(TestToolTransferReturnMixin):
    url = "/tools/transfer/"

    def transfer_successful_test(
        self,
        changed_field: str,
        new_field_value: str,
        none_field_name: str,
        changed_field_is_foreign_key: bool = False,
    ):
        tool_after_patch = self.begin_patch(patch_data={changed_field: new_field_value})
        actual_changed_field_value = getattr(tool_after_patch, changed_field)
        if changed_field_is_foreign_key:
            actual_changed_field_value = actual_changed_field_value.pk
        self.assertEquals(
            new_field_value,
            actual_changed_field_value,
            f"Expected {changed_field} to change (to {new_field_value}), "
            f"but it did not (got {actual_changed_field_value})",
        )
        self.assertIsNone(
            none_field_actual_value := getattr(tool_after_patch, none_field_name),
            f"{none_field_name.capitalize()} field must be None after transfer, but is {none_field_actual_value}",
        )

    def test_transfer_tool_to_employee(self):
        self.transfer_successful_test(
            changed_field="owner",
            changed_field_is_foreign_key=True,
            new_field_value=self.receiver_employeee_id,
            none_field_name="currently_at",
        )

    def test_transfer_tool_not_to_employee(self):
        self.transfer_successful_test(
            changed_field="currently_at",
            new_field_value="service",
            none_field_name="owner",
        )

    def test_patch_with_both_fields_none(self):
        response = self.client.patch(f"{self.url}{self.available_object_pk}")
        self.request_code_matches_expected_test(
            response=response, expected_status_code=400
        )

    def test_patch_with_both_fields_not_none(self):
        response = self.client.patch(
            f"{self.url}{self.available_object_pk}",
            data={"owner": 1, "currently_at": 2},
        )
        self.request_code_matches_expected_test(
            response=response, expected_status_code=400
        )


class TestToolReturnAPIView(TestToolTransferReturnMixin):
    url = "/tools/return/"

    def test_tool_return(self):
        tool_after_patch = self.begin_patch(patch_data={})
        self.assertEquals(
            "warehouse",
            tool_after_patch.currently_at,
            "Tool must be returned to warehouse",
        )
        self.assertIsNone(
            tool_after_patch.owner,
            f"After returning tool to warehouse owner must be None",
        )
