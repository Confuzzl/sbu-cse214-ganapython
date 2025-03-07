from parse import convert
from macro import *
import argparse
import pyperclip

PACKAGES = r"""\usepackage{amsmath}
\usepackage{xcolor, colortbl}
\usepackage{bigstrut}
\setlength{\parindent}{0pt}"""

# \newcommand{\comment}[1]{\textcolor{red}{// #1}}
# \newcommand{\func}[1]{\textcolor{funcnamecolor}{\textsc{#1}}}
# \newcommand{\method}[1]{\textcolor{funcnamecolor}{#1}}
# \newcommand{\var}[1]{\textcolor{varcolor}{$#1$}}
# \newcommand{\con}[1]{\textcolor{controlcolor}{\textbf{#1}}}
# \newcommand{\type}[1]{\textcolor{classcolor}{#1}}
# \newcommand{\op}[1]{\textcolor{bluewordcolor}{#1}}
# \newcommand{\str}[1]{\textcolor{stringcolor}{``#1''}}
# \newcommand{\num}[1]{\textcolor{numbercolor}{#1}}

# \newcommand{\while}{\con{while}}
# \newcommand{\true}{\op{$true$}}
# \newcommand{\false}{\op{$false$}}
# \newcommand{\null}{\op{$null$}}
# \newcommand{\not}{\op{not}}
# \newcommand{\and}{\op{and}}
# \newcommand{\or}{\op{or}}
# \newcommand{\return}{\con{return}}
# \newcommand{\break}{\con{break}}
# \newcommand{\continue}{\con{continue}}
# \newcommand{\print}{\con{print}}
# """

ESCAPE_YELLOW = "D7BA7D"
FUNC_YELLOW = "DCDCAA"
CONTROL_PURPLE = "C586C0"
KEYWORD_BLUE = "569CD6"
NUMBER_GREEN = "B5CEA8"
COMMENT_GREEN = "6A9955"
CLASS_GREEN = "4EC9B0"
VAR_BLUE = "9CDCFE"
CONST_BLUE = "4FC1FF"
STRING_ORANGE = "CE9178"


DEFAULT_MODE = Theme("000000", "CDF0FE", "FFFFFF",
                     "000000", "000000", "000000", "000000", "000000",  "000000", "000000", "000000")
LIGHT_MODE = Theme("DB861F", "EEEEEE", "FFFFFF",
                   "A679DC", "0086D1", COMMENT_GREEN, CLASS_GREEN, CONST_BLUE, "000000",  "777777", STRING_ORANGE)
DARK_MODE = Theme(FUNC_YELLOW, "444444", "222222",
                  CONTROL_PURPLE, KEYWORD_BLUE, NUMBER_GREEN, CLASS_GREEN, VAR_BLUE, "FFFFFF",  "555555", STRING_ORANGE)

THEMES = (DEFAULT_MODE, LIGHT_MODE, DARK_MODE)

MACROS = MacroList()
MACROS.new(Command("comment", r"\textcolor{red}{// #1}", 1))
MACROS.new(Command("func", r"\textcolor{funcnamecolor}{\textsc{#1}}", 1))
MACROS.new(Command("method", r"\textcolor{funcnamecolor}{#1}", 1))
MACROS.new(Command("var", r"\textcolor{varcolor}{$#1$}", 1))
MACROS.new(Command("con", r"\textcolor{controlcolor}{\textbf{#1}}", 1))
MACROS.new(Command("type", r"\textcolor{classcolor}{#1}", 1))
MACROS.new(Command("op", r"\textcolor{bluewordcolor}{#1}", 1))
MACROS.new(Command("str", r"\textcolor{stringcolor}{``#1''}", 1))
MACROS.new(Command("num", r"\textcolor{numbercolor}{#1}", 1))

# MACROS.new(Command("ass", r"$\leftarrow$"))
MACROS.new(Command("true", r"\op{$true$}"))
MACROS.new(Command("false", r"\op{$false$}"))
MACROS.new(Command("null", r"\op{$null$}", mangle=True))
MACROS.new(Command("not", r"\op{not}", mangle=True))
MACROS.new(Command("and", r"\op{and}", mangle=True))
MACROS.new(Command("or", r"\op{or}", mangle=True))
MACROS.new(Command("return", r"\con{return}"))
MACROS.new(Command("break", r"\con{break}", mangle=True))
MACROS.new(Command("continue", r"\con{continue}"))

MACROS.new(Command("while", r"\con{while} #1 \con{do}", 1))
MACROS.new(Command("if", r"\con{if} #1 \con{then}", 1, True))
MACROS.new(Command("elif", r"\con{else if} #1 \con{then}", 1, True))
MACROS.new(Command("else", r"\con{else}", 0, True))
MACROS.new(Command("for", r"\con{for} #1 \con{to} #2 \con{do}", 2))
MACROS.new(
    Command("forinc", r"\con{for} #1 \con{to} #2 \con{increment} #3 \con{do}", 3))
MACROS.new(Command("fordown", r"\con{for} #1 \con{down to} #2 \con{do}", 2))
MACROS.new(
    Command("fordec", r"\con{for} #1 \con{to} #2 \con{decrement} #3 \con{do}", 3))
MACROS.new(Command("print", r"\con{print} #1", 1))
MACROS.new(Environment("pseudocode",
                       r"""\noindent\begin{tabular}[t]{|>{\columncolor{funcbodybgcolor}\color{textcolor}}l|}%
	\hline%
	\bigstrut[t]\cellcolor{funcnamebgcolor}\textcolor{funcnamecolor}{\textsc{#1}}(#2)\\%
	\hline%
	\bigstrut[t]%""",
                       r"""\hline%
	\end{tabular}%""", 2))
MACROS.new(Environment(
    "scope", r"\begin{tabular}{!{\color{laddercolor}\vline}@{\hskip 1em}l}%", r"\end{tabular}%", 0))


def indent(str: str, start_scope=0):
    out = ""
    scope = start_scope
    for line in str.splitlines(True):
        if line.startswith(r"\end"):
            scope -= 1
        out += ("\t" * scope) + line
        if line.startswith(r"\begin"):
            scope += 1
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--prelude", action="store_true",
                        help="Prints out needed packages as well as pseudocode environment definition")
    parser.add_argument("-t", "--theme", type=int,
                        help="0 for default theme, 1 for light mode, 2 for dark mode. 0 if omitted")
    parser.add_argument("-d", "--debug", action="store_true",
                        help="Prints out the AST")
    parser.add_argument(
        "-o", "--output", help="Writes a new, standalone document with prelude included. Pseudocode only output is printed if omitted")
    parser.add_argument("-f", "--filename", help="File to be converted")
    args = parser.parse_args()

    if args.filename and args.output:
        theme = THEMES[args.theme if args.theme else 0]

        out = r"\documentclass[letterpaper]{article}""\n\n"
        out += PACKAGES + "\n\n"
        out += str(theme) + "\n\n"
        out += str(MACROS)
        # out += ENV_DEF + "\n\n"
        out += r"\begin{document}""\n"
        # out += convert(args.filename, args.debug, MACROS) -
        out += indent(convert(args.filename, args.debug, MACROS), 1)
        out += r"\end{document}"

        with open(args.output, "w") as f:
            f.write(out)
    else:
        if (args.prelude):
            print("% pseudocode packages")
            print(PACKAGES)
            print()
            print("% pseudocode environment definition")
            # print(ENV_DEF)
            print()

        if args.theme != None:
            theme = THEMES[args.theme]
            print(rf"""% pseudocode colors
{str(theme)}
""")
        if args.filename:
            out = indent(convert(args.filename, args.debug, MACROS))
            pyperclip.copy(out)
            print(out)


if __name__ == "__main__":
    main()
