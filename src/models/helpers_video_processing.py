import torch
import torchvision
from const import DEVICE

CHUNK_SIZE = 50
  
def select_frames(video, target_video_length_in_frames):
    video = video.to(DEVICE)     
    filtered_video_frames = []     
    processed_frames_count = 0
        
    for i in range(target_video_length_in_frames):
        frames_left_to_fill = target_video_length_in_frames - i
        total_frames_left = video.shape[0] - processed_frames_count
        frames_chunk_size = round(total_frames_left / frames_left_to_fill)
        
        frames = video[processed_frames_count : processed_frames_count + frames_chunk_size]
        filtered_video_frames.append(frames[0])
        
        processed_frames_count += frames_chunk_size
        
    filtered_video_frames = torch.stack(filtered_video_frames)    

    return filtered_video_frames.to('cpu')

def remove_empty_frames(video):
    black_pixel_percentage_threshold = 0.35
    black_pixel_iluminosity_threshold = 1

    filtered_video_frames = []
    
    video = video.to(DEVICE)
    
    for i in range(0, video.size(0), CHUNK_SIZE):
        chunk = video[i : i + CHUNK_SIZE]
        
        video_tensor_float = chunk.float()
        
        grayscale_tensor = (
            0.21 * video_tensor_float[:, :, :, 0]
            + 0.72 * video_tensor_float[:, :, :, 1]
            + 0.07 * video_tensor_float[:, :, :, 2]
        )
        
        grayscale_tensor = grayscale_tensor.unsqueeze(dim=3)
        
        black_pixel_count = (
            grayscale_tensor > black_pixel_iluminosity_threshold
        ).sum(dim=(1, 2, 3)).float()
        
        black_pixel_percentage = black_pixel_count / (180 * 320)

        frames_to_keep = black_pixel_percentage > black_pixel_percentage_threshold

        filtered_chunk = chunk[frames_to_keep]
        filtered_video_frames.append(filtered_chunk)

    filtered_video_tensor = torch.cat(filtered_video_frames, dim=0)

    return filtered_video_tensor.to('cpu')


def reconstruct_video(video):
    torchvision.io.write_video(
        filename="empty_frames.mp4", video_array=video, fps=1, video_codec="h264"
    )
    
def process_video(video, target_video_length_in_frames):
    full_video = remove_empty_frames(video)
    selected_frames = select_frames(full_video, target_video_length_in_frames)
    
    return selected_frames
        