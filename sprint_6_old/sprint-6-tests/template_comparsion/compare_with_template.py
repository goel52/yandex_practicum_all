from pprintast import pprintast as ppast
import ast
from template_comparsion.errors_response import ErrorLogOut, EmptyCodeError, CompareWithTemplateError

CODE_KEYWORD = "student_code_should_be_here"
STR_TO_REPLACE = ["*ваш код здесь*"]

def read_src(name):
    """
    Метод для чтения кода, на вход принимает путь
    """
    with open(name) as f:
        src = f.read()
    return src

def tree_from(src, fname):
    """
    Метод для построения ast-дерева
    """
    try:
        tree = ast.parse(src, fname, mode="exec")
    except Exception as e:
        return None, e
    _, value = next(ast.iter_fields(tree))
    if not value:
        return None, EmptyCodeError()
    return tree, None

def prepare_code(name, is_template = True, ErrorLog = None, str_to_rpl=STR_TO_REPLACE):
    """
    Метод для подготовке кода к сравнению.
    
    Для темплейта метод заменяет фразы *ваш код здесь* на
    CODE_KEYWORD чтобы можно было построить дерево и 
    игнорировать ветви по ключевому слову.
    Также при инициализации дерева темплейта происходит 
    инициализация отловщика ошибок
    
    Для студента просто происходит построение дерева,
    никакие изменения в код не вносятся. Если у студента 
    синтаксическая ошибка, то она появится на этом этапе
    """
    src = read_src(name)
    if is_template:
        src_errors = src.split("\n")
        for replaced in str_to_rpl:
            src = src.replace(replaced, CODE_KEYWORD)

    tree, e = tree_from(src, name)
    if is_template:
        ErrorLog = ErrorLogOut(src_errors, tree)
        ErrorLog.error_response(e, inner=True)
    else:
        ErrorLog.error_response(e)
    nodes = recursive_walk(tree, [])
    return nodes, ErrorLog

class Nodes(object):
    """
    Класс в котором хранятся конечные ветви дерева
    Также реализован метод сравнения двух нод между собой
    """
    def __init__(self, path, value):
        self.absolute_path = path
        self.value = value
        self.to_group = []
        self.path = ""
        self.timely_path_process()

    def timely_path_process(self):
        path = []
        nodes = self.absolute_path.split('__')
        for node in nodes:
            if node.isdigit():
                self.to_group.append(int(node))
            else:
                path.append(node)
        self.path = "__".join(path)
        
    def equals(self, node):
        return self.value == node.value and self.path == node.path
    
def recursive_walk(node, nodes_description, node_path=""):
    """
    Рекурсивный поиск конечных ветвей дерева для кода
    """
    for fieldname, value in ast.iter_fields(node):
        if fieldname in ['level', 'type_comment']:
            continue
        if isinstance(value, (ast.Store, ast.Load)):
            continue
        
        if len(node_path)==0:
            timely_path = fieldname
        else:
            timely_path = node_path + "__" + fieldname

        value_is_node = not isinstance(value, (int, float, str, list))
        if value_is_node and value is not None:
            recursive_walk(value, nodes_description, timely_path)
        elif isinstance(value, list):
            for i, val in enumerate(value):
                nodes_description = recursive_walk(val, nodes_description, timely_path+"__"+str(i))
        if isinstance(value, (str, float, int)) and value != CODE_KEYWORD:
            node = Nodes(timely_path, value)
            nodes_description.append(node)
    return nodes_description

def compare_nodes(nodes_template, nodes_user, ErrorLog):
    """
    Метод сравнения дерева темплейта со студенческим кодом.
    
    Метод последовательно проходит по ветвям дерева темплейта и 
    ищет соответствие в дереве решения студента. Если находит
    соответствие, то дальнейший поиск продолжает со следующего элемента 
    дерева студента не начиная сначала. Соответственно, если студент 
    поменяет в темплейте строки, то его код не будет принят.
    Но при этом между строк студент может добавлять любой код.
    """
    nodes_template_n = len(nodes_template)
    nodes_user_n = len(nodes_user)
    i, j = 0, 0
    flag = True

    while i != nodes_template_n:
        node_t = nodes_template[i]
        node_u = nodes_user[j]   

        if node_t.equals(node_u):
            i += 1
            j += 1
            continue
        elif j == nodes_user_n - 1:
            flag = False
            break
        else:
            j += 1
            
    if not flag:
        e = CompareWithTemplateError(node_t.to_group[0], node_t.value)
        ErrorLog.error_response(e)

