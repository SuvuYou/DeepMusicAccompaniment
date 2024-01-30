import os
from torch.utils.data import Dataset
import torch
from const import VIDEO_CHUNKS_SAVE_PATH, MUSIC_DATA_CHUNKS_SAVE_PATH

class MidiDatasetLoader(Dataset):
    def __init__(self):
        self.data_folder = VIDEO_CHUNKS_SAVE_PATH

    def __len__(self):
        return len(os.listdir(VIDEO_CHUNKS_SAVE_PATH))

    def __getitem__(self, idx):
        video_load_path = f"{VIDEO_CHUNKS_SAVE_PATH}/{idx}.pt"
        music_load_path = f"{MUSIC_DATA_CHUNKS_SAVE_PATH}/{idx}.pt"
        video_data = torch.load(video_load_path)
        music_data = torch.load(music_load_path)
        
        return (music_data['melody'], music_data['chords'], music_data['chords_context_inputs'], video_data['video']), (music_data['melody_target'], music_data['chords_target'])