import streamlit as st
import google.generativeai as genai

# Gemini APIキー設定
if "GEMINI_API_KEY" not in st.secrets:
    st.error(".streamlit/secrets.toml に GEMINI_API_KEY を設定してください。")
    st.stop()
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

st.title("箇条書き→レポート・4択Quiz自動生成アプリ")

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

# レポート生成
if st.button("レポート生成"):
    prompt = f"以下の箇条書きを、まとまったレポート形式の日本語文章に変換してください。\n\n{bullets}"
    model = genai.GenerativeModel("models/gemini-1.5-flash")
    response = model.generate_content(prompt)
    st.markdown("### レポート結果")
    st.write(response.text)

# Quiz生成
if st.button("quiz生成"):
    quiz_prompt = (
        "以下の授業資料から、4択のquizを30問日本語で作成してください。"
        "各問題は、問題文・選択肢A〜D・正解の選択肢・簡潔な解説を含めてJSON形式で出力してください。"
        "例: [{\"question\":..., \"choices\":[...], \"answer\":\"A\", \"explanation\":...}, ...]"
        f"\n\n授業資料:\n{bullets}"
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