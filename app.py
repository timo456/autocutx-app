import streamlit as st
import os
import shutil
from subprocess import run
import json

st.set_page_config(page_title="AutoCutX 上傳剪輯", layout="centered")

st.title("🎬 AutoCutX 自動剪輯工具")
st.markdown("請上傳影片與音訊，系統將自動進行精華剪輯與套用特效")

uploaded_video = st.file_uploader("📹 上傳影片", type=["mp4", "mov", "mpeg4"])
uploaded_audio = st.file_uploader("🎵 上傳背景音樂 (MP3)", type=["mp3"])

if uploaded_video and uploaded_audio:
    os.makedirs("sample", exist_ok=True)

    # 取得副檔名
    video_ext = os.path.splitext(uploaded_video.name)[1]
    audio_ext = os.path.splitext(uploaded_audio.name)[1]

    video_save_path = f"sample/input{video_ext}"
    audio_save_path = f"sample/input{audio_ext}"

    # 儲存檔案
    with open(video_save_path, "wb") as f:
        f.write(uploaded_video.read())
    with open(audio_save_path, "wb") as f:
        f.write(uploaded_audio.read())

    # 儲存 config.json 供 main.py 使用
    with open("config.json", "w") as f:
        json.dump({
            "video_path": video_save_path,
            "audio_path": audio_save_path
        }, f)

    st.success("✅ 檔案上傳成功！")

    if st.button("🚀 開始自動剪輯"):
        with st.spinner("剪輯影片中，請稍候..."):
            result = run(["python", "main.py"], capture_output=True, text=True)
            st.text(result.stdout)

        if os.path.exists("output/final_full_video.mp4"):
            st.video("output/final_full_video.mp4")
            st.success("🎉 剪輯完成，請觀看結果！")
            st.download_button(
                label="⬇️ 下載剪輯後的影片",
                data=open("output/final_full_video.mp4", "rb").read(),
                file_name="final_full_video.mp4",
                mime="video/mp4"
            )
        else:
            st.error("❌ 剪輯失敗，請檢查 log 訊息。")
