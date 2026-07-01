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
    # Exemple de poids : [Fondamentale, h2, h3, h4]
    poids = [1.0, 0.5, 0.25, 0.125]
    w = 2 * math.pi * freq * temps_actuel
    onde = 0
    for n, p in enumerate(poids, start=1):
        onde += p * math.sin(n * w)
    
    
    
    #PARAMÈTRES DE L'ENVELOPPE ADSR (en secondes)
    A_time = 0.01    # Attack (temps)
    D_time = 0.15    # Declay (temps pour attaindre le niveau de sustain)
    S_level = 0.3    # Sustain (taux de volume maintenu)
    R_time = 0.20    # Release (temps)
    
    # Sécurité pour les notes très courtes : le relâchement ne peut dépasser 30% de la note
    if R_time > duree_totale:
        R_time = duree_totale * 0.3
        
    temps_relachement = duree_totale - R_time
    
    #CALCUL DE L'ENVELOPPE DYNAMIQUE
    if temps_actuel < A_time:
        
        enveloppe = temps_actuel / A_time
        
    elif temps_actuel < (A_time + D_time):
        
        t_decay = temps_actuel - A_time
        enveloppe = 1.0 - (1.0 - S_level) * (t_decay / D_time)
        
    elif temps_actuel < temps_relachement:
        
        t_sustain = temps_actuel - (A_time + D_time)
        enveloppe = S_level * math.exp(-0.8 * t_sustain)
        
    else:
        
        t_sustain_total = temps_relachement - (A_time + D_time)
        if t_sustain_total < 0:
            val_debut_release = S_level
        else:
            val_debut_release = S_level * math.exp(-0.8 * t_sustain_total)
            
        t_release = temps_actuel - temps_relachement
        enveloppe = val_debut_release * (1.0 - (t_release / R_time))
        enveloppe = max(0.0, enveloppe)
        
    return onde * enveloppe



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