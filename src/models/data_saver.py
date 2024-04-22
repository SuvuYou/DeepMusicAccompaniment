import os
from torch.utils.data import Dataset
import torch
import numpy as np
import sys
from helpers_load import load_txt_song, load_video_frames
from helpers_encode import padd_encoded_song_with_rest
from helpers_mappings import convert_songs_to_int, get_mappings_size
from helpers import has_only_numbers, find_greatest_common_divisor
from helpers_video_processing import process_video
from const import MELODY_MAPPINGS_PATH, CHORDS_MAPPINGS_PATH, CHORDS_CONTEXT_MAPPINGS_PATH, MUSIC_DATA_CHUNKS_SAVE_PATH, VIDEO_CHUNKS_SAVE_PATH, DEFAULT_SEQUENCE_LENGTH, MAPPED_MIDI_DATA_FOLDER_PATH, DEVICE

np.set_printoptions(threshold=sys.maxsize, linewidth=100000)

class MidiDatasetSaver(Dataset):
    def __init__(self, midi_data_folder, video_data_folder, song_lengths, sequence_length = DEFAULT_SEQUENCE_LENGTH):
        self.current_total_chunks = 0
        self.sequence_length = sequence_length
        self.midi_data_folder = midi_data_folder
        self.video_data_folder = video_data_folder

        batches_count_per_song = list(map(lambda x: x - sequence_length, song_lengths))
        self.chunk_size = find_greatest_common_divisor(batches_count_per_song, upper_bound=50, lower_bound=30)

        self.classes_size = {
            "melody": get_mappings_size(MELODY_MAPPINGS_PATH),
            "chords": get_mappings_size(CHORDS_MAPPINGS_PATH),
            "chords_context_inputs": get_mappings_size(CHORDS_CONTEXT_MAPPINGS_PATH),
        }
        
        subfolders = [(path, inner_folders) for path, inner_folders, _ in os.walk(midi_data_folder)]
        
        subfolders_flat = [
            (f"{path}/{inner_folder}", inner_folder)
            for (path, inner_folders) in subfolders
            for inner_folder in inner_folders
        ]
        
        self.folders = [path for path, folder in subfolders_flat if has_only_numbers(folder)]
        
    def __len__(self):
        return len(self.folders)

    def __getitem__(self, idx):
        melody, chords, chords_context, video = self.extract_single_training_file(self.folders[idx])
        self.save_single_type_training_sequence(melody, chords, chords_context, video)
        
        return
    
    def extract_single_training_file(self, folder_path):
        melody = load_txt_song(folder_path, type='melody')
        chords = load_txt_song(folder_path, type='chords')
        chords_context = load_txt_song(folder_path, type='chords-context')
        max_length = max(len(melody.split()), len(chords.split()))

        video, fps = load_video_frames(f"{folder_path.replace(self.midi_data_folder, self.video_data_folder)}/original-180.mp4")
        
        clean_video = process_video(video, target_video_length_in_frames=max_length)

        melody = convert_songs_to_int(padd_encoded_song_with_rest(melody, to_length=max_length), MELODY_MAPPINGS_PATH)
        chords = convert_songs_to_int(padd_encoded_song_with_rest(chords, to_length=max_length), CHORDS_MAPPINGS_PATH)
        chords_context = convert_songs_to_int(padd_encoded_song_with_rest(chords_context, to_length=max_length, is_chords_context=True), CHORDS_CONTEXT_MAPPINGS_PATH)
        
        return melody, chords, chords_context, clean_video
    
    def save_single_type_training_sequence(self, melody, chords, chords_context, video):
        video = video.to(DEVICE)
        
        frames_count = video.shape[0]
        frames_per_data_item = frames_count // len(melody)
        num_sequences = len(melody) - self.sequence_length
        num_chunks = num_sequences // self.chunk_size
        
        for j in range(num_chunks):
            video_save_path = f"{VIDEO_CHUNKS_SAVE_PATH}/{self.current_total_chunks}.pt"
            music_data_save_path = f"{MUSIC_DATA_CHUNKS_SAVE_PATH}/{self.current_total_chunks}.pt"
            melody_inputs = []
            chords_inputs = []
            chords_context_inputs = []
            video_inputs = []
            melody_targets = []
            chords_targets = []
            
            for i in range(self.chunk_size):
                idx = i + (j * self.chunk_size)
                melody_inputs.append(melody[idx : idx + self.sequence_length])
                chords_inputs.append(chords[idx : idx + self.sequence_length])
                chords_context_inputs.append(chords_context[idx + self.sequence_length])
                melody_targets.append(melody[idx + self.sequence_length])
                chords_targets.append(chords[idx + self.sequence_length])
                frames = video[(idx * frames_per_data_item) : (idx + self.sequence_length) * frames_per_data_item]
                video_inputs.append(frames[[0, self.sequence_length / 2]])
            
            melody_inputs = torch.tensor(torch.nn.functional.one_hot(torch.tensor(melody_inputs), num_classes=self.classes_size['melody']), dtype=torch.float32)
            melody_targets = torch.tensor(torch.nn.functional.one_hot(torch.tensor(melody_targets), num_classes=self.classes_size['melody']), dtype=torch.float32)
            chords_inputs = torch.tensor(torch.nn.functional.one_hot(torch.tensor(chords_inputs), num_classes=self.classes_size['chords']), dtype=torch.float32)
            chords_targets = torch.tensor(torch.nn.functional.one_hot(torch.tensor(chords_targets), num_classes=self.classes_size['chords']), dtype=torch.float32)
            chords_context_inputs = torch.tensor(torch.nn.functional.one_hot(torch.tensor(chords_context_inputs), num_classes=self.classes_size['chords_context_inputs']), dtype=torch.float32)
            video_inputs = torch.stack(video_inputs)
     
            music_data = {'melody': melody_inputs, 'melody_target': melody_targets, 'chords': chords_inputs, 'chords_target': chords_targets, "chords_context_inputs": chords_context_inputs}
            video_data = {'video': video_inputs}
            
            torch.save(music_data, music_data_save_path)
            torch.save(video_data, video_save_path)
            
            print(j, ' - chunk')
            
            self.current_total_chunks = self.current_total_chunks + 1

def save_data(song_lengths):  
    dataset = MidiDatasetSaver(midi_data_folder = MAPPED_MIDI_DATA_FOLDER_PATH, video_data_folder = MAPPED_MIDI_DATA_FOLDER_PATH, song_lengths = song_lengths)

    for idx in range(len(dataset)):
        _ = dataset[idx]




  






