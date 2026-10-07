# Спринт 7/12: 7 спринт. Организация Data Lake 
# → Тема 7/7: Проектная работа по организации Data Lake 
# → Урок 2/3: Проектная работа по организации Data Lake
# ( https://practicum.yandex.ru/learn/data-engineer/courses/057886b7-b8ea-4907-98db-b24501e7b106/sprints/376631/topics/2cd8ca32-f77d-4de1-81c2-9b53ee0b3c98/lessons/aabdd971-0d11-402f-bc98-9c8d799a919f/#a443ac79-f014-456d-a219-6c53dcddfda4 )



# Библиотека классов проекта 7 спринта курса DE



# Джоба для создания первой витрины в разрезе пользователей
# на базе класса UsersCities



import sys
from class_library import UsersCities



def main():
    
    #n = sys.argv[1]
    
    uc = UsersCities()
    
    uc.users_cities()
    #uc.users_cities_result.show(5)
    uc.users_cities_result.write \
        .format('parquet') \
        .save('/user/evgtelegra/analytics/users_cities_result')



if __name__ == '__main__':
    main()