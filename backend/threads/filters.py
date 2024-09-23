import django_filters
from django.contrib.auth.models import User
from django_filters import filterset
from threads.models import Thread


class ThreadFilter(filterset.FilterSet):
    participants = django_filters.ModelMultipleChoiceFilter(
        queryset=User.objects.all(),
        field_name='participants__id',
        to_field_name='id',
        conjoined=False,
    )

    class Meta:
        model = Thread
        fields = ['participants']
