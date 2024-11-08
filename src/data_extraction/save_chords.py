import music21

black_keys_pitches = [1, 3, 6, 8, 10]

def select_pitch(pitch):
    remainder = pitch % 12
    
    if remainder in black_keys_pitches:
        remainder = remainder - 1
    
    return remainder + 60

def _map_pitch (note):
    start_pitch = 60
    
    match(note.replace("#", "")[0]):
        case 'C':
            start_pitch = 60        
        case 'D':
            start_pitch = 62  
        case 'E':
            start_pitch = 64          
        case 'F':
            start_pitch = 65 
        case 'G':
            start_pitch = 67 
        case 'A':
            start_pitch = 69
        case 'B':
            start_pitch = 71
            
    transposition_offset = 3            
            
    start_pitch = select_pitch(start_pitch + transposition_offset)
    
    second_pitch = select_pitch(start_pitch + 4)

    third_pitch = select_pitch(start_pitch + 7)
    
    return start_pitch, second_pitch, third_pitch
    

def _save_chord_progression(melody, step_duration, file_name):
    stream = music21.stream.Stream()    
    melody = [x for x in ' '.join(melody).lstrip('_ ').split()]
    
    melody = ['r','_', '_', '_', 'Em', '_', '_', '_', 'B', '_', '_', '_', '_', '_', '_', '_', 'E', '_', '_', '_', 'Em', '_', '_', '_', 'D', '_', '_', '_', 'B', '_', '_', '_', 'C', '_', '_', '_', 'B', '_', '_', '_', '_', '_', '_', '_', 'Bm', '_', '_', '_', 'C', '_', '_', '_', '_', '_', '_', '_', '_', 'D', '_', '_', 'B', '_', '_', '_', '_', '_', 'E', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', 'B', '_', '_', '_', '_', '_', '_', '_', 'Em', '_', '_', '_', '_', '_', 'C', '_', 'E', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', 'C', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', 'E', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', 'C', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', 'D', '_', '_', '_', '_', '_', '_', '_', 'Em', '_', '_', '_', '_', '_', '_', '_', 'C', '_', '_', '_', '_', '_', '_', '_', 'B', '_', '_', '_', '_', '_', '_', 'C', '_', '_', '_', '_', '_', '_', '_', '_', 'D', '_', '_', '_', '_', '_', '_', 'E', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', 'C', '_', '_', '_', '_', '_', 'B', '_', 'E', '_', '_', '_', '_', '_', '_', '_', 'C', '_', '_', '_', 'G', '_', '_', '_', 'F#', '_', '_', '_', '_', '_', '_', 'E', '_', '_', '_', '_', '_', 'B', '_', '_', 'E', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', 'Em', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', 'E', '_', '_', '_', '_', '_', '_', '_', '_', '_', 'G', '_', '_', '_', 'B', '_', '_', '_', 'E', '_', '_', '_', 'B', '_', '_', '_', 'E', '_', '_', '_', '_', '_', '_', '_', 'C', '_', '_', '_', '_', '_', 'Dm', '_', 'B', '_', '_', '_', '_', '_', 'D', '_', 'A', '_', '_', '_', '_', '_', 'C#m', '_', '_', '_', 'A', '_', '_', '_', '_', '_', 'Am', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', 'D', '_', '_', 'E', '_', '_', '_', '_', '_', '_', '_', 'C', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', 'B', '_', 'E', '_', '_', '_', 'Em', '_', '_', '_', 'A', '_', '_', '_', 'Bm', '_', '_', '_', 'E', '_', '_', '_', 'G', '_', '_', '_', 'A', '_', '_', '_', 'B', '_', '_', '_', 'C', '_', '_', '_', 'A', '_', '_', '_', 'E', '_', '_', '_', 'B', '_', '_', '_', 'C', '_', '_', '_', '_', '_', '_', '_', 'D', '_', '_', '_', 'B', '_', '_', '_', '_', '_', '_', 'C', '_', '_', '_', '_', 'E', '_', '_', '_', '_', '_', '_', 'C', '_', '_', '_', '_', 'E', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_']

    current_symbol = melody[0]
    current_symbol_step_counter = 1
    
    melody_length = len(melody[1:])

    for i, symbol in enumerate(melody[1:]):     
        if symbol == "_" and i != melody_length - 1:
            current_symbol_step_counter += 1
        else:
            quarter_length_duration = step_duration * current_symbol_step_counter
            
            if current_symbol == "r":
                event = music21.note.Rest(quarterLength=quarter_length_duration)
            else:
                event = music21.chord.Chord(notes=_map_pitch(current_symbol), quarterLength=quarter_length_duration)
                
            stream.append(event)
            
            current_symbol = symbol
            current_symbol_step_counter = 1
                
    stream.write('midi', file_name)
    
_save_chord_progression(melody=[], step_duration=1, file_name="chords.mid")