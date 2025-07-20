4択Quiz自動生成アプリ
AI（Gemini）を使って授業資料から4択クイズを自動生成するStreamlitアプリケーションです。
Show Image
Show Image
Show Image
特徴

📚 授業資料から自動生成: 箇条書きや授業ノートを入力するだけで4択クイズを自動作成
🤖 Gemini AI搭載: Google Geminiを使用した高品質な問題生成
✅ 即座に採点: リアルタイムでの自動採点と詳細な解説表示
🎯 資料準拠: 入力した資料の内容のみを根拠とした問題生成
💻 Webアプリ: ブラウザ上で簡単に利用可能

デモ画面
┌─────────────────────────────────────┐
│        4択Quiz自動生成アプリ          │
├─────────────────────────────────────┤
│ 授業資料や箇条書きを入力してください   │
│ ┌─────────────────────────────────┐ │
│ │ • フォワーダーとは、実運送人に対し  │ │
│ │   利用運送事業者である           │ │
│ │ • 混載業者は小口貨物を集める     │ │
│ └─────────────────────────────────┘ │
│                                     │
│        [quiz生成]                   │
└─────────────────────────────────────┘
インストール
必要な環境

Python 3.8以上
pip

手順

リポジトリをクローン

bashgit clone https://github.com/your-username/quiz-generator-app.git
cd quiz-generator-app

必要なパッケージをインストール

bashpip install streamlit google-generativeai

Gemini API キーの設定

.streamlit/secrets.toml ファイルを作成し、以下を追加：
tomlGEMINI_API_KEY = "your_gemini_api_key_here"
Gemini API キーの取得方法：

Google AI Studio にアクセス
Googleアカウントでログイン
「Create API Key」をクリック
生成されたキーをコピー

使い方
1. アプリケーションを起動
bashstreamlit run app.py
2. ブラウザでアクセス
通常は http://localhost:8501 で起動します。
3. クイズを生成

授業資料を入力: テキストエリアに箇条書きや授業ノートを貼り付け
「quiz生成」をクリック: AIが自動で4択クイズを生成
問題に回答: 各問題のラジオボタンで選択
「回答を提出・採点」をクリック: 自動採点と解説表示

入力例
- フォワーダーとは、実運送人に対し利用運送事業者（混載業者、貨物取扱業者）である。
- 混載業者は小口貨物を集め大口貨物にまとめる。
- 国際複合一貫運送業者は1つの運送契約を荷主と締結し、複合運送船荷証券を発行する。
- コンテナ船は定期船サービスを提供し、決められた航路とスケジュールで運航する。
- バルク船は不定期船として運航され、穀物や鉱石などのばら積み貨物を輸送する。
機能詳細
クイズ生成機能

最大10問の4択問題を自動生成
問題文、選択肢、正解、解説を含む完全な問題セット
入力資料の内容のみを根拠とした問題作成

採点・解説機能

即座の自動採点
正解率の表示（パーセンテージ）
各問題の詳細解説
正解/不正解の色分け表示

セッション管理

回答状況の保存
未回答問題の通知
リセット機能

ファイル構造
quiz-generator-app/
├── app.py                 # メインアプリケーション
├── .streamlit/
│   └── secrets.toml      # API キー設定（要作成）
├── requirements.txt      # 依存関係
└── README.md            # このファイル
技術仕様
使用技術

フロントエンド: Streamlit
AI エンジン: Google Gemini 1.5 Flash
言語: Python 3.8+
データ形式: JSON

API仕様
問題生成時のJSON形式：
json[
  {
    "question": "問題文",
    "choices": ["選択肢A", "選択肢B", "選択肢C", "選択肢D"],
    "answer": "A",
    "explanation": "解説文"
  }
]
トラブルシューティング
よくある問題
1. API キーエラー
.streamlit/secrets.toml に GEMINI_API_KEY を設定してください。
→ secrets.toml ファイルにAPIキーが正しく設定されているか確認
2. JSON解析エラー
JSONの解析に失敗しました
→ 入力内容を簡潔にするか、再度生成を試行
3. 問題生成に失敗
Quizの生成に失敗しました
→ ネットワーク接続とAPI制限を確認
デバッグ方法

Streamlitのデバッグモード: streamlit run app.py --logger.level=debug
エラー詳細は画面に表示されます

改善・カスタマイズ
問題数の変更
app.py の以下の行を修正：
pythonst.session_state.quiz_data = valid_quiz_data[:10]  # 最大10問 → 任意の数に変更
プロンプトのカスタマイズ
quiz_prompt 変数を編集して、問題の形式や難易度を調整可能
ライセンス
MIT License - 詳細は LICENSE ファイルを参照
貢献
プルリクエストやイシューの報告を歓迎します！

このリポジトリをフォーク
機能ブランチを作成 (git checkout -b feature/amazing-feature)
変更をコミット (git commit -m 'Add amazing feature')
ブランチにプッシュ (git push origin feature/amazing-feature)
プルリクエストを作成

サポート
質問や問題がある場合は、Issues で報告してください。
開発者

作成者: Natsuhiro Suzuki
Email: t233025@edu.kaiyodai.ac.jp


注意: このアプリケーションはGoogle Gemini APIを使用しています。API使用料金についてはGoogle AI Pricingを確認してください。Chat controls Sonnet 4