"""Record and save - audio, video and AV separately based on given recording time.

Set the duration and output directory parameters in __main__ and run it.
BEWARE of anti-virus blocking access to the webcam errors. You'll get runtime errors.

Incase you just want to record audio, or video, just call that specific function instead. The args are pretty self-explanatory. 
"""


import cv2
import numpy as np
import sounddevice as sd
import wave
import threading
import time
import os
from moviepy.editor import VideoFileClip, AudioFileClip

def record_video(duration, output_directory, end_time):
    """
    This function records a video using the default webcam and saves it as an AVI file.

    Args:
        duration (float): The duration of the video in seconds.
        output_directory (str): The directory where the video will be saved.
        end_time (float): The time when the video recording should end in seconds.

    Returns:
        None

    Raises:
        RuntimeError: If no frames were recorded, the function raises a RuntimeError indicating the cause.
"""
    # Video parameters
    video_width = 640
    video_height = 480
    video_fps = 30
    #This frame-rate is different because my webcam was not capturing at the fps=30 that it is advertising.
    out_framerate = 14.3 
    
    
    # OpenCV setup for video
    cap = cv2.VideoCapture(0)
    cap.set(3, video_width)
    cap.set(4, video_height)
    video_fps = cap.get(cv2.CAP_PROP_FPS)
    cap.set(5, video_fps)

    # Function to record video
    def record_video_frames():
        """Returns a list of video frames."""
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


    if len(video_frames) == 0:
        raise RuntimeError("No frames were recorded. Check your anti-virus permissions or your webcam to troubleshoot.")
    
    out = cv2.VideoWriter(video_output_filename, fourcc, out_framerate, (video_width, video_height))
    for frame in video_frames:
        out.write(frame)
    out.release()

    print(f"Video saved to {video_output_filename}")


def record_audio(duration, output_directory, end_time):
    """
    This function records audio from the default microphone and saves it as a WAV file.

    Args:
        duration (float): The duration of the audio in seconds.
        output_directory (str): The directory where the audio will be saved.
        end_time (float): The time when the audio recording should end in seconds since the epoch.

    Returns:
        None

    Raises:
        RuntimeError: If no audio data was recorded, the function raises a RuntimeError with an error message indicating the cause.
"""
    # Audio parameters
    audio_rate = 44100
    audio_channels = 2
    audio_dtype = np.int16

    # Function to record audio
    def record_audio_frames():
        """Returns a list of audio frames."""
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
    """
    This function combines a video and an audio file into a single audio-visual file.

    Args:
        video_path (str): The path to the video file.
        audio_path (str): The path to the audio file.
        av_filepath (str): The path where the audio-visual file will be saved.
        duration (float): The duration of the audio-visual file in seconds.

    Returns:
        None

    Raises:
        IOError: If the input files are not found or have a format unsupported by the function, the function raises an IOError with an error message indicating the cause.
        RuntimeError: If the video and audio files cannot be combined, the function raises a RuntimeError with an error message indicating the cause.
    """
    
    video_clip = VideoFileClip(video_path)
    audio_clip = AudioFileClip(audio_path)

    video_clip = video_clip.set_duration(duration)
    audio_clip = audio_clip.set_duration(duration)

    # Combine video and audio clips
    final_clip = video_clip.set_audio(audio_clip)

    # Write the final clip to a new file
    final_clip.write_videofile(av_filepath, codec="libx264", audio_codec="aac")

def start_recording(duration, output_directory):
    """
    Start recording a video and an audio in parallel, combine them, and save the results. Note that it saves the audio,
    video and audio-visual file separately.

    Args:
        duration (float): The duration of the recording in seconds.
        output_directory (str): The directory where the recording files will be saved.

    Returns:
        None
    """
    # Create the output directory if it doesn't exist
    print(time.time())
    end_time = time.time() + duration
    print(end_time)
    os.makedirs(output_directory, exist_ok=True)

    # Start recording video and audio in parallel
    video_thread = threading.Thread(target=record_video, args=(duration, output_directory, end_time))
    audio_thread = threading.Thread(target=record_audio, args=(duration, output_directory, end_time))

    video_thread.start()
    audio_thread.start()


    # Wait for both threads to finish
    video_thread.join()
    audio_thread.join()

    video_path = f"{output_directory}/just_video.avi"
    audio_path = f"{output_directory}/just_audio.wav"
    combined_path = f"{output_directory}/AV.mp4"

    combine_video_audio(video_path, audio_path, combined_path, duration)

if __name__ == "__main__":
    duration_in_sec = 5 
    output_directory = "/output/"

    start_recording(duration_in_sec, output_directory)
