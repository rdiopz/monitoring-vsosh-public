import logging

from rest_framework import serializers

logger = logging.getLogger(__name__)


def get_field_error_messages(model_class, field_name, custom_messages=None):
    """
    Возвращает словарь error_messages для поля сериализатора,
    автоматически подставляя verbose_name из модели.
    """
    try:
        model_field = model_class._meta.get_field(field_name)
        verbose_name = getattr(model_field, "verbose_name", field_name)
        max_length = getattr(model_field, "max_length", None)
    except Exception:
        verbose_name = field_name
        max_length = None

    messages = {
        "required": f"Заполните {verbose_name.lower()}",
        "blank": f"{verbose_name} не может быть пустым",
        "null": f"Заполните {verbose_name.lower()}",
    }

    if max_length:
        messages["max_length"] = f"{verbose_name} должно быть не длиннее {max_length} символов"

    if custom_messages:
        messages.update(custom_messages)

    return messages


class FlexibleModelSerializer(serializers.ModelSerializer):
    """
    Базовый сериализатор, который для PATCH запросов делает все поля необязательными.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get("request")
        if request and request.method == "PATCH":
            for field in self.fields.values():
                if not field.read_only:
                    field.required = False
