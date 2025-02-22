import ast
import builtins

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


class Theme:
    def __init__(self, funcnamecolor,
                 funcnamebgcolor, funcbodybgcolor,
                 controlcolor, bluewordcolor,
                 numbercolor, classcolor,
                 varcolor, textcolor,
                 laddercolor):
        self.color_list = rf"""\definecolor{{funcnamecolor}}{{HTML}}{{{funcnamecolor}}}
\definecolor{{funcnamebgcolor}}{{HTML}}{{{funcnamebgcolor}}}
\definecolor{{funcbodybgcolor}}{{HTML}}{{{funcbodybgcolor}}}
\definecolor{{controlcolor}}{{HTML}}{{{controlcolor}}}
\definecolor{{bluewordcolor}}{{HTML}}{{{bluewordcolor}}}
\definecolor{{numbercolor}}{{HTML}}{{{numbercolor}}}
\definecolor{{classcolor}}{{HTML}}{{{classcolor}}}
\definecolor{{varcolor}}{{HTML}}{{{varcolor}}}
\definecolor{{textcolor}}{{HTML}}{{{textcolor}}}
\definecolor{{laddercolor}}{{HTML}}{{{laddercolor}}}"""


my_theme: Theme = None

SCOPE_START = r"\begin{tabular}{!{\color{laddercolor}\vline}@{\hskip 1em}l}""\n"
NL = r"\\""\n"


def color(col: str, str: str):
    return rf"\textcolor{{{col}}}{{{str}}}"


def parse_if_or_elif(node: ast.If, keyword: str):
    out = color("controlcolor", rf"\textbf{{{keyword}}}") + \
        f" {parse(node.test)} " + color("controlcolor",
                                        r"\textbf{then}") + NL
    out += SCOPE_START
    for if_node in node.body:
        out += parse(if_node)
    out += r"\end{tabular}" + NL
    if len(node.orelse) == 0:
        return out

    if len(node.orelse) == 0:
        return out

    if type(node.orelse[0]) == ast.If:
        out += parse_if_or_elif(node.orelse[0], "else if")
    else:
        out += color("controlcolor", r"\textbf{else}") + NL
        out += SCOPE_START
        for else_node in node.orelse:
            out += f"{parse(else_node)}"
        out += r"\end{tabular}" + NL
    return out


def parse_ternary(node: ast.IfExp):
    return f"({parse(node.test)}) ? {parse(node.body)} : {parse(node.orelse)}"


def parse_array_bracket_list(pair: tuple[ast.AST, ast.AST] | tuple[str, str]):
    left, right = None, None
    a, b = pair
    match (type(a), type(b)):
        case (builtins.str, builtins.str):
            left, right = a, b
        case _:
            lp_a, rp_a = ("(", ")") if type(a) == ast.BinOp else ("", "")
            lp_b, rp_b = ("(", ")") if type(b) == ast.BinOp else ("", "")
            left, right = f"{lp_a}{parse(a)}{rp_a}", f"{lp_b}{parse(b)}{rp_b}"
    return rf"[{left}$\dots${right}]"


def parse_array_call_name_range(node: ast.Call, *, name: ast.Name = None, range: tuple[ast.AST, ast.AST] = None):
    if name == None and range == None:
        return f"{parse(node.args[0])}{parse_array_bracket_list(node.args[1].elts)}"
    return f"{parse(name)}{parse_array_bracket_list(range)}"


def parse_array_creation(node: ast.Call):
    return parse_array_bracket_list(node.args[0].elts)


def parse_array_call_from_assignment(node: ast.Call):
    a, b = None, None
    match (type(node.args[0]), type(node.args[1])):
        case (ast.Tuple, ast.Tuple):
            a, b = parse_array_bracket_list(
                node.args[0].elts), parse_array_bracket_list(node.args[1].elts)
        case (ast.Tuple, ast.Call):
            a, b = parse_array_bracket_list(
                node.args[0].elts), parse_array_call_name_range(node.args[1])
    if (a, b) == (None, None):
        raise ValueError(
            "invalid call argument format for parse_array_call_from_assignment")
    return rf"{a} $\leftarrow$ {b}"


def parse_print(content: str):
    return color("controlcolor", r"\textbf{print}") + " " + content


def parse_call(node: ast.Call):
    out = ""
    match type(node.func):
        case ast.Name:
            match node.func.id:
                case "Array":
                    return parse_array_call_name_range(node)
                case "print":
                    return parse_print(node.args[0].value)
            out += color("funcnamecolor", rf"\textsc{{{node.func.id}}}")
        case ast.Attribute:
            out += f"{parse(node.func.value)}." + \
                color("funcnamecolor", f"{node.func.attr}")
    out += f"({", ".join(parse(arg) for arg in node.args)})"
    return out


def parse_while(node: ast.While):
    out = color("controlcolor", r"\textbf{while}") + rf" {parse(node.test)} " + color(
        "controlcolor", r"\textbf{do}") + NL
    out += SCOPE_START
    for if_node in node.body:
        out += parse(if_node)
    out += r"\end{tabular}" + NL
    return out


def parse_for(node: ast.For):
    def parse_normal_for():
        out = color("controlcolor",
                    r"\textbf{for}") + rf" {parse(node.target)} $\leftarrow$ "
        lower = None
        upper = None
        direction = +1
        to = "to"
        crement = ""
        args = node.iter.args
        if len(args) == 1:
            lower = color("numbercolor", 1)
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
                    # value = parse(args[2].operand)
                    value = args[2].operand
                case _:
                    # value = parse(args[2])
                    value = args[2]
            match direction:
                case -1:
                    to = "down to"
                case 1:
                    to = "to"
            if value.value != 1:
                match direction:
                    case -1:
                        crement = color(
                            "controlcolor", r"\textbf{decrement}") + f" {parse(value)} "
                    case 1:
                        crement = color(
                            "controlcolor", r"\textbf{increment}") + f" {parse(value)} "

        out += rf"{lower} " + color("controlcolor", rf"\textbf{{{to}}}") + f" {upper} " + crement + \
            color("controlcolor", r"\textbf{{do}}")
        return out

    def parse_for_each():
        return color("controlcolor", r"\textbf{foreach}") + " " + \
            color("bluewordcolor", "child") + rf" {parse(node.target)} " + color("controlcolor", r"of") + \
            f" {parse(node.iter)} " + color("bluewordcolor", "node") + \
            " " + color("controlcolor", r"\textbf{do}")

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
    out += r"\end{tabular}" + NL
    return out


def parse_assign(node: ast.Assign):
    def data_structure(data_type: str):
        out = color("bluewordcolor", f"Create {"an" if data_type == "Array" else "a"}") + f" {
            color("classcolor", DATA_STRUCTURE_TYPES[data_type])} {parse(node.targets[0])}"

        args = node.value.args
        match data_type:
            case "Array":
                if len(args) == 1:
                    out += parse_array_creation(node.value)
                else:
                    out += parse_array_call_from_assignment(node.value)
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
                out += rf"[{parse(args[0].elts[0])
                            }$\dots${parse(args[0].elts[1])}][{parse(args[1].elts[0])
                                                               }$\dots${parse(args[1].elts[1])}]"
        out += NL
        return out

    if (type(node.targets[0]), type(node.value)) == (ast.Tuple, ast.Tuple):
        assignments = zip(node.targets[0].elts, node.value.elts)
        return "; ".join(rf"{parse(a)} $\leftarrow$ {parse(b)}" for a, b in assignments) + NL

    match type(node.value):
        case ast.Call:
            match type(node.value.func):
                case ast.Name:
                    match node.value.func.id:
                        case data_type if data_type in DATA_STRUCTURE_TYPES.keys():
                            return data_structure(data_type)
    return rf"{parse(node.targets[0])} $\leftarrow$ {parse(node.value)}" + NL


def parse_function_args(args: list[ast.arg]):
    def parse_arg(arg: ast.arg):
        if arg.annotation == None:
            return color("varcolor", f"${arg.arg}$")
        if type(arg.annotation) != ast.Call:
            raise ValueError("algorithm arg type annotation must be call")
        call = arg.annotation
        if call.func.id != "Array":
            raise ValueError(
                "algorithm arg type annotation of call must be Array")
        return f"{color("varcolor", f"${arg.arg}$")}{parse_array_bracket_list(call.args[0].elts)}"
    return ", ".join(parse_arg(arg) for arg in args)


def parse_function_def(node: ast.FunctionDef):
    out = r"\begin{pseudocode}"f"{{{node.name}}}"f"{{{parse_function_args(node.args.args)}}}\n"

    # out = r"\code{\textsc{"f"{node.name}""}("f"{
    #     parse_function_args(node.args.args)}"")}{\n"
    for body_node in node.body:
        out += parse(body_node)
    # out += r"}\\"
    out += r"\end{pseudocode}"
    return out


def parse_annotation_assign(node: ast.AnnAssign):
    match type(node.annotation):
        case ast.Call:
            call = node.annotation
            match call.func.id:
                case "Array":
                    return rf"{parse_array_call_name_range(node=None, name=node.target, range=call.args[0].elts)}" + NL
    raise ValueError("annotations should only be used for arrays")


def parse_constant(node: ast.Constant):
    match node.value:
        case True:
            return color("bluewordcolor", "$true$")
        case False:
            return color("bluewordcolor", "$false$")
        case None:
            return color("bluewordcolor", "$null$")
        case _:
            if (my_type := type(node.value)) != int:
                raise ValueError(f"constant value of {my_type} not recognized")
            return color("numbercolor", node.value)


def parse_unary_op(node: ast.UnaryOp):
    match type(node.op):
        case ast.Not:
            if type(node.operand) == ast.BoolOp:
                return color("bluewordcolor", r"not") + " " + f"({parse_binary_bool_op(node.operand)})"
            return color("bluewordcolor", r"not") + " " + parse(node.operand)
        case ast.UAdd:
            return f"$+${parse(node.operand)}"
        case ast.USub:
            return f"$-${parse(node.operand)}"
        case _:
            raise ValueError(
                f"unsupported unary operator of type {type(node.op)}")


def parse_binary_bool_op(node: ast.BoolOp, brackets=False):
    def parse_bool_op(op: ast.AST):
        match type(op):
            case ast.Not:
                return color("bluewordcolor", r"not")
            case ast.And:
                return color("bluewordcolor", r"and")
            case ast.Or:
                return color("bluewordcolor", r"or")
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

    def parse_bin(bin_op: ast.AST):
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
        match type(bin_op.op):
            case ast.Pow:
                return rf"$\text{{{parse_operand(bin_op.left)}}}^\text{{{parse_operand(bin_op.right)}}}$"
            case ast.FloorDiv:
                return rf"$\lfloor${parse_operand(bin_op.left)} $/$ {parse_operand(bin_op.right)}$\rfloor$"
            case _:
                return f"{parse_operand(bin_op.left)} {symbol(bin_op.op)} {parse_operand(bin_op.right)}"
    parsed = parse_bin(node)
    if this_type != parent_op_type and \
            this_type != ast.FloorDiv and \
            ORDER[this_type] >= ORDER[parent_op_type]:
        return f"({parsed})"
    return parsed


def parse_name(node: ast.Name):
    if node.id == "_":
        return ""
    return color("varcolor", f"${node.id.replace("_", r"\_")}$")


def parse_kv_pair(node: ast.List):
    return rf"$\langle${', '.join(parse(e) for e in node.elts)}$\rangle$"


def parse(node: ast.AST):
    match type(node):
        case ast.Constant:
            return parse_constant(node)
        case ast.Eq:
            return r"$=$"
        case ast.NotEq:
            return r"$\not=$"
        case ast.Lt:
            return r"$<$"
        case ast.LtE:
            return r"$\leq$"
        case ast.Gt:
            return r"$>$"
        case ast.GtE:
            return r"$\geq$"
        case ast.Expr:
            return rf"{parse(node.value)}" + NL
        case ast.BinOp:
            return parse_bin_op(node)
        case ast.BoolOp:
            return parse_binary_bool_op(node)
        case ast.UnaryOp:
            return parse_unary_op(node)
        case ast.Attribute:
            return f"{parse(node.value)}." + color("varcolor", f"${node.attr}$")
        case ast.Name:
            return parse_name(node)
        case ast.Subscript:
            return f"{parse(node.value)}[{parse(node.slice)}]"
        case ast.FunctionDef:
            return parse_function_def(node)
        case ast.Return:
            ret = color("controlcolor", r"\textbf{return}")
            if node.value:
                return ret + f" {parse(node.value)}" + NL
            return ret + NL
        case ast.Call:
            return parse_call(node)
        case ast.If:
            return parse_if_or_elif(node, "if")
        case ast.IfExp:
            return parse_ternary(node)
        case ast.While:
            return parse_while(node)
        case ast.For:
            return parse_for(node)
        case ast.Continue:
            return color("controlcolor", r"\textbf{continue}") + NL
        case ast.Break:
            return color("controlcolor", r"\textbf{break}") + NL
        case ast.Compare:
            return f"{parse(node.left)} {parse(node.ops[0])} {parse(node.comparators[0])}"
        case ast.Assign:
            return parse_assign(node)
        case ast.AugAssign:
            return rf"{parse(node.target)} $\leftarrow$ {parse(node.target)} {parse(node.op)} {parse(node.value)}" + NL
        case ast.AnnAssign:
            return parse_annotation_assign(node)
        case ast.List:
            return parse_kv_pair(node)

    return ""


def convert(theme: Theme, filename: str, debug: bool):
    global my_theme
    my_theme = theme

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
