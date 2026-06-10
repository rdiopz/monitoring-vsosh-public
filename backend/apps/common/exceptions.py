from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from rest_framework.exceptions import NotFound
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """Переводит ошибки Django на русский"""

    # Django Http404
    if isinstance(exc, (Http404, ObjectDoesNotExist)):
        exc = NotFound("Объект не найден")

    return exception_handler(exc, context)
