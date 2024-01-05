import cv2
import numpy as np
import sounddevice as sd
import wave
import threading
import time
import os
from moviepy.editor import VideoFileClip, AudioFileClip


def record_video(duration, output_directory, end_time):
    """Record video.

    Args:
        duration(int):
        output_directory(str):
        end_time(float):

    Returns:


    """
    # Video parameters
    video_width = 640
    video_height = 480

    # OpenCV setup for video
    cap = cv2.VideoCapture(0)
    cap.set(3, video_width)
    cap.set(4, video_height)
    video_fps = cap.get(cv2.CAP_PROP_FPS)
    cap.set(5, video_fps)

    # Function to record video
    def record_video_frames():
        frames = []
        while time.time() < end_time:
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)
        return frames

    # Start recording video
    video_frames = record_video_frames()

    # Release video resources
    cap.release()

    # Save video frames to AVI file
    video_output_filename = f"{output_directory}/just_video.avi"
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    # print(len(video_frames))

    #The frame-rate is hardcoded because my webcam was not capturing at the fps=30 that it is advertising.
    out = cv2.VideoWriter(video_output_filename, fourcc, 14.3, (video_width, video_height))
    for frame in video_frames:
        out.write(frame)
    out.release()

    print(f"Video saved to {video_output_filename}")


def record_audio(duration, output_directory, end_time):
    """Record audio.

    Args:
        duration(int):
        output_directory(str):
        end_time(float):

    Returns:
    """
    # Audio parameters
    audio_rate = 44100
    audio_channels = 2
    audio_dtype = np.int16

    # Function to record audio
    def record_audio_frames():
        frames = []
        while time.time() < end_time:
            audio_data = sd.rec(int(audio_rate * duration), samplerate=audio_rate, channels=audio_channels, dtype=audio_dtype)
            sd.wait()
            frames.append(audio_data)
        return frames

    # Start recording audio
    audio_frames = record_audio_frames()

    # Save audio frames to WAV file
    audio_output_filename = f"{output_directory}/just_audio.wav"
    wave_file = wave.open(audio_output_filename, 'wb')
    wave_file.setnchannels(audio_channels)
    wave_file.setsampwidth(2)
    wave_file.setframerate(audio_rate)
    wave_file.writeframes(b''.join(audio_frames))
    wave_file.close()

    print(f"Audio saved to {audio_output_filename}")


def combine_video_audio(video_path, audio_path, av_filepath, duration):
    """Function to mux audio and video files together.

    Args:
        video_path(str):
        audio_path(str):
        av_filepath(str):
        duration(int):

    Returns:
    
    """
    video_clip = VideoFileClip(video_path)
    audio_clip = AudioFileClip(audio_path)

    video_clip = video_clip.set_duration(duration)
    audio_clip = audio_clip.set_duration(duration)

    # Combine video and audio clips
    final_clip = video_clip.set_audio(audio_clip)

    # Write the final clip to a new file
    final_clip.write_videofile(av_filepath, codec="libx264", audio_codec="aac")


def start_recording(duration, output_dir):
    """Driver function for recording video.
    
    Args:
        duration(int):
        output_dir(str):
    """
    # Create the output directory if it doesn't exist
    print(time.time())
    end_time = time.time() + duration
    print(end_time)
    os.makedirs(output_dir, exist_ok=True)

    # Start recording video and audio in parallel
    video_thread = threading.Thread(target=record_video, args=(duration, output_dir, end_time))
    audio_thread = threading.Thread(target=record_audio, args=(duration, output_dir, end_time))

    video_thread.start()
    audio_thread.start()

    # Wait for both threads to finish
    video_thread.join()
    audio_thread.join()

    video_path = f"{output_dir}/just_video.avi"
    audio_path = f"{output_dir}/just_audio.wav"
    combined_path = f"{output_dir}/AV.mp4"

    combine_video_audio(video_path, audio_path, combined_path, duration)


if __name__ == "__main__":
    duration = 5  # in seconds
    output_directory = "output/"
    start_recording(duration, output_directory)
