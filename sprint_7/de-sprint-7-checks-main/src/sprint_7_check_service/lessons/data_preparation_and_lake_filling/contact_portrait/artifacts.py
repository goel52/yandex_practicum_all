"""Static validation of submission artifacts; shell and DAG code are never run."""
import ast
from pathlib import PurePosixPath
import shlex

FILES = ('connection_interests.py', 'run_jobs.sh', 'dag.py')


def command_args(command):
    tokens = shlex.split(command, comments=True)
    if not tokens or PurePosixPath(tokens[0]).name != 'spark-submit':
        return None
    for i, token in enumerate(tokens[1:], 1):
        if PurePosixPath(token).name == 'connection_interests.py':
            return tokens[i + 1:]
    raise ValueError('В spark-submit укажите connection_interests.py.')


def validate_paths(args, personal=False):
    if len(args) != 6:
        raise ValueError('Передайте шесть аргументов: date, days_count, events_base_path, '
                         'interests_base_path, verified_tags_path, output_base_path.')
    if str(args[1]) != '7':
        raise ValueError('Для задания требуется глубина 7 дней.')
    if not all(isinstance(value, str) for value in args):
        raise ValueError('Аргументы запуска должны быть строками.')
    expected = ('data/events', 'data/analytics/user_interests_d7',
                'data/analytics/connection_interests_d7')
    roots = []
    for path, suffix in zip((args[2], args[3], args[5]), expected):
        parts = PurePosixPath(path).parts
        if (len(parts) < 4 or parts[:2] != ('/', 'user')
                or str(PurePosixPath(*parts[3:])) != suffix):
            raise ValueError(f'Путь должен иметь вид /user/<логин>/{suffix}.')
        roots.append(parts[2])
    if personal:
        if len(set(roots)) != 1 or roots[0] in ('prod', 'master', 'examples'):
            raise ValueError('В DAG используйте одну личную папку для событий, интересов и результата.')
    elif roots != ['prod'] * 3:
        raise ValueError('В run_jobs.sh используйте пути продового слоя /user/prod/.')
    if not args[4].endswith('/data/snapshots/tags_verified/actual'):
        raise ValueError('Используйте актуальный снапшот tags_verified/actual.')
    if not personal and not args[4].startswith(('/user/prod/', '/user/master/')):
        raise ValueError('Для run_jobs.sh используйте актуальный продовый или общий снапшот /user/master/.')


def check_commands(source):
    found = False
    for line in source.replace('\\\n', ' ').splitlines():
        args = command_args(line)
        if args is None:
            continue
        found = True
        validate_paths(args)
        if args[0] != '2022-05-25':
            raise ValueError('В run_jobs.sh укажите дату 2022-05-25.')
    if not found:
        raise ValueError('В run_jobs.sh не найдена команда spark-submit.')


def check_dag(source):
    tree = ast.parse(source, filename='dag.py')
    aliases = {n.asname or n.name: n.name for node in ast.walk(tree)
               if isinstance(node, (ast.Import, ast.ImportFrom)) for n in node.names}
    values = {node.targets[0].id: node.value for node in ast.walk(tree)
              if isinstance(node, ast.Assign) and len(node.targets) == 1
              and isinstance(node.targets[0], ast.Name)}

    def call_name(node):
        if isinstance(node, ast.Name):
            return aliases.get(node.id, node.id)
        if isinstance(node, ast.Attribute):
            return node.attr
        return ''

    def literal(node, seen=frozenset()):
        if isinstance(node, ast.Name) and node.id in values and node.id not in seen:
            return literal(values[node.id], seen | {node.id})
        if isinstance(node, (ast.List, ast.Tuple)):
            return [literal(item, seen) for item in node.elts]
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            return literal(node.left, seen) + literal(node.right, seen)
        if isinstance(node, ast.JoinedStr):
            return ''.join(str(literal(item.value if isinstance(item, ast.FormattedValue)
                                       else item, seen)) for item in node.values)
        try:
            return ast.literal_eval(node)
        except (ValueError, TypeError):
            raise ValueError('Для проверки DAG задайте application и аргументы '
                             'строками, списком строк или переменными с такими значениями.') from None

    tasks = {}
    for name, value in values.items():
        if not isinstance(value, ast.Call):
            continue
        kind = call_name(value.func)
        kw = {arg.arg: arg.value for arg in value.keywords}
        if kind == 'SparkSubmitOperator':
            if 'application' not in kw or 'application_args' not in kw:
                continue
            app = PurePosixPath(literal(kw['application'])).name
            args = literal(kw['application_args'])
        elif kind == 'BashOperator' and 'bash_command' in kw:
            command = literal(kw['bash_command'])
            tokens = shlex.split(command)
            apps = [PurePosixPath(t).name for t in tokens if t.endswith('.py')]
            if not apps:
                continue
            app = apps[0]
            i = next(i for i, t in enumerate(tokens) if t.endswith('.py'))
            args = tokens[i + 1:]
        else:
            continue
        tasks[name] = (app, args)

    if not any(isinstance(n, ast.Call) and call_name(n.func) == 'DAG'
               for n in ast.walk(tree)):
        raise ValueError('В файле не найдено объявление DAG.')
    edges = set()

    def nodes(node):
        if isinstance(node, ast.Name):
            return {node.id}
        if isinstance(node, (ast.List, ast.Tuple)):
            return set().union(*(nodes(item) for item in node.elts))
        if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.RShift, ast.LShift)):
            left, right = nodes(node.left), nodes(node.right)
            edges.update((a, b) if isinstance(node.op, ast.RShift) else (b, a)
                         for a in left for b in right)
            return right
        return set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Expr):
            nodes(node.value)
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.args and node.func.attr in ('set_upstream', 'set_downstream')):
            left, right = nodes(node.func.value), nodes(node.args[0])
            edges.update((a, b) if node.func.attr == 'set_downstream' else (b, a)
                         for a in left for b in right)

    def upstream(source, target, seen=frozenset()):
        if source == target:
            return True
        if source in seen:
            return False
        return any(upstream(b, target, seen | {source}) for a, b in edges if a == source)

    if any(upstream(b, a) for a, b in edges):
        raise ValueError('В зависимостях DAG найден цикл.')

    candidates = [(name, args) for name, (app, args) in tasks.items()
                  if app == 'connection_interests.py']
    if not candidates:
        raise ValueError('В DAG не найден запуск connection_interests.py.')
    for name, args in candidates:
        validate_paths(args, personal=True)
        producers = [producer for producer, (app, params) in tasks.items()
                     if app == 'user_interests.py' and len(params) == 4
                     and params[:3] == args[:3] and params[3] == args[3]]
        if not any(upstream(producer, name) for producer in producers):
            raise ValueError('Джоба контактов должна зависеть от user_interests за те же дату, '
                             '7 дней и входные/выходные пути.')
