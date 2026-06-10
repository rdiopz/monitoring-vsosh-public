from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext


class PasswordValidator:
    """
    Валидатор взятый из django_password_validators (добавил max_length)
    Проверяет минимальную/максимальную длину и наличие цифр, букв, спецсимволов.
    """

    # Разрешённые символы (латиница + цифры + спецсимволы)
    ALLOWED_CHARACTERS = (
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "abcdefghijklmnopqrstuvwxyz"
        "0123456789"
        "~!@#$%^&*()_+-=[]{}|;:',.<>/? "
    )

    def __init__(
        self,
        min_length=8,
        max_length=256,
        min_length_digit=1,
        min_length_alpha=1,
        min_length_special=1,
        min_length_lower=1,
        min_length_upper=1,
        special_characters="~!@#$%^&*()_+-=[]{}|;:',.<>/?",
    ):
        self.min_length = min_length
        self.max_length = max_length
        self.min_length_digit = min_length_digit
        self.min_length_alpha = min_length_alpha
        self.min_length_special = min_length_special
        self.min_length_lower = min_length_lower
        self.min_length_upper = min_length_upper
        self.special_characters = special_characters

    def validate(self, password, user=None):
        errors = []

        # Проверка минимальной длины
        if len(password) < self.min_length:
            errors.append(
                ngettext(
                    "Введённый пароль слишком короткий. Он должен состоять из как минимум %(min_length)d символа.",
                    "Введённый пароль слишком короткий. Он должен состоять из как минимум %(min_length)d символов.",
                    self.min_length,
                )
                % {"min_length": self.min_length}
            )

        # Проверка максимальной длины
        if len(password) > self.max_length:
            errors.append(
                _("Пароль не может быть длиннее %(max_length)d символов.")
                % {"max_length": self.max_length}
            )

        # Проверка цифр
        digit_count = sum(1 for c in password if c.isdigit())
        if digit_count < self.min_length_digit:
            errors.append(
                ngettext(
                    "Пароль должен содержать как минимум %(min_length)d цифру.",
                    "Пароль должен содержать как минимум %(min_length)d цифры.",
                    self.min_length_digit,
                )
                % {"min_length": self.min_length_digit}
            )

        # Проверка букв
        alpha_count = sum(1 for c in password if c.isalpha())
        if alpha_count < self.min_length_alpha:
            errors.append(
                ngettext(
                    "Пароль должен содержать как минимум %(min_length)d букву.",
                    "Пароль должен содержать как минимум %(min_length)d буквы.",
                    self.min_length_alpha,
                )
                % {"min_length": self.min_length_alpha}
            )

        # Проверка заглавных букв
        upper_count = sum(1 for c in password if c.isupper())
        if upper_count < self.min_length_upper:
            errors.append(
                ngettext(
                    "Пароль должен содержать как минимум %(min_length)d заглавную букву.",
                    "Пароль должен содержать как минимум %(min_length)d заглавные буквы.",
                    self.min_length_upper,
                )
                % {"min_length": self.min_length_upper}
            )

        # Проверка строчных букв
        lower_count = sum(1 for c in password if c.islower())
        if lower_count < self.min_length_lower:
            errors.append(
                ngettext(
                    "Пароль должен содержать как минимум %(min_length)d строчную букву.",
                    "Пароль должен содержать как минимум %(min_length)d строчные буквы.",
                    self.min_length_lower,
                )
                % {"min_length": self.min_length_lower}
            )

        # Проверка спецсимволов
        special_count = sum(1 for c in password if c in self.special_characters)
        if special_count < self.min_length_special:
            errors.append(
                ngettext(
                    "Пароль должен содержать как минимум %(min_length)d спецсимвол.",
                    "Пароль должен содержать как минимум %(min_length)d спецсимвола.",
                    self.min_length_special,
                )
                % {"min_length": self.min_length_special}
            )

        # Проверка пробелов
        if " " in password:
            errors.append(_("Пароль не должен содержать пробелы."))

        # Проверка на недопустимые символы
        for c in password:
            if c not in self.ALLOWED_CHARACTERS:
                errors.append(_("Недопустимый символ в пароле: %(symbol)s") % {"symbol": c})

        if errors:
            raise ValidationError(errors)

    def get_help_text(self):
        requirements = [_("минимум %(min_length)d символов") % {"min_length": self.min_length}]
        if self.min_length_alpha:
            requirements.append(
                ngettext(
                    "%(min_length)d буква",
                    "%(min_length)d буквы",
                    self.min_length_alpha,
                )
                % {"min_length": self.min_length_alpha}
            )
        if self.min_length_digit:
            requirements.append(
                ngettext(
                    "%(min_length)d цифра",
                    "%(min_length)d цифры",
                    self.min_length_digit,
                )
                % {"min_length": self.min_length_digit}
            )
        if self.min_length_lower:
            requirements.append(
                ngettext(
                    "%(min_length)d строчная буква",
                    "%(min_length)d строчные буквы",
                    self.min_length_lower,
                )
                % {"min_length": self.min_length_lower}
            )
        if self.min_length_upper:
            requirements.append(
                ngettext(
                    "%(min_length)d заглавная буква",
                    "%(min_length)d заглавные буквы",
                    self.min_length_upper,
                )
                % {"min_length": self.min_length_upper}
            )
        if self.min_length_special:
            requirements.append(
                ngettext(
                    "%(min_length)d спецсимвол",
                    "%(min_length)d спецсимвола",
                    self.min_length_special,
                )
                % {"min_length": self.min_length_special}
            )
        return _("Пароль должен содержать: ") + ", ".join(requirements) + "."
