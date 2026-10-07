
import os
import sys

from .class_library import DistancesCities # Базовый класс проекта
from .class_library import UsersCities # Класс для создания первой витрины в разрезе пользователей
from .class_library import EventsCities # Класс для создания второй витрины (действия пользователей в разрезе зон)
from .class_library import RecommendedFriends # Класс для витрины рекомендаций друзей

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
