import os

from dotenv import load_dotenv

load_dotenv()


class Constans:
    # Длина полей типа CharField
    LENGTH_CHAR_FIELD_100 = 100
    LENGTH_CHAR_FIELD_20 = 20

    # Дефолтный цвет для ColorField
    DEFAULT_COLOR_FOR_TAG = '#FF0000'

    # Флаги
    POSITIVE_FLAG = '1'

    # Кол-во объект на странице для пагинации
    PAGE_SIZE = os.getenv('PAGE_SIZE', 20)

    # Значения времени приготовления рецептов
    MIN_COOKING_TIME = 1
    MAX_COOKING_TIME = 3000
