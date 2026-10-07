# Спринт 7/12: 7 спринт. Организация Data Lake 
# → Тема 7/7: Проектная работа по организации Data Lake 
# → Урок 2/3: Проектная работа по организации Data Lake
# ( https://practicum.yandex.ru/learn/data-engineer/courses/057886b7-b8ea-4907-98db-b24501e7b106/sprints/376631/topics/2cd8ca32-f77d-4de1-81c2-9b53ee0b3c98/lessons/aabdd971-0d11-402f-bc98-9c8d799a919f/#a443ac79-f014-456d-a219-6c53dcddfda4 )



# Библиотека классов проекта 7 спринта курса DE



# Вариант обхода ошибки о несуществующем пути к файлам 
# (от препода Руслана Бондарева).
# Использовать в начале тетрадки или файла python до импорта PySpark

# импортируем модуль os, который даёт возможность работы с ОС
# указание os.environ[…] настраивает окружение
import os 

# прописываем пути
os.environ['HADOOP_CONF_DIR'] = '/etc/hadoop/conf'
os.environ['YARN_CONF_DIR'] = '/etc/hadoop/conf'
os.environ['JAVA_HOME']='/usr'
os.environ['SPARK_HOME'] ='/usr/lib/spark'
os.environ['PYTHONPATH'] ='/usr/local/lib/python3.8'

# Из урока в качестве дополнения, если не работает
# Использовать в начале тетрадки или файла python до импорта PySpark
import findspark
findspark.init()
findspark.find()



# Системная библиотека 
# для обеспечения работы функции main()
import sys

# Библиотека PySpark
import pyspark
# Создание сессий и датафреймов PySpark
from pyspark.sql import SparkSession, DataFrame
# Конвертация типов в PySpark
from pyspark.sql.types import StructType, StructField, FloatType, StringType

# импортируем оконную функцию и модуль Spark Functions
from pyspark.sql.window import Window 
# Функции работы с датафреймами Spark
import pyspark.sql.functions as F

# Функции для работы с датой
from datetime import datetime, timedelta



import pandas as pd
import math



#----------
# Базовый класс проекта
#----------
class DistancesCities:
    
    # Объявление класса
    def __init__(self) -> None:
        # Объявление сессии
        self.spark = SparkSession \
            .builder \
            .master('local') \
            .appName('UsersCities') \
            .getOrCreate()
    
    #----------
    # Методы класса
    #----------
    
    # Метод перевода координат широт и долгот из градусов в радианы
    def degrees_to_radians(self, df, lat, lng) -> DataFrame:
        # Перевод градусов в радианы в текущие столбцы
        # -> тот же датафрейм, но с замененными значениями градусов на радианы
        return df \
            .withColumn('lat_rad', F.col(lat)*math.pi/180) \
            .withColumn('lng_rad', F.col(lng)*math.pi/180) \
            .drop(lat, lng) \
            .withColumnRenamed('lat_rad', lat) \
            .withColumnRenamed('lng_rad', lng)
    
    # Метод расчета расстояний по Алисе Pro
    def calculating_distances(self, df, lat_1, lat_2, lng_1, lng_2) -> DataFrame:
        # Радиус Земли в километрах
        r = 6371.0088
        # Формула по Алисе Pro (вариант 1) (похоже, не правильный)
        '''distances = F.acos( \
                  F.sin(F.col(lat_2)) * F.sin(F.col(lat_1)) \
                + F.cos(F.col(lat_2)) * F.cos(F.col(lat_1)) \
                * F.cos(F.col(lng_2)  -       F.col(lng_1)) \
            ) * r'''
        # Формула по Алисе Pro (вариант 2)
        dlat = F.col(lat_2) - F.col(lat_1)
        dlng = F.col(lng_2) - F.col(lng_1)
        a = F.sin(dlat / 2)**2 \
            - F.cos(F.col(lat_1)) \
            * F.cos(F.col(lat_2)) * F.sin(dlng / 2)**2
        distances = (2 * F.asin(F.sqrt(a))) * r
        # Добавление столбца с расчетом
        # -> исходный датафрейм с данными о событиях + 'distances'
        return df.withColumn('distances', distances)

    # Метод для создания плоского справочника 
    # пользователей, совершивших активное действие,
    # внутри датафрейма
    '''
    Информация о пользователях, совершивших активное действие, 
    храниться в разных полях:
    - `event.message_from` - отправитель сообщения.
    - `event.reaction_from` - автор реакции на сообщение.
    - `event.user` - пользователь, совершивший действие.

    Для упрощения работы с этими полями в рамках данного проекта 
    предлагается объединить эти поля в одно с указанием в отдельном поле 
    название исходного поля расположения идентификатора пользователя.
    '''
    def flat_user_directory(self, df) -> DataFrame:
        # -> исходный датафрейм с данными о событиях + 'flat_user'
        return df.withColumn('flat_user' \
                             , F.coalesce(F.col('event.message_from') \
                                          , F.col('event.reaction_from') \
                                          , F.col('event.user')))
    
    # Добавлеие идентификаторов событий
    def assigning_event_id(self, df) -> None:
        return df.withColumn('event_id', F.monotonically_increasing_id())
    
    #----------
    
    # Метод чтения сэмпла датафрейма событий
    def reading_and_preparing_events(self) -> None:
        # Объявление сессии
        if not 'spark' in globals():
            self.spark = SparkSession \
                .builder \
                .master('local') \
                .appName('UsersCities') \
                .getOrCreate()
        
        # Чтение данных
        df1 = self.spark.read.parquet('/user/evgtelegra/events_sample')
        df2 = self.spark.read.parquet('/user/evgtelegra/event_onlywithgeo_sample')
        self.events = df1.unionAll(df2)
        #events = df2
        
        # Переимеование столбцов
        self.events = self.events.withColumnRenamed('lat', 'lat_1').withColumnRenamed('lon', 'lng_1')
        
        # Перевод координат градусов в радианы
        self.events = self.degrees_to_radians(self.events, 'lat_1', 'lng_1')
        
        # Добавлеие идентификаторов событий
        self.events = self.assigning_event_id(self.events)
        
        # Добавление плоского справочника пользователей
        self.events = self.flat_user_directory(self.events)
        
        # Кэширование датафрейма
        self.events.repartition('event.datetime').cache()
        
        # -> исходный датафрейм с данными о событиях
        #return events

    # Метод чтения данных о городах из файла
    def reading_and_preparing_cities(self) -> None:
        # Объявление сессии
        if not 'spark' in globals():
            self.spark = SparkSession \
                .builder \
                .master('local') \
                .appName('UsersCities') \
                .getOrCreate()
        
        # Чтение данных
        schema = StructType([StructField('id', StringType(), True) \
                             , StructField('city', StringType(), True) \
                             , StructField('lat', FloatType(), True) \
                             , StructField('lng', FloatType(), True)])
        self.sities = self.spark \
            .read \
            .options(delimiter=';') \
            .csv('/user/evgtelegra/geo.csv', header=True, schema=schema)
        
        # Переимеование столбцов
        self.sities = self.sities.withColumnRenamed('lat', 'lat_2').withColumnRenamed('lng', 'lng_2')
        
        # Перевод координат градусов в радианы
        self.sities = self.degrees_to_radians(self.sities, 'lat_2', 'lng_2')
        
        # Кэширование датафрейма
        self.sities.repartition('id').cache()
        
        # -> исходный датафрейм с данными о городах
        #return sities
    
    #----------
    
    # Удаленность события от города
    def event_distance_from_nearest_city(self) -> DataFrame:
        
        # Чтение и подготовка данных для проекта
        if not 'events' in globals(): self.reading_and_preparing_events()
        if not 'cities' in globals(): self.reading_and_preparing_cities()
        
        # Объединение датафреймов с данными о событиях и городах
        # с удалением лишней информации
        events_cross_sities = self.events.select('event_id', 'event.datetime', 'flat_user', 'lat_1', 'lng_1') \
            .crossJoin(self.sities.select('city', 'lat_2', 'lng_2')) \
            .withColumnRenamed('flat_user', 'user')
        events_cross_sities = events_cross_sities.repartition('event_id', 'city').cache()
        
        # Метод расчета расстояний по Алисе Pro
        events_cross_sities = self.calculating_distances(events_cross_sities, 'lat_1', 'lat_2', 'lng_1', 'lng_2')
        events_cross_sities = events_cross_sities.repartition('event_id', 'user', 'distances').cache()

        # Выбор ближайшего города
        window = Window.partitionBy('event_id').orderBy('distances')
        # event_id, datetime, user, lat_1, lng_1, city, lat_2, lng_2, distances
        return events_cross_sities \
            .where('distances IS NOT NULL') \
            .withColumn('distances_rank', F.row_number().over(window)) \
            .where('distances_rank = 1') \
            .drop('distances_rank')
    
    #----------
    
    # Добавление идентификатора для 'events'
    def adding_event_id(self) -> None:
        
        # Чтение данных
        if not 'events' in globals(): self.reading_and_preparing_events()
        
        # Добавлеие идентификаторов событий
        self.event_id = self.assigning_event_id(self.events).select('event.*', 'event_id')
        self.event_id.repartition('datetime').cache()
    
    #----------
    
    # Метод определения идентификатора временной зоны
    def zone_id(self, df, city_column) -> DataFrame:
        return df \
            .withColumn('tz', F.concat(F.lit('Australia/'), F.col(city_column))) \
            .withColumn('zone_id' \
                        , F.when(F.col('tz') == 'Australia/Townsville', 'Australia/Brisbane') \
                        .when(F.col('tz') == 'Australia/Cairns', 'Australia/Brisbane') \
                        .when(F.col('tz') == 'Australia/Gold Coast', 'Australia/Brisbane') \
                        .when(F.col('tz') == 'Australia/Ipswich', 'Australia/Brisbane') \
                        .when(F.col('tz') == 'Australia/Toowoomba', 'Australia/Brisbane') \
                        .when(F.col('tz') == 'Australia/Rockhampton', 'Australia/Brisbane') \
                        .when(F.col('tz') == 'Australia/Mackay', 'Australia/Brisbane') \
                        .when(F.col('tz') == 'Australia/Ballarat', 'Australia/Melbourne') \
                        .when(F.col('tz') == 'Australia/Bendigo', 'Australia/Melbourne') \
                        .when(F.col('tz') == 'Australia/Cranbourne', 'Australia/Melbourne') \
                        .when(F.col('tz') == 'Australia/Geelong', 'Australia/Melbourne') \
                        .when(F.col('tz') == 'Australia/Launceston', 'Australia/Melbourne') \
                        .when(F.col('tz') == 'Australia/Wollongong', 'Australia/Melbourne') \
                        .when(F.col('tz') == 'Australia/Bunbury', 'Australia/Perth') \
                        .when(F.col('tz') == 'Australia/Maitland', 'Australia/Sydney') \
                        .when(F.col('tz') == 'Australia/Newcastle', 'Australia/Sydney') \
                        .when(F.col('tz') == 'Australia/Cairns', 'Australia/Sydney') \
                        .otherwise(F.col('tz'))) \
            .select(city_column, 'zone_id').distinct()
        
    
    # Метод расчета локального временеи последнего события
    def event_timezone(self, df, basic_column, city_column, datetime_column) -> DataFrame:
        #df = df.join(self.zone_id(df, city_column), city_column, 'left')
        return df \
            .withColumn('tz', F.concat(F.lit('Australia/'), F.col(city_column))) \
            .withColumn('zone_id' \
                        , F.when(F.col('tz') == 'Australia/Townsville', 'Australia/Brisbane') \
                        .when(F.col('tz') == 'Australia/Cairns', 'Australia/Brisbane') \
                        .when(F.col('tz') == 'Australia/Gold Coast', 'Australia/Brisbane') \
                        .when(F.col('tz') == 'Australia/Ipswich', 'Australia/Brisbane') \
                        .when(F.col('tz') == 'Australia/Toowoomba', 'Australia/Brisbane') \
                        .when(F.col('tz') == 'Australia/Rockhampton', 'Australia/Brisbane') \
                        .when(F.col('tz') == 'Australia/Mackay', 'Australia/Brisbane') \
                        .when(F.col('tz') == 'Australia/Ballarat', 'Australia/Melbourne') \
                        .when(F.col('tz') == 'Australia/Bendigo', 'Australia/Melbourne') \
                        .when(F.col('tz') == 'Australia/Cranbourne', 'Australia/Melbourne') \
                        .when(F.col('tz') == 'Australia/Geelong', 'Australia/Melbourne') \
                        .when(F.col('tz') == 'Australia/Launceston', 'Australia/Melbourne') \
                        .when(F.col('tz') == 'Australia/Wollongong', 'Australia/Melbourne') \
                        .when(F.col('tz') == 'Australia/Bunbury', 'Australia/Perth') \
                        .when(F.col('tz') == 'Australia/Maitland', 'Australia/Sydney') \
                        .when(F.col('tz') == 'Australia/Newcastle', 'Australia/Sydney') \
                        .when(F.col('tz') == 'Australia/Cairns', 'Australia/Sydney') \
                        .otherwise(F.col('tz'))) \
            .withColumn('local_time', F.from_utc_timestamp(F.col(datetime_column), F.col('zone_id'))) \
            .select(basic_column, 'zone_id', 'local_time')
    
    #----------
    
    # Ключевой метод для сохранения основного параметра класса
    def distances_cities(self) -> None:
        self.distances_cities_result = self.event_distance_from_nearest_city()
        self.distances_cities_result.repartition('datetime').cache()
    
    
    # Параметры экземпляров класса
    
    # self.spark # Сессия pyspark.sql.SparkSession
    # self.distances_cities_result # Сэмпл датафрейма событий
    # self.city_geo # Данные о городах из файла



#----------
# Класс UsersCities дочерний для DistancesCities
# Для создания первой витрины в разрезе пользователей
#----------
# Класс UsersCities дочерний для DistancesCities
# Для создания первой витрины в разрезе пользователей
class UsersCities(DistancesCities):
    
    # Объявление класса
    def __init__(self):
        if not 'distances_cities_result' in globals():
            super().distances_cities()
    
    #----------
    
    # Метод определения последнего адреса
    def act_address(self) -> DataFrame:
        window = Window.partitionBy('user').orderBy(F.col('datetime').desc())
        return self.distances_cities_result.withColumn('rank', F.row_number().over(window)) \
            .where('rank = 1') \
            .where('city IS NOT NULL') \
            .selectExpr('user', 'city AS act_city', 'datetime')
    
    # Метод определения домашнего адреса
    # (Вариант определения домашнего города по 27 дням активности)
    def home_address_27days(self) -> DataFrame:
        window_date = Window.partitionBy('user', 'city').orderBy('datetime')
        window_count = Window.partitionBy('user', 'city').orderBy(F.desc('events_count'))
        return self.distances_cities_result \
            .select('user', 'city', 'datetime') \
            .withColumn('events_count' \
                       , F.sum(F.when(F.datediff(F.col('datetime') \
                                                 , F.min('datetime').over(window_date)) <= 27, 1).otherwise(0)).over(window_date)) \
            .withColumn('rank', F.row_number().over(window_count)) \
            .filter(F.col('rank') == 1) \
            .selectExpr('user', 'city AS home_city')

    # Метод определения домашнего адреса
    # (моя версия с определеием домашнего адреса 
    # по максимальному количеству эвентов пользователя в городе)
    '''
    Соласно условию проекта, предлагается воспользоваться возможностью 
    выбрать самостоятельно вариант определения домашнего адреса. 
    В связи с этим, предлагается вариант определения домашнего адреса 
    по максимальному количество эвентов пользователя в городе.
    '''
    def home_address(self) -> DataFrame:
        window = Window.partitionBy('user').orderBy(F.desc('count'))
        return self.distances_cities_result \
            .select('user', 'city', 'datetime') \
            .groupBy('user', 'city') \
            .agg(F.count('datetime').alias('count')) \
            .withColumn('rank', F.row_number().over(window)) \
            .filter(F.col('rank') == 1).filter(F.col('city').isNotNull()) \
            .selectExpr('user', 'city AS home_city')
    
    # Метод расчета количества 
    # и списка городов путешествий пользователя
    def travel_address(self) -> DataFrame:
        # Требуется использовать функцию "act_and_home_address(event_geo, city_geo)",
        # а также добавить до группировки в расчет городов, 
        # посещенных пользователем, если "домашние" города не надо учитывать
        window = Window.partitionBy('user').orderBy('datetime')
        return self.distances_cities_result \
            .withColumn('city_travel', F.lag('city', 1).over(window)) \
            .where('city != city_travel') \
            .groupBy('user') \
            .agg(F.count('city').alias('travel_count') \
                 , F.collect_list('city').alias('travel_array'))
    
    #----------
    
    # Создание датафрейма с данными о последних, домашних и посещенных городах,
    # а также о количестве посещенных городов
    def act_home_travel_address(self) -> DataFrame:
        df = self.act_address() \
            .join(self.home_address(), 'user', 'full') \
            .join(self.travel_address(), 'user', 'full')
        return df.drop('datetime') \
            .join(self.event_timezone(df, 'user', 'act_city', 'datetime'), 'user', 'full') \
            .drop('timezone')
    
    #----------
    
    # Ключевой метод для сохранения основного параметра класса
    def users_cities(self) -> None:
        # Преобразование данных
        #self.users_cities_result = self.act_home_travel_address()
        # Добавление актуальных, домашних и посещенных городов
        self.users_cities_result = self.act_address() \
            .join(self.home_address(), 'user', 'full') \
            .join(self.travel_address(), 'user', 'full')
        # Добавление идентификатора зоны и локального времени
        local_time = super().event_timezone(self.users_cities_result, 'user', 'act_city', 'datetime')
        self.users_cities_result = self.users_cities_result \
            .join(local_time, 'user', 'left') \
            #.drop('timezone')
        self.users_cities_result = self.users_cities_result \
            .selectExpr('user AS user_id' \
                        , 'act_city', 'home_city' \
                        , 'travel_count', 'travel_array' \
                        , 'local_time')
        # Проверка данных
        #self.users_cities_result.show(5)
        # Кэширование данных
        self.users_cities_result.repartition('user_id').cache()



#----------
# Класс `EventsCities` дочерний для `DistancesCities` 
# Для создания второй витрины (действия пользователей в разрезе зон)
#----------
class EventsCities(DistancesCities):
    
    # Объявление класса
    def __init__(self):
        super().distances_cities()
        super().adding_event_id()
        self.events_cities_result = self.distances_cities_result \
            .select('event_id', 'datetime', 'user', 'city')
    
    #----------
    
    # Ключевой метод для сохранения основного параметра класса
    def events_cities(self) -> None:
        
        # Создание основной переменной класса с датафреймом
        self.events_cities_result = self.event_id \
            .select('event_id', 'datetime', 'message_from', 'reaction_from', 'subscription_user')
        
        # Добавление поля с данными о месяце и неделе
        self.events_cities_result = self.events_cities_result \
            .withColumn('month', F.month(self.events_cities_result.datetime)) \
            .withColumn('week', F.weekofyear(self.events_cities_result.datetime))
        
        # Ранжирование событий datetime и их нумерация
        window = Window.partitionBy('message_from').orderBy('datetime')
        self.events_cities_result = self.events_cities_result \
            .withColumn('message_rank' \
                        , F.row_number().over(window)) \
            .withColumn('message_rank_1', F.when(F.col('message_rank') == 1, 1).otherwise(0)) \
            .drop('message_rank')
        
        # Подсчет количества событий по неделям
        self.events_cities_result = self.events_cities_result \
            .join(self.distances_cities_result, 'event_id', 'left') \
            .groupBy('week', 'month', 'city') \
            .agg(F.count('message_from').alias('week_message') \
                 , F.count('reaction_from').alias('week_reaction') \
                 , F.count('subscription_user').alias('week_subscription') \
                 , F.sum('message_rank_1').alias('week_user')) \
            .drop('message_rank_1')
        
        # Подсчет количества событий по месяцам
        window = Window.partitionBy('month', 'city')
        self.events_cities_result = self.events_cities_result \
            .withColumn('month_message', F.sum('week_message').over(window)) \
            .withColumn('month_reaction', F.sum('week_reaction').over(window)) \
            .withColumn('month_subscription', F.sum('week_subscription').over(window)) \
            .withColumn('month_user', F.sum('week_user').over(window)) \
            .orderBy('month', 'week', 'city')
        
        # Добавление идентификатора timezone
        #self.events_cities_result.show(5)
        zone_id = super().zone_id(self.events_cities_result, 'city')
        self.events_cities_result = self.events_cities_result \
            .join(zone_id, 'city', 'left')
        
        # Создание итогового датафрейма
        self.events_cities_result = self.events_cities_result \
            .selectExpr('month', 'week', 'zone_id' \
                        , 'week_message', 'week_reaction', 'week_subscription', 'week_user' \
                        , 'month_message', 'month_reaction', 'month_subscription', 'month_user')
        
        # Кэширование данных
        self.events_cities_result.repartition('week').cache()



#----------
# Класс для витрины рекомендаций друзей
#----------
class RecommendedFriends(DistancesCities):
    
    # Объявление класса
    def __init__(self):
        
        if not 'events' in globals():
            super().reading_and_preparing_events()
        
        if not 'sities' in globals():
            super().reading_and_preparing_cities()
        
        if not 'event_id' in globals():
            super().adding_event_id()
        
        # так не работает (два дочеринх класса прямо не видят друг друга)
        #if not 'users_cities_result' in globals():
        #    super().distances_cities()
    
    #----------
    
    '''
    Схема работы класса:
1. Найти каналы `subscription_channel` с более чем одним подписчиком `user`.
2. Создать список пользователей в виде пар `user` - `subscription_channel` из подписчиков каналов, в которых более одного подписчика.
3. Образовать все возможные варианты пар из всех пользователей, подписанных к одному каналу.
4. Сделать список всех уникальных личных переписок из `message_from` и `message_to`.
5. Выбрать из списка пар подписантов к каналам те, которые не были найдены в личных переписках.
6. Определить расстояние между участниками пар подписчиков одного канала, не переписывающихся ранее. Оставить только те пары, участники которых расположены на расстоянии не более 1 км.
7. Определить по первому участнику пары город и локальное время.
'''
    
    # 1 Каналы с более чем одним подписчиком
    def channels_with_multiple_subscribers(self) -> None:
        # Преобразование данных
        self.channels = self.event_id \
            .select('user', 'subscription_channel') \
            .where('subscription_channel IS NOT NULL') \
            .distinct() \
            .groupBy('subscription_channel').agg(F.count('user').alias('count_users')) \
            .where('count_users > 1') \
            .selectExpr('subscription_channel AS channel')
        # Кэширование данных
        self.channels.cache()
        # Проверка данных
        #print('1. channels:')
        #self.channels.show(5)
        #self.channels.count()
    
    # 2. Подписчики каналов с более чем одним подписчиком
    def subscribers_of_selected_channels(self) -> None:
        # Преобразование данных
        self.channels_users = self.event_id \
            .selectExpr('user', 'subscription_channel AS channel') \
            .where('channel IS NOT NULL') \
            .distinct() \
            .join(self.channels, 'channel', 'inner')
        # Кэширование данных
        self.channels_users.cache()
        # Проверка данных
        #print('2. channels_users:')
        #self.channels_users.show(5)
        #self.channels_users.count()
    
    # 3. Пары пользователй, являющихся подписчиками одного канала
    def channel_subscriber_pairs(self) -> None:
        # Преобразование данных
        window = Window.partitionBy('channel')
        self.channel_user_pairs = self.channels_users.alias('df1') \
            .crossJoin(self.channels_users.alias('df2')) \
            .where('df1.channel = df2.channel') \
            .where('df1.user != df2.user') \
            .selectExpr('df1.user AS user_left', 'df2.user AS user_right')
        # Кэширование данных
        self.channel_user_pairs.cache()
        # Проверка данных
        #print('3. channel_user_pairs:')
        #self.channel_user_pairs.show(5)
        #self.channel_user_pairs.count()
    
    # 4. Все пары пользователей, участвующих в личной переписке
    def users_in_personal_communicaton(self) -> None:
        # Только уникальные пары пользователей, участвующих в личной переписке
        self.personal_user_pairs = self.event_id \
            .select('message_from', 'message_to') \
            .where('message_to IS NOT NULL') \
            .distinct()
        # Вариант 3. Пары отправитель-получатель и получатель-отправитель личных сообщений
        self.personal_user_pairs = self.personal_user_pairs \
            .selectExpr('message_from AS user_left', 'message_to AS user_right') \
            .union(self.personal_user_pairs \
                .selectExpr('message_to AS user_left', 'message_from AS user_right'))
        # Кэширование данных
        self.personal_user_pairs.cache()
        # Проверка данных
        #print('4. personal_user_pairs:')
        #self.personal_user_pairs.orderBy('user_left', 'user_right').show()
        #print(self.personal_user_pairs.count())
    
    # 5. Исключение из списка пар-пользователей, 
    # явлюящихся подписчиками групп с более чем одним подписчиком, 
    # тех, кто общался через личные сообщения
    def channels_users_and_not_personal(self) -> None:
        # Преобразование данных
        self.channel_user_pairs = self.channel_user_pairs \
            .join(self.personal_user_pairs, ['user_left', 'user_right'], 'leftanti')
        # Кэширование данных
        self.channel_user_pairs.cache()
        # Проверка данных
        #print('5. channel_user_pairs:')
        #self.channel_user_pairs.show(5)
        #self.channel_user_pairs.count()
    
    # 6. Расчет расстояния между пользователями в парах
    def calculating_distances_between_users(self) -> None:
        # Определение последнего события пользователя
        window = Window.partitionBy('flat_user').orderBy('datetime')
        self.distances_between_users = self.events \
            .select('event.datetime', 'flat_user', 'lat_1', 'lng_1') \
            .withColumn('rank', F.row_number().over(window)) \
            .where('rank = 1').drop('rank')
        # В целях данного проекта принимаем предположение о том,
        # что все пользователи соцсети находятся в Австралии. 
        # В связи с этим, если у пользователей нет геоданных, 
        # предполагаем, что они с высокой вероятностью находятся 
        # в Сиднее - самом густонаселенном городе Австралии 
        # Координаты Sydney в градусах:-33.865, 151.2094;
        # в радианах: -0.5910557804826516; 2.6391018264753536
        # ЭТО НЕ ИДЕАЛЬНОЕ, НО ИНТЕРЕСНОЕ РЕШЕНИЕ!
        # В ином случае отсекать пары без геоданных.
        # В имеющемся сэмпле без этого нет пар с расстоянием, меньше 1 км
        sydney = self.sities.where('city = "Sydney"')
        #sydney.show()
        # Замена геокоорднат, равных null, координатами Сиднея
        self.distances_between_users = self.distances_between_users \
            .withColumn('lat_full', F.when(F.col('lat_1').isNull(), sydney.first()['lat_2']).otherwise(F.col('lat_1'))) \
            .withColumn('lng_full', F.when(F.col('lng_1').isNull(), sydney.first()['lng_2']).otherwise(F.col('lng_1'))) \
            .drop('lat_1', 'lng_1') \
            .withColumnRenamed('lat_full', 'lat_1') \
            .withColumnRenamed('lng_full', 'lng_1')
        #self.distances_between_users.show(5)
        # Добавление координат в данные о парах пользователей
        self.distances_between_users = self.channel_user_pairs \
            .join(self.distances_between_users.alias('df1') \
                  .withColumnRenamed('flat_user', 'user_left') \
                  .withColumnRenamed('lat_1', 'left_lat') \
                  .withColumnRenamed('lng_1', 'left_lng') \
                  .withColumnRenamed('datetime', 'left_datetime') \
                  , 'user_left', 'left') \
            .join(self.distances_between_users.alias('df2') \
                  .withColumnRenamed('flat_user', 'user_right') \
                  .withColumnRenamed('lat_1', 'right_lat') \
                  .withColumnRenamed('lng_1', 'right_lng') \
                  .withColumnRenamed('datetime', 'right_datetime') \
                  , 'user_right', 'left') \
            #.selectExpr('')
        # Расчет расстояния между пользователями в паре 
        # и выбор только пар, у которых расстояние 
        # меньше или равно 1 км
        self.distances_between_users = super().calculating_distances(self.distances_between_users \
                                                                     , 'left_lat', 'right_lat' \
                                                                     , 'left_lng', 'right_lng') \
            .withColumnRenamed('distances','users_distances') \
            .where('users_distances <= 1').where('users_distances IS NOT NULL')
        # Кэширование данных
        self.distances_between_users.cache()
        # Проверка данных
        #print('distances_between_users:')
        #self.distances_between_users.show(5)
        #print(self.distances_between_users.count())
    
    # 7. Определить по первому участнику пары город и локальное время.
    # Ключевой метод для данного класса
    def recommended_friends(self) -> None:
        # Активация расчета данных о городах для данных о парах пользователей
        self.channels_with_multiple_subscribers() # 1
        self.subscribers_of_selected_channels() # 2
        self.channel_subscriber_pairs() # 3
        self.users_in_personal_communicaton() # 4
        self.channels_users_and_not_personal() # 5
        self.calculating_distances_between_users() # 6
        # Добавление данных о городах в данные о парах пользователей
        self.recommended_friends_result = self.distances_between_users \
            .crossJoin(self.sities)
        self.recommended_friends_result.cache()
        # Расчет дистанции от первого пользователя пары до всех городов
        self.recommended_friends_result = super().calculating_distances(self.recommended_friends_result \
                                                                     , 'left_lat', 'lat_2' \
                                                                     , 'left_lng', 'lng_2')
        # Выбор ближайшего города
        window = Window.partitionBy('user_left').orderBy('distances')
        self.recommended_friends_result = self.recommended_friends_result \
            .where('distances IS NOT NULL') \
            .withColumn('distances_rank', F.row_number().over(window)) \
            .where('distances_rank = 1') \
            .drop('distances_rank')
        # Добавление идентификатора пары
        self.recommended_friends_result = self.recommended_friends_result \
            .withColumn('pair_id', F.monotonically_increasing_id())
        # Расчет локального времени для каждой пары
        local_datetime = super().event_timezone(self.recommended_friends_result, 'pair_id', 'city', 'left_datetime')
        # Добавление локального времени в конечный датафрейм
        self.recommended_friends_result = self.recommended_friends_result \
            .join(local_datetime, 'pair_id', 'left') \
            .drop('pair_id')
        # Очистка конечного датафрейма от расчетных данных
        self.recommended_friends_result = self.recommended_friends_result \
            .selectExpr('user_right', 'user_left' \
                        , 'current_timestamp() AS processed_dttm' \
                        , 'zone_id', 'local_time')
        # Кэширование данных
        self.recommended_friends_result.cache()
        # Проверка данных
        #print('recommended_friends_result:')
        #self.recommended_friends_result.show()
    