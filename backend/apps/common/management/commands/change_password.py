from django.contrib.auth import password_validation
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand

from apps.account.models import UserAccount


class Command(BaseCommand):
    help = "Изменить пароль любого пользователя"

    def add_arguments(self, parser):
        parser.add_argument("--email", help="Почта пользователя", required=True)
        parser.add_argument("--newPass", help="Новый пароль", required=True)

    def handle(self, *args, **options):
        email = options.get("email")
        password = str(options.get("newPass"))

        if not UserAccount.objects.filter(email=email).exists():
            self.stdout.write(self.style.ERROR(f"Пользователь с почтой {email} не существует"))
            return

        try:
            user = UserAccount(email=email)
            password_validation.validate_password(password, user=user)
        except ValidationError as e:
            self.stdout.write(self.style.ERROR("\n".join(e.messages)))
            return

        password_hash = make_password(password)

        UserAccount.objects.update(
            password_hash=password_hash,
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Пользователь {email} теперь имеет такой хэш пароля {password_hash}"
            )
        )
