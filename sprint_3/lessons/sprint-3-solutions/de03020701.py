import os
import pandas as pd

class TerminalColors:
        HEADER = '\033[95m'
        OKBLUE = '\033[94m'
        OKCYAN = '\033[96m'
        OKGREEN = '\033[92m'
        WARNING = '\033[93m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'


def de_test(
        full_lesson_path: str,
        realization_file='realization.py',
        sql_author=None,
        dsn='postgresql://jovyan:jovyan@localhost:5432/de'):

    stage_files = os.walk(f'{full_lesson_path}/stage')


    for root, dirs, files in stage_files:
        if 'user_order_log.csv' not in files:
            return False, f'\n{TerminalColors.WARNING}В каталоге {root} не найден файл `user_order_log.csv`{TerminalColors.ENDC}'    
        if 'user_activity_log.csv' not in files:
            return False, f'\n{TerminalColors.WARNING}В каталоге {root} не найден файл `user_activity_log.csv`{TerminalColors.ENDC}'    
        if 'customer_research.csv' not in files:
            return False, f'\n{TerminalColors.WARNING}В каталоге {root} не найден файл `customer_research.csv`{TerminalColors.ENDC}'    

        return True, None

    return False, f'\n{TerminalColors.WARNING}Не найден каталог {full_lesson_path}/stage{TerminalColors.ENDC}'    
  

if __name__ == '__main__':
    COHORT_NUMBER = 99
    NICKNAME = 'tester'
    REPORT_ID = 'TWpBeU1pMHdOQzB6TUZRd05Ub3hPRG96TVFsMFpYTjBaWEk9'
    FILE_NAME = 'customer_research.csv'
    storage_url = f'https://storage.yandexcloud.net/s3-sprint3/cohort_{COHORT_NUMBER}/{NICKNAME}/{REPORT_ID}/{FILE_NAME}'
    df_order_log = pd.read_csv(storage_url)
    print(df_order_log)
    print(storage_url)
