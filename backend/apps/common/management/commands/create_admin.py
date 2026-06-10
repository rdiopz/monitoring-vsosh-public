from django.contrib.auth import password_validation
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand

from apps.account.models import UserAccount, UserRole


class Command(BaseCommand):
    help = "Создать пользователя с ролью администратора без заявки"

    def add_arguments(self, parser):
        parser.add_argument("--email", help="Почта админа", required=True)
        parser.add_argument("--password", help="Пароль админа", required=True)

    def handle(self, *args, **options):
        admin_role = UserRole.objects.filter(name="Администратор").first()
        email = options.get("email")
        password = options.get("password")

        if not admin_role:
            self.stdout.write(self.style.ERROR('Роли "Админ" не существует'))
            return

        if UserAccount.objects.filter(email=email).exists():
            self.stdout.write(self.style.ERROR(f"Пользователь с почтой {email} уже существует"))
            return

        try:
            user = UserAccount(email=email)
            password_validation.validate_password(password, user=user)
        except ValidationError as e:
            self.stdout.write(self.style.ERROR("\n".join(e.messages)))
            return

        password_hash = make_password(password)

        UserAccount.objects.create(
            email=email,
            password_hash=password_hash,
            role=admin_role,
        )
        self.stdout.write(self.style.SUCCESS(f"Пользователь {email} теперь админ"))
