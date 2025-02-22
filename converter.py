from string import Template
from parse import convert, Theme
import argparse
import pyperclip

PACKAGES = r"""\usepackage{amsmath}
\usepackage{xcolor, colortbl}
\usepackage{bigstrut}"""
ENV_DEF = r"""\newenvironment{pseudocode}[2]{
	\noindent\begin{tabular}[t]{|>{\columncolor{funcbodybgcolor}\color{textcolor}}l|}%
	\hline
	\bigstrut[t]\cellcolor{funcnamebgcolor}\textcolor{funcnamecolor}{\textsc{#1}}(#2)\\%
	\hline
	\bigstrut[t]
}{
	\hline
	\end{tabular}\\
}"""

ESCAPE_YELLOW = "D7BA7D"
FUNC_YELLOW = "DCDCAA"
CONTROL_PURPLE = "C586C0"
KEYWORD_BLUE = "569CD6"
NUMBER_GREEN = "B5CEA8"
COMMENT_GREEN = "6A9955"
CLASS_GREEN = "4EC9B0"
VAR_BLUE = "9CDCFE"
CONST_BLUE = "4FC1FF"


DEFAULT_MODE = Theme("000000", "CDF0FE", "FFFFFF",
                     "000000", "000000", "000000", "000000", "000000",  "000000", "000000")
LIGHT_MODE = Theme(ESCAPE_YELLOW, "EEEEEE", "FFFFFF",
                   "A679DC", "0086D1", COMMENT_GREEN, CLASS_GREEN, CONST_BLUE, "000000",  "777777")
DARK_MODE = Theme(FUNC_YELLOW, "444444", "222222",
                  CONTROL_PURPLE, KEYWORD_BLUE, NUMBER_GREEN, CLASS_GREEN, VAR_BLUE, "FFFFFF",  "555555")

THEMES = (DEFAULT_MODE, LIGHT_MODE, DARK_MODE)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--prelude", action="store_true",
                        help="Prints out needed packages as well as pseudocode environment definition")
    parser.add_argument("-t", "--theme", type=int,
                        help="0 for default theme, 1 for light mode, 2 for dark mode")
    parser.add_argument("-d", "--debug", action="store_true",
                        help="Prints out the AST")
    parser.add_argument(
        "-o", "--output", help="Writes a new document with prelude included. Pseudocode output only is printed if omitted")
    parser.add_argument("filename", help="File to be converted")
    args = parser.parse_args()

    if args.output:
        with open(args.output, "w") as f:
            theme = THEMES[args.theme if args.theme else 0]

            out = r"\documentclass[letterpaper]{article}""\n\n"
            out += PACKAGES + "\n\n"
            out += theme.color_list + "\n\n"
            out += ENV_DEF + "\n\n"
            out += r"\begin{document}""\n"
            out += convert(theme, args.filename, args.debug)
            out += r"\end{document}"
            f.write(out)
    else:
        if (args.prelude):
            print("% pseudocode packages")
            print(PACKAGES)
            print()
            print("% pseudocode environment definition")
            print(ENV_DEF)
            print()

        if args.theme:
            theme = THEMES[args.theme]
            print(rf"""% pseudocode colors
{theme.color_list}
""")
        out = convert(THEMES[0], args.filename, args.debug)
        pyperclip.copy(out)
        print(out)


if __name__ == "__main__":
    main()
