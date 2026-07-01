import wave
import math
import struct

# ==============================================================
                #BANQUE D'INSTRUMENTS
# ==============================================================

def son_bip(temps_actuel, freq, duree_totale):
    # Génère un son bip simple (sinusoïde)
    valeur = math.sin(2 * math.pi * freq * temps_actuel) * 0.3

    # Enveloppe simple
    if temps_actuel < 0.01:
        valeur *= (temps_actuel / 0.01)
    elif temps_actuel > duree_totale - 0.01:
        valeur *= ((duree_totale - temps_actuel) / 0.01)
        
    return valeur

def son_piano(temps_actuel, freq, duree_totale):
    B = 0.00015  # Coefficient d'inharmonicité, en réalité les harmoniques ne sont pas exactement des multiples de la fondamentale
    vitesse_extinction_harmoniques = 2.0  
    
    # Spectre initial au moment de l'impact (Fondamentale, h2, h3, h4, h5, h6, h7)
    poids_initiaux = [1.0, 0.6, 0.35, 0.15, 0.08, 0.04, 0.02]
    
    # 2. SYNTHÈSE ADDITIVE DYNAMIQUE DES HARMONIQUES
    onde = 0.0
    for idx, p in enumerate(poids_initiaux):
        n = idx + 1  # Rang de l'harmonique
        
        # Formule physique de l'inharmonicité d'une corde 
        freq_harmonique = n * freq * math.sqrt(1 + B * (n ** 2))
        w_n = 2 * math.pi * freq_harmonique * temps_actuel
        
        # Amortissement dynamique
        amortissement = math.exp(-vitesse_extinction_harmoniques * n * temps_actuel)
        
        onde += p * math.sin(w_n) * amortissement
    
    # Équilibrage du volume de l'onde harmonique pour éviter la saturation
    onde *= 0.35
    
    # Marteau
    bruit_marteau = 0.0
    if temps_actuel < 0.015:
        
        bruit_blanc_simule = math.sin(temps_actuel * 80000.0) * math.cos(temps_actuel * 45000.0)
        # Enveloppe de percussion ultra-rapide
        bruit_marteau = bruit_blanc_simule * 0.12 * math.exp(-350.0 * temps_actuel)
    
    # On assemble la corde vibrante et l'impact du marteau
    son_physique = onde + bruit_marteau

    # Enveloppe
    A_time = 0.005   # Attack
    R_time = 0.15    # Release
    
    if R_time > duree_totale:
        R_time = duree_totale * 0.3
        
    temps_relachement = duree_totale - R_time
    
    if temps_actuel < A_time:
        enveloppe = temps_actuel / A_time
    elif temps_actuel < temps_relachement:

        enveloppe = 1.0
    else:
        # Phase de Relâchement
        t_release = temps_actuel - temps_relachement
        enveloppe = 1.0 - (t_release / R_time)
        enveloppe = max(0.0, enveloppe)
        
    return son_physique * enveloppe



# Dictionnaire associant les numéros aux fonctions instruments 
BANQUE_INSTRUMENTS = {
    0: son_bip,
    1: son_piano,
}

def frequence_note(note, octave):
#le LA octave 4 est à 440 Hz, et chaque demi-ton est une multiplication par la racine douzième de 2
    demi_tons = (note - 10) + (octave - 4) * 12
    return 440.0 * (2 ** (demi_tons / 12.0))

def generer_audio(donnees_musicales, nom_fichier="output.wav"):
    bpm = donnees_musicales["bpm"]
    notes = donnees_musicales["notes"]
    
    # 1 temps en secondes = 60 / BPM
    duree_un_temps_sec = 60.0 / bpm
    
    sample_rate = 44100  # Qualité CD standard (44100 échantillons par seconde)
    
    #Trouver la durée totale de la partition
    if not notes:
        print("La partition est vide !")
        return
        
    duree_totale_temps = max(n["temps_0"] + n["duree"] for n in notes)
    duree_totale_sec = duree_totale_temps * duree_un_temps_sec
    nombre_samples = int(sample_rate * duree_totale_sec)
    
    
    piste_audio = [0.0] * nombre_samples
    
    
    for n in notes:
        freq = frequence_note(n["note"], n["octave"])
        debut_sec = n["temps_0"] * duree_un_temps_sec
        duree_sec = n["duree"] * duree_un_temps_sec
        
        debut_sample = int(debut_sec * sample_rate)
        duree_sample = int(duree_sec * sample_rate)
        
        for i in range(duree_sample):
            idx = debut_sample + i
            if idx < nombre_samples:
                temps_actuel = i / sample_rate
                
                fonction_instrument = BANQUE_INSTRUMENTS.get(n["instrument"], son_bip)
                valeur = fonction_instrument(temps_actuel, freq, duree_sec)
                
                piste_audio[idx] += valeur

    
    with wave.open(nom_fichier, 'w') as f:
        f.setnchannels(1)  # Mono
        f.setsampwidth(2)  # 16 bits
        f.setframerate(sample_rate)
        
        for sample in piste_audio:
            
            sample = max(-1.0, min(1.0, sample))
            # Conversion en entier 16 bits (format attendu par le fichier WAV)
            valeur_int = int(sample * 32767)
            f.writeframesraw(struct.pack('<h', valeur_int))
    
    print(f"🎵 Fichier audio '{nom_fichier}' généré avec succès !")