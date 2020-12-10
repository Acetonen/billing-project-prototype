from django.conf import settings
from django.db import models
from model_utils.models import TimeStampedModel


class ParentModel(models.Model):
    class Meta:
        abstract = True


class CreateUpdateParentModel(ParentModel):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE,
                                   related_name='created_%(app_label)s_%(class)s_set', editable=False)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE,
                                    related_name='modified_%(app_label)s_%(class)s_set', editable=False)

    class Meta:
        abstract = True


class TimeStampParentModel(ParentModel, TimeStampedModel):
    class Meta:
        abstract = True


class FullParentModel(CreateUpdateParentModel, TimeStampedModel):
    class Meta:
        abstract = True
