import streamlit as st
import google.generativeai as genai

# Gemini APIキー設定
if "GEMINI_API_KEY" not in st.secrets:
    st.error(".streamlit/secrets.toml に GEMINI_API_KEY を設定してください。")
    st.stop()
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

st.title("4択Quiz自動生成アプリ")

# 入力欄
bullets = st.text_area("授業資料や箇条書きを入力してください", height=200)

# セッション状態の初期化
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = None
if "user_answers" not in st.session_state:
    st.session_state.user_answers = [None] * 30
if "grading" not in st.session_state:
    st.session_state.grading = False
if "explanations" not in st.session_state:
    st.session_state.explanations = None

# Quiz生成
if st.button("quiz生成"):
    quiz_prompt = (
        "あなたは与えられた授業資料（lecture notes）の内容だけを使い、4択クイズ（最大10問）を自動生成するAIです。\n"
        "【重要】\n"
        "- 問題・選択肢・解説はすべて日本語で作成してください。\n"
        "- 問題文・選択肢・解説は必ず授業資料の内容だけを根拠にしてください。一般知識や資料外の内容は使わないでください。\n"
        "- 各問題は4つの選択肢（A〜D）を用意し、必ず1つだけ正解を含めてください。\n"
        "- 出力は必ずPythonのリスト形式のJSON（[]で囲む）で返してください。\n"
        "- 1問あたりのJSON要素は question, choices, answer, explanation の4つだけです。\n"
        "- answerはA/B/C/Dのいずれか1文字で指定してください。\n"
        "- 出力例の形式を厳密に守ってください。\n"
        "- 出力は10問以内にしてください。\n"
        "\n"
        "【入力例】\n"
        "• フォワーダーとは、実運送人に対し利用運送事業者（混載業者、貨物取扱業者）である。\n"
        "• 混載業者は小口貨物を集め大口貨物にまとめる。\n"
        "• 国際複合一貫運送業者は1つの運送契約を荷主と締結し、複合運送船荷証券を発行する。\n"
        "\n"
        "【出力例】\n"
        "[\n"
        "  {\n"
        "    \"question\": \"フォワーダーの主な役割は何ですか？\",\n"
        "    \"choices\": [\"荷主の小口貨物を集め大口貨物にまとめる\", \"運送契約を結ばない\", \"貨物を保管するだけ\", \"運賃を決めるだけ\"],\n"
        "    \"answer\": \"A\",\n"
        "    \"explanation\": \"混載業者（フォワーダー）は小口貨物を集め大口貨物にまとめる役割があります。\"\n"
        "  }\n"
        "]\n"
        "\n"
        "【出力は必ず上記の形式で、[]で囲んだJSONリストとして返してください。】\n"
        f"\n授業資料:\n{bullets}"
    )
    model = genai.GenerativeModel("models/gemini-1.5-flash")
    response = model.generate_content(quiz_prompt)
    import json
    try:
        quiz_data = json.loads(response.text)
        if not isinstance(quiz_data, list) or len(quiz_data) < 1:
            raise ValueError
        st.session_state.quiz_data = quiz_data[:30]  # 30問まで
        st.session_state.user_answers = [None] * len(st.session_state.quiz_data)
        st.session_state.grading = False
        st.session_state.explanations = None
        st.success("Quizを生成しました！下に表示されます。")
    except Exception:
        st.error("Quizの自動生成に失敗しました。入力内容を見直すか、再度お試しください。")

# Quiz表示・解答
if st.session_state.quiz_data:
    st.markdown("---")
    st.header("4択Quiz (30問)")
    for idx, q in enumerate(st.session_state.quiz_data):
        st.markdown(f"**問題{idx+1}**: {q.get('question', '')}")
        st.session_state.user_answers[idx] = st.radio(
            f"選択肢 (問題{idx+1})",
            options=["A", "B", "C", "D"],
            format_func=lambda x: f"{x}: {q.get('choices', ['','','',''])[ord(x)-65] if q.get('choices') else ''}",
            key=f"quiz_{idx}",
            index=(ord(st.session_state.user_answers[idx])-65) if st.session_state.user_answers[idx] else -1
        )
        st.markdown("---")

    if st.button("回答を提出・採点"):
        correct = 0
        explanations = []
        for idx, q in enumerate(st.session_state.quiz_data):
            user_ans = st.session_state.user_answers[idx]
            correct_ans = q.get("answer", "")
            if user_ans == correct_ans:
                correct += 1
            explanations.append({
                "user": user_ans,
                "correct": correct_ans,
                "explanation": q.get("explanation", "")
            })
        st.session_state.grading = True
        st.session_state.explanations = explanations
        st.success(f"{correct} / {len(st.session_state.quiz_data)} 問正解！")

# 採点・解説表示
if st.session_state.grading and st.session_state.explanations:
    st.header("採点・解説")
    for idx, q in enumerate(st.session_state.quiz_data):
        exp = st.session_state.explanations[idx]
        st.markdown(f"**問題{idx+1}**: {q.get('question', '')}")
        st.write(f"あなたの回答: {exp['user']} / 正解: {exp['correct']}")
        st.info(f"解説: {exp['explanation']}")
        st.markdown("---")