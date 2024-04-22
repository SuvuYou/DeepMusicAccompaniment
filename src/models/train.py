import torch 
import json
import os
import numpy as np
from data_loader import MidiDatasetLoader
from models import MelodyLSTM, ChordsLSTM
from const import MODEL_SETTINGS, MELODY_MAPPINGS_PATH, CHORDS_MAPPINGS_PATH, DEFAULT_MODEL_WEIGHTS_FOLDER_NAME, DEFAULT_CHORDS_MODEL_WEIGHTS_FILE_NAME, DEFAULT_MELODY_MODEL_WEIGHTS_FILE_NAME, DEVICE

print("DEVICE -", DEVICE)
        
melody_model = MelodyLSTM(melody_input_size = MODEL_SETTINGS['melody']['melody_input_size'], 
                          chords_context_input_size = MODEL_SETTINGS['melody']['chords_context_input_size'], 
                          hidden_size = MODEL_SETTINGS['melody']['hidden_size'], 
                          num_layers = MODEL_SETTINGS['melody']['num_layers'],  
                          output_size = MODEL_SETTINGS['melody']['output_size'],
                          cnn_feature_size = MODEL_SETTINGS['melody']['cnn_feature_size'],
                          chords_feature_size = MODEL_SETTINGS['melody']['chords_feature_size']
                          )

chords_model = ChordsLSTM(input_size = MODEL_SETTINGS['chords']['input_size'], 
                          hidden_size = MODEL_SETTINGS['chords']['hidden_size'], 
                          num_layers = MODEL_SETTINGS['chords']['num_layers'],  
                          output_size = MODEL_SETTINGS['chords']['output_size'],
                          cnn_feature_size = MODEL_SETTINGS['chords']['cnn_feature_size'],
                          )

starting_weights_idx = 67

melody_model.load_state_dict(torch.load(DEFAULT_MELODY_MODEL_WEIGHTS_FILE_NAME(starting_weights_idx)))
chords_model.load_state_dict(torch.load(DEFAULT_CHORDS_MODEL_WEIGHTS_FILE_NAME(starting_weights_idx)))

melody_model = melody_model.to(DEVICE)
chords_model = chords_model.to(DEVICE)

with open(MELODY_MAPPINGS_PATH, "r") as fp:
            melody_mappings = json.load(fp)
    
with open(CHORDS_MAPPINGS_PATH, "r") as fp:
            chords_mappings = json.load(fp)        
            
melody_symbols_count = melody_mappings['counter']['mapped_symbols']
melody_mappings_indexes = melody_mappings['mappings'] 

chords_symbols_count = chords_mappings['counter']['mapped_symbols']
chords_mappings_indexes = chords_mappings['mappings']

melody_symbols_count_list = np.array(list(melody_symbols_count.values())).copy()
chords_symbols_count_list = np.array(list(chords_symbols_count.values())).copy()

# melody_class_weights = torch.ones(len(melody_symbols_count_list))
melody_class_weights = torch.tensor(sum(melody_symbols_count_list) / (len(melody_symbols_count_list) * melody_symbols_count_list), dtype=torch.float32)

# chords_class_weights = torch.ones(len(chords_symbols_count_list))
chords_class_weights = torch.tensor(sum(chords_symbols_count_list) / (len(chords_symbols_count_list) * chords_symbols_count_list), dtype=torch.float32)

def print_class_weights(message):
    print(message)
    print("Melody weights")
    for key in melody_mappings_indexes.keys():
        print(f"{key}: {melody_class_weights[melody_mappings_indexes[key]]}")
        
    print("Chords weights")
    for key in chords_mappings_indexes.keys():
        print(f"{key}: {chords_class_weights[chords_mappings_indexes[key]]}")    
    
def update_melody_class_weight_by_percentage(symbol, percentage):
    melody_class_weights[melody_mappings_indexes[symbol]] = melody_class_weights[melody_mappings_indexes[symbol]] * (0.01 * percentage)
    
def update_chords_class_weight_by_percentage(symbol, percentage):
    chords_class_weights[chords_mappings_indexes[symbol]] = chords_class_weights[chords_mappings_indexes[symbol]] * (0.01 * percentage)    
      
    
print_class_weights("Initial weights:")

update_melody_class_weight_by_percentage(symbol='_', percentage=195)
update_melody_class_weight_by_percentage(symbol='64', percentage=90)
update_melody_class_weight_by_percentage(symbol='65', percentage=95)
update_melody_class_weight_by_percentage(symbol='71', percentage=95)

update_chords_class_weight_by_percentage(symbol='_', percentage=175)

melody_criterion = torch.nn.CrossEntropyLoss(weight=melody_class_weights)
chords_criterion = torch.nn.CrossEntropyLoss(weight=chords_class_weights)
melody_criterion = melody_criterion.to(DEVICE)
chords_criterion = chords_criterion.to(DEVICE)

# TODO: Concider adding LR schedule
melody_optimizer = torch.optim.Adam(melody_model.parameters(), lr=0.00001)
chords_optimizer = torch.optim.Adam(chords_model.parameters(), lr=0.00001)

dataset = MidiDatasetLoader()
data_loader = torch.utils.data.DataLoader(dataset, batch_size=6, shuffle=True)  
        
num_epochs = MODEL_SETTINGS['num_epochs']      

# Training loop
for epoch in range(num_epochs):
    total_melody_correct = 0
    total_melody_samples = 0
    total_chords_correct = 0
    total_chords_samples = 0
    
    for batch_idx, ((melody_batches, chords_batches, chords_context_batches, video_batches), (melody_target_batches, chords_target_batches)) in enumerate(data_loader):  
        if batch_idx % 50 == 0:   
            print(f"batch idx - {batch_idx}")
              
        for i in range(melody_batches.shape[0]):        
            melody = melody_batches[i].to(DEVICE)
            chords = chords_batches[i].to(DEVICE)
            chords_context = chords_context_batches[i].to(DEVICE)
            video = video_batches[i].to(DEVICE)
            melody_target = melody_target_batches[i].to(DEVICE)
            chords_target = chords_target_batches[i].to(DEVICE)

            # Zero gradients
            melody_optimizer.zero_grad()  
            chords_optimizer.zero_grad()

            # Forward pass
            chords_output = chords_model(chords, video.float())
            melody_output = melody_model(melody, chords_context.float(), video.float())

            # Calculate the loss
            chords_loss = chords_criterion(chords_output, chords_target.float())
            melody_loss = melody_criterion(melody_output, melody_target.float())

            # Backward pass and optimization
            chords_loss.backward()
            chords_optimizer.step()
            melody_loss.backward()
            melody_optimizer.step()
            
            # Calculate accuracy
            _, predicted = torch.max(melody_output, 1)
            melody_output_binary = torch.zeros_like(melody_output)
            melody_output_binary.scatter_(1, predicted.view(-1, 1), 1)
            
            _, predicted = torch.max(chords_output, 1)
            chords_output_binary = torch.zeros_like(chords_output)
            chords_output_binary.scatter_(1, predicted.view(-1, 1), 1)
            
            total_chords_correct += (chords_output_binary == chords_target).all(dim=1).sum().item()
            total_melody_correct += (melody_output_binary == melody_target).all(dim=1).sum().item()
            total_chords_samples += chords_target.size(0)
            total_melody_samples += melody_target.size(0)
            
    chords_accuracy = total_chords_correct / total_chords_samples
    melody_accuracy = total_melody_correct / total_melody_samples
    print(f'Epoch [{epoch + 1}/{num_epochs}], Melody Loss: {melody_loss.item()}, Melody Accuracy: {melody_accuracy * 100:.2f}%, Chords Accuracy: {chords_accuracy * 100:.2f}%')
    
    save_weight_idx = starting_weights_idx + epoch + 1
    
    # if not os.path.exists(DEFAULT_MODEL_WEIGHTS_FOLDER_NAME(idx = save_weight_idx)):
    #     os.makedirs(DEFAULT_MODEL_WEIGHTS_FOLDER_NAME(idx = save_weight_idx))
        
    # torch.save(chords_model.state_dict(), DEFAULT_CHORDS_MODEL_WEIGHTS_FILE_NAME(idx = save_weight_idx))
    # torch.save(melody_model.state_dict(), DEFAULT_MELODY_MODEL_WEIGHTS_FILE_NAME(idx = save_weight_idx))
    

print_class_weights("Final weights:")



            