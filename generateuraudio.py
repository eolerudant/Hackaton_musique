import wave
import math
import struct


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
                
                
                valeur = math.sin(2 * math.pi * freq * temps_actuel) * 0.3
                
                # Enveloppe
                if i < 500: 
                    valeur *= (i / 500)
                elif i > duree_sample - 500: 
                    valeur *= ((duree_sample - i) / 500)
                
                
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