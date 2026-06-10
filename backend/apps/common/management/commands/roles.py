from django.core.management.base import BaseCommand

from apps.account.models import UserRole


class Command(BaseCommand):
    help = "Управление ролями"

    def add_arguments(self, parser):
        parser.add_argument(
            "action",
            choices=["create", "list"],
            help='create - создать роли "Сотрудник, Администратор", list - показать все роли',
        )

    def handle(self, *args, **options):
        action = options["action"]

        if action == "create":
            self.create_default_roles()
        elif action == "list":
            self.list_roles()

    def create_default_roles(self):
        """Создать роли"""
        default_roles = ["Сотрудник", "Администратор"]

        for role_name in default_roles:
            role_obj, created = UserRole.objects.get_or_create(name=role_name)

            if created:
                msg = f'Создана роль "{role_obj.name}"'
                self.stdout.write(self.style.SUCCESS(msg))
            else:
                msg = f'Роль "{role_obj.name}" уже существует'
                self.stdout.write(self.style.NOTICE(msg))

    def list_roles(self):
        """Показать все роли"""
        roles = UserRole.objects.all()

        if not roles:
            self.stdout.write(self.style.WARNING("Нет ролей в базе"))
            return

        self.stdout.write(self.style.MIGRATE_HEADING("Список ролей:"))
        for role in roles:
            self.stdout.write(f"\t{role.role_id}. {role.name}")
