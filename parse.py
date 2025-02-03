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


def parse_if_or_elif(node: ast.If, keyword: str):
    out = rf"""\textbf{{{keyword}}} {parse(node.test)} \textbf{{then}}\\""""\n"
    out += r"\begin{tabular}{@{\hskip 0.25em}|@{\hskip 1em}l}""\n"
    for if_node in node.body:
        out += parse(if_node)
    out += r"\end{tabular}\\""\n"
    if len(node.orelse) == 0:
        return out

    for else_node in node.orelse:
        match type(else_node):
            case ast.If:
                out += parse_if_or_elif(else_node, "else if")
            case _:
                out += rf"\textbf{{else}}\\""\n"
                out += r"\begin{tabular}{@{\hskip 0.25em}|@{\hskip 1em}l}""\n"
                out += f"{parse(else_node)}"
                out += r"\end{tabular}\\""\n"
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
    return f"{a} $\leftarrow$ {b}"


def parse_call(node: ast.Call):
    out = ""
    match type(node.func):
        case ast.Name:
            match node.func.id:
                case "Array":
                    return parse_array_call_name_range(node)
                    # return parse_array_call(node)
            out += rf"\textsc{{{node.func.id}}}"
        case ast.Attribute:
            out += parse(node.func)
    out += f"({", ".join(parse(arg) for arg in node.args)})"
    return out


def parse_while(node: ast.While):
    out = rf"\textbf{{while}} {parse(node.test)} \textbf{{do}}\\""\n"
    out += r"\begin{tabular}{@{\hskip 0.25em}|@{\hskip 1em}l}""\n"
    for if_node in node.body:
        out += parse(if_node)
    out += r"\end{tabular}\\""\n"
    return out


def parse_for(node: ast.For):
    def parse_normal_for():
        out = r"\textbf{for} "rf"{parse(node.target)} $\leftarrow$ "
        lower = None
        upper = None
        direction = +1
        to = "to"
        crement = ""
        args = node.iter.args
        if len(args) == 1:
            lower = "1"
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
                    value = parse(args[2].operand)
                case _:
                    value = parse(args[2])
            match direction:
                case -1:
                    to = "down to"
                case 1:
                    to = "to"
            if value != "1":
                match direction:
                    case -1:
                        crement = f"decrement {value}"
                    case 1:
                        crement = f"increment {value}"

        out += rf"{lower} \textbf{{{to}}} {upper} {crement}\textbf{{do}}"
        return out

    def parse_for_each():
        return r"\textbf{foreach} child "rf"{parse(node.target)} of {
            parse(node.iter)} node"r" \textbf{do}"

    out = ""
    match type(node.iter):
        case ast.Call:
            out += parse_normal_for()
        case ast.Name:
            out += parse_for_each()
    out += r"\\""\n"
    out += r"\begin{tabular}{@{\hskip 0.25em}|@{\hskip 1em}l}""\n"
    for body_node in node.body:
        out += parse(body_node)
    out += r"\end{tabular}\\""\n"
    return out


def parse_assign(node: ast.Assign):
    def data_structure(data_type: str):
        out = rf"Create {"an" if data_type == "Array" else "a"} {
            DATA_STRUCTURE_TYPES[data_type]} {parse(node.targets[0])}"

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
                out += rf"[{parse(args[0].elts[0])
                            }$\dots${parse(args[0].elts[1])}][{parse(args[1].elts[0])
                                                               }$\dots${parse(args[1].elts[1])}]"
        out += r"\\""\n"
        return out

    if (type(node.targets[0]), type(node.value)) == (ast.Tuple, ast.Tuple):
        assignments = zip(node.targets[0].elts, node.value.elts)
        return "; ".join(f"{parse(a)} $\leftarrow$ {parse(b)}" for a, b in assignments) + r"\\""\n"

    match type(node.value):
        case ast.Call:
            match type(node.value.func):
                case ast.Name:
                    match node.value.func.id:
                        case data_type if data_type in DATA_STRUCTURE_TYPES.keys():
                            return data_structure(data_type)
    return rf"{parse(node.targets[0])} $\leftarrow$ {parse(node.value)}\\""\n"


def parse_function_arg(arg: str):
    parsed = parse(ast.parse(arg).body[0])
    return parsed.replace(r"\\", "").replace("\n", "")  # remove \\ and \n


def parse_function_args(args: list[ast.arg]):
    def parse_arg(arg: ast.arg):
        if arg.annotation == None:
            return f"${arg.arg}$"
        if type(arg.annotation) != ast.Call:
            raise ValueError("algorithm arg type annotation must be call")
        call = arg.annotation
        if call.func.id != "Array":
            raise ValueError(
                "algorithm arg type annotation of call must be Array")
        return f"${arg.arg}${parse_array_bracket_list(call.args[0].elts)}"
    return ", ".join(parse_arg(arg) for arg in args)


def parse_function_def(node: ast.FunctionDef):
    out = r"\code{\textsc{"f"{node.name}"r"}("f"{
        parse_function_args(node.args.args)}"")}{""\n"
    for body_node in node.body:
        out += parse(body_node)
    out += r"}\\"
    return out


def parse_annotation_assign(node: ast.AnnAssign):
    match type(node.annotation):
        case ast.Call:
            call = node.annotation
            match call.func.id:
                case "Array":
                    return rf"{parse_array_call_name_range(node=None, name=node.target, range=call.args[0].elts)}\\""\n"
    raise ValueError("annotations should only be used for arrays")


def parse(node: ast.AST):
    match type(node):
        case ast.Constant:
            return f"{node.value}"
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
        case ast.Add | ast.UAdd:
            return "$+$"
        case ast.Sub | ast.USub:
            return "$-$"
        case ast.Mult:
            return r"$\times$"
        case ast.Div:
            return "$/$"
        case ast.Mod:
            return r"$\%$"
        case ast.And:
            return r"\textbf{and}"
        case ast.Or:
            return r"\textbf{or}"
        case ast.Not:
            return r"\textbf{not}"
        case ast.Expr:
            return rf"{parse(node.value)}\\""\n"
        case ast.BinOp:
            if type(node.op) == ast.FloorDiv:
                return rf"$\lfloor${parse(node.left)} $/$ {parse(node.right)}$\rfloor$"
            return f"{parse(node.left)} {parse(node.op)} {parse(node.right)}"
        case ast.BoolOp:
            return f" {parse(node.op)} ".join(parse(val) for val in node.values)
        case ast.UnaryOp:
            spacing = "" if type(node.op) in (ast.UAdd, ast.USub) else " "
            return f"{parse(node.op)}{spacing}{parse(node.operand)}"
        case ast.Attribute:
            return f"{parse(node.value)}.${node.attr}$"
        case ast.Name:
            return f"${node.id.replace("_", "\_")}$"
        case ast.Subscript:
            return f"{parse(node.value)}[{parse(node.slice)}]"
        case ast.FunctionDef:
            return parse_function_def(node)
        case ast.Return:
            return r"\textbf{return} "f"{parse(node.value)}"r"\\""\n"
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
            return r"\textbf{continue}\\""\n"
        case ast.Compare:
            return f"{parse(node.left)} {parse(node.ops[0])} {parse(node.comparators[0])}"
        case ast.Assign:
            return parse_assign(node)
        case ast.AugAssign:
            return rf"{parse(node.target)} $\leftarrow$ {parse(node.target)} {parse(node.op)} {parse(node.value)}\\""\n"
        case ast.AnnAssign:
            return parse_annotation_assign(node)
    return ""


def main():
    filename = "pseudo.py"
    text = None
    with open(filename) as f:
        text = f.read()

    tree = ast.parse(text)
    print(ast.dump(tree, indent=4))

    output = ""
    for node in tree.body:
        output += parse(node)
    print(output)


if __name__ == "__main__":
    main()
