from faster_whisper import WhisperModel
from moviepy.editor import CompositeVideoClip, ImageClip
import numpy as np
from utils.text_overlay import create_text_image

model = WhisperModel("base", device="cpu", compute_type="int8")

import re

def generate_subtitles(video_path, min_text_len=3):
    segments, _ = model.transcribe(video_path, beam_size=5)
    subtitles = []
    for segment in segments:
        text = segment.text.strip()

        # 濾掉無字元或只有標點符號（如 "!!", "...", "‖‖"）
        if len(text) < min_text_len:
            continue
        if not re.search(r'[a-zA-Z\u4e00-\u9fff]', text):  # 沒有英文或中文字
            continue

        subtitles.append({
            "start": segment.start,
            "end": segment.end,
            "text": text
        })
    return subtitles



def overlay_subtitles(video, subtitles, fontsize=40):
    clips = [video]
    for seg in subtitles:
        img = create_text_image(seg["text"], width=video.w, height=80, font_size=fontsize)
        txt_clip = ImageClip(np.array(img)).set_duration(seg["end"] - seg["start"])
        txt_clip = txt_clip.set_start(seg["start"]).set_position(("center", "bottom"))
        clips.append(txt_clip)
    return CompositeVideoClip(clips).set_duration(video.duration)
