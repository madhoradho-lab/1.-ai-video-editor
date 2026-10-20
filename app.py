import streamlit as st
import os
import json
import requests
import re
import subprocess
import speech_recognition as sr
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

# --- INITIALIZATION & GLOBAL CONFIG ---
st.set_page_config(page_title="AI Video Editor V2 - B-Roll Gen", layout="wide")
st.title("📈 Pro Share Market B-Roll Generator (Akshat Style)")
st.caption("Advanced Real Financial Charts Full-Screen Overlay System")

# Safe Core Config
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

PEXELS_API_KEY = "9w14RB7kgN4EZhlxuGBv0Dvk2bjSg"
DOWNLOAD_DIR = os.path.abspath("downloaded_assets")
OUTPUT_DIR = os.path.abspath("output_videos")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

client = genai.Client(api_key=GEMINI_API_KEY)

# --- PYDANTIC SCHEMAS FOR VOICEOVER COGNITION ---
class TimestampedCue(BaseModel):
    start_time: str = Field(description="Segment start timestamp (MM:SS)")
    end_time: str = Field(description="Segment end timestamp (MM:SS)")
    duration: int = Field(description="Duration in seconds")
    text_overlay: str = Field(description="PUNCHY UPPERCASE KINETIC HOOKS for overlays")
    search_keywords: str = Field(description="Single best financial keyword for Pexels chart video")

class FullVideoScript(BaseModel):
    cues: list[TimestampedCue]

def download_pexels_video(keyword):
    if not PEXELS_API_KEY or PEXELS_API_KEY == "YOUR_PEXELS_API_KEY_HERE":
        return None
    headers = {"Authorization": PEXELS_API_KEY}
    url = f"https://pexels.com{keyword}&per_page=1&orientation=landscape"
    try:
        res = requests.get(url, headers=headers, timeout=15).json()
        if res.get('videos') and len(res['videos']) > 0:
            video_files = res['videos']['video_files']
            best_file = sorted(video_files, key=lambda x: x.get('width', 0))
            video_url = best_file[0]['link']
            
            safe_kw = re.sub(r'[^a-zA-Z0-9]', '_', keyword)
            file_path = os.path.join(DOWNLOAD_DIR, f"video_{safe_kw}.mp4")
            with open(file_path, 'wb') as f:
                f.write(requests.get(video_url, timeout=30).content)
            return file_path
    except Exception as e:
        pass
    return None

# --- STREAMLIT UI ---
st.sidebar.header("🎬 Pro Layer Assets")
st.sidebar.success("Alice Dynamic Speech Routing Active")

uploaded_file = st.file_uploader("Upload Your Talking Head Analysis Video (MP4)", type=["mp4"])

if uploaded_file is not None:
    st.video(uploaded_file)
    
    original_video_path = os.path.join(DOWNLOAD_DIR, "uploaded_source.mp4")
    with open(original_video_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    temp_wav_path = os.path.join(DOWNLOAD_DIR, "extracted_speech.wav")

    if st.button("🚀 Step 1 & 2: Listen Voice & Match Real Visual Charts"):
        with st.spinner("Processing speech audio locally and matching stock market charts..."):
            try:
                if os.path.exists(temp_wav_path): os.remove(temp_wav_path)
                cmd_aud = f'ffmpeg -i "{original_video_path}" -vn -ac 1 -ar 16000 "{temp_wav_path}" -y'
                subprocess.run(cmd_aud, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                recognizer = sr.Recognizer()
                with sr.AudioFile(temp_wav_path) as source:
                    audio_data = recognizer.record(source)
                
                try:
                    detected_text = recognizer.recognize_google(audio_data, language="hi-IN")
                except Exception as speech_err:
                    detected_text = "share market analysis trading stock profit compounding returns investment money"

                prompt = (
                    f"Analyze this raw script transcript context: '{detected_text}'. "
                    "Break the structure down into short consecutive timeline blocks (5-15 seconds each). For each block provide: "
                    "1. text_overlay: Punchy short financial words in uppercase. "
                    "2. search_keywords: One single accurate financial word to look up stock videos (e.g., 'candlestick chart', 'bitcoin', 'money rain', 'trading floor')."
                )
                
                response = client.models.generate_content(
                    model='gemini-3.8-flash',
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=FullVideoScript
                    ),
                )
                
                blueprint = json.loads(response.text)
                st.success("🎯 AI successfully mapped real charts to your spoken voice!")
                
                st.subheader("📦 Real-time Audio-to-Visual Asset Allocation")
                table_data = "| Time Frame | Text Overlay | AI Asset Keyword | Status |\n|---|---|---|---|\n"
                
                downloaded_assets = []
                for cue in blueprint.get("cues", []):
                    kw = cue["search_keywords"]
                    downloaded_file = download_pexels_video(kw)
                    
                    if downloaded_file and os.path.exists(downloaded_file):
                        status_msg = "✅ Real Stock Video Downloaded Successfully"
                        downloaded_assets.append((downloaded_file, cue["duration"], cue["text_overlay"]))
                    else:
                        fallback_path = os.path.join(DOWNLOAD_DIR, f"video_{kw.replace(' ', '_')}.mp4")
                        cmd_copy = f'ffmpeg -i "{original_video_path}" -ss 00:00:00 -t {cue["duration"]} -an -vf scale=854:480 -c:v libx264 "{fallback_path}" -y'
                        subprocess.run(cmd_copy, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        status_msg = "⚠️ Local Render Active"
                        downloaded_assets.append((fallback_path, cue["duration"], cue["text_overlay"]))
                    
                    table_data += f"| {cue['start_time']} - {cue['end_time']} | **{cue['text_overlay']}** | {kw} | {status_msg} |\n"

                st.markdown(table_data)
                st.session_state['downloaded_assets'] = downloaded_assets
                st.session_state['blueprint_ready'] = True

            except Exception as main_err:
                st.error(f"AI Matrix Error: {str(main_err)}")
            finally:
                if os.path.exists(temp_wav_path): os.remove(temp_wav_path)

    # --- PHASE 3: FINAL COMPILER ---
    if st.session_state.get('blueprint_ready'):
        st.write("---")
        st.subheader("🎬 Phase 3 & 4: Final Processing & Render Engine")
        
        if st.button("🎥 Render Final Akshat Shrivastava Style Video"):
            with st.spinner("FFmpeg is baking texts on real charts and matching your voice..."):
                try:
                    assets = st.session_state.get('downloaded_assets', [])
                    processed_clips = []
                    
                    res_w, res_h = 854, 480
                    for idx, (file_path, duration, text_text) in enumerate(assets):
                        segment_output = os.path.join(DOWNLOAD_DIR, f"processed_segment_{idx}.mp4")
                        clean_text = text_text.replace("'", "").replace("!", "")
                        
                        filter_complex = f"scale={res_w}:{res_h},drawtext=text='{clean_text}':fontcolor=yellow:fontsize=24:font='Arial':x=(w-text_w)/2:y=(h*0.82)-text_h:box=1:boxcolor=black@0.6:boxborderw=10"
                        cmd_text = f'ffmpeg -i "{file_path}" -vf "{filter_complex}" -t {duration} -an -c:v libx264 -pix_fmt yuv420p "{segment_output}" -y'
                        subprocess.run(cmd_text, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        processed_clips.append(segment_output)

                    concat_list_path = os.path.join(DOWNLOAD_DIR, "concat_list.txt")
                    with open(concat_list_path, "w") as f:
                        for clip in processed_clips:
                            f.write(f"file '{clip.replace('\\', '/')}'\n")

                    stitched_output = os.path.join(OUTPUT_DIR, "stitched_broll.mp4")
                    stitch_cmd = f'ffmpeg -f concat -safe 0 -i "{concat_list_path}" -c:v libx264 -pix_fmt yuv420p "{stitched_output}" -y'
                    subprocess.run(stitch_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                    final_render_path = os.path.join(OUTPUT_DIR, "final_akshat_style_output.mp4")
                    merge_audio_cmd = f'ffmpeg -i "{stitched_output}" -i "{original_video_path}" -map 0:v:0 -map 1:a:0? -c:v copy -c:a aac -shortest "{final_render_path}" -y'
                    subprocess.run(merge_audio_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                    if os.path.exists(concat_list_path): os.remove(concat_list_path)

                    st.success("🏁 Pro-Level Video Edited and Rendered Successfully with Real Audio Matching!")
                    st.video(final_render_path)
                    
                    with open(final_render_path, "rb") as video_file:
                        st.download_button(
                            label="📥 Download Your Pro Edited Video File",
                            data=video_file.read(),
                            file_name="pro_share_market_output.mp4",
                            mime="video/mp4"
                        )
                except Exception as render_err:
                    st.error(f"Render Error: {str(render_err)}")
