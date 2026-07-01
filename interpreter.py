from lark import Transformer

class InterpreteurMusical(Transformer):
    def bpm(self, args):
        return float(args[0])
    
    def duree(self, args):
        return float(args[0])
        
    def temps_0(self, args):
        return float(args[0])
        
    def nom_note(self, args):

        valeur = int(args[0])
        
        #On vérifie que c'est bien une note valide
        if not (1 <= valeur <= 12):
            raise ValueError(f"Erreur : La note doit être comprise entre 1 et 12 (valeur lue : {valeur})")
            
        return valeur
        
        
    def octave(self, args):
        valeur = int(args[0])
        if not (0 <= valeur <= 8):
            raise ValueError(f"Erreur : L'octave doit être compris entre 0 et 8 (valeur lue : {valeur})")
            
        return valeur

    def note(self, elements):
        
        return {
            "duree": float(elements[0]),
            "temps_0": float(elements[1]),
            "note": int(elements[2]),
            "octave": int(elements[3])
        }


    def partition(self, args):

        return {
            "bpm": args[0],
            "notes": args[1:]
        }