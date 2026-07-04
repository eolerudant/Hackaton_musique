import wave
import math
import struct

# Configuration par défaut si l'instrument demandé n'existe pas ou est mal défini
DEFAULT_INSTRUMENT = {
    "oscillator": "sin",
    "enveloppe": [0.01, 0.15, 0.3, 0.2],
    "harmonics": [1.0]
}

def frequence_note(note, octave):
#le LA octave 4 est à 440 Hz, et chaque demi-ton est une multiplication par la racine douzième de 2
    demi_tons = (note - 10) + (octave - 4) * 12
    return 440.0 * (2 ** (demi_tons / 12.0))

def generer_forme_onde(type_onde, phase):
    """
    Génère l'amplitude de l'onde pour une phase donnée selon le type d'oscillateur.
    """
    type_onde = type_onde.lower()
    if "sin" in type_onde:
        return math.sin(phase)
    elif "saw" in type_onde or "scie" in type_onde:
        t_f = phase / (2 * math.pi)
        return 2.0 * (t_f - math.floor(0.5 + t_f))
    elif "square" in type_onde or "carre" in type_onde:
        return 1.0 if math.sin(phase) >= 0 else -1.0
    elif "triangle" in type_onde:
        t_f = phase / (2 * math.pi)
        return 2.0 * abs(2.0 * (t_f - math.floor(t_f + 0.5))) - 1.0
    elif "bruit" in type_onde or "noise" in type_onde:
        # Bruit pseudo-aléatoire déterministe basé sur la phase
        return math.sin(phase * 13.17) * math.cos(phase * 7.43)
    else:
        return math.sin(phase)


def calculer_enveloppe_adsr(temps_actuel, duree_totale, enveloppe_params):

    A_raw, D_raw, S_raw, R_raw = enveloppe_params
    S_level = max(0.0, min(1.0, S_raw))
    
    # Sécurité d'échelle : si la somme Attack + Decay + Release dépasse la durée totale de la note,
    # on les réduit proportionnellement pour éviter les clics et s'adapter au format.
    total_transition = A_raw + D_raw + R_raw
    if total_transition > duree_totale:
        scale = duree_totale / (total_transition * 1.1) if total_transition > 0 else 0.0
        A_time = A_raw * scale
        D_time = D_raw * scale
        R_time = R_raw * scale
    else:
        A_time = A_raw
        D_time = D_raw
        R_time = R_raw
        
    temps_relachement = duree_totale - R_time
    
    if temps_actuel < A_time:
        # Phase A : Attack
        return temps_actuel / A_time if A_time > 0 else 1.0
    elif temps_actuel < (A_time + D_time):
        # Phase D : Decay (on crée une rampe douce vers le niveau de sustain)
        t_decay = temps_actuel - A_time
        ratio = t_decay / D_time if D_time > 0 else 1.0
        return 1.0 - (1.0 - S_level) * ratio
    elif temps_actuel < temps_relachement:
        # Phase S : Sustain (avec une très douce extinction exponentielle pour rester organique)
        t_sustain = temps_actuel - (A_time + D_time)
        return S_level * math.exp(-0.2 * t_sustain)
    else:
        # Phase R : Relâchement en fin de note
        t_sustain_total = temps_relachement - (A_time + D_time)
        if t_sustain_total < 0:
            val_debut_release = S_level
        else:
            val_debut_release = S_level * math.exp(-0.2 * t_sustain_total)
            
        t_release = temps_actuel - temps_relachement
        ratio = t_release / R_time if R_time > 0 else 1.0
        val = val_debut_release * (1.0 - ratio)
        return max(0.0, val)



def generer_audio(donnees_musicales, nom_fichier="ma_musique.wav"):
    meta_data = donnees_musicales.get("meta", {})
    partition_data = donnees_musicales["partition"]
    instruments_banque = donnees_musicales["instruments"]
    
    bpm = meta_data.get("bpm", 120.0)
    notes = partition_data["notes"]
    
    duree_un_temps_sec = 60.0 / bpm
    sample_rate = 44100  # Qualité CD standard 
    
    if not notes:
        print("La partition est vide !")
        return
        
    duree_totale_temps = max(n["temps_0"] + n["duree"] for n in notes)
    duree_totale_sec = duree_totale_temps * duree_un_temps_sec
    nombre_samples = int(sample_rate * duree_totale_sec)
    
    # Créer une piste audio vide 
    piste_audio = [0.0] * nombre_samples
    
    dernier_instrument_nom = "default"
    
    # Ajouter le son de chaque note
    for n in notes:
        # Si la note a un instrument spécifié, il devient le nouvel instrument actif
        if n["instrument"] is not None:
            dernier_instrument_nom = n["instrument"]
        else:
            # Sinon, elle hérite du dernier instrument actif
            n["instrument"] = dernier_instrument_nom
            
        freq = frequence_note(n["note"], n["octave"])
        debut_sec = n["temps_0"] * duree_un_temps_sec
        duree_sec = n["duree"] * duree_un_temps_sec
        
        debut_sample = int(debut_sec * sample_rate)
        duree_sample = int(duree_sec * sample_rate)
        
        # Récupération sécurisée : si l'instrument s'appelle "default" (ou s'il est inconnu),
        # on charge notre dictionnaire de configuration DEFAULT_INSTRUMENT
        inst_def = instruments_banque.get(n["instrument"], DEFAULT_INSTRUMENT)
        oscillator_data = inst_def.get("oscillator", {"type": "sin", "phase": 0.0})
        if isinstance(oscillator_data, str):
            # Cas de secours si l'oscillateur est resté une simple chaîne de caractères
            oscillator_type = oscillator_data
            oscillator_phase = 0.0
        else:
            # Extraction propre de la forme d'onde et de sa phase
            oscillator_type = oscillator_data.get("type", "sin")
            oscillator_phase = oscillator_data.get("phase", 0.0)


        enveloppe_params = inst_def.get("enveloppe", [0.01, 0.15, 0.3, 0.2])
        harmonics = inst_def.get("harmonics", [1.0])
    
        # Application d'un coefficient d'inharmonicité si on imite un piano
        is_piano = "piano" in n["instrument"].lower()
        B = 0.00015 if is_piano else 0.0
        
        for i in range(duree_sample):
            idx = debut_sample + i
            if idx < nombre_samples:
                temps_actuel = i / sample_rate
                
                # Synthèse Additive des Harmoniques
                signal_note = 0.0
                for rank_idx, p in enumerate(harmonics):
                    n_harmonic = rank_idx + 1  
                    #loi physique de l'inharmonicité pour les cordes de piano
                    freq_harmonique = n_harmonic * freq * math.sqrt(1 + B * (n_harmonic ** 2))
                    w_n = 2 * math.pi * freq_harmonique * temps_actuel + oscillator_phase
                    
                    onde_partielle = generer_forme_onde(oscillator_type, w_n)
                    
                    # Amortissement naturel des aiguës
                    amortissement = math.exp(-2.0 * n_harmonic * temps_actuel)
                    
                    signal_note += p * onde_partielle * amortissement
                
                signal_note *= 0.35
                
                #Enveloppe ADSR
                env_val = calculer_enveloppe_adsr(temps_actuel, duree_sec, enveloppe_params)
                valeur_finale = signal_note * env_val
                
                piste_audio[idx] += valeur_finale

    # Sauvegarder dans le fichier .wav
    with wave.open(nom_fichier, 'w') as f:
        f.setnchannels(1)  # Mono
        f.setsampwidth(2)  # 16 bits
        f.setframerate(sample_rate)
        
        for sample in piste_audio:
            sample = max(-1.0, min(1.0, sample))
            valeur_int = int(sample * 32767)
            f.writeframesraw(struct.pack('<h', valeur_int))
    
    print(f"🎵 Fichier audio '{nom_fichier}' généré avec succès !")


