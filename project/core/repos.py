from decimal import Decimal
from typing import Union

from asgiref.sync import sync_to_async
from django.db import models
from django.db.models.expressions import F

from project.core.abstract_data_types import AbstractRepo
from project.core.data import BaseData


class ORMRepo(AbstractRepo):
    def _decode(self, orm_model: models.Model) -> BaseData:
        """
        Decode ORM model to DataClass.
        """

        return self.data_class.from_orm(orm_model)

    def _set_attrs_for_update(self, orm_model, data_instance):
        """
        Set all attributes from dataclass model to orm_model for update.
        """
        for field in data_instance.fields:
            # orm_field = f"{field}_id" if field in data_instance._reference else field
            try:
                setattr(orm_model, field, getattr(data_instance, field))
            except ValueError:  # try to represent field as id
                setattr(orm_model, f"{field}_id", getattr(data_instance, field).id)

        return orm_model

    def _get_orm_object(self, with_lock: bool = False, **kwargs):
        """
        Get object from ORM with lock or not.
        """
        if not with_lock:
            orm_model = self.orm_class.objects.get(**kwargs)
        else:
            orm_model = (
                self.orm_class.objects.filter(**kwargs).select_for_update().first()
            )

        return orm_model

    def create(self, **kwargs) -> int:
        """
        Create new object in ORM.
        """
        orm_model = self.orm_class.objects.create(**kwargs)
        return orm_model.id

    def update(self, data_instance: BaseData, with_lock: bool = False) -> int:
        """
        data_instance: DataClass
        with_lock: pass True if you want to use SELECT ... FOR UPDATE in SQL.
        """
        orm_model = self._get_orm_object(id=data_instance.id, with_lock=with_lock)
        orm_model = self._set_attrs_for_update(orm_model, data_instance)
        orm_model.save()

        return orm_model.id

    def get(self, with_lock: bool = False, **kwargs) -> BaseData:
        """
        Get object from ORM and return dataclass instance.
        with_lock: pass True if you want to use SELECT ... FOR UPDATE in SQL.
        """
        orm_model = self._get_orm_object(**kwargs, with_lock=with_lock)

        return self._decode(orm_model)

    def update_incrementally(
        self,
        data_instance: BaseData,
        field: str,
        value: Union[int, Decimal, float],
    ):
        self.orm_class.objects.filter(id=data_instance.id).update(
            **{field: F(field) + value}
        )

    @sync_to_async
    def async_get(self, *args, **kwargs):
        return self.get(*args, **kwargs)

    @sync_to_async
    def async_create(self, **kwargs):
        return self.create(**kwargs)

    @sync_to_async
    def async_update(self, *args, **kwargs):
        return self.update(*args, **kwargs)

    @sync_to_async
    def async_update_incrementally(self, *args, **kwargs):
        return self.update_incrementally(*args, **kwargs)
