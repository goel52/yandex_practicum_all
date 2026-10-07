import importlib
import json
import sys
import time

import requests


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

def generate_report(nickname: str, cohort: int) -> str:
    
    url = 'https://d5dg1j9kt695d30blp03.apigw.yandexcloud.net'

    headers = {
        "X-API-KEY": "5f55e6c0-e9e5-4a9c-b313-63c01fc31460",
        "X-Nickname": nickname,
        "X-Cohort": str(cohort)
    }
    
    method_url = '/generate_report'

    r = requests.post(url + method_url, headers=headers)

    response_dict = json.loads(r.content)

    task_id = response_dict['task_id']
    
    return task_id

def de_test(
        full_lesson_path: str,
        realization_file='realization.py',
        sql_author=None,
        dsn='postgresql://jovyan:jovyan@localhost:5432/de'):

 
    sys.path.append(full_lesson_path)    
    try:
        user_params = importlib.import_module(realization_file[:-3])
    except Exception as e:
        return False, f'\n{TerminalColors.WARNING}{e.__class__.__name__}\n\n{e}{TerminalColors().ENDC}\n'

    try:
        task_id = user_params.task_id
        if type(task_id) != str:
            return False, f'\n{TerminalColors.WARNING}Переменная `task_id` в файле `realization.py` должна быть типа `str`{TerminalColors().ENDC}\n'
        nickname = user_params.nickname
        if type(nickname) != str:
            return False, f'\n{TerminalColors.WARNING}Переменная `nickname` в файле `realization.py` должна быть типа `str`{TerminalColors().ENDC}\n'
        cohort = user_params.cohort
        if type(cohort) != int:
            return False, f'\n{TerminalColors.WARNING}Переменная `cohort` в файле `realization.py` должна быть типа `int`{TerminalColors().ENDC}\n'
    except AttributeError:
        return False, f'\n{TerminalColors.WARNING}Не найдена переменная `task_id`{TerminalColors.ENDC}' 
    except Exception as e:
        return False, f'\n{TerminalColors.WARNING}{e}{TerminalColors.ENDC}' 

    ###
    # print('--- test generate_report ---')
    # nickname = 'tester'
    # cohort = 99
    # # task_id = generate_report(nickname, cohort)
    # task_id = 'MjAyMi0wNC0zMFQwNToxODozMQl0ZXN0ZXI='
    # # print('task_id', task_id)
    # # time.sleep(60)
    ###

    url = 'https://d5dg1j9kt695d30blp03.apigw.yandexcloud.net'
    
    headers = {
        "X-API-KEY": "5f55e6c0-e9e5-4a9c-b313-63c01fc31460",
        "X-Nickname": nickname,
        "X-Cohort": str(cohort)
    }

    #проверяем создание данных
    method_url = '/get_report'

    payload = {'task_id': task_id}

    try:
        r = requests.get(url + method_url, params=payload, headers=headers)
    except Exception as e:
        return False, e

    if r.status_code == 400:
        return False, f'\n{TerminalColors.WARNING}{r.text}{TerminalColors.ENDC}' 

    report_dict = json.loads(r.content)

    if report_dict['status'] != 'SUCCESS':
        return False, f'\n{TerminalColors.WARNING}Запрос данных с параметрами: nickname: {nickname}, cohort: {cohort}, task_id: {task_id} завершился с ошибкой.{TerminalColors.ENDC}' 

    return True, None
