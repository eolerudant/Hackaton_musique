
Readme · MD
# Synthétiseur Musical DSL (Lark & Python)
 
Ce projet implémente un synthétiseur audio basé sur un langage dédié (DSL - *Domain Specific Language*) pour la création musicale. Il permet d'écrire une partition structurée au format texte et de la compiler en un fichier audio `.wav` de haute qualité.
 
##  Installation
 
### Prérequis
 
Le projet requiert **Python 3** et la bibliothèque d'analyse syntaxique **Lark**.
 
Le moteur audio utilise exclusivement les modules natifs de Python (`wave`, `struct`, `math`), évitant ainsi d'installer des bibliothèques audio lourdes ou complexes à compiler.
 
### Étape 1 : Installer Lark
 
Ouvrez votre terminal et installez Lark via `pip` :
 
```bash
pip install lark
```
 
> **Note :** Si votre environnement est géré par un outil strict comme `uv` ou que vous êtes dans un environnement système managé, utilisez l'une des commandes suivantes :
>
> ```bash
> uv pip install lark
> # Ou :
> python -m pip install lark --break-system-packages
> ```
 

 
Le langage de programmation développé est divisé en trois sections claires et obligatoires :
 
```
#[meta]
bpm = 90;
title = "runaway";
 
#[instruments]
piano = {
    oscillator = sin phase 0.0
    enveloppe = 0.005, 0.15, 0.3, 0.2
    harmonics = [1.0, 0.6, 0.35, 0.15, 0.08, 0.04, 0.02]
}
 
#[partition]
2 0 5 5 piano;
2 2 5 5 ;
2 4 5 5 ;
2 6 5 4
```
 
### Description des sections :
 
1. **`#[meta]`** : Contient les métadonnées globales de votre morceau, comme le tempo (`bpm`) et le titre (`title`). Chaque ligne doit se terminer par un point-virgule `;`.
2. **`#[instruments]`** : Permet de concevoir des synthétiseurs sur mesure.
   * **`oscillator`** : Type d'onde (`sin`, `square`, `saw`, `triangle`, `noise`) et sa phase optionnelle (ex : `phase 0.25`).
   * **`enveloppe`** : Paramètres ADSR globaux (Attaque, Déclin, Maintien, Relâchement).
   * **`harmonics`** : Spectre harmonique (poids de la fondamentale et des harmoniques successives pour la synthèse additive).
3. **`#[partition]`** : Suite de notes séparées par des points-virgules `;`. Chaque note s'écrit sous la forme de 4 ou 5 valeurs :
   **Format d'une note :** `durée temps_début note octave [instrument_optionnel]`
   * Exemple : `2 0 5 5 piano` jouera une note de durée 2 temps, démarrant au temps 0, jouant la note 5 à l'octave 5 avec l'instrument piano. Il y a 12 notes par octave. Les notes suivantes héritent de cet instrument tant qu'aucun autre n'est spécifié.
## 🚀 Comment exécuter le projet
 
1. Placez votre partition (par exemple `runaway.txt`) à la racine du projet.
2. Ouvrez le fichier de commande principal `main.py`.
3. Configurez la ligne 7 pour charger votre partition : `nom_fichier_partition = "runaway.txt"`
4. Exécutez le script dans votre terminal :
```bash
   python main.py
```
 
5. Un fichier nommé `musique_finale.wav` est instantanément créé à la racine. Ouvrez-le et profitez de votre composition !
## 📁 Architecture des Fichiers
 
* **`grammaire.lark`** : Définition formelle EBNF de notre langage.
* **`parser.py`** : Charge la grammaire et génère l'arbre de syntaxe abstraite (AST).
* **`interpreter.py`** : Transforme l'AST produit par Lark en dictionnaires et objets Python exploitables.
* **`generateuraudio.py`** : Notre moteur audio de synthèse additive (physique des harmoniques, enveloppe ADSR, inharmonicité d'Euler-Bernoulli, et transitoire d'impact de marteau).
* **`main.py`** : Script coordinateur principal.
