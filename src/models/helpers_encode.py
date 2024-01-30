import music21
from helpers import closest, custom_sort_key
from const import ACCEPTABLE_DURATIONS

black_keys_pitches = [1, 3, 6, 8, 10]

def select_pitch(pitch):
    remainder = pitch % 12
    
    if remainder in black_keys_pitches:
        remainder = remainder - 1
    
    return remainder + 60
            
def encode_melody(song, time_step=ACCEPTABLE_DURATIONS[0]):
    encoded_song = []

    for event in song.flatten().notesAndRests:
        event_duration = closest(ACCEPTABLE_DURATIONS, event.duration.quarterLength)
        
        if isinstance(event, music21.note.Note):
            symbol = select_pitch(event.pitch.midi)
            # symbol = event.pitch.midi
            
        if isinstance(event, music21.chord.Chord):
            symbol = select_pitch(event.pitches[0].midi)
            # symbol = event.pitches[0].midi

        elif isinstance(event, music21.note.Rest):
            symbol = "r"
            
            if event.duration.quarterLength < ACCEPTABLE_DURATIONS[0]:
                continue
                     
        steps = int(event_duration / time_step)
        
        for step in range(steps):
            if step == 0:
                encoded_song.append(symbol)
            else:
                encoded_song.append("_")

    encoded_song = " ".join(map(str, encoded_song))
    
    return encoded_song

def encode_chords(song, time_step=ACCEPTABLE_DURATIONS[0]):
    encoded_song = []

    for event in song.flatten().notesAndRests:
        event_duration = closest(ACCEPTABLE_DURATIONS, event.duration.quarterLength)
                
        if isinstance(event, music21.chord.Chord):
            chord = "-".join(sorted(event.pitchNames, key=custom_sort_key))
            symbol = f"({chord})"

        elif isinstance(event, music21.note.Rest):
            symbol = "r"
            
            if event.duration.quarterLength < ACCEPTABLE_DURATIONS[0]:
                continue    
                     
        steps = int(event_duration / time_step)
        
        for step in range(steps):
            if step == 0:
                encoded_song.append(symbol)
            else:
                encoded_song.append("_")

    encoded_song = " ".join(map(str, encoded_song))

    return encoded_song

def encode_chords_with_no_duration(song, time_step=ACCEPTABLE_DURATIONS[0]):
    encoded_song = []

    for event in song.flatten().notesAndRests:
        event_duration = closest(ACCEPTABLE_DURATIONS, event.duration.quarterLength)
                
        if isinstance(event, music21.chord.Chord):
            chord = "-".join(sorted(event.pitchNames, key=custom_sort_key))
            symbol = f"({chord})"

        elif isinstance(event, music21.note.Rest):
            symbol = "r"
            
            if event.duration.quarterLength < ACCEPTABLE_DURATIONS[0]:
                continue    
                     
        steps = int(event_duration / time_step)
        
        for _ in range(steps):
            encoded_song.append(symbol)


    encoded_song = " ".join(map(str, encoded_song))

    return encoded_song

def padd_encoded_song_with_rest(song, to_length, is_chords_context = False):
    encoded_song = song.split()
    
    if len(encoded_song) >= to_length:
        return song

    symbols = [symbol for symbol in encoded_song if symbol != '_']
    last_symbol = symbols[len(symbols) - 1]
    
    if last_symbol != 'r':
        encoded_song.append('r')
        
    if is_chords_context:
        encoded_song.extend(["r"] * (to_length - len(encoded_song)))
    else:
        encoded_song.extend(["_"] * (to_length - len(encoded_song)))   
    
    encoded_song = " ".join(map(str, encoded_song))
    
    return encoded_song
