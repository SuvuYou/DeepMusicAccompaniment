import os
import music21
from helpers_encode import encode_chords, encode_melody, encode_chords_with_no_duration
from const import TRANSPOSED_DATASET_PATH, CLEAN_DATA_FOLDER_PATH
import torchvision

def load_midi_songs(type):
    """
    type: "melody" | "chords"
    """
    load_path = TRANSPOSED_DATASET_PATH
    save_path = CLEAN_DATA_FOLDER_PATH
    songs = []
    paths = []

    for path, _, files in os.walk(load_path):
        if len(files) > 0:
            song_load_path = path
            song_transposed_path = path
            song_save_path = path.replace(load_path, save_path)
            
            for file in files:
                if file[-3:] == "mid":  
                    if ((type == "melody" and "midi-melody" in file) or 
                        (type == "chords" and "midi-chords" in file)):
                        print(song_load_path, file)
                        song = music21.converter.parse(os.path.join(path, file))
                        songs.append(song)
                        paths.append((song_load_path, song_transposed_path, song_save_path))

    return zip(songs, paths)

def load_txt_songs(type):
    """
    type: "melody" | "chords" | "chords-context"
    """
    load_path = CLEAN_DATA_FOLDER_PATH
    songs = []

    for path, _, files in os.walk(load_path):    
        for file in files:
            if file[-3:] == "txt":  
                if ((type == "melody" and "melody" in file) or 
                    (type == "chords" and "chords" in file and "chords-context" not in file) or
                    (type == "chords-context" and "chords-context" in file)):
                    
                    with open(os.path.join(path, file), "r") as f:
                        song = f.read()

                    songs.append(song)

    song_lengths = [len(song.split()) for song in songs]
    
    return songs, song_lengths
            
def load_txt_song(load_path, type):
    """
    type: "melody" | "chords" | "chords-context"
    """
                    
    with open(f"{os.path.join(load_path, type)}.txt", "r") as f:
        song = f.read()

    return song

def save_to_file(data, folder_path, save_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    with open(save_path, "w") as fp:
        fp.write(data)   
    

def export_encoded_songs(type):
    """
    type: "melody" | "chords" | "chords-context"
    """
    songs = load_midi_songs(type)
    
    for song, paths in songs:
        _, _, save_path = paths
        
        print(paths)
        
        if type == 'chords':
            encoded_song = encode_chords(song)
            encoded_song_context = encode_chords_with_no_duration(song)
            save_to_file(data=encoded_song, folder_path=save_path, save_path=f"{save_path}/{type}.txt")
            save_to_file(data=encoded_song_context, folder_path=save_path, save_path=f"{save_path}/{type}-context.txt")
        else:
            encoded_song = encode_melody(song)  
            save_to_file(data=encoded_song, folder_path=save_path, save_path=f"{save_path}/{type}.txt")
       
                           
            
def load_video_frames(folder_path):
    video, _, fps_data = torchvision.io.read_video(folder_path)
    
    print(video.shape, fps_data)

    return video, fps_data['video_fps']