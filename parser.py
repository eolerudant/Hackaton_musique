from lark import Lark

def analyser_code(code_musical):

    # 1. On charge la grammaire depuis notre fichier EBNF
    with open("grammaire.lark", "r", encoding="utf-8") as f:
        grammaire_musicale = f.read()


    parser = Lark(grammaire_musicale, start='start')
    
   
    return parser.parse(code_musical)