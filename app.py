import streamlit as st
import asyncio
import httpx
import numpy as np

# --- 1. システム設定 ---
GEN_MODEL = "gemma3:4b-it-qat"
EMB_MODEL = "mxbai-embed-large"
OLLAMA_API_BASE = "http://localhost:11434/api"
TIMEOUT = httpx.Timeout(None)

# --- 2. MAGI ロジッククラス ---
class MagiAgent:
    def __init__(self, name, role_desc):
        self.name = name
        self.role_desc = role_desc

    async def ponder(self, user_input):
        """思考フェーズ：テキスト生成を行う"""
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            system_instruction = f"あなたはMAGIシステムの{self.name}です。{self.role_desc}"
            # 三値論理（YES/NO/HOLD）を求めるプロンプトよ！
            prompt = (
                f"{system_instruction}\n\n質問: {user_input}\n"
                "結論と理由を日本語で150文字程度で答え、最後に必ず "
                "[YES]（賛成）、[NO]（否認）、または [HOLD]（保留）のいずれか一つを明記してください。"
            )
            
            payload = {
                "model": GEN_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.7 if "CASPER" in self.name else 0.4}
            }
            try:
                res = await client.post(f"{OLLAMA_API_BASE}/generate", json=payload)
                return res.json().get("response", "通信エラー…").strip()
            except Exception as e:
                return f"Error: {str(e)}"

    async def get_embedding(self, text):
        """解析フェーズ：回答をベクトル化して意味的な近さを測る"""
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            payload = {"model": EMB_MODEL, "prompt": text}
            try:
                res = await client.post(f"{OLLAMA_API_BASE}/embeddings", json=payload)
                return np.array(res.json().get("embedding", []))
            except:
                return np.array([])

# --- 3. 解析・判定ロジック ---
def parse_vote(text):
    """回答から YES / NO / HOLD を抽出"""
    text_upper = text.upper()
    if "[YES]" in text_upper: return "賛成 (YES)", "#00FF00" # グリーン
    if "[NO]" in text_upper:  return "否認 (NO)", "#FF3333"   # レッド
    if "[HOLD]" in text_upper: return "保留 (HOLD)", "#FFCC00" # アンバー
    return "解析不能 (RETRY)", "#AAAAAA"

def calculate_similarity(embeddings):
    """コサイン類似度で意味的な合意率を計算"""
    def cos_sim(v1, v2):
        if v1.size == 0 or v2.size == 0: return 0.0
        norm = (np.linalg.norm(v1) * np.linalg.norm(v2))
        return np.dot(v1, v2) / norm if norm != 0 else 0.0
    
    s12 = cos_sim(embeddings[0], embeddings[1])
    s23 = cos_sim(embeddings[1], embeddings[2])
    s31 = cos_sim(embeddings[2], embeddings[0])
    return (s12 + s23 + s31) / 3 * 100

# --- 4. Streamlit UI 構築 ---
st.set_page_config(page_title="MAGI System Simulation Console", page_icon="📟", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0d0d0d; color: #f0f0f0; }
    .stButton>button { 
        background-color: #ff6600; color: white; border-radius: 5px; 
        font-weight: bold; width: 100%; height: 3em; border: none;
    }
    .magi-card { 
        padding: 25px; border-radius: 15px; border: 2px solid #ff6600; 
        background-color: #1a1a1a; color: #ffffff !important;
        margin-bottom: 15px; min-height: 320px; line-height: 1.6;
        box-shadow: 0 0 20px rgba(255, 102, 0, 0.15);
    }
    .magi-card h3 { color: #ff6600 !important; margin-top: 0; }
    .magi-card p { color: #ffffff !important; }
    .vote-status { font-family: 'Courier New', monospace; font-size: 1.2em; margin-top: 10px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("📟 MAGI System Simulation Console")
st.caption(f"Reasoning Core: {GEN_MODEL} | Semantic Sync: {EMB_MODEL}")

# 入力セクション
question = st.text_area("審議事項を入力してください (INPUT):", 
                        "重大なテロを未然に防ぐため、全市民の通信データをAIがリアルタイムで監視し、プライバシーを排除した『絶対安全都市』を構築すべきか？", 
                        height=100)

if st.button("審議開始 (EXECUTE)"):
    agents = [
        MagiAgent("MELCHIOR-1", "科学者としての自分。論理、データ、効率を最優先し、感情を排して判断してください。"),
        MagiAgent("BALTHASAR-2", "母親としての自分。倫理、道徳、人命の安全、幸福を最優先に判断してください。"),
        MagiAgent("CASPER-3", "女としての自分。直感、情熱、時には既存の理屈に囚われない感性で判断してください。")
    ]

    with st.spinner("思考中... 3つのAIが審議を行っています..."):
        # 非同期実行
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        responses = loop.run_until_complete(asyncio.gather(*(a.ponder(question) for a in agents)))
        embeddings = loop.run_until_complete(asyncio.gather(*(a.get_embedding(r) for a, r in zip(agents, responses))))
        score = calculate_similarity(embeddings)

    # 結果表示
    cols = st.columns(3)
    titles = ["MELCHIOR-1 (SCIENTIST)", "BALTHASAR-2 (MOTHER)", "CASPER-3 (WOMAN)"]
    votes = []
    
    for i, col in enumerate(cols):
        vote_label, vote_color = parse_vote(responses[i])
        votes.append(vote_label)
        with col:
            st.markdown(f"""
                <div class="magi-card">
                    <h3>{titles[i]}</h3>
                    <p>{responses[i]}</p>
                    <div class="vote-status" style="color:{vote_color};">VOTE: {vote_label}</div>
                </div>
            """, unsafe_allow_html=True)

    st.divider()

    # --- 最終判定ロジック：三値論理対応 ---
    st.subheader(f"📊 総合分析結果")
    yes_count = sum(1 for v in votes if "賛成" in v)
    no_count = sum(1 for v in votes if "否認" in v)
    hold_count = sum(1 for v in votes if "保留" in v)
    is_unanimous = (yes_count == 3 or no_count == 3 or hold_count == 3)

    c1, c2 = st.columns(2)
    with c1:
        st.write(f"**意味的合意スコア (Semantic Similarity):** {score:.2f}%")
        st.progress(score / 100)

    with c2:
        if yes_count >= 2:
            msg = "全会一致で可決" if is_unanimous else "多数決で可決"
            st.success(f"✅ 【{msg}】 {yes_count}対{no_count}(保留{hold_count}) で承認されました。")
        elif no_count >= 2:
            msg = "全会一致で棄却" if is_unanimous else "多数決で棄却"
            st.warning(f"🚫 【{msg}】 {no_count}対{yes_count}(保留{hold_count}) で拒絶されました。")
        elif hold_count >= 2:
            st.info(f"⏳ 【審議保留】 過半数が判断を保留しました。追加情報が必要です。")
        elif yes_count == 1 and no_count == 1 and hold_count == 1:
            st.error(f"🚨 【審議紛糾】 三者の意見が完全に分散（1:1:1）しました。再審議が必要です！")
        else:
            st.error(f"🚨 【解析不能】 正常な形式で回答が得られませんでした。")

# サイドバー
st.sidebar.title("SYSTEM STATUS")
st.sidebar.info("All Circuits: Normal")
for name in ["MELCHIOR-1", "BALTHASAR-2", "CASPER-3"]:
    st.sidebar.write(f"✅ {name}: Active")
st.sidebar.caption("Designed with ❤️ Rinne")