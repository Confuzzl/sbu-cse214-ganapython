class Command:
    def __init__(self, name: str, body: str, args=0, mangle=False):
        self.name = name
        self.full_name = f"c{name.title()}" if mangle else name
        self.body = body
        self.args = args

    def __call__(self, *args):
        def wrap(s):
            return f"{{{s}}}"
        assert len(args) == self.args
        return rf"\{self.full_name}{"{}" if self.args == 0 else "".join(wrap(s) for s in args)}"

    def __str__(self):
        return rf"\newcommand{{\{self.full_name}}}[{self.args}]{{{self.body}}}"


class Environment:
    def __init__(self, name: str, begin: str, end: str, args: int):
        self.name = name
        self.begin = begin
        self.end = end
        self.args = args

    def __call__(self, *args):
        def wrap(s):
            return f"{{{s}}}"
        assert len(args) - 1 == self.args
        out = rf"\begin{{{self.name}}}{"".join(wrap(arg) for arg in args[:-1])}""\n"
        out += "\t" + args[-1] + "\n"
        out += rf"\end{{{self.name}}}"
        return out

    def __str__(self):
        return rf"\newenvironment{{{self.name}}}[{self.args}]" + "{%\n" \
            f"\t{self.begin}\n" + \
            "}{%\n" + \
            f"\t{self.end}\n" + \
            "}%\n"


class MacroList:
    def new(self, mac: Command | Environment):
        setattr(self, f"_{mac.name}", mac)

    def __str__(self):
        return "\n".join(str(v) for v in self.__dict__.values())


class Theme:
    COLORS = ("funcnamecolor", "funcnamebgcolor", "funcbodybgcolor", "controlcolor", "bluewordcolor",
              "numbercolor", "classcolor", "varcolor", "textcolor", "laddercolor", "stringcolor")

    def __init__(self, *colors):
        self.colors = dict(zip(Theme.COLORS, colors))

    def __str__(self):
        return "\n".join(rf"\definecolor{{{name}}}{{HTML}}{{{value}}}" for name, value in self.colors.items())
