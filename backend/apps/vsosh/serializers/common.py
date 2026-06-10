from rest_framework import serializers


def _add_message(data: dict, view, created_msg, updated_msg):
    """Добавить сообщение об успехе в ответ сериализатора"""
    if view:
        msgs = {
            "create": created_msg,
            "update": updated_msg,
            "partial_update": updated_msg,
        }
        msg = msgs.get(view.action)
        if msg:
            data["message"] = msg


class ExportRequestSerializer(serializers.Serializer):
    """Сериализатор для запроса экспорта с выбором колонок"""

    columns = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="Список колонок для экспорта. Если не указаны, экспортируются все с учётом текущих фильтров.",
    )
