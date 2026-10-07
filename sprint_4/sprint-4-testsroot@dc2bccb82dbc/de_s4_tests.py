import sys
import importlib

def run_tests(full_lesson_path = None, de_s4_test = None, realization_file = 'realization.sql'):
    sys.path.append('/app/sprint-4-tests')
    if de_s4_test is None:
        return f'Не указан код теста. {full_lesson_path}'
    my_test = importlib.import_module(de_s4_test)
    import de_s4_code

    all_keys_file = f'/app/sprint-4-tests/keys'
    all_keys = open(all_keys_file, 'r').read()
    task_keys = all_keys[10*(de_s4_code.DES3CODE[de_s4_test][0]-1):10+(de_s4_code.DES3CODE[de_s4_test][0]-1)*10]

    result = my_test.de_test(full_lesson_path)

    if result[0]:
        if de_s4_code.DES3CODE[de_s4_test][0] == 0:
            return f'\033[96m\n{de_s4_code.DES3CODE[de_s4_test][1]}\n\nДвигайтесь дальше!\n\033[0m'
        return f'\033[96m\n{de_s4_code.DES3CODE[de_s4_test][1]}\n\nДвигайтесь дальше! Ваш код: \033[92m{task_keys}\n\033[0m'
    return result[1]