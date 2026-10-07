import json
import os
from collections import defaultdict
from decimal import Decimal
from datetime import datetime
from models import Car, CarFullInfo, CarStatus, Model, ModelSaleStats, Sale
from typing import List, Dict, Any, Optional


class CarService:
    def __init__(self, root_directory_path: str) -> None:
        self.root_directory_path = root_directory_path
        os.makedirs(root_directory_path, exist_ok=True)

    def _add_record(self, record: Any, data_filename: str, index_filename: str) -> Any:
        '''Общий метод для добавления записи в файл данных и индекс'''
        data_path = os.path.join(self.root_directory_path, data_filename)
        index_path = os.path.join(self.root_directory_path, index_filename)

        # Читаем текущий индекс
        index_data = []
        if os.path.exists(index_path):
            with open(index_path, 'r', encoding='utf-8') as f:
                index_data = [line.strip() for line in f.readlines() if line.strip()]

        # Проверяем, существует ли уже запись с таким ключом
        record_key = record.index()
        for line in index_data:
            if line.split(':')[0] == record_key:
                raise ValueError(f'Запись с ключом {record_key} уже существует')

        # Добавляем запись в файл данных
        with open(data_path, 'a', encoding='utf-8') as f:
            position = f.tell()
            f.write(f'{record.json()}\n')

        # Добавляем запись в индекс
        index_entry = f"{record_key}:{position}"
        index_data.append(index_entry)
        index_data.sort()

        # Сохраняем обновленный индекс
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(index_data) + '\n')

        return record

    def _read_index(self, index_filename: str) -> List[str]:
        '''Чтение индексного файла'''
        index_path = os.path.join(self.root_directory_path, index_filename)
        if os.path.exists(index_path):
            with open(index_path, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f.readlines() if line.strip()]
        return []

    def _find_in_index(self, key: str, index_filename: str) -> int:
        '''Поиск позиции в файле данных по ключу через индекс'''
        index_data = self._read_index(index_filename)
        for entry in index_data:
            parts = entry.split(':')
            if len(parts) >= 2 and parts[0] == key:
                return int(parts[1])
        return -1

    def _get_record_by_position(self, data_filename: str, position: int, record_class):
        '''Чтение записи из файла данных по позиции'''
        data_path = os.path.join(self.root_directory_path, data_filename)
        if not os.path.exists(data_path):
            return None

        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                f.seek(position)
                line = f.readline().strip()
                if line:
                    data = json.loads(line)
                    # Конвертируем специальные типы данных
                    return self._convert_data_types(data, record_class)
        except (json.JSONDecodeError, KeyError, ValueError):
            return None
        return None

    def _convert_data_types(self, data: dict, record_class):
        '''Конвертация типов данных из JSON в Python объекты'''
        converted_data = data.copy()

        # Определяем ожидаемые типы для каждого класса
        if record_class == Car:
            if 'price' in converted_data and isinstance(converted_data['price'], str):
                converted_data['price'] = Decimal(converted_data['price'])
            if 'date_start' in converted_data and isinstance(converted_data['date_start'], str):
                converted_data['date_start'] = datetime.fromisoformat(converted_data['date_start'])
            if 'status' in converted_data and isinstance(converted_data['status'], str):
                converted_data['status'] = CarStatus(converted_data['status'])
            if 'model' in converted_data and isinstance(converted_data['model'], str):
                converted_data['model'] = int(converted_data['model'])

        elif record_class == Sale:
            if 'cost' in converted_data and isinstance(converted_data['cost'], str):
                converted_data['cost'] = Decimal(converted_data['cost'])
            if 'sales_date' in converted_data and isinstance(converted_data['sales_date'], str):
                converted_data['sales_date'] = datetime.fromisoformat(converted_data['sales_date'])

        elif record_class == Model:
            if 'id' in converted_data and isinstance(converted_data['id'], str):
                converted_data['id'] = int(converted_data['id'])

        return record_class(**converted_data)

    def _update_record_by_position(self, data_filename: str, position: int, record):
        '''Обновление записи в файле данных по позиции'''
        data_path = os.path.join(self.root_directory_path, data_filename)

        with open(data_path, 'r+', encoding='utf-8') as f:
            f.seek(position)

            # Записываем новую строку
            new_line = record.json()
            f.write(new_line + '\n')

    def _get_all_records(self, data_filename: str, record_class):
        '''Получение всех записей из файла'''
        data_path = os.path.join(self.root_directory_path, data_filename)
        if not os.path.exists(data_path):
            return []

        records = []
        with open(data_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        data = json.loads(line)
                        record = self._convert_data_types(data, record_class)
                        records.append(record)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        # Пропускаем некорректные строки
                        continue
        return records

    def _find_sale_by_sales_number(self, sales_number: str) -> Optional[Sale]:
        '''Поиск продажи по номеру продажи'''
        sales = self._get_all_records('sales.txt', Sale)
        for sale in sales:
            if sale.sales_number == sales_number:
                return sale
        return None

    def _find_sale_by_car_vin(self, car_vin: str) -> Optional[Sale]:
        '''Поиск продажи по VIN автомобиля'''
        sales = self._get_all_records('sales.txt', Sale)
        for sale in sales:
            if sale.car_vin == car_vin:
                return sale
        return None

    def _get_model_by_id(self, model_id: int) -> Optional[Model]:
        '''Получение модели по ID'''
        model_position = self._find_in_index(str(model_id), 'models_index.txt')
        if model_position == -1:
            return None
        return self._get_record_by_position('models.txt', model_position, Model)

    def _get_car_by_vin(self, vin: str) -> Optional[Car]:
        '''Получение автомобиля по VIN'''
        car_position = self._find_in_index(vin, 'cars_index.txt')
        if car_position == -1:
            return None
        return self._get_record_by_position('cars.txt', car_position, Car)

    def _get_average_price_by_model_id(self, model_id: int) -> Decimal:
        '''Получение средней цены автомобилей по модели'''
        cars = self._get_all_records("cars.txt", Car)
        model_cars = [car for car in cars if car.model == model_id]
        if not model_cars:
            return Decimal('0')

        total_price = sum(car.price for car in model_cars)
        return total_price / len(model_cars)

    def _update_sale_car_vin(self, old_vin: str, new_vin: str) -> None:
        '''Обновление VIN в записях о продажах'''
        sales_path = os.path.join(self.root_directory_path, 'sales.txt')
        sales_index_path = os.path.join(self.root_directory_path, 'sales_index.txt')

        if not os.path.exists(sales_path):
            return

        # Читаем все продажи
        sales = self._get_all_records('sales.txt', Sale)

        # Обновляем VIN в продажах
        updated_sales = []
        for sale in sales:
            if sale.car_vin == old_vin:
                sale.car_vin = new_vin
            updated_sales.append(sale)

        # Перезаписываем файл продаж
        with open(sales_path, 'w', encoding='utf-8') as f:
            for sale in updated_sales:
                f.write(f'{sale.json()}\n')

        # Перестраиваем индекс продаж
        sales_index_data = []
        with open(sales_path, 'r', encoding='utf-8') as f:
            position = 0
            for line in f:
                if line.strip():
                    try:
                        sale_data = json.loads(line.strip())
                        sale_key = sale_data['car_vin']
                        sales_index_data.append(f'{sale_key}:{position}')
                        position = f.tell()
                    except (json.JSONDecodeError, KeyError):
                        continue

        sales_index_data.sort()
        with open(sales_index_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(sales_index_data) + '\n')

    def _rewrite_file_without_record(self, data_filename: str, index_filename: str, key_to_remove: str, record_class) -> None:
        '''Перезапись файла без указанной записи'''
        data_path = os.path.join(self.root_directory_path, data_filename)
        index_path = os.path.join(self.root_directory_path, index_filename)

        if not os.path.exists(data_path):
            return

        # Читаем все записи
        records = self._get_all_records(data_filename, record_class)

        # Фильтруем записи, удаляя ту, которую нужно удалить
        filtered_records = [record for record in records if record.index() != key_to_remove]

        # Перезаписываем файл данных
        with open(data_path, 'w', encoding='utf-8') as f:
            for record in filtered_records:
                f.write(f'{record.json()}\n')

        # Перестраиваем индекс
        index_data = []
        with open(data_path, 'r', encoding='utf-8') as f:
            position = 0
            for line in f:
                if line.strip():
                    try:
                        record_data = json.loads(line.strip())
                        # Определяем ключ в зависимости от класса
                        if record_class == Car:
                            record_key = record_data['vin']
                        elif record_class == Model:
                            record_key = str(record_data['id'])
                        elif record_class == Sale:
                            record_key = record_data['car_vin']
                        else:
                            record_key = list(record_data.keys())[0]

                        index_data.append(f'{record_key}:{position}')
                        position = f.tell()
                    except (json.JSONDecodeError, KeyError):
                        continue

        index_data.sort()
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(index_data) + '\n')

    # Задание 1. Сохранение автомобилей и моделей
    def add_model(self, model: Model) -> Model:
        return self._add_record(model, 'models.txt', 'models_index.txt')

    def add_car(self, car: Car) -> Car:
        model_position = self._find_in_index(str(car.model), 'models_index.txt')
        if model_position == -1:
            raise ValueError(f'Модель с id {car.model} не найдена')
        return self._add_record(car, 'cars.txt', 'cars_index.txt')

    # Задание 2. Сохранение продаж
    def sell_car(self, sale: Sale) -> Car:
        self._add_record(sale, 'sales.txt', 'sales_index.txt')

        car_position = self._find_in_index(sale.car_vin, 'cars_index.txt')
        if car_position == -1:
            raise ValueError(f'Автомобиль с VIN {sale.car_vin} не найден')

        car = self._get_record_by_position('cars.txt', car_position, Car)
        if not car:
            raise ValueError(f'Не удалось прочитать автомобиль с VIN {sale.car_vin}')

        car.status = CarStatus.sold
        self._update_record_by_position('cars.txt', car_position, car)

        return car

    # Задание 3. Доступные к продаже
    def get_cars(self, status: CarStatus) -> list[Car]:
        cars = self._get_all_records('cars.txt', Car)
        return [car for car in cars if car.status == status]

    # Задание 4. Детальная информация
    def get_car_info(self, vin: str) -> CarFullInfo | None:
        car_position = self._find_in_index(vin, 'cars_index.txt')
        if car_position == -1:
            return None

        car = self._get_record_by_position('cars.txt', car_position, Car)
        if not car:
            return None

        model = self._get_model_by_id(car.model)
        if not model:
            return None

        sale = self._find_sale_by_car_vin(vin)

        return CarFullInfo(
            vin=car.vin,
            car_model_name=model.name,
            car_model_brand=model.brand,
            price=car.price,
            date_start=car.date_start,
            status=car.status,
            sales_date=sale.sales_date if sale else None,
            sales_cost=sale.cost if sale else None
        )

    # Задание 5. Обновление ключевого поля
    def update_vin(self, vin: str, new_vin: str) -> Car:
        car_position = self._find_in_index(vin, 'cars_index.txt')
        if car_position == -1:
            raise ValueError(f'Автомобиль с VIN {vin} не найден')

        car = self._get_record_by_position('cars.txt', car_position, Car)
        if not car:
            raise ValueError(f'Не удалось прочитать автомобиль с VIN {vin}')

        if self._find_in_index(new_vin, 'cars_index.txt') != -1:
            raise ValueError(f'Автомобиль с VIN {new_vin} уже существует')

        old_vin = car.vin
        car.vin = new_vin

        self._update_record_by_position('cars.txt', car_position, car)

        index_data = self._read_index('cars_index.txt')
        new_index_data = []
        for entry in index_data:
            entry_key, entry_position = entry.split(':')
            if entry_key == old_vin:
                new_index_data.append(f'{new_vin}:{entry_position}')
            else:
                new_index_data.append(entry)

        new_index_data.sort()
        index_path = os.path.join(self.root_directory_path, 'cars_index.txt')
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_index_data) + '\n')

        self._update_sale_car_vin(old_vin, new_vin)

        return car

    # Задание 6. Удаление продажи
    def revert_sale(self, sales_number: str) -> Car:
        sale = self._find_sale_by_sales_number(sales_number)
        if not sale:
            raise ValueError(f'Продажа с номером {sales_number} не найдена')

        car_position = self._find_in_index(sale.car_vin, 'cars_index.txt')
        if car_position == -1:
            raise ValueError(f'Автомобиль с VIN {sale.car_vin} не найден')

        car = self._get_record_by_position('cars.txt', car_position, Car)
        if not car:
            raise ValueError(f'Не удалось прочитать автомобиль с VIN {sale.car_vin}')

        self._rewrite_file_without_record('sales.txt', 'sales_index.txt', sale.car_vin, Sale)

        if car.status == CarStatus.sold:
            car.status = CarStatus.available

        self._update_record_by_position('cars.txt', car_position, car)

        return car

    # Задание 7. Самые продаваемые модели
    def top_models_by_sales(self) -> list[ModelSaleStats]:
        # 1. Заводим словарь для подсчета продаж по моделям
        model_sales_count: Dict[int, int] = defaultdict(int)

        # 2. Читаем файл sales.txt построчно
        sales = self._get_all_records('sales.txt', Sale)

        # 3. Для каждой продажи находим модель автомобиля и инкрементируем счетчик
        for sale in sales:
            car = self._get_car_by_vin(sale.car_vin)
            if car:
                model_sales_count[car.model] += 1

        # 4. Если нет продаж, возвращаем пустой список
        if not model_sales_count:
            return []

        # 5. Получаем информацию о моделях для сортировки по цене
        models_info = {}
        for model_id in model_sales_count.keys():
            model = self._get_model_by_id(model_id)
            if model:
                # Получаем среднюю цену автомобилей этой модели
                cars = self._get_all_records('cars.txt', Car)
                model_cars = [car for car in cars if car.model == model_id]
                avg_price = Decimal('0')
                if model_cars:
                    total_price = sum(car.price for car in model_cars)
                    avg_price = total_price / len(model_cars)

                models_info[model_id] = {
                    'model': model,
                    'avg_price': avg_price,
                    'sales_count': model_sales_count[model_id]
                }

        # 6. Сортируем модели по количеству продаж (по убыванию), 
        # а при равных продажах - по средней цене (по убыванию)
        sorted_models = sorted(
            models_info.items(),
            key=lambda x: (-x[1]['sales_count'], -x[1]['avg_price'])
        )

        # 7. Берем первые 3 элемента
        top_3_models = sorted_models[:3]

        # 8. Формируем результат
        result = []
        for model_id, info in top_3_models:
            result.append(ModelSaleStats(
                car_model_name=info['model'].name,
                brand=info['model'].brand,
                sales_number=info['sales_count']
            ))

        return result
