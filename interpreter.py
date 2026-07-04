from lark import Transformer, Token

class InterpreteurMusical(Transformer):
    def start(self, args):
        # La règle de départ regroupe les métadonnées, les instruments et la partition
        return {
            "meta": args[0],
            "instruments": args[1],
            "partition": args[2]
        }

    def meta_section(self, args):
        meta_dict = {}
        for item in args:
            if item is not None:
                meta_dict[item[0]] = item[1]
        return meta_dict

    def meta_entry(self, args):
        key = str(args[0])
        val = args[1]
        return (key, val)

    def val(self, args):
        val = args[0]
        if isinstance(val, Token) and val.type == 'ESCAPED_STRING':
            # On retire les guillemets de la chaîne de texte lue
            return str(val)[1:-1]
        return float(val)

    def instruments_section(self, args):
        inst_dict = {}
        for inst in args:
            if inst is not None:
                inst_dict[inst[0]] = inst[1]
        return inst_dict

    def instrument_def(self, args):
        name = str(args[0])
        properties = {}
        for prop in args[1:]:
            if prop is not None:
                properties[prop[0]] = prop[1]
        return (name, properties)

    def inst_property(self, args):
        key = str(args[0])
        val = args[1]
        return (key, val)

    def property_val(self, args):
        return args[0]

    def oscillator_val(self, args):

        osc_type = str(args[0])
        phase_val = float(args[1]) if len(args) > 1 and args[1] is not None else 0.0
        
        return {
            "type": osc_type,
            "phase": phase_val
        }

    def enveloppe_val(self, args):
        # Retourne les 4 paramètres ADSR sous forme de liste de floats
        return [float(a) for a in args]

    def harmonics_val(self, args):
        # Retourne les poids des harmoniques sous forme de liste de floats
        return [float(a) for a in args]

    def partition_section(self, args):
        return {
            "notes": args
        }
    
    def bpm(self, args):
        return float(args[0])

    def note(self, args):
        duree = float(args[0])
        temps_0 = float(args[1])
        note_val = int(args[2])
        octave = int(args[3])
        inst = str(args[4]) if len(args) > 4 and args[4] is not None else None
        
        return {
            "duree": duree,
            "temps_0": temps_0,
            "note": note_val,
            "octave": octave,
            "instrument": inst
        }