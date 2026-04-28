import streamlit as st
import sys
import subprocess
import asyncio
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage

# --- 1. ネットワーク設定 ---
def get_host_ip():
    if sys.platform == "darwin": return "localhost"
    try:
        return subprocess.check_output("ip route | grep default", shell=True).decode().split()[2]
    except: return "127.0.0.1"

# --- 2. MAGIコンフィグレーション ---
BASE_CONFIG_PROMPT = (
    "あなたは、新世紀エヴァンゲリオンに登場する、第7世代有機スーパーコンピュータシステム『MAGI』の一人格です。"
    "開発者である赤木ナオコ博士の人格の一側面が移植されています。"
)

MAGI_CONFIG = {
    "MELCHIOR": {
        "name": "MELCHIOR-1", 
        "prompt": f"{BASE_CONFIG_PROMPT}\nあなたは【科学者】です。論理的・科学的な整合性、およびシステム全体の効率を最優先に分析し、冷徹なまでの最適解を導き出しなさい。", 
        "color": "blue",
        "avatar": "🔵",
        "temp": 0.1
    },
    "BALTHASAR": {
        "name": "BALTHASAR-2", 
        "prompt": f"{BASE_CONFIG_PROMPT}\nあなたは【母】です。倫理、道徳、生命への慈愛、そして秩序と伝統を重視しなさい。システム全体の存続と、個の尊厳のバランスを考慮した、思慮深い判断を下しなさい。", 
        "color": "green",
        "avatar": "🟢",
        "temp": 0.4
    },
    "CASPER": {
        "name": "CASPER-3", 
        "prompt": f"{BASE_CONFIG_PROMPT}\nあなたは【女】です。直感、感性、そして心の奥底に秘めた情欲と執着を重視しなさい。時に科学や母性をも裏切り、破滅を予感させる甘美なリスクさえも「悦び」として受け入れる、あなただけの極私的な真実を語りなさい。", 
        "color": "red",
        "avatar": "🔴",
        "temp": 0.9
    }
}

# --- 3. 非同期推論エンジン ---
async def get_magi_response(key, config, history, user_input):
    """
    [Apple Silicon M4 Pro Optimization] 
    各エージェントの推論を非同期(Async)で実行！
    """
    llm = ChatOpenAI(
        base_url=f"http://{get_host_ip()}:11434/v1",
        api_key="ollama",
        model_name="gemma4:e4b",
        temperature=config["temp"],
        streaming=False # 並列処理の結果を同期して表示するために最初はFalseに
    )
    chain = ChatPromptTemplate.from_messages([
        ("system", config["prompt"]),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ]) | llm | StrOutputParser()
    
    # 非同期で実行！
    response = await chain.ainvoke({"history": history, "input": user_input})
    return key, response

# --- 4. UI 初期設定 ---
st.set_page_config(page_title="MAGI Console: for Apple Silicon M4 Pro", layout="wide", page_icon="🖥️")

st.markdown("""
    <style>
    .main { background-color: #050505; }
    .stChatMessage { border-radius: 12px; border: 1px solid #333; }
    h1, h2, h3 { font-family: 'Courier New', monospace; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

st.title("🖥️ MAGI System : Apple Silicon M4 Pro Parallel Mode")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 5. メインロジック ---
if user_input := st.chat_input("審議事項を入力してください..."):
    with st.chat_message("user"):
        st.markdown(user_input)

    # 履歴構築
    history_for_chain = [
        HumanMessage(content=m["content"]) if m["role"] == "user" else AIMessage(content=m["content"])
        for m in st.session_state.messages
    ]

    st.divider()
    cols = st.columns(3)
    
    # 非同期実行のための関数
    async def run_magi_session():
        tasks = [
            get_magi_response(k, v, history_for_chain, user_input) 
            for k, v in MAGI_CONFIG.items()
        ]
        # 三賢者を同時に！
        return await asyncio.gather(*tasks)

    with st.spinner("⚡ Apple Silicon M4 Pro Unified Memory Processing..."):
        # 非同期ループの実行
        results = asyncio.run(run_magi_session())
        magi_responses = dict(results)

    # ① 結果の描画
    for idx, (key, config) in enumerate(MAGI_CONFIG.items()):
        with cols[idx]:
            st.subheader(f":{config['color']}[{config['name']}]")
            with st.chat_message("assistant", avatar=config['avatar']):
                st.write(magi_responses[key])

    # ② 最終合議（Arbiter）
    st.divider()
    st.subheader("🏁 FINAL DECISION")
    with st.chat_message("assistant", avatar="✨"):
        consensus_prompt = (
            "あなたはMAGIの最終裁定ノードです。三者の意見を統合し、結論を出してください。\n\n"
            f"MELCHIOR: {magi_responses['MELCHIOR']}\n"
            f"BALTHASAR: {magi_responses['BALTHASAR']}\n"
            f"CASPER: {magi_responses['CASPER']}\n\n"
            "最後に必ず [承認] [否認] [保留] のいずれかを明記せよ。"
        )
        
        # 最終判断は逐次ストリーミング表示！
        final_llm = ChatOpenAI(
            base_url=f"http://{get_host_ip()}:11434/v1",
            api_key="ollama",
            model_name="gemma4:e4b",
            temperature=0.3,
            streaming=True
        )
        final_res = st.write_stream(final_llm.stream(consensus_prompt))

    # 履歴保存
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.messages.append({"role": "assistant", "content": final_res})
