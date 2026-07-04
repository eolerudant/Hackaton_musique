from parser import analyser_code
from interpreter import InterpreteurMusical
from generateuraudio import generer_audio  

if __name__ == "__main__":
    
    nom_fichier_partition = "runaway.txt"  # Nom du fichier contenant la partition musicale à analyser
    
    try:
        print(f" Lecture de la partition : {nom_fichier_partition}...")
        with open(nom_fichier_partition, "r", encoding="utf-8") as fichier:
            code_musical = fichier.read()
        
        # Analyse syntaxique (Lark)
        arbre_syntaxique = analyser_code(code_musical)
        
        # Interprétation en données Python structurées
        interpreteur = InterpreteurMusical()
        donnees_musicales = interpreteur.transform(arbre_syntaxique)
        
        # Génération du fichier audio final
        nom_audio_sortie = "musique_finale.wav"
        generer_audio(donnees_musicales, nom_audio_sortie)
            
    except FileNotFoundError:
        print(f"Erreur : Le fichier '{nom_fichier_partition}' est introuvable.")
        print(f"Vérifie que tu as bien créé un fichier nommé {nom_fichier_partition} dans ton dossier de travail.")
    except Exception as e:
        print("Erreur pendant l'exécution :", e)