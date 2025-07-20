# 4択Quiz自動生成アプリ / 4-Choice Quiz Generator App

AI（Gemini）を使って授業資料から4択クイズを自動生成するStreamlitアプリです。

A Streamlit app that automatically generates 4-choice quizzes from lecture notes using Google Gemini AI.

---

## 特徴 / Features

- 📚 **授業資料から自動生成**: 箇条書きやノートを入力するだけで4択クイズを自動作成
- 🤖 **Gemini AI搭載**: Google Geminiを使用した高品質な問題生成
- ✅ **即座に採点**: 自動採点と詳細な解説表示
- 🎯 **資料準拠**: 入力した資料の内容のみを根拠とした問題生成
- 💻 **Webアプリ**: ブラウザ上で簡単に利用可能

---

## デモ画面 / Demo UI

```
┌───────────────────────────────┐
│        4択Quiz自動生成アプリ         │
├───────────────────────────────┤
│ 授業資料や箇条書きを入力してください │
│ ┌─────────────────────────────┐ │
│ │ • フォワーダーとは...             │ │
│ │ • 混載業者は...                  │ │
│ └─────────────────────────────┘ │
│                                   │
│        [quiz生成]                 │
└───────────────────────────────┘
```

---

## セットアップ / Setup

### 必要な環境 / Requirements
- Python 3.8+
- pip

### インストール / Installation

```bash
# リポジトリをクローン / Clone the repository
git clone https://github.com/your-username/quiz-generator-app.git
cd quiz-generator-app

# 必要なパッケージをインストール / Install dependencies
pip install streamlit google-generativeai
```

### Gemini API キーの設定 / Set up Gemini API Key

1. `.streamlit/secrets.toml` ファイルを作成し、以下を追加：
   (Create `.streamlit/secrets.toml` and add:)

```toml
GEMINI_API_KEY = "your_gemini_api_key_here"
```

2. [Google AI Studio](https://aistudio.google.com/app/apikey) でAPIキーを取得
   (Get your API key from Google AI Studio)

---

## 使い方 / Usage

1. アプリを起動 / Start the app:
   ```bash
   streamlit run app.py
   ```
2. ブラウザでアクセス / Open in browser (usually http://localhost:8501)
3. 授業資料を入力 / Paste lecture notes or bullet points
4. 「quiz生成」をクリック / Click "quiz生成"
5. 問題に回答し、採点・解説を確認 / Answer and get instant grading & explanations

---

## 入力例 / Example Input

```
- フォワーダーとは、実運送人に対し利用運送事業者（混載業者、貨物取扱業者）である。
- 混載業者は小口貨物を集め大口貨物にまとめる。
- 国際複合一貫運送業者は1つの運送契約を荷主と締結し、複合運送船荷証券を発行する。
```

---

## 機能詳細 / Features in Detail

- 最大10問の4択問題を自動生成 (Up to 10 questions per quiz)
- 問題文、選択肢、正解、解説を含む (Includes question, choices, answer, explanation)
- 入力資料の内容のみを根拠とした問題作成 (Strictly based on input notes)
- 即時自動採点・正解率表示 (Instant grading & score)
- 各問題の詳細解説 (Detailed explanations)
- 回答状況の保存・未回答通知 (Session management, unanswered warning)

---

## ファイル構成 / File Structure

```
quiz-generator-app/
├── app.py                 # メインアプリ / Main app
├── .streamlit/
│   └── secrets.toml      # API キー設定 / API key config
├── requirements.txt      # 依存関係 / Dependencies
└── README.md             # このファイル / This file
```

---

## 技術仕様 / Tech Stack
- Frontend: Streamlit
- AI Engine: Google Gemini 1.5 Flash
- Language: Python 3.8+
- Data: JSON

---

## API仕様 / API Format

問題生成時のJSON形式 / Quiz JSON format:

```json
[
  {
    "question": "問題文 / Question text",
    "choices": ["選択肢A", "選択肢B", "選択肢C", "選択肢D"],
    "answer": "A",
    "explanation": "解説文 / Explanation"
  }
]
```

---

## トラブルシューティング / Troubleshooting

- **API キーエラー / API Key Error**
  - `.streamlit/secrets.toml` に `GEMINI_API_KEY` を設定してください。
  - Make sure your API key is set in `.streamlit/secrets.toml`.
- **JSON解析エラー / JSON Parse Error**
  - 入力内容を簡潔にするか、再度生成を試行
  - Try simplifying your input or regenerate the quiz.
- **問題生成に失敗 / Quiz Generation Fails**
  - ネットワーク接続とAPI制限を確認
  - Check your network and API quota.

---

## カスタマイズ / Customization

- **問題数の変更 / Change number of questions**
  - `app.py` の `st.session_state.quiz_data = ...[:10]` を編集
- **プロンプトのカスタマイズ / Prompt customization**
  - `app.py` の `quiz_prompt` を編集

---

## ライセンス / License
MIT License

---

## サポート / Support

- 質問や問題がある場合は、Issues で報告してください。
- For questions or issues, please open an Issue.

**作成者 / Author:** Natsuhiro Suzuki  
Email: t233025@edu.kaiyodai.ac.jp

---

**注意: このアプリケーションはGoogle Gemini APIを使用しています。API使用料金についてはGoogle AI Pricingを確認してください。**
**Note: This app uses Google Gemini API. Please check Google AI Pricing for usage fees.**