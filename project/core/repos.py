from decimal import Decimal
from typing import Union

from django.db import models
from django.db.models.expressions import F
from django.forms import model_to_dict

from project.core.abstract_data_types import AbstractRepo, AbstractData


class ORMRepo(AbstractRepo):
    def _decode(self, orm_model: models.Model) -> AbstractData:
        """
        Decode ORM model to DataClass.
        """
        return self.data_class(**model_to_dict(orm_model))  # noqa

    def _set_attrs_for_update(self, orm_model, data_instance):
        """
        Set all attributes from dataclass model to orm_model for update.
        """
        for field in data_instance.fields:
            setattr(orm_model, field, getattr(data_instance, field))

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

    def update(self, data_instance: AbstractData, with_lock: bool = False) -> int:
        """
        data_instance: DataClass
        with_lock: pass True if you want to use SELECT ... FOR UPDATE in SQL.
        """
        orm_model = self._get_orm_object(id=data_instance.id, with_lock=with_lock)
        orm_model = self._set_attrs_for_update(orm_model, data_instance)
        orm_model.save()

        return orm_model.id

    def get(self, with_lock: bool = False, **kwargs) -> AbstractData:
        """
        Get object from ORM and return dataclass instance.
        with_lock: pass True if you want to use SELECT ... FOR UPDATE in SQL.
        """
        orm_model = self._get_orm_object(**kwargs, with_lock=with_lock)

        return self._decode(orm_model)

    def update_incrementally(
        self,
        data_instance: AbstractData,
        field: str,
        value: Union[int, Decimal, float],
    ):
        self.orm_class.objects.filter(id=data_instance.id).update(
            **{field: F(field) + value}
        )
