from server.apps.core.models import Employee
from server.apps.core.tests import (
    AbstractTestMixin,
    AbstractListCreateViewTest,
    AbstractRetrieveUpdateDestroyViewTest,
    AbstractDetailsMixin,
    authenticated,
)
from server.apps.tools.models import ToolCategory, Tool
from server.apps.tools.serializers import (
    ToolCategorySerializer,
    ToolDetailSerializer,
    ToolListCreateSerializer,
    ToolHistorySerializer,
)


class ToolCategoryTestMixin(AbstractTestMixin):
    url = "/tools/category/"

    def setUp(self):
        for category_name in ("Drill", "Screwdriver"):
            ToolCategory.objects.create(
                name=category_name, description=category_name * 2
            )

    def tearDown(self):
        ToolCategory.objects.all().delete()


@authenticated
class TestToolCategoryListCreateAPIView(
    ToolCategoryTestMixin, AbstractListCreateViewTest
):
    serializer = ToolCategorySerializer
    create_data = {"name": "Saw", "description": "Saws"}

    def test_list_tool_category(self):
        self.basic_list_functionality_test()

    def test_create_tool_category(self):
        self.basic_create_functionality_test()


@authenticated
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
        ToolCategory.objects.get_or_create(name="Drill", description="Drills")
        screwdriver = ToolCategory.objects.get_or_create(
            name="Screwdriver", description="Screwdrives"
        )[0]
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

    def tearDown(self):
        for cls in (Tool, Employee, ToolCategory):
            cls.objects.all().delete()


@authenticated
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


@authenticated
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

    def get_update_excluded_fields(self):
        return ("currently_at", "owner")

    def test_request_by_unexisting_id(self):
        self.request_by_unexisting_id()

    def test_retrieve_tool(self):
        self.basic_retrieve_functionality_test()

    def test_update_tool(self):
        self.basic_update_functionality_test()

    def test_delete_tool(self):
        self.basic_delete_functionality_test()


@authenticated
class TestToolTransferAPIView(ToolTestMixin, AbstractDetailsMixin):
    url = "/tools/transfer/"
    serializer = ToolDetailSerializer

    def setUp(self):
        screwdriver = ToolCategory.objects.get_or_create(
            name="Screwdriver", description="Screwdrives"
        )[0]
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

    def transfer_to_same_destination_test(self, is_person: bool = None):
        tool = self.get_available_object()
        pk = tool.pk
        if not is_person:
            setattr(tool, "currently_at", Tool.DEFAULT_PLACE)
            setattr(tool, "owner", None)
            tool.save()
        response = self.client.patch(
            f"{self.url}{pk}",
            data={
                "owner"
                if is_person
                else "currently_at": tool.owner.id
                if is_person
                else tool.currently_at
            },
        )
        self.request_code_matches_expected_test(
            response=response, expected_status_code=400
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

    def test_patched_tool_not_found(self):
        response = self.client.patch(self.get_url() + "1")
        self.request_code_matches_expected_test(
            response=response, expected_status_code=404
        )

    def test_transfer_tool_to_same_owner(self):
        self.transfer_to_same_destination_test(is_person=True)

    def test_transfer_tool_to_same_place(self):
        self.transfer_to_same_destination_test(is_person=False)


@authenticated
class TestToolChangesHistoryAPIView(ToolTestMixin, AbstractDetailsMixin):
    url = "/tools/history/"
    serializer = ToolHistorySerializer

    @property
    def available_object_pk(self) -> int:
        return Tool.objects.last().pk

    @property
    def transfer_url(self):
        return f"/tools/transfer/{self.available_object_pk}"

    @property
    def put_url(self):
        return f"/tools/{self.available_object_pk}"

    def test_history_record_is_created(self):
        self.client.patch(self.transfer_url, data={"currently_at": "service"})
        response = self.client.get(self.url)
        self.request_code_matches_expected_test(response, 200)
        response_data = response.data
        self.assertEquals(1, len(response_data), "Hisorical record is not created")

    def test_put_doesnt_create_records(self):
        self.client.put(
            self.put_url, data=TestToolRetrieveUpdateDestroyAPIView.update_data
        )
        response = self.client.get(self.url)
        self.request_code_matches_expected_test(response, 200)
        response_data = response.data
        self.assertEquals(
            0,
            len(response_data),
            "Hisorical record is created while doing put, but must not be created",
        )
