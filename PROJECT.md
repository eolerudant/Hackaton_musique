# Rapport de Projet - Synthétiseur Musical
 
Ce document décrit notre démarche, nos choix d'implémentation et les solutions apportées aux défis physiques et informatiques rencontrés lors du Hackathon.
 
## Démarche
 
L'objectif de ce projet était de concevoir un langage capable de modéliser une partition musicale et de synthétiser des fichiers audio réalistes. J'ai choisi de reproduire l'introduction de la musique "Runaway" de Kanye West qui est constitué d'une melodie
simple et lente au piano
 
Voici les différentes étapes du projet :
 
1. Modélisation d'un son simple (sinusoïde pure, enveloppe ADSR).
2. Création d'une grammaire formelle avec Lark pour parser des suites de notes.
3. Implémentation de la physique acoustique (harmoniques, inharmonicité des cordes de piano, et transitoire d'attaque) pour dépasser le son froid d'un synthétiseur classique.
4. Transition vers une grammaire multi-instruments structurée en blocs clairs (`#[meta]`, `#[instruments]`, `#[partition]`).

 
###  Analyse syntaxique via Lark
 
Nous avons retenu la bibliothèque Lark avec un parseur LALR. Ce choix nous a permis d'écrire une grammaire formelle EBNF robuste et d'exploiter la classe `Transformer` pour convertir l'arbre de syntaxe abstraite (AST) directement en structures de données Python (dictionnaires et listes) sans parsing manuel fastidieux.
 
###  Synthèse additive et Amortissement Harmonique Dynamique
 
Plutôt que d'utiliser des ondes figées, nous calculons chaque note par sommation d'harmoniques de rangs différents. Le timbre brillant du piano s'atténue naturellement au cours du temps grâce à l'application d'un amortissement exponentiel dépendant du rang de l'harmonique $n$ :
 
$$\text{amortissement} = e^{-\alpha \cdot n \cdot t}$$
 
Où :
- $\alpha$ est la vitesse d'extinction (ici fixée à $2.0$).
- $n$ est le rang harmonique.
- $t$ est le temps actuel en secondes.
Cela permet de simuler un déclin (*Decay*) et un maintien (*Sustain*) physiques de manière 100% autonome, les composantes aiguës s'éteignant beaucoup plus vite que la fondamentale.
 
###  Inharmonicité physique d'Euler-Bernoulli
 
Pour simuler le comportement d'une corde métallique rigide de piano, nous avons intégré la correction d'inharmonicité physique :
 
$$f_n = n \cdot f_0 \cdot \sqrt{1 + B \cdot n^2}$$
 
Le coefficient $B = 0.00015$ étire légèrement les fréquences des harmoniques supérieures, donnant au son synthétisé cette chaleur et ce timbre typique du piano acoustique.
Le programme choisit ce type de modélisation physique si l'instrument défini dans la partition s'appelle "piano".

## Difficultés Rencontrées & Solutions
 
###  Le filtrage des terminaux anonymes par Lark
 
**Problème :** Lors de l'écriture de la règle d'oscillateur avec phase optionnelle, Lark filtrait silencieusement le type d'onde, provoquant des crashs `list index out of range` dans l'interpréteur.
 
**Solution :** Passage par un terminal nommé en majuscules `OSCILLATOR_TYPE` pour contraindre Lark à conserver l'information dans l'AST.
 
###  L'empaquetage "Tree" automatique de Lark
 
**Problème :** L'utilisation de minuscules pour les paramètres d'une note poussait Lark à créer des objets `Tree` intermédiaires, empêchant de convertir les durées et hauteurs en valeurs numériques réelles (`float() argument must be a string...`).
 
**Solution :** Utilisation du préfixe `?` dans notre grammaire (`?duree : NUMBER`) pour demander à Lark d'extraire la valeur brute sans encapsuler inutilement.
 
## Organisation du projet
 
Nous avons travaillé en intégration continue directe :
 
- Un fichier de grammaire (`grammaire.lark`) servant de référence commune.
- Un interpréteur (`interpreter.py`) transformant les structures syntaxiques en données pures.
- Un synthétiseur (`generateuraudio.py`) isolé, facilitant les tests de physique acoustique indépendamment du parser
