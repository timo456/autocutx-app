import librosa
import json
import os

def extract_beats(audio_path):
    y, sr = librosa.load(audio_path)
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)
    return beat_times.tolist()

def save_beats(beat_times, output_path):
    with open(output_path, 'w') as f:
        json.dump(beat_times, f, indent=2)

def align_segment_to_beat(start, end, beats, max_shift=0.3):
    """
    將一段 [start, end] 對齊到最近節奏點
    如果偏移太遠（> max_shift），就不對齊。
    """
    if not beats:
        return start, end

    nearest = min(beats, key=lambda b: abs(b - start))

    if abs(nearest - start) > max_shift:
        return start, end

    duration = end - start
    return nearest, nearest + duration
