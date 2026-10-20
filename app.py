import streamlit as st
import os, json, requests, re, subprocess
import speech_recognition as sr
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

st.set_page_config(page_title="AI Shorts Editor V5", layout="wide")
st.title("📱 AI Shorts & Reels Pro Editor (Akshat Style)")
st.caption("Auto-Screenplay Changing Engine for Short-Form Vertical Videos")

GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
PEXELS_API_KEY = st.secrets.get("PEXELS_API_KEY", "")
D_DIR, O_DIR = os.path.abspath("downloaded_assets"), os.path.abspath("output_videos")
os.makedirs(D_DIR, exist_ok=True); os.makedirs(O_DIR, exist_ok=True)
client = genai.Client(api_key=GEMINI_API_KEY)

class TimestampedCue(BaseModel):
    start_time: str = Field(description="Start timestamp (MM:SS)")
    end_time: str = Field(description="End timestamp (MM:SS)")
    duration: int = Field(description="Duration in seconds")
    text_overlay: str = Field(description="UPPERCASE PUNCHY SHORTS HOOK")
    search_keywords: str = Field(description="Single financial word (chart, trading, money, bull, bear)")

class FullVideoScript(BaseModel):
    cues: list[TimestampedCue]

def download_pexels(keyword):
    if not PEXELS_API_KEY: return None
    url = f"https://pexels.com{keyword.replace(' ', '%20')}&per_page=1&orientation=landscape"
    try:
        res = requests.get(url, headers={"Authorization": PEXELS_API_KEY}, timeout=15)
        if res.status_code == 200:
            v_files = res.json().get('videos', [{}]).get('video_files', [])
            v_url = [v for v in v_files if v.get('width', 0) <= 1920][0]['link']
            f_path = os.path.join(D_DIR, f"v_{re.sub(r'[^a-zA-Z0-9]', '_', keyword)}.mp4")
            with open(f_path, 'wb') as f: f.write(requests.get(v_url, timeout=30).content)
            return f_path
    except: pass
    return None

uploaded_file = st.file_uploader("Upload Your Shorts Raw Video (MP4)", type=["mp4"])
if uploaded_file:
    orig_path = os.path.join(D_DIR, "src.mp4")
    with open(orig_path, "wb") as f: f.write(uploaded_file.getbuffer())
    t_wav, enh_aud = os.path.join(D_DIR, "aud.wav"), os.path.join(D_DIR, "enh.aac")

    if st.button("🚀 Match Pro Voice & Build Graphics Screenplay"):
        with st.spinner("Analyzing Speech & Setting Up Financial Backgrounds..."):
            try:
                subprocess.run(f'ffmpeg -i "{orig_path}" -vn -af "highpass=f=200,lowpass=f=3000,dynaudnorm" -ac 1 -ar 16000 "{t_wav}" -y', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                rec, det_text = sr.Recognizer(), ""
                with sr.AudioFile(t_wav) as src:
                    for offset in range(0, int(src.DURATION), 30):
                        try: det_text += " " + rec.recognize_google(rec.record(src, duration=30), language="hi-IN")
                        except: continue
                if not det_text.strip(): det_text = "share market analysis profit trading stock chart"
                
                resp = client.models.generate_content(
                    model='gemini-3.8-flash', contents=f"Analyze script: '{det_text}'. Break into 4-8s punchy blocks with uppercase text_overlay and financial keywords.",
                    config=types.GenerateContentConfig(response_mime_type="application/json", response_schema=FullVideoScript),
                )
                blueprint = json.loads(resp.text)
                st.success("🎯 Screenplay mapped successfully across the timeline!")
                
                assets, table = [], "| Time Frame | Text Overlay | AI Chart Graphic | Status |\n|---|---|---|---|\n"
                for cue in blueprint.get("cues", []):
                    kw = cue["search_keywords"]
                    f_dl = download_pexels(kw)
                    if f_dl and os.path.exists(f_dl):
                        assets.append((f_dl, cue["duration"], cue["text_overlay"], True))
                        table += f"| {cue['start_time']} - {cue['end_time']} | **{cue['text_overlay']}** | {kw} | 📈 Stock Chart Linked |\n"
                    else:
                        assets.append((orig_path, cue["duration"], cue["text_overlay"], False))
                        table += f"| {cue['start_time']} - {cue['end_time']} | **{cue['text_overlay']}** | {kw} | 👤 Talking Head (Zoom) |\n"
                st.markdown(table)
                st.session_state['assets'], st.session_state['ready'] = assets, True
            except Exception as e: st.error(f"Error: {e}")
            finally:
                if os.path.exists(t_wav): os.remove(t_wav)

    if st.session_state.get('ready'):
        if st.button("🎥 Render Final Pro-Level Vertical Short Video"):
            with st.spinner("FFmpeg Engine is converting to Vertical Shorts format & baking graphics..."):
                try:
                    clips = []
                    # 9:16 Shorts dimensions (Vertical Crop Engine)
                    w_shorts, h_shorts = 608, 1080
                    
                    for idx, (path, dur, txt, is_graphic) in enumerate(st.session_state.get('assets', [])):
                        out = os.path.join(D_DIR, f"seg_{idx}.mp4")
                        if is_graphic:
                            flt = f"scale={w_shorts}:{h_shorts}:force_original_aspect_ratio=increase,crop={w_shorts}:{h_shorts},drawtext=text='{txt.replace(chr(39),chr(32))}':fontcolor=yellow:fontsize=28:font='Arial':x=(w-text_w)/2:y=(h*0.5)-text_h:box=1:boxcolor=black@0.7:boxborderw=15"
                        else:
                            # Dynamic Zoom-In for Talking Head clips to make it look cinematic
                            flt = f"scale=2*iw:-1,crop={w_shorts}:{h_shorts}:(iw-{w_shorts})/2:(ih-{h_shorts})/2,drawtext=text='{txt.replace(chr(39),chr(32))}':fontcolor=yellow:fontsize=28:font='Arial':x=(w-text_w)/2:y=(h*0.75)-text_h:box=1:boxcolor=black@0.7:boxborderw=15"
                        
                        subprocess.run(f'ffmpeg -i "{path}" -vf "{flt}" -t {dur} -an -c:v libx264 -pix_fmt yuv420p "{out}" -y', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        clips.append(out)
                    
                    c_txt = os.path.join(D_DIR, "list.txt")
                    with open(c_txt, "w") as f:
                        for c in clips: f.write(f"file '{c.replace('\\', '/')}'\n")
                    
                    st_out = os.path.join(O_DIR, "stitched.mp4")
                    subprocess.run(f'ffmpeg -f concat -safe 0 -i "{c_txt}" -c:v libx264 -pix_fmt yuv420p "{st_out}" -y', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    subprocess.run(f'ffmpeg -i "{orig_path}" -vn -af "afftdn,highpass=f=120,lowpass=f=3500,volume=2.0" -c:a aac "{enh_aud}" -y', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    
                    f_render = os.path.join(O_DIR, "final_shorts_output.mp4")
                    subprocess.run(f'ffmpeg -i "{st_out}" -i "{enh_aud}" -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -shortest "{f_render}" -y', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    
                    st.success("🏁 Pro-Level Vertical Short Edited & Rendered Successfully!")
                    st.video(f_render)
                    with open(f_render, "rb") as vf:
                        st.download_button("📥 Download Pro Short (9:16)", data=vf.read(), file_name="pro_shorts_output.mp4", mime="video/mp4")
                except Exception as re_e: st.error(f"Render Error: {re_e}")
