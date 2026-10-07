import ast
import sys


is_py39 = sys.version_info >= (3, 9)


def py39_compatible(cls):
    "Change ast.Num and ast.Str to ast.Constant"

    if is_py39 and (cls == ast.Str or cls == ast.Num):
        return ast.Constant
    else:
        return cls


def read_src(fname):
    with open(fname, "r+", encoding='utf-8') as f:
        content = f.read()
    return content


def custom_assert(condition, msg):
    if not condition:
        print(msg)
        sys.exit(1)


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
                        or (isinstance(obj_parent, ast.Subscript) and aname == "value")  # noqa
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
