class Roles:
    """Роли пользователей"""

    ADMINISTRATOR = "Администратор"
    STAFF = "Сотрудник"


class Errors:
    """Сообщения об ошибках"""

    # Регистрация
    INVALID_CODE = "Неверный код регистрации"
    CODE_LENGTH = "Код должен быть от 6 до 24 символов"

    # Настройки
    MONITORING_YEARS_FORMAT = "Формат: ГГГГ-ГГГГ (например, 2022-2025)"
    MONITORING_YEARS_ORDER = "Первый год должен быть меньше второго"
    CLEANUP_DAYS_INVALID = "Число должно быть ≥ 1"
    AUDIT_RETENTION_DAYS_INVALID = "Число должно быть ≥ 30"

    # Email
    INVALID_EMAIL = "Некорректный email"
    EMAIL_REGISTERED = "Email уже зарегистрирован"
    PENDING_APPLICATION = "Заявка уже подана"

    # Рассмотрение заявки
    ROLE_REQUIRED_FOR_APPROVAL = "При одобрении заявки необходимо указать роль"
    ROLE_NOT_FOUND = "Роль с указанным ID не найдена"

    # Пароли
    PASSWORDS_MISMATCH = "Пароли не совпадают"
    PASSWORD_TOO_WEAK = (
        "Пароль должен:\n"
        "• Содержать только латинские буквы, цифры и спецсимволы\n"
        "• Иметь хотя бы одну заглавную букву (A-Z)\n"
        "• Иметь хотя бы одну строчную букву (a-z)\n"
        "• Иметь хотя бы одну цифру (0-9)\n"
        "• Иметь хотя бы один спецсимвол\n"
        "• Быть от 8 до 256 символов\n"
        "• Не содержать пробелов"
    )
    INVALID_PASSWORD = "Неверный текущий пароль"
    PASSWORD_DIFFERENT = "Новый пароль должен отличаться от старого"

    # Логин
    ACCOUNT_BLOCKED = "Аккаунт заблокирован. Обратитесь к администратору."
    INVALID_CREDENTIALS = "Неверные учетные данные"
    USER_NOT_FOUND = "Пользователь не найден"

    # Токены
    TOKEN_INVALID = "Токен недействителен или истёк. Войдите в систему заново."
    REFRESH_TOKEN_NOT_FOUND = "Сессия не найдена. Пожалуйста, войдите в систему заново."

    # Сессии
    SESSION_NOT_FOUND = "Сессия не найдена"
    SESSION_NOT_ACTIVE = "Сессия завершена"
    SESSION_ACTIVE = "Сессия активна"
    FINGERPRINT_MISMATCH = "Отпечаток не соответствует"
    CANNOT_REVOKE_CURRENT_SESSION = "Нельзя завершить текущую сессию"
    SESSION_REVOKED_OR_NOT_FOUND = "Сессия не найдена или уже завершена"

    # Заблокировать свой же аккаунт
    CANNOT_ACT_ON_SELF = "Запрещено выполнять это действие для своего аккаунта"
    CANNOT_REVOKE_SESSIONS_BY_FP = "Нельзя завершать сессии по собственному отпечатку"

    # Unique-ограничения моделей
    USER_ROLE_EXISTS = "Роль с таким названием уже существует"
    USER_EMAIL_EXISTS = "Email уже зарегистрирован"
    APPLICATION_EMAIL_EXISTS = "Заявка с таким email уже существует"
    SYSTEM_SETTING_KEY_EXISTS = "Настройка с таким ключом уже существует"

    QUERY_INT_PARAM = "Ожидается целое число, получено: {value}"


class Messages:
    """Сообщения об успехе"""

    # Регистрация
    CODE_VALID = "Код верный"
    APPLICATION_CREATED = "Успешно подана заявка"

    # Логин
    LOGIN_SUCCESS = "Успешный вход"
    TOKEN_REFRESHED = "Токен успешно обновлен"

    # Сессии
    LOGOUT_SUCCESS = "Вы успешно вышли из системы"
    SESSION_TERMINATED = "Сессия завершена"
    SESSIONS_REVOKED = "Завершено {count} сессий"

    # Пароль
    PASSWORD_CHANGED = "Пароль успешно изменён"

    # Заявка
    APPLICATION_REVIEWED = "Заявка {result}"

    # Настройка
    SETTING_UPDATE = "Настройка успешно изменена"


class RevokeReasons:
    """Причины отзыва сессии"""

    LOGOUT = "выход"
    UPDATE = "обновление токенов"
    FINGERPRINT_CHANGED = "смена устройства"
    PASSWORD_CHANGED = "смена пароля"
    REVOKE_ALL = "все сессии"
    REVOKE_OTHER = "отзыв"
    REVOKE_OTHERS = "другие сессии"
