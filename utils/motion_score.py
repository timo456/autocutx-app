# utils/motion_score.py

import cv2
import numpy as np

def compute_motion_score(video_path, num_frames=8):
    cap = cv2.VideoCapture(video_path)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    if frame_count <= 1:
        return 0.0

    # 均勻取 num_frames 張 frame
    idxs = np.linspace(0, frame_count - 1, num_frames, dtype=int)
    frames = []
    for i in range(frame_count):
        ret, frame = cap.read()
        if not ret:
            break
        if i in idxs:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frames.append(gray)
    cap.release()

    # 計算相鄰帧差異
    diffs = []
    for i in range(len(frames) - 1):
        diff = cv2.absdiff(frames[i], frames[i + 1])
        diffs.append(np.mean(diff))

    # ✅ 改為回傳最大值（不是平均）
    return float(np.max(diffs)) if diffs else 0.0
