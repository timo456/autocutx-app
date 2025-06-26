from moviepy.editor import VideoFileClip
import os

def classify_motion_segments(video_path, segments, classify_func, score_threshold=10.0):
    highlight_segments = []

    video = VideoFileClip(video_path)
    original_size = video.size  # 保留影片比例

    for idx, (start, end) in enumerate(segments):
        start = float(start)
        end = float(end)
        print(f"🔍 分析片段 {idx+1}: {start:.2f}s ~ {end:.2f}s")

        raw_clip = video.subclip(start, end)
        if raw_clip.duration < 0.1:
            print("⏭️ 片段太短，跳過")
            continue

        final_clip = raw_clip.resize(newsize=original_size)
        temp_clip_path = f"output/temp_segment_{idx}.mp4"
        final_clip.write_videofile(
            temp_clip_path,
            codec="libx264",
            audio=True,
            preset="ultrafast",
            logger=None,
            ffmpeg_params=[
                "-vf", "scale=iw:ih,setdar=9/16",
                "-aspect", "9:16"
            ]
        )

        result = classify_func(temp_clip_path)
        name, score = result.rsplit('(', 1)
        score = float(score.strip(')'))

        if score > score_threshold:
            print(f"✅ 高分動作：{name.strip()} ({score:.2f})")
            highlight_segments.append((start, end))
        else:
            print(f"❌ 分數太低：{name.strip()} ({score:.2f})")

    return highlight_segments

