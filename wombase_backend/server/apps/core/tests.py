from django.db.models import Model
from django.test import TestCase


class AbstractTestMixin(TestCase):
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


class AbstractListCreateViewTest(AbstractTestMixin):
    creation_data = {}

    def list_test_method(self):
        """Response list must contain all objects that were created and return 200 status code"""
        response = self.client.get(self.url)

        self.assertEqual(
            status_code := response.status_code,
            200,
            f"Status code should be 200, got {status_code}",
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

    def create_test_method(self):
        """Post request must create new object in DB when data is valid, return 201 status code and created object"""
        response = self.client.post(self.url, data=self.creation_data)
        self.assertEquals(
            201,
            response_code := response.status_code,
            f"Expected status code 201, got {response_code}",
        )
        response_data = response.data
        for field in self.creation_data:
            if field == "password":
                continue
            self.assertEquals(
                exptected := self.creation_data.get(field),
                actual := response_data.get(field),
                f"Field {field}: expected {exptected}, actual {actual}",
            )
        self.assertEquals(
            3, self.model.objects.count(), "Newly created object is not in the DB"
        )


class AbstractRetrieveUpdateDestroyViewTest(AbstractTestMixin):
    update_data = {}

    @property
    def available_object_pk(self) -> int:
        return self.model.objects.last().pk

    def get_url(self) -> str:
        return super(self.__class__, self).url + str(self.available_object_pk)

    def request_by_unexisting_id(self):
        response = self.client.get(self.get_url() + "1")
        self.assertEquals(
            404,
            status_code := response.status_code,
            f"Expected status code 404, got {status_code}",
        )

    def retrieve_test_method(self):
        """Get request must return object from db and status code 200"""
        response = self.client.get(self.get_url())
        expected_object = self.to_narrowed_dict(
            self.model.objects.get(pk=self.available_object_pk)
        )
        actual_object = self.to_narrowed_dict(response.data)
        self.assertEqual(
            200,
            actual_status_code := response.status_code,
            f"Reponse status code must be 200, got {actual_status_code}",
        )
        self.assertEqual(
            expected_object,
            actual_object,
            f"Expected {expected_object}, got {actual_object}",
        )

    def update_test_method(self):
        """Put request must return changed object data and changed password must be hashed. Status code 200"""
        response = self.client.put(self.get_url(), data=self.update_data)
        object_in_db = self.model.objects.get(pk=self.available_object_pk)
        self.assertEquals(
            expected := self.to_narrowed_dict(self.update_data, include_blank=False),
            actual := self.to_narrowed_dict(object_in_db, include_blank=False),
            f"Object in db is not the same as in put request. Expected {expected}, got {actual}",
        )
        self.assertEquals(
            self.to_narrowed_dict(response.data),
            actual := self.to_narrowed_dict(object_in_db),
            f"Response data must match the data in db. Expected {expected}, got {actual}",
        )
        self.assertEquals(
            200,
            actual_status_code := response.status_code,
            f"Expecrted status code 200, got {actual_status_code}",
        )

    def delete_test_method(self):
        """Object must dissapear from db after deletion and status code must be 204"""
        url = self.get_url()
        deleted_object_pk = self.available_object_pk
        response = self.client.delete(url)
        self.assertIsNone(
            self.model.objects.filter(pk=deleted_object_pk).first(),
            "Object is still present in the db. It must be deleted",
        )
        self.assertEquals(
            204,
            actual_status_code := response.status_code,
            f"Expected status code 204, got {actual_status_code}",
        )
