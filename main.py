from moviepy.editor import (
    VideoFileClip, CompositeVideoClip, concatenate_videoclips,
    ImageClip, AudioFileClip, CompositeAudioClip
)
import numpy as np
import os
import json

from utils.audio_utils import align_segment_to_beat, extract_beats, save_beats
from utils.subtitle_utils import generate_subtitles, overlay_subtitles
from utils.video_effects import add_flash_effect, add_ghost_effect
from utils.video_utils import add_slowmotion, detect_motion_segments, save_segments
from utils.motion_score import compute_motion_score
from utils.text_overlay import create_logo_image
from auto_highlight import classify_motion_segments


def split_into_segments_with_highlight(video_duration, highlights):
    highlights = sorted(highlights)
    segments = []
    prev_end = 0.0

    for start, end in highlights:
        if start > prev_end:
            segments.append((prev_end, start, False))
        segments.append((start, end, True))
        prev_end = end

    if prev_end < video_duration:
        segments.append((prev_end, video_duration, False))

    return segments


if __name__ == "__main__":
    ADD_LOGO = True
    ADD_TEXT = True
    
    with open("config.json", "r") as f:
        config = json.load(f)
    if not config:
        raise ValueError("配置檔 config.json 讀取失敗或內容為空。請檢查檔案是否存在且格式正確。")

    video_path = config["video_path"]
    audio_path = config["audio_path"]
    
    os.makedirs("output", exist_ok=True)

    print("分析節奏點中...")
    beats = extract_beats(audio_path)
    save_beats(beats, "output/beat_times.json")
    print(f"節奏點完成，共 {len(beats)} 個拍點")

    print("偵測高動作區段中...")
    segments = detect_motion_segments(video_path, threshold=0.1, min_duration=0.2, debug=True)
    save_segments(segments, "output/motion_segments.json")
    print(f"動作偵測完成，共 {len(segments)} 段")

    if not segments:
        print("⚠️ 偵測到的動作區段為空，請檢查影片內容或參數設置。")
        exit(1)

    if isinstance(segments[0], dict):
        segments = [(float(s["start"]), float(s["end"])) for s in segments]

    aligned_segments = []
    for start, end in segments:
        aligned_start, aligned_end = align_segment_to_beat(start, end, beats)
        aligned_segments.append((aligned_start, aligned_end))
        print(f"對齊拍點：{start:.2f}s → {aligned_start:.2f}s")

    video = VideoFileClip(video_path)
    video_duration = video.duration

    print("分析精彩度中...")
    highlight_segments = classify_motion_segments(
        video_path,
        aligned_segments,
        classify_func=lambda p: f"motion ({compute_motion_score(p):.2f})",
        score_threshold=0.5,
    )

    segments_with_flags = split_into_segments_with_highlight(video_duration, highlight_segments)

    for start, end, is_hl in segments_with_flags:
        tag = "[H]" if is_hl else "   "
        print(f"{tag} {start:.2f} ~ {end:.2f}")

    final_clips = []
    for idx, (start, end, is_highlight) in enumerate(segments_with_flags):
        clip = video.subclip(start, end)

        if is_highlight:
            clip_no_audio = clip.without_audio()
            slow_clip = add_slowmotion(clip_no_audio, slow_duration=0.5, speed_factor=0.5)
            
            clip = slow_clip
            
            if ADD_LOGO:
                logo_img = create_logo_image("Timo | AutoCutX", width=300, height=60)
                logo_clip = ImageClip(np.array(logo_img)).set_duration(clip.duration).set_position(("right", "top"))
                clip = CompositeVideoClip([clip, logo_clip])

        final_clips.append(clip)

    if final_clips:
        final_video = concatenate_videoclips(final_clips, method="compose")

        if ADD_TEXT :
            print("自動產生字幕中...")
            subtitles = generate_subtitles(video_path)
            final_video = overlay_subtitles(final_video, subtitles)

        # ✅ 加入完整背景音樂混音
        print("合成音訊：背景音樂 + 原聲壓低")
        bgm = AudioFileClip(audio_path).volumex(1.0)

        audio_duration = min(final_video.duration, video.audio.duration)
        original_audio = video.audio.subclip(0, audio_duration).volumex(0.4)
        
        mixed_audio = CompositeAudioClip([original_audio, bgm.set_duration(final_video.duration)])
        final_video = final_video.set_audio(mixed_audio)

        final_video.write_videofile(
            "output/final_full_video.mp4",
            codec="libx264",
            preset="ultrafast",
            audio=True,
            ffmpeg_params=[
                "-vf", "scale=iw:ih,setdar=9/16",
                "-aspect", "9:16"
            ]
        )
        print("完整影片已產生！")
    else:
        print("沒有可輸出的片段。")
