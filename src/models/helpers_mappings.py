import json
from collections import Counter

def create_mapping(songs, mapping_path):
    mappings = {}
    
    songs = [song.split() for song in songs]
    songs_flat = sum(songs, [])
    
    unique_symbols = list(set(songs_flat))
    symbols_counts = Counter(songs_flat)
    mapped_symbols_counts = {}
   
    for i, symbol in enumerate(unique_symbols):
        mappings[symbol] = i
        mapped_symbols_counts[i] = symbols_counts[symbol]
        
    data = {
        'mappings': mappings,
        'counter': {
            "symbols": symbols_counts,
            "mapped_symbols": mapped_symbols_counts
            }
        }    

    with open(mapping_path, "w") as fp:
        json.dump(data, fp, indent=4)
        
def convert_songs_to_int(songs, mapping_path):
    int_songs = []

    with open(mapping_path, "r") as fp:
        data = json.load(fp)

    songs = songs.split()

    for symbol in songs:
        int_songs.append(data["mappings"][symbol])

    return int_songs

def get_mappings_size(mapping_path):
    with open(mapping_path, "r") as fp:
        data = json.load(fp)

    return len(data["mappings"].items())
