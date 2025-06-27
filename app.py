import streamlit as st
import os
import json
from pathlib import Path
from datetime import datetime
from subprocess import run
import sys  # 新增這一行

st.set_page_config(page_title="AutoCutX 上傳剪輯", layout="centered")
st.title(" AutoCutX 自動剪輯工具")
st.markdown("請上傳影片與音訊，系統將自動進行精華剪輯與套用特效")

uploaded_video = st.file_uploader("📹 上傳影片", type=["mp4", "mov", "mpeg4"])
uploaded_audio = st.file_uploader("🎵 上傳背景音樂 (MP3)", type=["mp3"])

if uploaded_video and uploaded_audio:
    # 🔐 防呆處理
    if uploaded_video.size == 0:
        st.error("上傳的影片檔案為空，請重新上傳。")
        st.stop()

    # ⏰ 唯一命名避免衝突
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    video_ext = Path(uploaded_video.name).suffix
    video_path = f"sample/input_{timestamp}{video_ext}"
    audio_path = f"sample/input_{timestamp}.mp3"

    os.makedirs("sample", exist_ok=True)

    # ✅ 寫入檔案
    with open(video_path, "wb") as f:
        f.write(uploaded_video.read())

    with open(audio_path, "wb") as f:
        f.write(uploaded_audio.read())

    st.success(f"儲存影片為: {video_path}\n 儲存音訊為: {audio_path}")

    # ✅ 寫入 config.json
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump({
            "video_path": video_path.replace("\\", "/"),
            "audio_path": audio_path.replace("\\", "/")
        }, f, indent=4)

    if st.button(" 開始自動剪輯"):
        with st.spinner("影片剪輯中，請稍候..."):
            result = run([sys.executable, "main.py"], capture_output=True, text=True)
            st.text(result.stdout)

            if result.stderr:
                st.error(" 發生錯誤：")
                st.code(result.stderr, language="bash")

        if os.path.exists("output/final_full_video.mp4"):
            st.video("output/final_full_video.mp4")
            st.download_button(
                label="下載剪輯後影片",
                data=open("output/final_full_video.mp4", "rb").read(),
                file_name="final_full_video.mp4",
                mime="video/mp4"
            )
        else:
            st.error(" 剪輯失敗，請檢查錯誤訊息。")
