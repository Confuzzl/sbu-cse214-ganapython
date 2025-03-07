import ast
import builtins
from macro import MacroList

DATA_STRUCTURE_TYPES = {
    "Array": "array",
    "List": "dynamic array",
    "Mat": "2-D matrix",
    "SLL": "SinglyLinkedList",
    "CSLL": "CircularSinglyLinkedList",
    "DLL": "DoublyLinkedList",
    "Stack": "stack",
    "Queue": "queue",
    "Deque": "deque",
    "BST": "BalancedSearchTree",
    "Set": "hash set",
    "Map": "hash map",
    "MinHeap": "min-heap",
    "MaxHeap": "max-heap"
}

c: MacroList = None
line_count = 0

# SCOPE_START = r"\begin{tabular}{!{\color{laddercolor}\vline}@{\hskip 1em}l}""\n"
# SCOPE_END = r"\end{tabular}"
SCOPE_START = r"\begin{scope}""\n"
SCOPE_END = r"\end{scope}"
NL = r"\\""\n"


ELLIPSIS = r"$\,\dots\,$"


def function_name_transform(str: str):
    def caps(str: builtins.str):
        return str[0].upper() + str[1:]
    return "-".join(caps(word) for word in str.split("_"))


def parse_if_or_elif(node: ast.If, keyword: str):
    # out = f"{c._con(keyword)} {parse(node.test)} {c._con("then")}" + NL
    out = getattr(c, f"_{keyword}")(parse(node.test)) + NL
    out += SCOPE_START
    for if_node in node.body:
        out += parse(if_node)
    out += SCOPE_END
    if len(node.orelse) == 0:
        return out

    global line_count
    line_count += 1
    out += NL

    if type(node.orelse[0]) == ast.If:
        out += parse_if_or_elif(node.orelse[0], "elif")
    else:
        out += c._else() + NL
        out += SCOPE_START
        for else_node in node.orelse:
            out += f"{parse(else_node)}"
        out += SCOPE_END
    return out


def parse_ternary(node: ast.IfExp):
    return f"({parse(node.test)}) ? {parse(node.body)} : {parse(node.orelse)}"


def parse_assign_array_0():
    return rf"[{parse_constant(ast.Constant(1))}{ELLIPSIS}{parse_name(ast.Name("n"))}]"


def parse_assign_array_1(first: ast.Tuple | ast.Subscript):
    match type(first):
        case ast.Tuple:
            return rf"{parse_assign_array_0()} $\leftarrow$ [{parse(first.elts[0])}{ELLIPSIS}{parse(first.elts[1])}]"
        case ast.Subscript:
            return rf"{parse_assign_array_0()} $\leftarrow$ {parse_array_subscript(first)}"
        case _:
            raise ValueError(f"invalid argument type {type(first)} for Array")


def parse_assign_array_2(first: ast.Tuple, second: ast.Tuple | ast.Subscript):
    match type(second):
        case ast.Tuple:
            return rf"[{parse(first.elts[0])}{ELLIPSIS}{parse(first.elts[1])}]" + r" $\leftarrow$ " + \
                rf"[{parse(second.elts[0])}{ELLIPSIS}{parse(second.elts[1])}]"
        case ast.Subscript:
            return rf"[{parse(first.elts[0])}{ELLIPSIS}{parse(first.elts[1])}]" + r" $\leftarrow$ " + \
                parse_array_subscript(second)
        case _:
            raise ValueError(f"invalid argument type {type(first)} for Array")


def parse_array_subscript(node: ast.Subscript):
    match type(node.slice):
        case ast.Slice:
            return rf"{parse_name(node.value)}[{parse(node.slice.lower)}{ELLIPSIS}{parse(node.slice.upper)}]"
        case _:
            return rf"{parse_name(node.value)}[{parse(node.slice)}]"


def parse_array_type_annotation(args: list[ast.AST]):
    match len(args):
        case 0:
            return parse_assign_array_0()
        case 1:
            return rf"[{parse(args[0].elts[0])}{ELLIPSIS}{parse(args[0].elts[1])}]"
        case _:
            raise ValueError(
                "invalid number of arguments passed to Array")


def parse_print(node: ast.Constant | ast.JoinedStr):
    def parse_fstring(node: ast.JoinedStr):
        def parse_val(node: ast.FormattedValue | ast.Constant):
            match type(node):
                case ast.FormattedValue:
                    parsed = ast.parse(node.value)
                    return parse(parsed)
                case ast.Constant:
                    return node.value
                case _:
                    raise ValueError(
                        f"invalid fstring parameter type {type(node)}")
        return "".join(parse_val(val) for val in node.values)

    match type(node):
        case ast.Constant:
            # return f"{c._con("print")} {node.value}"
            return c._print(node.value)
        case ast.JoinedStr:
            # return f"{c._con("print")} {parse_fstring(node)}"
            return c._print(parse_fstring(node))
        case _:
            raise ValueError(f"unknown type {type(node)} passed to print")


def parse_call(node: ast.Call):
    out = ""
    match type(node.func):
        case ast.Name:
            match node.func.id:
                case "print":
                    return parse_print(node.args[0])
            out += c._func(function_name_transform(node.func.id))
        case ast.Attribute:
            out += f"{parse(node.func.value)}." + \
                c._method(function_name_transform(node.func.attr))
    out += f"({", ".join(parse(arg) for arg in node.args)})"
    return out


def parse_while(node: ast.While):
    out = c._while(parse(node.test)) + NL
    out += SCOPE_START
    for if_node in node.body:
        out += parse(if_node)
    out += SCOPE_END
    return out


def parse_for(node: ast.For):
    def parse_normal_for():
        # out = c._con("for") + rf" {parse(node.target)} $\leftarrow$ "
        out = ""
        lower = None
        upper = None
        direction = +1
        to = "to"
        crement = None
        args = node.iter.args
        if len(args) == 1:
            lower = c._num(1)
            upper = parse(node.iter.args[0])
        else:
            lower = parse(node.iter.args[0])
            upper = parse(node.iter.args[1])
        if len(args) == 3:
            value = None
            match type(args[2]):
                case ast.UnaryOp:
                    if type(args[2].op) == ast.USub:
                        direction = -1
                    else:
                        direction = +1
                    value = args[2].operand
                case _:
                    value = args[2]
            match direction:
                case -1:
                    to = "down to"
                case 1:
                    to = "to"
            if value.value != 1:
                crement = parse(value)
        cond = rf"{parse(node.target)} $\leftarrow$ {lower}"
        match to:
            case "to":
                out += c._forinc(cond, upper,
                                 crement) if crement else c._for(cond, upper)
            case "down to":
                out += c._fordec(cond, upper,
                                 crement) if crement else c._fordown(cond, upper)
        return out

    def parse_for_each():
        return c._con("foreach") + " " + \
            c._op("child") + rf" {parse(node.target)} " + c._op("of") + \
            f" {parse(node.iter)} " + c._op("node") + \
            " " + c._con("do")

    out = ""
    match type(node.iter):
        case ast.Call:
            out += parse_normal_for()
        case ast.Attribute:
            out += parse_for_each()
    out += NL
    out += SCOPE_START
    for body_node in node.body:
        out += parse(body_node)
    out += SCOPE_END
    return out


def parse_assign(node: ast.Assign):
    def data_structure_prelude(data_type: str):
        return f"{c._op(f"Create {"an" if data_type == "Array" else "a"}")} {c._type(DATA_STRUCTURE_TYPES[data_type])} {parse_name(node.targets[0])}"

    def data_structure(data_type: str):
        out = data_structure_prelude(data_type)
        args = node.value.args
        match data_type:
            case "Array":
                match len(args):
                    case 0:
                        out += parse_assign_array_0()
                    case 1:
                        out += parse_assign_array_1(node.value.args[0])
                    case 2:
                        out += parse_assign_array_2(node.value.args[0],
                                                    node.value.args[1])
                    case _:
                        raise ValueError(
                            "invalid number of arguments passed to Array")
            case "List":
                out += r" $\leftarrow$ "
                if len(args) == 0:
                    out += r"[\;]"
                if len(args) == 1:
                    out += parse(args[0])
            case "Mat":
                if len(args) != 2:
                    raise ValueError(
                        "Mat() requires tuple arguments (1, n), (1, m)")
                out += f"[{parse(args[0].elts[0])}{ELLIPSIS}{parse(args[0].elts[1])}]" + \
                    f"[{parse(args[1].elts[0])}{ELLIPSIS}{parse(args[1].elts[1])}]"
        return out

    if (type(node.targets[0]), type(node.value)) == (ast.Tuple, ast.Tuple):
        assignments = zip(node.targets[0].elts, node.value.elts)
        return "; ".join(rf"{parse(a)} $\leftarrow$ {parse(b)}" for a, b in assignments)

    if type(node.value) == ast.Call and type(node.value.func) == ast.Name:
        if (data_type := node.value.func.id) in DATA_STRUCTURE_TYPES.keys():
            return data_structure(data_type)

    return rf"{parse(node.targets[0])} $\leftarrow$ {parse(node.value)}"


def parse_function_args(args: list[ast.arg]):
    def parse_arg(arg: ast.arg):
        if arg.annotation == None:
            return c._var(arg.arg)
        # if type(arg.annotation) != ast.Call:
        #     raise ValueError("algorithm arg type annotation must be call")
        call = arg.annotation
        if call.func.id != "Array":
            raise ValueError(
                "algorithm arg type annotation of call must be Array")
        return f"{c._var(arg.arg)}{parse_array_type_annotation(call.args)}"
    return ", ".join(parse_arg(arg) for arg in args)


def parse_function_def(node: ast.FunctionDef):
    global line_count
    line_count = 0

    out = r"\begin{pseudocode}"f"{{{function_name_transform(node.name)}}}"f"{{{parse_function_args(node.args.args)}}}\n"
    body = ""
    for body_node in node.body:
        body += parse(body_node)

    out += r"\begin{tabular}{@{}r}""\n"
    out += "".join(rf"{i}\\" for i in range(1, line_count + 1)) + "\n"
    out += r"\end{tabular}""\n"
    out += r"\begin{tabular}{@{}l@{}}""\n"
    out += body
    out += r"\end{tabular}" + NL
    out += r"\end{pseudocode}"
    return out


def parse_constant(node: ast.Constant):
    match node.value:
        case True:
            return c._true()
        case False:
            return c._false()
        case None:
            return c._null()
        case _:
            match type(node.value):
                case builtins.int | builtins.float:
                    return c._num(node.value)
                case builtins.str:
                    return c._str(node.value)
                case _:
                    raise ValueError(
                        f"constant value of {type(node.value)} not recognized")


def parse_unary_op(node: ast.UnaryOp):
    match type(node.op):
        case ast.Not:
            if type(node.operand) == ast.BoolOp:
                return f"{c._not()} ({parse_binary_bool_op(node.operand)})"
            return f"{c._not()} {parse(node.operand)}"
        case ast.UAdd:
            if type(node.operand) == ast.BinOp:
                return f"$+$({parse_bin_op(node.operand)})"
            return f"$+${parse(node.operand)}"
        case ast.USub:
            if type(node.operand) == ast.BinOp:
                return f"$-$({parse_bin_op(node.operand)})"
            return f"$-${parse(node.operand)}"
        case _:
            raise ValueError(
                f"unsupported unary operator of type {type(node.op)}")


def parse_binary_bool_op(node: ast.BoolOp, brackets=False):
    def parse_bool_op(op: ast.And | ast.Or):
        match type(op):
            case ast.And:
                return c._and()
            case ast.Or:
                return c._or()
            case _:
                raise ValueError("unreachable")

    def parse_potential_or_brackets(node: ast.AST):
        match type(node):
            case ast.BoolOp:
                return parse_binary_bool_op(node, True)
            case _:
                return parse(node)

    if type(node.op) == ast.And:
        return f" {parse_bool_op(node.op)} ".join(parse_potential_or_brackets(val) for val in node.values)

    if brackets and type(node.op) == ast.Or:
        return f"({parse_binary_bool_op(node)})"

    return f" {parse_bool_op(node.op)} ".join(parse(val) for val in node.values)


def parse_bin_op(node: ast.BinOp, parent_op_type: type = None):
    ORDER = {ast.Pow: 0, ast.Mult: 1, ast.Div: 1,
             ast.FloorDiv: 1, ast.Mod: 1,  ast.Add: 2, ast.Sub: 2, None: 100}
    this_type = type(node.op)

    def parse_operand(node: ast.AST):
        nonlocal this_type
        match type(node):
            case ast.BinOp:
                return parse_bin_op(node, this_type)
            case _:
                return parse(node)

    def parse_bin(node: ast.BinOp):
        def symbol(operator: ast.AST):
            match type(operator):
                case ast.Mult:
                    return r"$\times$"
                case ast.Div:
                    return "$/$"
                case ast.Mod:
                    return r"$\%$"
                case ast.Add:
                    return "$+$"
                case ast.Sub:
                    return "$-$"
                case _:
                    raise ValueError(f"unreachable {type(operator)}")

        match type(node.op):
            case ast.Pow:
                return rf"$\text{{{parse_operand(node.left)}}}^\text{{{parse_operand(node.right)}}}$"
            case ast.FloorDiv:
                return rf"$\lfloor${parse_operand(node.left)} $/$ {parse_operand(node.right)}$\rfloor$"
            case ast.Mult:
                def single(node: ast.AST):
                    return type(node) == ast.Name and len(node.id) == 1

                l, r = type(node.left), type(node.right)
                match (l, r):
                    case (ast.Constant, ast.Name):
                        if single(node.right):
                            return f"{parse_constant(node.left)}{parse_name(node.right)}"
                    case (ast.Name, ast.Name):
                        if single(node.left) and single(node.right):
                            return f"{parse_name(node.left)}{parse_name(node.right)}"
                    case (ast.BinOp, ast.Name):
                        if single(node.left.right) and single(node.right):
                            return f"{parse_bin(node.left)}{parse_name(node.right)}"
                    case (ast.Name, ast.BinOp):
                        if single(node.left) and single(node.right.left):
                            return f"{parse_name(node.left)}{parse_bin(node.right)}"
        return f"{parse_operand(node.left)} {symbol(node.op)} {parse_operand(node.right)}"
    parsed = parse_bin(node)
    if this_type != parent_op_type and \
            this_type != ast.FloorDiv and \
            ORDER[this_type] >= ORDER[parent_op_type]:
        return f"({parsed})"
    return parsed


def parse_name(node: ast.Name):
    if node.id == "_":
        return ""
    return c._var(node.id.replace("_", r"\_"))


def parse_kv_pair(node: ast.List):
    return rf"$\langle${', '.join(parse(e) for e in node.elts)}$\rangle$"


def parse_tuple(node: ast.Tuple):
    return f"({", ".join(parse(val) for val in node.elts)})"


def parse(node: ast.AST):
    out = ""
    match type(node):
        case ast.Constant:
            out = parse_constant(node)
        case ast.Eq:
            out = r"$=$"
        case ast.NotEq:
            out = r"$\not=$"
        case ast.Lt:
            out = r"$<$"
        case ast.LtE:
            out = r"$\leq$"
        case ast.Gt:
            out = r"$>$"
        case ast.GtE:
            out = r"$\geq$"
        case ast.Expr:
            out = rf"{parse(node.value)}"
        case ast.BinOp:
            out = parse_bin_op(node)
        case ast.BoolOp:
            out = parse_binary_bool_op(node)
        case ast.UnaryOp:
            out = parse_unary_op(node)
        case ast.Attribute:
            out = f"{parse(node.value)}." + c._var(node.attr)
        case ast.Name:
            out = parse_name(node)
        case ast.Subscript:
            out = parse_array_subscript(node)
        case ast.FunctionDef:
            out = parse_function_def(node)
        case ast.Return:
            ret = c._return()
            if node.value:
                out = ret + f" {parse(node.value)}"
            else:
                out = ret
        case ast.Call:
            out = parse_call(node)
        case ast.If:
            out = parse_if_or_elif(node, "if")
        case ast.IfExp:
            out = parse_ternary(node)
        case ast.While:
            out = parse_while(node)
        case ast.For:
            out = parse_for(node)
        case ast.Continue:
            out = c._con("continue")
        case ast.Break:
            out = c._con("break")
        case ast.Pass:
            out = c._con("TODO")
        case ast.Compare:
            out = f"{parse(node.left)} {parse(node.ops[0])} {parse(node.comparators[0])}"
        case ast.Assign:
            out = parse_assign(node)
        case ast.AugAssign:
            out = rf"{parse(node.target)} $\leftarrow$ {parse_bin_op(ast.BinOp(node.target, node.op, node.value))}"
        case ast.Tuple:
            out = parse_tuple(node)
        case ast.List:
            out = parse_kv_pair(node)

    global line_count
    if isinstance(node, ast.stmt):
        if type(node) != ast.FunctionDef:
            line_count += 1
        return out + NL
    return out


def convert(filename: str, debug: bool, cmd: MacroList):
    global c
    c = cmd

    text = None
    with open(filename) as f:
        text = f.read()
    tree = ast.parse(text)

    if (debug):
        print(ast.dump(tree, indent=4))

    out = ""
    for node in tree.body:
        out += parse(node) + "\n"
    return out
