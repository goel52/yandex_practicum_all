import hashlib
import os


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


def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def de_test(
        full_lesson_path: str,
        realization_file='realization.py',
        sql_author=None,
        dsn='postgresql://jovyan:jovyan@localhost:5432/de'):

    stage_files = os.walk('/data')
    # stage_files = os.walk('/home/hugin/YxTmPr/YxTmDe/sp6/tests')


    # s3files = ('users.csv', 'groups_OLD.csv', 'dialogs.csv')

    s3files = {
        'groups_OLD.csv': 'a588dac8169144d3c8f3b98c1489e6c9',
        'users.csv': '88af3e52db674ebd0beb0b61881bdfb0',
        'dialogs.csv': '61fc274aafb756ecbdd44e7136dc4b58'
    }

    for root, dirs, files in stage_files:
        for s3file in s3files.keys():
            if s3file not in files:
                return False, f'\n{TerminalColors.WARNING}В каталоге `{root}` не найден файл `{s3file}`{TerminalColors.ENDC}'    
            md5file = md5(f'{root}/{s3file}')
            # print(md5file)
            if md5file != s3files[s3file]:
                return False, f'\n{TerminalColors.WARNING}Проверьте что скачали файл верно. Контрольная сумма файла `{s3file}` не равна {s3files[s3file]}.{TerminalColors.ENDC}'
            print(s3file, md5(f'{root}/{s3file}'))

        return True, None

    return False, f'\n{TerminalColors.WARNING}Не найден каталог {full_lesson_path}/stage{TerminalColors.ENDC}'    
    



if __name__ == '__main__':
    print(de_test(''))
