from lark import Lark

def analyser_code(code_musical):
    """
    Lit la grammaire EBNF, initialise Lark et analyse le code musical fourni.
    Retourne l'arbre syntaxique abstrait (AST).
    """
    # 1. On charge la grammaire depuis notre fichier EBNF
    with open("grammaire.lark", "r", encoding="utf-8") as f:
        grammaire_musicale = f.read()

    # 2. Création du parseur
    parser = Lark(grammaire_musicale, start='partition')
    
    # 3. Analyse du code et renvoi de l'arbre
    return parser.parse(code_musical)