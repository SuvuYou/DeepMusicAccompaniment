import json
import numpy as np
import torch
import music21
from models import MelodyLSTM, ChordsLSTM
from helpers_load import load_video_frames
from helpers_video_processing import process_video
from const import DEFAULT_SEQUENCE_LENGTH, MELODY_MAPPINGS_PATH, CHORDS_MAPPINGS_PATH, CHORDS_CONTEXT_MAPPINGS_PATH, MODEL_SETTINGS, DEFAULT_MELODY_MODEL_WEIGHTS_FILE_NAME, DEFAULT_CHORDS_MODEL_WEIGHTS_FILE_NAME, ACCEPTABLE_DURATIONS

class Generator:
    def __init__(self, weights_path, save_file_name):
        self.save_file_name = save_file_name
        self.melody_model_weights_path = DEFAULT_MELODY_MODEL_WEIGHTS_FILE_NAME(weights_path)
        self.chords_model_weights_path = DEFAULT_CHORDS_MODEL_WEIGHTS_FILE_NAME(weights_path)
        
        melody_generation_model = MelodyLSTM(**MODEL_SETTINGS['melody'])

        melody_generation_model.load_state_dict(torch.load(self.melody_model_weights_path))
        
        chords_generation_model = ChordsLSTM(**MODEL_SETTINGS['chords'])

        chords_generation_model.load_state_dict(torch.load(self.chords_model_weights_path))
            
        self.melody_generation_model = melody_generation_model
        self.chords_generation_model = chords_generation_model
        
        with open(MELODY_MAPPINGS_PATH, "r") as fp:
            self._melody_mappings = json.load(fp)['mappings']
            
        with open(CHORDS_MAPPINGS_PATH, "r") as fp:
            self._chords_mappings = json.load(fp)['mappings']    
            
        with open(CHORDS_CONTEXT_MAPPINGS_PATH, "r") as fp:
            self._chords_context_mappings = json.load(fp)['mappings'] 


    def generate(self, melody_seed, chords_seed, chords_context_seed, video, num_steps, max_sequence_length, temperature):
        with torch.no_grad():
            melody_seed = melody_seed.split()
            chords_seed = chords_seed.split()
            chords_context_seed = chords_context_seed.split()
            
            melody = melody_seed
            chords = chords_seed
        
            melody_seed = [self._melody_mappings[symbol] for symbol in melody_seed]
            chords_seed = [self._chords_mappings[symbol] for symbol in chords_seed]
            chords_context_seed = [self._chords_context_mappings[symbol] for symbol in chords_context_seed]

            for idx in range(num_steps):
                # Slice seeds  
                melody_seed = melody_seed[-max_sequence_length:]
                seed_length = len(melody_seed)
                chords_seed = chords_seed[-max_sequence_length:]
                chords_context_seed = chords_context_seed[-max_sequence_length:]
                video_seed = video[idx : idx + seed_length]
                video_seed = video_seed[[0, len(video_seed) / 2]]
                
                # Generate next chord symbol
                onehot_chords_seed = torch.nn.functional.one_hot(torch.tensor(chords_seed, dtype=torch.int64), num_classes=len(self._chords_mappings))
                chords_output = self.chords_generation_model(onehot_chords_seed.unsqueeze(0).float(), video_seed.unsqueeze(0).float())
                chords_probabilities = chords_output[0]
                chords_output_int = self._sample_with_temperature(chords_probabilities, temperature)      
                chords_output_symbol = [k for k, v in self._chords_mappings.items() if v == chords_output_int][0]
                chords_seed.append(chords_output_int)
                chords.append(chords_output_symbol)
                
                # Get chord context from generated chord for melody model
                if chords_output_symbol == '_':
                    chords_context_output_int = chords_context_seed[seed_length - 1]
                else:
                    chords_context_output_int = self._chords_context_mappings[chords_output_symbol]
                
                selected_chord_context = torch.nn.functional.one_hot(torch.tensor([chords_context_output_int], dtype=torch.int64), num_classes=len(self._chords_context_mappings))
                chords_context_seed.append(chords_context_output_int)
                
                # Generate next melody symbol
                onehot_melody_seed = torch.nn.functional.one_hot(torch.tensor(melody_seed, dtype=torch.int64), num_classes=len(self._melody_mappings))
                melody_output = self.melody_generation_model(onehot_melody_seed.unsqueeze(0).float(), selected_chord_context.float(), video_seed.unsqueeze(0).float())
                melody_probabilities = melody_output[0]
                melody_output_int = self._sample_with_temperature(melody_probabilities, temperature)
                melody_output_symbol = [k for k, v in self._melody_mappings.items() if v == melody_output_int][0]
                melody_seed.append(melody_output_int)
                melody.append(melody_output_symbol)
                
            return chords, melody

    def _sample_with_temperature(self, probabilites, temperature):
        predictions = np.log(probabilites.numpy()) / temperature
        probabilites = np.exp(predictions) / np.sum(np.exp(predictions))

        choices = range(len(probabilites))
        index = np.random.choice(choices, p=probabilites)

        return index
    
    
    def _save_melody(self, melody, step_duration, file_name):
        stream = music21.stream.Stream()    
        melody = [x for x in ' '.join(melody).lstrip('_ ').split()]

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
                    event = music21.note.Note(int(current_symbol), quarterLength=quarter_length_duration)
                    
                stream.append(event)
                
                current_symbol = symbol
                current_symbol_step_counter = 1
                    
        stream.write('midi', file_name)
    
    def _save_chord_progression(self, chords, step_duration, file_name):
        stream = music21.stream.Stream()    
        chords = [x for x in ' '.join(chords).lstrip('_ ').split()]

        current_symbol = chords[0]
        current_symbol_step_counter = 1
        
        melody_length = len(chords[1:])

        for i, symbol in enumerate(chords[1:]):     
            if symbol == "_" and i != melody_length - 1:
                current_symbol_step_counter += 1
            else:
                quarter_length_duration = step_duration * current_symbol_step_counter
                
                if current_symbol == "r":
                    event = music21.note.Rest(quarterLength=quarter_length_duration)
                else:
                    current_symbol = current_symbol.replace('(', '').replace(')', '').split('-')
                    event = music21.chord.Chord(notes=current_symbol, quarterLength=quarter_length_duration)
                    
                stream.append(event)
                
                current_symbol = symbol
                current_symbol_step_counter = 1
                    
        stream.write('midi', file_name)
        
    def save_to_file(self, chords, melody, step_duration=ACCEPTABLE_DURATIONS[0]):
        self._save_chord_progression(chords, step_duration, file_name=f'generated/{self.save_file_name}_chords.mid')
        self._save_melody(melody, step_duration, file_name=f'generated/{self.save_file_name}_melody.mid')        
    
def init_seed(type):
    notes_to_generage_count = 200
    seeds = {
        "fast":{
            "seed_melody": "64 71 69 64 64 71 69 64 64 71 69 64",
            "seed_chords": "(C-E-A) _ _ _ _ _ _ _ _ _ _ _",
            "seed_chords_context": "(C-E-A) _ _ _ _ _ _ _ _ _ _ _".replace("_", "(C-E-A)")
        },
        "fast1":{
            "seed_melody": "60 64 69 60 60 64 69 60 _ _ _ 67 71 64 67 71 71 64 67 71 71 64 67 71",
            "seed_chords": "(C-E-G) _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ (C-E-G) _ _ _ _ _ _ _",
            "seed_chords_context": "(C-E-G) _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ (C-E-G) _ _ _ _ _ _ _".replace("_", "(C-E-G)")
        },
        "slow1":{
            "seed_melody": "69 _ _ _ _ _ _ _ 69 _ 64 _ 71 _ 60 _ 60 _ _ _ _ _",
            "seed_chords": "(D-F-A) _ _ _ _ _ _ _ (C-E-A) _ _ _ _ _ _ _ (C-E-A) _ _ _ _ _ _",
            "seed_chords_context": "(D-F-A) _ _ _ _ _ _ _ (C-E-A) _ _ _ _ _ _ _ (C-E-A) _ _ _ _ _ _".replace("_", "(C-E-A)")
        },
        "slow":{
            "seed_melody": "r _ _ _ _ _ _ _ _ _ _ _",
            "seed_chords": "(D-F-B) _ _ _ _ _ _ _ _ _ _ _",
            "seed_chords_context": "(D-F-B) _ _ _ _ _ _ _ _ _ _ _".replace("_", "(D-F-B)")
        }
    }
    
    seed_melody = seeds[type]["seed_melody"]
    seed_chords = seeds[type]["seed_chords"]
    seed_chords_context = seeds[type]["seed_chords_context"]
    
    seed_video, fps = load_video_frames(folder_path=f"generated/original-180-{type}.mp4")

    video_frames = process_video(video=seed_video, target_video_length_in_frames=notes_to_generage_count + len(seed_melody.split()))
    
    return seed_melody, seed_chords, seed_chords_context, video_frames, notes_to_generage_count
    
def init_generator(weights_path, save_file_name):
    generator = Generator(weights_path, save_file_name)
    
    return generator

def generate_music(generator, seed_melody, seed_chords, seed_chords_context, video_frames, notes_to_generage_count):
    chords, melody = generator.generate(melody_seed=seed_melody,
                         chords_seed=seed_chords,
                         chords_context_seed=seed_chords_context,
                         video=video_frames,
                         num_steps=notes_to_generage_count, 
                         max_sequence_length=DEFAULT_SEQUENCE_LENGTH, 
                         temperature=0.9)
    
    print(chords, melody)
    generator.save_to_file(chords, melody)
    
    
if __name__ == "__main__":
    generator = init_generator(weights_path="19", save_file_name="generated")
    seed_melody, seed_chords, seed_chords_context, video_frames, notes_to_generage_count = init_seed(type="fast1")
    
    generate_music(generator, seed_melody, seed_chords, seed_chords_context, video_frames, notes_to_generage_count)  