import sys
import ast

class EmptyCodeError(Exception):
    """
    Ошибка для пустого кода
    """
    def __init__(self,):
        pass
    
class CompareWithTemplateError(Exception):
    """
    Ошибка сравнения
    """
    def __init__(self, code_block, value):
        self.code_block = code_block
        self.value = value

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class ErrorLogOut(object):
    """
    Обработчик ошибок студенческого кода
    и вывод несоответствий в темплейте и в коде студента
    """
    def __init__(self, src_errors, tree):
        self.code_parts = []
        self.split_template_code_by_strings(tree, src_errors)
    
    def split_template_code_by_strings(self, tree, src_errors):
        """
        Метод разбивает код прекода на блоки различных
        верхнеуровневых действий в коде
        """
        for node in ast.iter_child_nodes(tree):
            start = node.lineno - 1
            end = node.end_lineno - 1
            if start == end:
                self.code_parts.append(src_errors[start])
            else:
                src = "\n".join(src_errors[start:end])
                self.code_parts.append(src)
    
    def error_response(self, e, inner = False):
        """
        Метод отлавливает ошибки в уязвимых местах, выводит 
        сообщения с описанием ошибки в консоль и завершает
        исполнение
        """
        if e is not None:
            if inner:
                print(f"{bcolors.FAIL}Внутренняя ошибка платформы{bcolors.ENDC}\n")
                print("Обратитесь пожалуйста к разработчикам")
                sys.exit()
            
            if isinstance(e, EmptyCodeError):
                print(f"{bcolors.FAIL}Ваш код нельзя исполнить{bcolors.ENDC}\n")
                print(f"Вы сдали пустой код\n")
            elif isinstance(e, SyntaxError):
                print(f"{bcolors.FAIL}Ваш код нельзя исполнить{bcolors.ENDC}\n")
                print(f"Ошибка интерпретатора: {bcolors.FAIL}{type(e)}{bcolors.ENDC}")
                print(f"Найдена синтаксическая ошибка в файле {e.args[1][0]}, строка {e.args[1][1]}")
                print(f"Часть кода с ошибкой:\n\n{e.args[1][-1]}")
            elif isinstance(e, CompareWithTemplateError):
                print(f"{bcolors.FAIL}Ваш код не соответствует прекоду{bcolors.ENDC}\n")
                print(f"Не найдено значение {bcolors.FAIL}{e.value}{bcolors.ENDC}")
                print(f"Часть прекода в котором найдено несоответствие:\n\n{self.code_parts[e.code_block]}\n")
                print(f"{bcolors.WARNING}Сравните приложенный прекод со своим решением.{bcolors.ENDC}")
                print(f"{bcolors.WARNING}Убедитесь в том, что вы не перепутали строки прекода.{bcolors.ENDC}")
            else:
                print(f"{bcolors.FAIL}Ваш код нельзя исполнить{bcolors.ENDC}\n")
                print(f"Ошибка интерпретатора: {bcolors.FAIL}{type(e)}{bcolors.ENDC}")
            
            
            sys.exit()