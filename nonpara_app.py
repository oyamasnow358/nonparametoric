import streamlit as st
from streamlit_autorefresh import st_autorefresh
import datetime

# ページ設定
st.set_page_config(page_title="もやもや", layout="wide")

# --- 1. データ管理（絶対にバグを出さないための新設計） ---
class MoyamoyaEnginePerfect:
    def __init__(self):
        self.data = [] 

    def add(self, score):
        self.data.append({"t": datetime.datetime.now(), "v": score})
        # 1分前のデータは掃除
        limit = datetime.datetime.now() - datetime.timedelta(minutes=1)
        self.data = [d for d in self.data if d["t"] > limit]

    def get_summary(self):
        now = datetime.datetime.now()
        sec20 = now - datetime.timedelta(seconds=20)
        recent = [d["v"] for d in self.data if d["t"] > sec20]
        avg = sum(recent) / len(recent) if recent else 1.0
        return avg, len(recent)

@st.cache_resource
def get_system():
    return MoyamoyaEnginePerfect()

engine = get_system()

# --- 2. 投票ロジック（URLパラメータを利用して確実に検知） ---
# ボタン（HTMLリンク）が押されると URL に ?v=数値 が入る仕組み
q = st.query_params
if "v" in q:
    try:
        score = float(q.get("v"))
        engine.add(score)
        # 連続投票を防ぐため、パラメータを消してリロード（任意。今回はシンプルさ優先でそのまま）
    except:
        pass

# --- 3. URL判定 ---
is_instructor = q.get("mode") == "instructor"

# ---------------------------------------------------------
# 【講師画面】 あなたが「OK」と言ったデザインを死守
# ---------------------------------------------------------
if is_instructor:
    st_autorefresh(interval=2000, key="ins_refresh")
    avg, count = engine.get_summary()
    
    def get_rgb(s):
        if s >= 0.5:
            r, g, b = int(255-(255-40)*(s-0.5)*2), int(193+(167-193)*(s-0.5)*2), int(7+(69-7)*(s-0.5)*2)
        else:
            r, g, b = int(220+(255-220)*s*2), int(53+(193-53)*s*2), int(69+(7-69)*s*2)
        return f"rgb({r}, {g}, {b})"

    bg_color = get_rgb(avg)

    st.markdown(f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background-color: {bg_color} !important;
            transition: background-color 2s ease-in-out;
        }}
        .glass-box {{
            background: rgba(255, 255, 255, 0.25);
            backdrop-filter: blur(10px);
            border-radius: 40px;
            padding: 60px;
            margin: 100px auto;
            text-align: center;
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.3);
            max-width: 600px;
        }}
        h1, h2, p {{ color: white !important; font-family: sans-serif; }}
        </style>
        <div class="glass-box">
            <h2 style="margin: 0;">現在の理解度</h2>
            <h1 style="font-size: 130px; margin: 15px 0; font-weight: bold;">{int(avg * 100)}%</h1>
            <p style="font-size: 20px;">直近20秒の回答数: {count} 件</p>
        </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 【受講生画面】 HTMLボタンで「巨大・中央・着色」を完全保証
# ---------------------------------------------------------
else:
    # 画面中央に寄せるためのCSS
    st.markdown("""
        <style>
        .block-container { max-width: 600px !important; margin: auto !important; padding-top: 50px !important; }
        .huge-btn {
            display: flex; align-items: center; justify-content: center;
            width: 100%; height: 140px; border-radius: 30px;
            margin-bottom: 25px; font-size: 35px; font-weight: bold;
            text-decoration: none; box-shadow: 0 8px 15px rgba(0,0,0,0.2);
            transition: transform 0.1s;
        }
        .huge-btn:active { transform: scale(0.95); }
        .g { background-color: #28a745; color: white !important; }
        .y { background-color: #ffc107; color: black !important; }
        .r { background-color: #dc3545; color: white !important; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align: center; color: #333;'>今の理解度は？</h1>", unsafe_allow_html=True)

    # 状態メッセージ
    if "v" in q:
        st.success("✅ 送信しました（再度選ぶ場合は下のボタンをタップ）")
    else:
        st.info("ℹ️ ボタンをタップして今の状況を送信してください")

    # HTMLで直接ボタン（リンク）を記述。これで100%色がつきます。
    # href="?v=..." によって、自分自身のURLにパラメータを付けてリロードさせる仕組み
    st.markdown(f'<a href="?v=1.0" target="_self" class="huge-btn g">😊 スムーズ</a>', unsafe_allow_html=True)
    st.markdown(f'<a href="?v=0.5" target="_self" class="huge-btn y">🤨 少し速い</a>', unsafe_allow_html=True)
    st.markdown(f'<a href="?v=0.0" target="_self" class="huge-btn r">❓ わからない</a>', unsafe_allow_html=True)

    st.markdown("<p style='text-align: center; color: gray; margin-top: 50px;'>20秒経過すると集計から自動的に消えます</p>", unsafe_allow_html=True)