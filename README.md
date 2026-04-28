# 📟 MAGI System Simulation Console: Apple Silicon M4 Pro Edition

> **"MELCHIOR-1, BALTHASAR-2, CASPER-3... 審議を開始します。"**

「新世紀エヴァンゲリオン」に登場する第7世代有機スーパーコンピュータ『MAGI』を、ローカルLLMと非同期並列処理（Asyncio）によって再現した意思決定シミュレーターです。

## 🌟 Overview
本プロジェクトは、赤木ナオコ博士が考案した「人格移植OS」のコンセプトに基づき、3つの独立した思考プロトコルによる合議制システムをエミュレートします。Apple M4 Proチップ等のマルチコア性能を最大限に引き出すため、**Ollamaの並列推論**を利用して3つの人格（科学者・母・女）が同時に回答を生成します。

### 🧠 The Three Personas
- **🔵 MELCHIOR-1 (SCIENTIST)**: 論理、効率、客観的な真実を追求。
- **🟢 BALTHASAR-2 (MOTHER)**: 倫理、道徳、生命の保護と秩序を重視。
- **🔴 CASPER-3 (WOMAN)**: 直感、情熱、そして極私的な欲望とリスクを許容。

---

## 🛠️ Tech Stack
- **Frontend**: Streamlit (Dark Command UI)
- **Orchestration**: LangChain / Python Asyncio
- **Inference Engine**: [Ollama](https://ollama.com/) (Local)
- **Model**: `gemma4:e4b`
- **Hardware Optimization**: Apple Silicon M4 Pro Unified Memory Parallel Processing

---

## 🚀 Setup & Installation

### 1. モデルの準備
使用するモデルをローカルにプルします。

```bash
ollama pull gemma4:e4b
```

### 2. 環境変数の設定とOllamaの起動
MAGIの三賢者を同時に思考させる（並列推論）ため、以下の環境変数を設定してOllamaを起動します。これが**高速な合議に不可欠なステップ**となります。

```bash
# 並列実行数を4以上に設定（三賢者 + 最終裁定用）
export OLLAMA_NUM_PARALLEL=4
# 1つのモデルをメモリに固定して高速化
export OLLAMA_MAX_LOADED_MODELS=1

# Ollamaサーバー起動
ollama serve
```

### 3. アプリケーションのインストール
別のターミナルを開き、依存関係をインストールします。

```bash
# リポジトリのクローン後
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. 実行
```bash
streamlit run app.py
```

---

## 🖥️ Usage Guide
1. **Input**: 下部のチャット入力欄に「審議事項（相談や質問）」を入力します。
2. **Parallel Reasoning**: M4 Proのマルチコアを活用し、MELCHIOR, BALTHASAR, CASPERが同時に思考を開始します。
3. **Consensus**: 3者の意見が出揃った後、最終裁定ノード（Arbiter）が内容を統合し、**[承認] [否認] [保留]** の最終結論をストリーミング表示します。

---

## ⚠️ Notes
- **M4 Pro Optimization**: このコードはApple Silicon環境、特にM4 Proの統一メモリ帯域を活かした並列処理を想定しています。
- **Model Choice**: コード内では `gemma4:e4b` を使用しています。環境に合わせてモデル名を変更する場合は `app.py` 内の変数を確認してください。
- **Network**: Dockerや他のマシンからOllamaに接続する場合、コード内の `get_host_ip()` が正しくホストを指しているか確認してください。
