from const import MAPPINGS_PATH
from helpers_load import load_txt_songs, export_encoded_songs
from helpers_mappings import create_mapping
from data_saver import save_data

if __name__ == "__main__":
    export_encoded_songs(type='melody')
    export_encoded_songs(type='chords')

    melody_songs, melody_lengths = load_txt_songs(type='melody')
    chords_songs, chords_lengths = load_txt_songs(type='chords')
    chords_context_songs, chords_context_lengths = load_txt_songs(type='chords-context')

    create_mapping(melody_songs, f"{MAPPINGS_PATH}/melody_mappings.json")
    create_mapping(chords_songs, f"{MAPPINGS_PATH}/chords_mappings.json")
    create_mapping(chords_context_songs, f"{MAPPINGS_PATH}/chords_context_mappings.json")

    # song_lengths = melody_lengths + chords_lengths
    save_data(song_lengths = melody_lengths + chords_lengths)