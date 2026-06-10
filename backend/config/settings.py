from datetime import timedelta
from pathlib import Path

from celery.schedules import crontab  # type: ignore[import-untyped]
from decouple import Csv, config

# ======================== БАЗОВЫЕ НАСТРОЙКИ ========================
# Базовая директория проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# ======================== БЕЗОПАСНОСТЬ ========================
SECRET_KEY = config("DJANGO_SECRET_KEY")  # Секретный ключ для подписей и шифрования
DEBUG = config("DEBUG", default=False, cast=bool)  # Режим отладки (ВКЛ/ВЫКЛ)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="", cast=Csv())  # Доверенные домены
SECURE_BROWSER_XSS_FILTER = True  # Защита от XSS-атак в браузере
SECURE_CONTENT_TYPE_NOSNIFF = True  # Запрет подмены MIME-типов
X_FRAME_OPTIONS = "DENY"  # Защита от кликджекинга (iframe)

# ======================== БАЗА ДАННЫХ ========================
# Настройки PostgreSQL (https://docs.djangoproject.com/en/5.2/ref/settings/#databases)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME"),
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": config("DB_HOST", "localhost"),
        "PORT": config("DB_PORT", "5432"),
        "OPTIONS": {
            "sslmode": config("DB_SSLMODE", "disable"),  # SSL режим
            # 'options': f"-c search_path={config('DB_SCHEMA', 'public')}"
        },
    }
}
# ======================== REDIS НАСТРОЙКИ ========================
REDIS_URL = config("REDIS_URL", default="redis://localhost:6379/0")
REDIS_SESSION_URL = config("REDIS_SESSION_URL", default="redis://localhost:6379/1")
REDIS_CACHE_URL = config("REDIS_CACHE_URL", default="redis://localhost:6379/2")
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_CACHE_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "IGNORE_EXCEPTIONS": True,
            "SOCKET_CONNECT_TIMEOUT": 5,
            "SOCKET_TIMEOUT": 5,
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 50,
            },
        },
        "KEY_PREFIX": "cache",
        "TIMEOUT": 300,
    },
    "sessions": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_SESSION_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "SOCKET_CONNECT_TIMEOUT": 5,
            "SOCKET_TIMEOUT": 5,
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 100,
            },
        },
        "KEY_PREFIX": "jwt_sessions",
        "TIMEOUT": None,
    },
}

# ======================== ПРИЛОЖЕНИЯ ========================
# Список встроенных Django приложений
DJANGO_APPS = [
    "django.contrib.auth",  # Система аутентификации (нужна для JWT)
    "django.contrib.contenttypes",  # ContentTypes framework (нужен для моделей)
    "django.contrib.staticfiles",  # Статические файлы
]

MIGRATION_MODULES = {
    "admin": None,
    "sessions": None,
    "auth": None,
}

# Список сторонних приложений (установленные через pip)
SECOND_APPS = [
    "django_filters",  # Фильтрация для Django REST
    "corsheaders",  # CORS заголовки для Vue.js фронтенда
    "rest_framework",  # Django REST Framework
    "rest_framework_simplejwt",  # JWT аутентификация
    "drf_yasg",  # Автоматизировать генерацию схем Swagger
    "ipware",  # Для получение IP клиента
]

# Список локальных приложений
LOCAL_APPS = ["apps.vsosh", "apps.account", "apps.common"]

# Объединённый список всех приложений
INSTALLED_APPS = DJANGO_APPS + SECOND_APPS + LOCAL_APPS

# ======================== MIDDLEWARE ========================
# Система «промежуточного слоя» или «плагинов» для глобальной обработки HTTP-запросов и ответов
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # CORS заголовки
    "django.middleware.security.SecurityMiddleware",  # Безопасность
    "django.middleware.common.CommonMiddleware",  # Стандартная обработка запросов
    "django.middleware.clickjacking.XFrameOptionsMiddleware",  # Защита от кликджекинга
]

# ======================== КОНФИГУРАЦИЯ URL И ШАБЛОНОВ ========================
ROOT_URLCONF = "config.urls"  # Главный файл маршрутизации

# Шаблоны (их нет)
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # Пустая
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [],
        },
    },
]

# WSGI приложение для деплоя
WSGI_APPLICATION = "config.wsgi.application"

# ======================== ВАЛИДАЦИЯ ПАРОЛЕЙ ========================
AUTH_PASSWORD_VALIDATORS = [
    # Проверка похожести
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
        "OPTIONS": {
            "user_attributes": ["email"],
            "max_similarity": 0.7,
        },
    },
    # Проверка на простой пароль
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    # Требования к паролю
    {
        "NAME": "apps.common.validators.PasswordValidator",
        "OPTIONS": {
            "min_length": 8,
            "max_length": 256,
            "min_length_digit": 1,
            "min_length_alpha": 1,
            "min_length_special": 1,
            "min_length_lower": 1,
            "min_length_upper": 1,
            "special_characters": "~[!@#$%^&*()_+\\-=\\[\\]{};':\"\\|,.<>/?]",
        },
    },
]

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.BCryptPasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    # 'django.contrib.auth.hashers.Argon2PasswordHasher',
]

# ======================== МЕЖДУНАРОДНЫЕ НАСТРОЙКИ ========================
LANGUAGE_CODE = "ru-ru"  # Язык интерфейса
TIME_ZONE = "Europe/Moscow"  # Часовой пояс "UTC"
USE_I18N = True  # Включение интернационализации
USE_TZ = True  # Использование часовых поясов

# ======================== СТАТИЧЕСКИЕ И МЕДИА ФАЙЛЫ ========================
# URL для доступа к статическим файлам (CSS, JavaScript, изображения)
STATIC_URL = "/static/"
STATIC_ROOT = (
    BASE_DIR / "staticfiles"
)  # Папка для сбора всех статических файлов командой collectstatic
STATICFILES_DIRS = []  # Дополнительные папки со статическими файлами

# Если существует общая папка static в проекте - добавляем её
if (BASE_DIR / "static").exists():
    STATICFILES_DIRS.append(BASE_DIR / "static")

# URL для доступа к медиафайлам
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / config("MEDIA_ROOT", "media")  # Папка для хранения загруженных файлов

# ======================== ОСНОВНЫЕ НАСТРОЙКИ МОДЕЛЕЙ ========================
# Стандартный тип первичного ключа для моделей
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ======================== JWT НАСТРОЙКИ ========================
SIMPLE_JWT = {
    # Время жизни токенов
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=config("JWT_ACCESS_TOKEN_LIFETIME_MINUTES", default=60, cast=int)
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        days=config("JWT_REFRESH_TOKEN_LIFETIME_DAYS", default=7, cast=int)
    ),
    # Безопасность токенов
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": False,
    # Алгоритмы и ключи
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,
    # Заголовки
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    # Поля пользователя
    "USER_ID_FIELD": "user_id",
    "USER_ID_CLAIM": "user_id",
    # Идентификатор токена
    "JTI_CLAIM": "jti",
}

JWT_SESSION_SETTINGS = {
    "REVOKED_SESSION_TTL": 7 * 24 * 3600,  # 7 дней
}

# ======================== DJANGO REST FRAMEWORK ========================
REST_FRAMEWORK = {
    # Классы аутентификации (JWT tokens)
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "apps.account.authentication.CustomJWTAuthentication",
    ],
    # Классы разрешений (только авторизованные пользователи)
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    # Рендереры (JSON всегда, BrowsableAPI только при DEBUG)
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ]
    + (["rest_framework.renderers.BrowsableAPIRenderer"] if DEBUG else []),
    # Парсеры
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",  # JSON данные
        "rest_framework.parsers.MultiPartParser",  # Form-data (файлы)
        "rest_framework.parsers.FormParser",  # Form-urlencoded
    ],
    # Фильтр, Поиск, Сортировка
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    # Ограничение запросов (защита от DDoS)
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",  # Для анонимных пользователей
        "rest_framework.throttling.UserRateThrottle",  # Для авторизованных пользователей
    ],
    # Пагинация (разбивка на страницы)
    "DEFAULT_PAGINATION_CLASS": "apps.common.pagination.CustomPageNumberPagination",
    # Лимиты запросов
    "DEFAULT_THROTTLE_RATES": {
        "anon": "800/hour",
        "user": "1500/hour",
    },
    # Обработка исключений
    "EXCEPTION_HANDLER": "apps.common.exceptions.custom_exception_handler",
    # Форматы дат
    "DATETIME_FORMAT": "%Y-%m-%dT%H:%M:%S%z",
    "DATE_FORMAT": "%Y-%m-%d",
    "TIME_FORMAT": "%H:%M:%S",
}

# ======================== CELERY НАСТРОЙКИ ========================
CELERY_BROKER_URL = config("CELERY_BROKER_URL", default="redis://localhost:6379/0")
CELERY_RESULT_BACKEND = config("CELERY_RESULT_BACKEND", default="redis://localhost:6379/0")
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 минут
CELERY_RESULT_EXPIRES = 3600
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# Celery Beat настройки для периодических задач
CELERY_BEAT_SCHEDULE = {
    "cleanup-stale-jti-daily": {
        "task": "apps.account.tasks.cleanup_stale_jti",
        "schedule": crontab(hour=4, minute=0),  # Каждый день в 04:00
    },
    "cleanup-applications-daily": {
        "task": "apps.account.tasks.cleanup_applications",
        "schedule": crontab(hour=4, minute=30),  # Каждый день в 04:30
    },
    "cleanup-audit-logs-weekly": {
        "task": "apps.account.tasks.cleanup_audit_logs",
        "schedule": crontab(hour=3, minute=0, day_of_week=1),  # Каждый понедельник в 03:00
    },
}

# ======================== ЛОГИРОВАНИЕ В КОНСОЛЬ И В ФАЙЛ========================
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "debug.log",
        },
        "console": {
            "level": "DEBUG" if DEBUG else "INFO",
            "class": "logging.StreamHandler",
        },
        "redis_handler": {
            "level": "ERROR",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file", "console"],
            "level": "INFO",
            "propagate": True,
        },
        "apps": {
            "handlers": ["file", "console"],
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
        "celery": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": True,
        },
    },
}
# ======================== CORS (Cross-Origin Resource Sharing) ========================
CORS_ALLOW_ALL_ORIGINS = DEBUG

# Если не разрешены все источники - загружаем список разрешённых
if not DEBUG:
    CORS_ALLOWED_ORIGINS = config("CORS_ALLOWED_ORIGINS", default="", cast=Csv())

# Дополнительные CORS настройки
CORS_ALLOW_CREDENTIALS = True  # Разрешить cookies, authorization headers
CORS_ALLOW_METHODS = [  # Разрешённые HTTP методы
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]
CORS_ALLOW_HEADERS = [  # Разрешённые заголовки
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-requested-with",
    "cache-control",  # Для кэширования
    "pragma",  # Для кэширования (старый стандарт)
    "if-modified-since",  # Для условных запросов
    "content-disposition",  # Для скачивания файлов
    "content-range",  # Для загрузки больших файлов по частям
]
# ======================== DJANGO IPWARE ========================
# Настройки для определения IP-адреса клиента через прокси
if DEBUG:
    IPWARE_PROXY_TRUSTED_IPS = [
        "127.0.0.1",  # localhost
        "localhost",
        "10.0.0.0/8",  # Docker сети
        "172.16.0.0/12",
        "192.168.0.0/16",
    ]
else:
    IPWARE_PROXY_TRUSTED_IPS = [  # (docker network inspect)
        "10.0.0.0/8",  # Docker сети
        "172.16.0.0/12",
        "192.168.0.0/16",
    ]

# ======================== Swagger ========================

SWAGGER_SETTINGS = {
    "USE_SESSION_AUTH": False,
    "SECURITY_DEFINITIONS": {"Bearer": {"type": "apiKey", "name": "Authorization", "in": "header"}},
}

# ======================== НАСТРОЙКИ РАЗРАБОТКИ ========================
if DEBUG:
    # Debug Toolbar
    INSTALLED_APPS += ["debug_toolbar"]
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")
    INTERNAL_IPS = ["127.0.0.1", "localhost", "172.18.0.1"]

    # Показывать SQL запросы в консоли
    LOGGING["loggers"]["django.db.backends"] = {  # type: ignore[index]
        "level": "DEBUG" if DEBUG else "INFO",
        "handlers": ["console"],
        "propagate": False,
    }
    try:
        import redis

        r = redis.from_url(REDIS_URL)
        r.ping()
        print(f"[Redis] подключен: {REDIS_URL}")
    except redis.ConnectionError:
        print(f"[Redis] НЕ подключен: {REDIS_URL}")
