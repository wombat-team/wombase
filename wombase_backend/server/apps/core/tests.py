from django.db.models import Model
from django.test import TestCase
from rest_framework.test import APIClient


class AbstractTestMixin(TestCase):
    client_class = APIClient
    serializer = None
    url: str = None

    @property
    def model(self):
        return self.serializer.Meta.model

    @property
    def primary_key(self):
        return self.model._meta.primary_key

    def to_narrowed_dict(
        self,
        instance: Model | dict,
        fields: tuple = (),
        excluded_fields: tuple = (),
        include_blank: bool = True,
    ):
        if not fields:
            fields = self.serializer.Meta.fields
        if not include_blank:
            blank_fields = [
                field.name for field in self.model._meta.fields if field.blank
            ]
        if self.serializer and not isinstance(instance, dict):
            instance = self.serializer(instance).data
        if self.serializer:
            write_only_fields = [
                field_name
                for field_name, field in self.serializer().get_fields().items()
                if field.write_only is True
            ]
        if not isinstance(instance, dict):
            instance = {field: getattr(instance, field) for field in fields}
        excluded_fields = (
            *excluded_fields,
            *(blank_fields if not include_blank else ()),
            *(write_only_fields if self.serializer else ()),
        )
        instance = {
            field: value
            for field, value in instance.items()
            if field in fields and field not in excluded_fields
        }
        return instance

    def request_code_matches_expected_test(self, response, expected_status_code: int):
        self.assertEquals(
            expected_status_code,
            status_code := response.status_code,
            f"Status code must be {expected_status_code}, but got {status_code}",
        )


class AbstractListViewTestMixin(AbstractTestMixin):
    def basic_list_functionality_test(self):
        """Response list must contain all objects that were created and return 200 status code"""
        response = self.client.get(self.url)
        self.request_code_matches_expected_test(
            response=response, expected_status_code=200
        )
        exptected_objects = [
            self.to_narrowed_dict(instance) for instance in self.model.objects.all()
        ]
        actual_objects = [dict(instance) for instance in response.data]
        self.assertListEqual(
            exptected_objects,
            actual_objects,
            "Objects of present db dataset must be equal to objects returned by get request",
        )

    def query_param_test_set(
        self,
        query_param: str,
        exptected_queryset_length: int,
        failure_message: str = "",
        param_value: str = None,
    ):
        response_data = self.client.get(
            f"{self.url}?{query_param}" + (f"={param_value}" if param_value else "")
        ).data
        self.assertEquals(
            exptected_queryset_length,
            element_quantity := len(response_data),
            failure_message
            if failure_message
            else f"{query_param.capitalize()} filtering test failure"
            + f". Expected queryset length {exptected_queryset_length}, got {element_quantity}",
        )
        if not param_value:
            return
        for element in response_data:
            element = dict(element)
            self.assertIn(
                param_value.lower(),
                full_param_value_name := element.get(query_param),
                f"Expected parameter value {param_value} to be in {full_param_value_name}",
            )


class AbstractCreateViewTestMixin(AbstractTestMixin):
    create_data = {}

    def get_create_data(self):
        return self.create_data

    def basic_create_functionality_test(self):
        """Post request must create new object in DB when data is valid, return 201 status code and created object"""
        db_size_before_post = self.model.objects.count()
        create_data = self.get_create_data()
        response = self.client.post(self.url, data=create_data)
        self.request_code_matches_expected_test(
            response=response, expected_status_code=201
        )
        response_data = response.data
        for field in create_data:
            if field == "password":
                continue
            self.assertEquals(
                exptected := create_data.get(field),
                actual := response_data.get(field),
                f"Field {field}: expected {exptected}, actual {actual}",
            )
        self.assertEquals(
            db_size_before_post + 1,
            self.model.objects.count(),
            "Newly created object is not in the DB",
        )


class AbstractListCreateViewTest(
    AbstractListViewTestMixin, AbstractCreateViewTestMixin
):
    ...


class AbstractDetailsMixin(AbstractTestMixin):
    @property
    def available_object_pk(self) -> int:
        return self.model.objects.last().pk

    def get_url(self) -> str:
        return super(self.__class__, self).url + str(self.available_object_pk)

    def get_available_object(self):
        return self.model.objects.get(pk=self.available_object_pk)

    def request_by_unexisting_id(self):
        response = self.client.get(self.get_url() + "1")
        self.request_code_matches_expected_test(
            response=response, expected_status_code=404
        )


class AbstractRetrieveViewMixin(AbstractDetailsMixin):
    def basic_retrieve_functionality_test(self):
        """Get request must return object from db and status code 200"""
        response = self.client.get(self.get_url())
        self.request_code_matches_expected_test(
            response=response, expected_status_code=200
        )
        expected_object = self.to_narrowed_dict(
            self.get_available_object()
        )
        actual_object = self.to_narrowed_dict(response.data)
        self.assertEqual(
            expected_object,
            actual_object,
            f"Expected {expected_object}, got {actual_object}",
        )


class AbstractUpdateViewMixin(AbstractDetailsMixin):
    update_data = {}

    def get_update_excluded_fields(self):
        return ()

    def get_update_data(self):
        return self.update_data

    def basic_update_functionality_test(self):
        """Put request must return changed object data and changed password must be hashed. Status code 200"""
        update_data = self.get_update_data()
        response = self.client.put(self.get_url(), data=update_data)
        object_in_db = self.get_available_object()
        self.request_code_matches_expected_test(
            response=response, expected_status_code=200
        )
        self.assertEquals(
            expected := self.to_narrowed_dict(
                self.get_update_data(),
                include_blank=False,
                excluded_fields=self.get_update_excluded_fields(),
            ),
            actual := self.to_narrowed_dict(
                object_in_db,
                include_blank=False,
                excluded_fields=self.get_update_excluded_fields(),
            ),
            f"Object in db is not the same as in put request. Expected {expected}, got {actual}",
        )
        self.assertEquals(
            self.to_narrowed_dict(response.data),
            actual := self.to_narrowed_dict(object_in_db),
            f"Response data must match the data in db. Expected {expected}, got {actual}",
        )


class AbstractDestroyViewMixin(AbstractDetailsMixin):
    def basic_delete_functionality_test(self):
        """Object must dissapear from db after deletion and status code must be 204"""
        url = self.get_url()
        deleted_object_pk = self.available_object_pk
        response = self.client.delete(url)
        self.request_code_matches_expected_test(
            response=response, expected_status_code=204
        )
        self.assertIsNone(
            self.model.objects.filter(pk=deleted_object_pk).first(),
            "Object is still present in the db. It must be deleted",
        )


class AbstractRetrieveUpdateDestroyViewTest(
    AbstractRetrieveViewMixin,
    AbstractUpdateViewMixin,
    AbstractDestroyViewMixin,
):
    ...
