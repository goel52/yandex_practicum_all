import ast
import sys


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

    with open(f'{full_lesson_path}/{realization_file}', 'r') as file_user:
        src = file_user.read()

    fname = realization_file

    tree = NodeQuery(ast.parse(src, fname, mode="exec"))

    constants = (
        'nickname',
        'cohort',
        'api_token'
    )

    for constant in constants:
        if not tree.node(ast.Assign, targets__0__id=constant).exists:
            return False, f'\n{TerminalColors.WARNING}Не найдено объявление переменной `{constant}`{TerminalColors.ENDC}'

    if not tree.node(ast.FunctionDef, name='create_files_request').exists:
        return False, f'\n{TerminalColors.WARNING}Не найдена функция `create_files_request`{TerminalColors.ENDC}'

    create_files_request = tree.node(ast.FunctionDef, name='create_files_request')

    if not create_files_request.node(ast.Assign, targets__0__id='api_conn').exists:
        return False, f'\n{TerminalColors.WARNING}В функции `create_files_request` не найдено объявление переменной `api_conn`{TerminalColors.ENDC}'

    if not create_files_request.node(ast.Assign, value__func__value__id='BaseHook').exists:
        return False, f"\n{TerminalColors.WARNING}В функции `create_files_request` переменная `api_conn` != BaseHook.get_connection('create_files_api'){TerminalColors.ENDC}"

    if not tree.node(ast.Assign, targets__0__id='task').exists:
        return False, f'\n{TerminalColors.WARNING}Не найдено объявление переменной task{TerminalColors.ENDC}'

    task = tree.node(ast.Assign, targets__0__id='task')

    if not task.node(ast.Call, func__id = 'PythonOperator').exists:
        return False, f'\n{TerminalColors.WARNING}task != PythonOperator(...){TerminalColors.ENDC}'

    if not task.node(ast.Call, keywords__0__arg = 'task_id').exists:
        return False, f'\n{TerminalColors.WARNING}Не найдено обявление параметра task_id функции PythonOperator(task_id="create_files_request"){TerminalColors.ENDC}'

    if not task.node(ast.Call, keywords__1__arg = 'python_callable').exists:
        return False, f'\n{TerminalColors.WARNING}Не найдено обявление параметра python_callable функции PythonOperator(..., python_callable=create_files_request){TerminalColors.ENDC}'

    if not task.node(ast.Call, keywords__2__arg = 'op_kwargs').exists:
        return False, f'\n{TerminalColors.WARNING}Не найдено обявление параметра op_kwargs функции PythonOperator(..., ..., op_kwargs={{"headers": headers}}){TerminalColors.ENDC}'

    if not task.node(ast.Call, keywords__3__arg = 'dag').exists:
        return False, f'\n{TerminalColors.WARNING}Не найдено обявление параметра dag функции PythonOperator(..., ..., ..., dag=dag{TerminalColors.ENDC}'

    return True, None
