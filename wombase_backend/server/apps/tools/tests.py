from server.apps.core.tests import (
    AbstractTestMixin,
    AbstractListCreateViewTest,
    AbstractRetrieveUpdateDestroyViewTest,
)
from server.apps.tools.models import ToolCategory, Tool
from server.apps.tools.serializers import ToolCategorySerializer, ToolSerializer
from server.apps.core.models import Employee


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
            )


class TestToolListCreateAPIView(ToolTestMixin, AbstractListCreateViewTest):
    serializer = ToolSerializer
    create_data = {
        "name": "Drill SD-491 Lviv",
        "identifier": "D-8182",
        "category": "Drill",
        "description": "It works. Kind of",
    }

    def get_create_data(self):
        return {**self.create_data, "owner": self.employee_id}

    def test_get_queryset(self):
        self.get_queryset_contains_test()

    def test_list_tools(self):
        self.basic_list_functionality_test()

    def test_create_tools(self):
        self.basic_create_functionality_test()


class TestToolRetrieveUpdateDestroyAPIView(
    ToolTestMixin, AbstractRetrieveUpdateDestroyViewTest
):
    serializer = ToolSerializer
    update_data = {
        "name": "Drill SD-492 Kyiv",
        "identifier": "D-8182",
        "category": "Drill",
        "description": "It works. Surely",
    }

    def get_update_data(self):
        return {**self.update_data, "owner": self.employee_id}

    def test_request_by_unexisting_id(self):
        self.request_by_unexisting_id()

    def test_retrieve_tool(self):
        self.basic_retrieve_functionality_test()

    def test_update_tool(self):
        self.basic_update_functionality_test()

    def test_delete_tool(self):
        self.basic_delete_functionality_test()
