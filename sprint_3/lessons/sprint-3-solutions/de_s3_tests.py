import sys
import importlib
import os

def run_tests(full_lesson_path = None, de_s3_test = None, realization_file = 'realization.sql'):
    sys.path.append('/app/sprint-3-tests')
    if de_s3_test is None:
        return f'Не указан код теста. {full_lesson_path}'
    my_test = importlib.import_module(de_s3_test)
    import de_s3_code

    all_keys_file = f'{os.path.dirname(os.path.abspath(__file__))}/keys'
    all_keys = open(all_keys_file, 'r').read()
    task_keys = all_keys[10*(de_s3_code.DES3CODE[de_s3_test][0]-1):10+(de_s3_code.DES3CODE[de_s3_test][0]-1)*10]

    result = my_test.de_test(full_lesson_path)

    if result[0]:
        return f'\033[96m\n{de_s3_code.DES3CODE[de_s3_test][1]}\n\nДвигайтесь дальше! Ваш код: \033[92m{task_keys}\n\033[0m'
    return result[1]

if __name__ == '__main__':
    full_lesson_path = '/home/hugin/YxTmPr/de-vsc-pg-server/vsc-pg-mb-airflow/sprint-3/lessons/2. Анализ вводных по задаче/6. Подключение к API/Задание 1'
    de_s3_test = 'de03020601'
    print(run_tests(full_lesson_path, de_s3_test))

if __name__ == '__main__':
    sys.path.append('/home/hugin/YxTmPr/sprint-3-tests')
    # my_test = importlib.import_module(de_s5_tests)
    import de_s3_code
    all_keys_file = f'/home/hugin/YxTmPr/sprint-3-tests/keys'
    all_keys = open(all_keys_file, 'r').read()
    for item, value in de_s3_code.DES3CODE.items():
        task_keys = all_keys[10*(de_s3_code.DES3CODE[item][0]-1):10+(de_s3_code.DES3CODE[item][0]-1)*10]
        print(item, task_keys, value)