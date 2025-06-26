import streamlit as st
import os
import shutil
from subprocess import run

st.set_page_config(page_title="AutoCutX 上傳剪輯", layout="centered")

st.title("🎬 AutoCutX 自動剪輯工具")
st.markdown("請上傳影片與音訊，系統將自動進行精華剪輯與套用特效")

uploaded_video = st.file_uploader("📹 上傳影片 (MP4)", type=["mp4"])
uploaded_audio = st.file_uploader("🎵 上傳背景音樂 (MP3)", type=["mp3"])

if uploaded_video and uploaded_audio:
    os.makedirs("sample", exist_ok=True)
    with open("sample/input.mp4", "wb") as f:
        f.write(uploaded_video.read())
    with open("sample/input.mp3", "wb") as f:
        f.write(uploaded_audio.read())
    with open("output/final_full_video.mp4", "rb") as f:
        st.download_button("⬇️ 下載影片", f, file_name="highlight.mp4")

    st.success("✅ 檔案上傳成功！")

    if st.button("🚀 開始自動剪輯"):
        with st.spinner("剪輯影片中，請稍候..."):
            result = run(["python", "main.py"], capture_output=True, text=True)
            st.text(result.stdout)

        if os.path.exists("output/final_full_video.mp4"):
            st.video("output/final_full_video.mp4")
            st.success("🎉 剪輯完成，請觀看結果！")
        else:
            st.error("❌ 剪輯失敗，請檢查 log 訊息。")
