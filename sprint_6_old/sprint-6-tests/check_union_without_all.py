import re
import sys


def check(sql_user):
    regex = r"union\s*^(?!\s*all).+"

    matches = re.finditer(regex, sql_user, re.IGNORECASE | re.MULTILINE)

    flag_re = False

    for matchNum, match in enumerate(matches, start=1):
        print (f'Найдено использование UNION без ALL (позиции {match.start()}-{match.end()}): {match.group()}')
        flag_re = True
    
    if flag_re:
        print('Не допускается использовать UNION без ALL')
        sys.exit()