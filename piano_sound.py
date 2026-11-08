"""
File: piano_sound.py
Name: Juan Sanchez

Description:
Extracts audio for Transkun and adds it to the annotated video.
ChatGPT assisted with the audio processing code.

Source: https://ffmpeg.org/ffmpeg.html
"""
import subprocess

import imageio_ffmpeg


def extract_audio(video, output):
    # Keep stereo PCM16 audio at the model's sample rate.
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-v', 'error', '-i', str(video),
                    '-vn', '-ac', '2', '-ar', '44100', '-c:a', 'pcm_s16le',
                    '-y', str(output)], check=True)


def add_audio(silent_video, audio, output):
    # Add audio to the output video.
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-v', 'error',
                    '-i', str(silent_video), '-i', str(audio),
                    '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'libx264',
                    '-pix_fmt', 'yuv420p', '-crf', '18', '-movflags', '+faststart',
                    '-c:a', 'aac', '-shortest', '-y', str(output)], check=True)
