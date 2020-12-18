from django.forms import model_to_dict


class BaseData:
    @property
    def fields(self):
        return self.__dict__.keys()


class BaseORMRepo:
    def _decode(self, orm_model):
        """Decode ORM model to DataClass"""
        return self.data_class(**model_to_dict(orm_model))  # noqa

    def _set_attrs_for_update(self, orm_model, transaction):
        for key, value in transaction.__dict__:
            setattr(orm_model, key, value)

        return orm_model

    def get(self, **kwargs):
        orm_model = self.orm_class.objects.get(**kwargs)  # noqa

        return self._decode(orm_model)

    def create(self, **kwargs):
        self.orm_class.objects.create(**kwargs)  # noqa

    def update(self, data_instance):
        orm_transaction = self.orm_class.objects.get(id=data_instance.id)  # noqa
        orm_transaction = self._set_attrs_for_update(orm_transaction, data_instance)
        orm_transaction.save(update_fields=data_instance.fields)
