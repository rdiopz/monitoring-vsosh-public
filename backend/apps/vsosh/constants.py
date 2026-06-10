class Errors:
    """Сообщения об ошибках для модуля VSOSH"""

    # Муниципалитет
    MUNICIPALITY_EXISTS = "Муниципалитет с таким названием уже существует"
    MUNICIPALITY_IN_USE = (
        "Невозможно удалить: муниципалитет используется в образовательных учреждениях"
    )

    # Предмет
    SUBJECT_EXISTS = "Предмет с таким полным названием уже существует"
    SUBJECT_SHORT_EXISTS = "Предмет с таким кратким названием уже существует"
    SUBJECT_IN_USE = "Невозможно удалить: предмет используется в участиях в олимпиадах"

    # Образовательное учреждение
    INSTITUTION_EXISTS = (
        "Образовательное учреждение с таким названием уже существует в данном муниципалитете"
    )
    INSTITUTION_IN_USE = "Невозможно удалить: учреждение используется в участиях в олимпиадах"

    # Участник
    PARTICIPANT_DATE_INVALID = "Некорректная дата рождения. Укажите дату с 1950 года по текущую."
    PARTICIPANT_IN_USE = "Невозможно удалить: участник используется в участиях в олимпиадах"
    PARTICIPANT_NOT_SPECIFIED = (
        "Укажите либо существующего участника либо введите личные данные участника"
    )

    # Участие в олимпиадах
    PARTICIPANT_REQUIRED = "Необходимо указать участника или данные участника"
    PARTICIPATION_EXIST = "Участие с таким участником, предметом, этапом и годом уже существует"
    PARTICIPANT_CLASS_INVALID = "Некорректный класс (допустимо: 1-11)"
    PARTICIPATION_YEAR_INVALID = "Некорректный год олимпиады"
    PARTICIPATION_DATE_INVALID = (
        "Некорректная дата рождения участника. Укажите дату с 1950 года по текущую."
    )

    # Отчёты
    REPORT_NOT_FOUND = "Отчёт '{report_key}' не найден"

    # Импорт/Экспорт
    IMPORT_FILE_REQUIRED = "Необходимо загрузить файл"
    IMPORT_INVALID_FORMAT = (
        "Не удалось прочитать файл. Проверьте, что файл не повреждён и имеет формат XLSX или CSV."
    )
    IMPORT_CSV_ENCODING_ERROR = (
        "Не удалось прочитать CSV-файл. "
        "Сохраните файл в кодировке UTF-8 или Windows-1251 и попробуйте снова."
    )
    EXPORT_NO_DATA = "Нет данных для экспорта"
    WORKSHEET_NOT_CREATED = "Не удалось создать рабочий лист"

    # Ошибки импорта (шаблоны)
    IMPORT_REQUIRED_FIELDS = "Строка {row_num}: Обязательные поля отсутствуют: {fields}"
    IMPORT_FIELD_TOO_LONG = (
        "Строка {row_num}: '{field}' превышает {max_len} символов (текущая: {length})"
    )
    IMPORT_BIRTH_DATE_INVALID = (
        "Строка {row_num}: некорректная дата рождения. Допустимо с {min_year} года по текущую."
    )
    IMPORT_STAGE_INVALID = "Строка {row_num}: Неверный этап '{value}'. Допустимые: {allowed}"
    IMPORT_STATUS_INVALID = "Строка {row_num}: Неверный статус '{value}'. Допустимые: {allowed}"
    IMPORT_CLASS_INVALID = "Строка {row_num}: Класс должен быть от {min} до {max}"
    IMPORT_YEAR_INVALID = "Строка {row_num}: Год должен быть не менее {min_year}"
    IMPORT_INSTITUTION_NOT_FOUND = "Образовательное учреждение '{name}' не найдено"
    IMPORT_SUBJECT_NOT_FOUND = "Предмет '{name}' не найден"
    IMPORT_MUNICIPALITY_MISMATCH = (
        "Муниципалитет '{municipality}' не соответствует учреждению '{institution}'"
    )
    IMPORT_MAX_ROWS_EXCEEDED = (
        "Превышен лимит строк. Файл содержит {actual_rows} строк, максимально допустимо {max_rows}"
    )
    IMPORT_GENDER_INVALID = (
        "Строка {row_num}: Неверное значение пола '{gender}'. Допустимо: {allowed}"
    )
    IMPORT_GENDER_REQUIRED = "Строка {row_num}: Пол обязателен. Допустимо: {allowed}"

    # Подсказки при импорте
    SUGGEST_DID_YOU_MEAN = "Строка {row_num}: '{name}' не найдено. Возможно, вы имели в виду: '{suggestion}' (регистр не важен)"
    SUGGEST_ADD_TO_DIR = "Строка {row_num}: '{name}' не найдено. Сначала добавьте его в справочник."
    SUGGEST_WRONG_MUNICIPALITY = (
        "Строка {row_num}: '{name}' существует в муниципалитете '{actual_municipality}', "
        "но не в '{expected_municipality}'. Исправьте муниципалитет."
    )
    SUGGEST_IMPORT_REF = (
        "Строка {row_num}: '{name}' не найдено. Сначала добавьте его через импорт {ref_name}."
    )
    IMPORT_MUNICIPALITY_NOT_FOUND = "Строка {row_num}: Муниципалитет '{name}' не найден"
    EMPTY_CELL = "Строка {row_num}: Пустая ячейка в колонке '{display_name}'"

    DATE_EMPTY = "Дата не может быть пустой"
    DATE_INVALID_FORMAT = "Не удалось распознать формат даты: {value}"
    DATE_INVALID_TYPE = "Некорректный тип данных для даты"

    IMPORT_MISSING_HEADERS = "Обязательные поля отсутствуют: {fields}"
    IMPORT_NOT_COMPLETED = "Импорт не выполнен: {error}"


class Messages:
    """Сообщения об успехе для модуля VSOSH"""

    # Муниципалитет
    MUNICIPALITY_CREATED = "Муниципалитет успешно создан"
    MUNICIPALITY_UPDATED = "Муниципалитет успешно обновлен"

    # Предмет
    SUBJECT_CREATED = "Предмет успешно создан"
    SUBJECT_UPDATED = "Предмет успешно обновлен"

    # Образовательное учреждение
    INSTITUTION_CREATED = "Образовательное учреждение успешно создано"
    INSTITUTION_UPDATED = "Образовательное учреждение успешно обновлено"

    # Участник
    PARTICIPANT_CREATED = "Участник успешно создан"
    PARTICIPANT_UPDATED = "Участник успешно обновлен"

    # Участие в олимпиаде
    PARTICIPATION_CREATED = "Участие в олимпиаде успешно зарегистрировано"
    PARTICIPATION_UPDATED = "Участие в олимпиаде успешно обновлено"

    # Импорт/Экспорт
    IMPORT_SUCCESS = "Импорт успешно завершен: Создано {created}, Обновлено {updated}"
    IMPORT_WITH_ERRORS = (
        "Импорт завершён с ошибками: {error_count} шт. Исправьте ошибки и попробуйте ещё!"
    )
    EXPORT_SUCCESS = "Успешно экспортировано: {rows_count} записей ({cols_count} колонок)."


# Лимиты
class Limits:
    NAME = 150
    SUBJECT_FULL_NAME = 100
    SUBJECT_SHORT_NAME = 25
    INSTITUTION_FULL_NAME = 500
    INSTITUTION_SHORT_NAME = 300
    IMPORT_MAX_ROWS = 10000
    SUPPORTED_IMPORT_FORMATS = (".xlsx", ".csv")
    CLASS_MIN = 1
    CLASS_MAX = 11
    BIRTH_DATE_MIN_YEAR = 1950
    YEAR_MIN = 1960
    GENDER_VALUES = ("М", "Ж")
    GENDER_MAP = {
        "м": "М",
        "м.": "М",
        "муж": "М",
        "муж.": "М",
        "мужской": "М",
        "ж": "Ж",
        "ж.": "Ж",
        "жен": "Ж",
        "жен.": "Ж",
        "женский": "Ж",
    }
    STAGE_VALUES = ("ШЭ", "МЭ", "РЭ", "ЗЭ")
    STATUS_VALUES = ("победитель", "призёр", "участник")
