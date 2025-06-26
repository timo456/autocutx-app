import cv2
import numpy as np
import json
import matplotlib.pyplot as plt  # ← 加這行在最上面
from moviepy.editor import concatenate_videoclips
from moviepy.video.fx.all import speedx

def add_slowmotion(clip, slow_duration=0.5, speed_factor=0.5):
    """
    將 clip 中央 slow_duration 秒設為慢動作，其他維持原速。
    - speed_factor: 慢動作倍率（0.5 = 半速）
    """
    center_time = clip.duration / 2
    start = max(0, center_time - slow_duration / 2)
    end = min(clip.duration, center_time + slow_duration / 2)

    # 切三段：前段、慢段、後段
    pre_clip = clip.subclip(0, start)
    slow_clip = clip.subclip(start, end).fx(speedx, speed_factor)
    post_clip = clip.subclip(end)

    # 調整時間軸並串接
    return concatenate_videoclips([pre_clip, slow_clip, post_clip])

def detect_motion_segments(video_path, threshold=30, min_duration=0.5, window_size=5, debug=False):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    duration = cap.get(cv2.CAP_PROP_FRAME_COUNT) / fps

    last_frame = None
    diffs = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if last_frame is not None:
            diff = cv2.absdiff(gray, last_frame)
            mean_diff = np.mean(diff)
            diffs.append(mean_diff)
        last_frame = gray

    cap.release()

    # 平滑處理（滑動平均）
    smoothed = np.convolve(diffs, np.ones(window_size)/window_size, mode='valid')

    if debug:
        import matplotlib.pyplot as plt
        plt.plot(smoothed)
        plt.axhline(y=threshold, color='r', linestyle='--')
        plt.title("每幀畫面變化值 (滑動平均)")
        plt.xlabel("Frame")
        plt.ylabel("Difference")
        plt.show()

    # 動作區間偵測（高於 threshold）
    motion_segments = []
    is_segment = False
    segment_start = 0

    for i, val in enumerate(smoothed):
        t = i / fps
        if val > threshold:
            if not is_segment:
                segment_start = t
                is_segment = True
        else:
            if is_segment:
                if t - segment_start >= min_duration:
                    motion_segments.append({"start": round(segment_start, 2), "end": round(t, 2)})
                is_segment = False

    return motion_segments

def save_segments(segments, output_path):
    with open(output_path, 'w') as f:
        json.dump(segments, f, indent=2)
