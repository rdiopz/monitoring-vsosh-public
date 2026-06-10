from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from apps.account.models import SystemSetting


class Command(BaseCommand):
    help = "Управление системными настройками (set/get/list/default)"

    DEFAULT_SETTINGS = {
        "registration_code": {
            "value": "424242",
            "description": "Код для регистрации. Формат: 6–24 символов. Пример: 42onfim42",
        },
        "monitoring_years": {
            "value": "2022-2025",
            "description": "Период мониторинга в заголовке. Формат: ГГГГ-ГГГГ. Пример: 2022-2025",
        },
        "application_cleanup_days": {
            "value": "3",
            "description": "Удаление отклонённых заявок (дней). Формат: целое ≥ 1. Пример: 3",
        },
        "audit_log_retention_days": {
            "value": "90",
            "description": "Срок хранения логов аудита (дней). Формат: целое ≥ 30. Пример: 90",
        },
    }

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="action", required=True)

        set_parser = subparsers.add_parser("set", help="Установить настройку")
        set_parser.add_argument("--key", required=True, help="Ключ настройки")
        set_parser.add_argument("--value", required=True, help="Значение")
        set_parser.add_argument("--desc", default="", help="Описание")

        get_parser = subparsers.add_parser("get", help="Получить настройку")
        get_parser.add_argument("--key", required=True, help="Ключ настройки")

        subparsers.add_parser("list", help="Список всех настроек")

        default_parser = subparsers.add_parser("default", help="Создать дефолтные настройки")
        default_parser.add_argument("--key", help="Ключ для создания одной настройки")

    def handle(self, *args, **options):
        action_handlers = {
            "set": self.handle_set,
            "get": self.handle_get,
            "list": lambda _: self.handle_list(),
            "default": self.handle_default,
        }

        handler = action_handlers.get(options["action"])
        handler(options)

    def handle_set(self, options):
        """Установка или обновление настройки"""
        key = options.get("key")
        value = options.get("value")
        description = options.get("desc")

        setting, created = SystemSetting.objects.update_or_create(
            key=key, defaults={"value": value, "description": description}
        )

        status = "создана" if created else "обновлена"
        self.stdout.write(self.style.SUCCESS(f"Настройка {status}"))
        self.show_setting_detail(setting)

    def handle_get(self, options):
        """Получение значения настройки по ключу"""
        key = options.get("key")

        try:
            setting = SystemSetting.objects.get(key=key)
            self.show_setting_detail(setting)
        except ObjectDoesNotExist:
            self.stdout.write(self.style.WARNING(f'Настройка "{key}" не найдена'))

    def handle_list(self):
        """Вывод всех настроек"""
        settings = SystemSetting.objects.all()

        if not settings.exists():
            self.stdout.write(self.style.WARNING("Нет сохраненных настроек"))
            return

        self.stdout.write(self.style.MIGRATE_HEADING("Системные настройки:"))
        for setting in settings:
            self.show_setting_detail(setting)

    def handle_default(self, options):
        """Создание настройки по умолчанию"""
        key = options.get("key")
        if key:
            self.create_single_default(key)
        else:
            self.create_all_defaults()

    def create_single_default(self, key):
        """Создать или вернуть к исходному состоянию значение и описание ключа"""
        if key not in self.DEFAULT_SETTINGS:
            self.stderr.write(self.style.ERROR(f"Нет дефолтной настройки для ключа: {key}"))
            return

        data = self.DEFAULT_SETTINGS[key]
        setting, created = SystemSetting.objects.update_or_create(key=key, defaults=data)

        status = "создана" if created else "обновлена"
        self.stdout.write(self.style.SUCCESS(f"Настройка {status}"))
        self.show_setting_detail(setting)

    def create_all_defaults(self):
        """Создать все дефолтные настройки"""
        created_count = 0
        existing_count = 0

        for key, data in self.DEFAULT_SETTINGS.items():
            _, created = SystemSetting.objects.update_or_create(key=key, defaults=data)

            if created:
                created_count += 1
                self.stdout.write(f"Создана: {key}")
            else:
                existing_count += 1
                self.stdout.write(f"Существует: {key}")

        total = created_count + existing_count
        self.stdout.write(
            self.style.SUCCESS(
                f"Готово! Создано: {created_count}, существует: {existing_count}, всего: {total}"
            )
        )

    def show_setting_detail(self, setting):
        """Показать детали настройки"""
        self.stdout.write(
            f"{setting.setting_id}. {self.style.SQL_FIELD(setting.key)} = {setting.value}"
        )
        self.stdout.write(f"– Описание = {setting.description}")
        self.stdout.write(f"– Обновлен = {setting.updated_at}")
