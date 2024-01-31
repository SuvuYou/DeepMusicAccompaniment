import json
import os
import torch

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
RAW_DATASET_PATH = "data"
TRANSPOSED_DATASET_PATH = f"{RAW_DATASET_PATH}/transposed_midi"
CLEAN_DATA_FOLDER_PATH = f"{RAW_DATASET_PATH}/processed_with_mapping"
MAPPINGS_PATH = f"{RAW_DATASET_PATH}/processed_with_mapping"
MUSIC_DATA_CHUNKS_SAVE_PATH = "data/tensors"
VIDEO_CHUNKS_SAVE_PATH = "data/tensors_video"
SONG_LENGTHS_FILE_PATH = "data/processed_with_mapping/song_lengths.txt"
DEFAULT_SEQUENCE_LENGTH = 24
DEFAULT_MODEL_WEIGHTS_FOLDER_NAME = lambda idx: f"weights/{idx}"
DEFAULT_MELODY_MODEL_WEIGHTS_FILE_NAME = lambda idx: f"weights/{idx}/melody_model_weights.pth"
DEFAULT_CHORDS_MODEL_WEIGHTS_FILE_NAME = lambda idx: f"weights/{idx}/chords_model_weights.pth"

ACCEPTABLE_DURATIONS = [
    0.25, 
    0.5,
    0.75,
    1.0, 
    1.25,
    1.5,
    1.75,
    2,
    2.5,
    3,
    3.5,
    4
]

SORTED_CHORDS_LIST = ["C", "D", "E", "F", "G", "A", "B"]

melody_mappings_file_path = f"{MAPPINGS_PATH}/melody_mappings.json"
chords_mappings_file_path = f"{MAPPINGS_PATH}/chords_mappings.json"
chords_context_mappings_file_path = f"{MAPPINGS_PATH}/chords_context_mappings.json"

if os.path.exists(melody_mappings_file_path):
    with open(melody_mappings_file_path, "r") as fp:
        melody_mappings = json.load(fp)['mappings']
else:
    melody_mappings = {}
    
if os.path.exists(chords_mappings_file_path):
    with open(chords_mappings_file_path, "r") as fp:
        chords_mappings = json.load(fp)['mappings']
else:
    chords_mappings = {}    
    
if os.path.exists(chords_context_mappings_file_path):
    with open(chords_context_mappings_file_path, "r") as fp:
        chords_context_mappings = json.load(fp)['mappings']
else:
    chords_context_mappings = {}     

melody_classes_count = len(list(melody_mappings.items()))
chords_classes_count = len(list(chords_mappings.items()))
chords_context_classes_count = len(list(chords_context_mappings.items()))

MODEL_SETTINGS = {
    "melody": {
        "melody_input_size": melody_classes_count,
        "chords_context_input_size": chords_context_classes_count,
        "hidden_size": 1024,
        "output_size": melody_classes_count,
        "cnn_feature_size": 128,
        "chords_feature_size": 32,
        "num_layers": 3,
    },
    "chords": {
        "input_size": chords_classes_count,
        "hidden_size": 1024,
        "output_size": chords_classes_count,
        "cnn_feature_size": 128,
        "num_layers": 3,
    },
    "num_epochs": 50
}
