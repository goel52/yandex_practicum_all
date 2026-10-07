import os
import sys
import importlib
import traceback
import ast

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

is_py39 = sys.version_info >= (3, 9)
def py39_compatible(cls):
    "Change ast.Num and ast.Str to ast.Constant"

    if is_py39 and (cls == ast.Str or cls == ast.Num):
        return ast.Constant
    else:
        return cls

class NodeQuery(ast.NodeVisitor):
    """
    Class to query ast tree in jQuery style

    NodeQuery(your_tree).node(ast.Assign, targets__0__id='a')

    First arg : Ast node type
    Keywords  : query to attributes in Django style
    """

    def __init__(self, node):
        self.result = []
        self.all = [node]
        self.q = {}
        self.anyvalue = object()

    def node(self, *args, **kwargs):
        if len(args) > 0:
            if isinstance(args[0], type) and issubclass(args[0], ast.AST):
                kwargs["class"] = py39_compatible(args[0])
            else:
                kwargs[args[0]] = self.anyvalue
        self.q = kwargs

        self.result = []
        for node in self.all:
            self.visit(node)
        nnext = NodeQuery(None)
        nnext.all = self.result

        return nnext

    def visit(self, node):
        """Custom Visit a node."""
        q = self.q
        fits = len(q) != 0

        override_result = None

        for key in q:
            path = key.split("__")
            obj = node
            obj_parent = obj
            for aname in path:
                if aname.isdecimal():
                    if (type(obj) is list or type(obj) is tuple) and (
                            int(aname) < len(obj)
                    ):
                        obj = obj[int(aname)]
                    else:
                        fits = False
                        break
                elif aname == "class" or aname == "nclass":
                    obj = obj.__class__
                elif hasattr(obj, aname):
                    obj_parent = obj
                    obj = getattr(obj, aname)
                elif is_py39 and (
                        (
                                isinstance(obj_parent, ast.Constant)
                                and (aname == "s" or aname == "n")
                        )
                        or (isinstance(obj_parent, ast.Subscript) and aname == "value")
                ):
                    pass
                else:
                    fits = False
                    break

            if fits and q[key] == self.anyvalue:
                override_result = obj
            else:
                fits = fits and (obj == py39_compatible(q[key]))

            if not fits:
                break

        if fits:
            if override_result is None:
                override_result = node
            self.result.append(override_result)

        return self.generic_visit(node)

    @property
    def exists(self):
        return len(self.all) > 0

    def attr(self, *args):
        """
        Get attr of node if it exists
        Ex:   node('...').attr('func__id')
        """
        nargs = len(args)
        if nargs == 0:
            return None
        elif nargs > 2:
            raise ValueError("Too many arguments")

        index = args[1] if nargs == 2 else 0

        if index >= len(self.all):
            return None
        path = args[0].split("__")
        obj = self.all[index]
        for aname in path:
            if aname.isdecimal():
                if (type(obj) is list or type(obj) is tuple) and (
                        int(aname) < len(obj)
                ):
                    obj = obj[int(aname)]
                else:
                    return None
            elif hasattr(obj, aname):
                obj = getattr(obj, aname)
            else:
                return None
        return obj

    def __bool__(self):
        return False


def de_test(
        full_lesson_path: str,
        realization_file='realization.py',
        sql_author=None,
        dsn='postgresql://jovyan:jovyan@localhost:5432/de'):

    sys.path.append(full_lesson_path)

    with open(f'{full_lesson_path}/{realization_file}', 'r') as file_user:
        src = file_user.read()

    try:
        user_py = importlib.import_module(realization_file[:-3])
    
        uh = user_py.headers

        if '**headers)' in src:
            ures = user_py.create_files_request(**uh)
        else:
            ures = user_py.create_files_request(uh)


    except Exception as e:
        return False, f'\n{TerminalColors.WARNING}{e.__class__.__name__}\n\n{e}{TerminalColors().ENDC}\n' 

    

    
    fname = realization_file
    
    tree = NodeQuery(ast.parse(src, fname, mode="exec"))

    function_req = tree.node(ast.FunctionDef, name = "create_files_request")
    if not function_req.exists:
        return False, f'\n{TerminalColors.WARNING}Не найдена функция `create_files_request`{TerminalColors.ENDC}' 

    # args_name = ["conn_name", "business_dt"]
    # for name in args_name:
    #     if not function_req.node(ast.arg, arg=name).exists:
    #         return False, f'\n{TerminalColors.WARNING}Не найден аргумент `{name}` в функции `create_files_request`{TerminalColors.ENDC}'

    calls = function_req.node(ast.Call)
    # basehook_call = calls.node(ast.Attribute).node(ast.Name, id='BaseHook')
    # if not basehook_call.exists:
    #     return False, f'\n{TerminalColors.WARNING}Не найдено использования метода `BaseHook`{TerminalColors.ENDC}'

    # get_connection_call = calls.node(ast.Attribute, attr = 'get_connection')
    # if not get_connection_call.exists:
    #     return False, f'\n{TerminalColors.WARNING}Проверьте правильность использования метода BaseHook (get_connection){TerminalColors.ENDC}'

    # requests_expr = function_req.node(ast.Expr).node(ast.Call).node(ast.Name, id = 'requests')
    # if not requests_expr.exists:
    #     return False, f'\n{TerminalColors.WARNING}Не найдено использования метода создания POST запроса (requests){TerminalColors.ENDC}'

    # post = function_req.node(ast.Expr).node(ast.Call).node(ast.Attribute, attr='post')
    # if not post.exists:
    #     return False, f'\n{TerminalColors.WARNING}Не найдено использования метода создания POST запроса (requests.post) {TerminalColors.ENDC}'

    # host_attr = function_req.node(ast.Expr).node(ast.Attribute, attr='host')
    # if not host_attr.exists:
    #     return False, f'\n{TerminalColors.WARNING}Не найден параметр `conn.host` метода requests.post{TerminalColors.ENDC}'

    # business_attr = function_req.node(ast.Expr).node(ast.Name, id='business_dt')
    # if not business_attr.exists:
    #     return False, f'\n{TerminalColors.WARNING}Не найден параметр `data={{`business_dt`:business_dt}}` метода requests.post{TerminalColors.ENDC}'

    python_operator = tree.node(ast.Call)
    if not python_operator.node(ast.Name, id="PythonOperator").exists:
        return False, f'\n{TerminalColors.WARNING}Не найдено вызова PythonOperator{TerminalColors.ENDC}'

    keywords_name = ["task_id", "python_callable", "op_kwargs", "dag"]
    for name in keywords_name:
        if not python_operator.node(ast.keyword, arg=name).exists:
            return False, f'\n{TerminalColors.WARNING}Не найдено аргумента `{name}` в функции PythonOperator{TerminalColors.ENDC}'

    callable = python_operator.node(ast.keyword, arg = "python_callable").node(ast.Name, id = "create_files_request")
    if not callable.exists:
        return False, f'\n{TerminalColors.WARNING}Проверьте правильность вызова PythonOperator (python_callable=create_files_request){TerminalColors.ENDC}'

    # def create_files_request( headers):
    #    api_conn = BaseHook.get_connection('create_files_api')
    
    if not function_req.node(ast.Assign, targets__0__id='api_conn').exists:
        return False, f'\n{TerminalColors.WARNING}Не найдена переменная api_conn функции create_files_request{TerminalColors.ENDC}\n'
    # if function_req.node(ast.Assign, targets__0__id='api_conn').all[0].value.func.value.id != 'BaseHook':
    #     return False, f'\n{TerminalColors.WARNING}api_conn функции create_files_request != BaseHook.get_connection(`create_files_api`){TerminalColors.ENDC}\n'
    # if function_req.node(ast.Assign, targets__0__id='api_conn').all[0].value.func.attr != 'get_connection':
    #     return False, f'\n{TerminalColors.WARNING}api_conn функции create_files_request != BaseHook.get_connection(`create_files_api`){TerminalColors.ENDC}\n'
    # if function_req.node(ast.Assign, targets__0__id='api_conn').all[0].value.args[0].value != 'create_files_api':
    #     return False, f'\n{TerminalColors.WARNING}api_conn функции create_files_request != BaseHook.get_connection(`create_files_api`){TerminalColors.ENDC}\n'

    # def create_files_request( headers):
    #    api_endpoint = api_conn.host
    if not function_req.node(ast.Assign, targets__0__id='api_endpoint').exists:
        return False, f'\n{TerminalColors.WARNING}Не найдена переменная api_endpoint функции create_files_request{TerminalColors.ENDC}\n'
    # if function_req.node(ast.Assign, targets__0__id='api_endpoint').all[0].value.value.id != 'api_conn':
    #     return False, f'\n{TerminalColors.WARNING}api_endpoint функции create_files_request != api_conn.host{TerminalColors.ENDC}\n'
    # if function_req.node(ast.Assign, targets__0__id='api_endpoint').all[0].value.attr != 'host':
    #     return False, f'\n{TerminalColors.WARNING}api_endpoint функции create_files_request != api_conn.host{TerminalColors.ENDC}\n'

    # def create_files_request( headers):
    #    method_url = '/generate_report'
    if not function_req.node(ast.Assign, targets__0__id='method_url').exists:
        return False, f'\n{TerminalColors.WARNING}Не найдена переменная method_url функции create_files_request{TerminalColors.ENDC}\n'
    # if function_req.node(ast.Assign, targets__0__id='method_url').all[0].value.value != '/generate_report':
    #     return False, f'\n{TerminalColors.WARNING}method_url функции create_files_request != `/generate_report`{TerminalColors.ENDC}\n'

    # def create_files_request( headers):
    #    r = requests.post('https://'+api_endpoint + method_url, headers=headers)
    if not function_req.node(ast.Assign, targets__0__id='r').exists:
        return False, f'\n{TerminalColors.WARNING}Не найдена переменная r функции create_files_request{TerminalColors.ENDC}\n'
    if not function_req.node(ast.Assign, value__func__value__id='requests').exists:
        return False, f'\n{TerminalColors.WARNING}Переменная r функции create_files_request != requests.post(`https://`+api_endpoint + method_url, headers=headers){TerminalColors.ENDC}\n'
    if not function_req.node(ast.Assign, value__func__attr='post').exists:
        return False, f'\n{TerminalColors.WARNING}Переменная r функции create_files_request != requests.post(`https://`+api_endpoint + method_url, headers=headers){TerminalColors.ENDC}\n'
    if not function_req.node(ast.Assign, value__args__0__left__left__value='https://').exists:
        return False, f'\n{TerminalColors.WARNING}Переменная r функции create_files_request != requests.post(`https://`+api_endpoint + method_url, headers=headers){TerminalColors.ENDC}\n'
    if not function_req.node(ast.Assign, value__args__0__left__right__id='api_endpoint').exists:
        return False, f'\n{TerminalColors.WARNING}Переменная r функции create_files_request != requests.post(`https://`+api_endpoint + method_url, headers=headers){TerminalColors.ENDC}\n'
    if not function_req.node(ast.Assign, value__args__0__right__id='method_url').exists:
        return False, f'\n{TerminalColors.WARNING}Переменная r функции create_files_request != requests.post(`https://`+api_endpoint + method_url, headers=headers){TerminalColors.ENDC}\n'
    if not function_req.node(ast.Assign, value__keywords__0__arg='headers').exists:
        return False, f'\n{TerminalColors.WARNING}Переменная r функции create_files_request != requests.post(`https://`+api_endpoint + method_url, headers=headers){TerminalColors.ENDC}\n'
    if not function_req.node(ast.Assign, value__keywords__0__value__id='headers').exists:
        return False, f'\n{TerminalColors.WARNING}Переменная r функции create_files_request != requests.post(`https://`+api_endpoint + method_url, headers=headers){TerminalColors.ENDC}\n'

    # def create_files_request( headers):
    #    response_dict = json.loads(r.content)
    if not function_req.node(ast.Assign, targets__0__id='response_dict').exists:
        return False, f'\n{TerminalColors.WARNING}Не найдена переменная response_dict функции create_files_request{TerminalColors.ENDC}\n'
    if not function_req.node(ast.Assign, value__func__value__id='json').exists:
        return False, f'\n{TerminalColors.WARNING}Переменная response_dict функции create_files_request != json.loads(r.content){TerminalColors.ENDC}\n'
    if not function_req.node(ast.Assign, value__func__attr='loads').exists:
        return False, f'\n{TerminalColors.WARNING}Переменная response_dict функции create_files_request != json.loads(r.content){TerminalColors.ENDC}\n'
    if not function_req.node(ast.Assign, value__args__0__value__id='r').exists:
        return False, f'\n{TerminalColors.WARNING}Переменная response_dict функции create_files_request != json.loads(r.content){TerminalColors.ENDC}\n'
    if not function_req.node(ast.Assign, value__args__0__attr='content').exists:
        return False, f'\n{TerminalColors.WARNING}Переменная response_dict функции create_files_request != json.loads(r.content){TerminalColors.ENDC}\n'

    # task = PythonOperator(task_id='create_files_request',
    #                                     python_callable=create_files_request,
    #                                     op_kwargs={
    #                                                 'headers': headers
    #                                                 },
    #                                     dag=dag)
    if not tree.node(ast.Assign, targets__0__id='task').exists:
        return False, f'\n{TerminalColors.WARNING}Не найдена переменная task{TerminalColors.ENDC}\n'
    
    # продолжить здесь







    # op_kwargs = python_operator.node(ast.keyword, arg = "op_kwargs").node(ast.Name, id = "business_dt")
    # if not op_kwargs.exists:
    #     return False, f'\n{TerminalColors.WARNING}Проверьте правильность вызова PythonOperator{TerminalColors.ENDC}'

    # проверка импортом

    sys.path.append(full_lesson_path)

    try:
        user_py = importlib.import_module(realization_file[:-3])



    except Exception as e:
        return False, f'\n{TerminalColors.WARNING}{e.__class__.__name__}\n\n{e}{TerminalColors().ENDC}\n'


    return True, None
    