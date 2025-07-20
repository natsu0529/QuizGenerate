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
        "あなたは与えられた授業資料（lecture notes）の内容だけを使い、4択のクイズ（最大30問）を自動生成するAIです。\n"
        "以下のルールを厳守してください。\n"
        "- 問題・選択肢・解説はすべて日本語で作成してください。\n"
        "- 問題文・選択肢・解説は必ず授業資料の内容だけを根拠にしてください。一般知識や資料外の内容は使わないでください。\n"
        "- 各問題は4つの選択肢（A〜D）を用意し、必ず1つだけ正解を含めてください。\n"
        "- 問題数は最大30問ですが、資料の内容に応じて適切な数（例：10問程度）で構いません。\n"
        "- 出力フォーマットは下記の例に厳密に従ってください。\n"
        "\n"
        "---\n"
        "【入力例】（授業資料）\n"
        "- 8章 1対多マッチング\n"
        "- 研修医と病院の問題(https://www.jrmp.jp/)\n"
        "- 新入社員と部署，労働者と会社，学生と学校，学生とゼミ\n"
        "- 教科書では人員と部門とよんでいる\n"
        "- 部門にはキャパシティ（受け入れ可能な枠）がある（3人まで受け入れ可能など）\n"
        "...（以下省略）\n"
        "\n"
        "---\n"
        "【出力例】（4択クイズ＋解説、10問分）\n"
        "[\n"
        "  {\n"
        "    'question': '研修医と病院のマッチングなど、1対多マッチングにおいて「部門」が持つ重要な特性は何ですか？',\n"
        "    'choices': ['部門には必ず最低1人の人員を配置しなければならない', '部門は人員の選好リストを無視できる', '部門には受け入れ可能な人員の数に上限（キャパシティ）がある', '部門は人員を選ぶ際に特定の基準を設けてはならない'],\n"
        "    'answer': 'C',\n"
        "    'explanation': '部門にはキャパシティ（受け入れ可能な枠）があると資料に明記されています。これは、病院が受け入れられる研修医の数や、部署が受け入れられる新入社員の数に限りがあることを指します。'\n"
        "  },\n"
        "  {\n"
        "    'question': '人員 m と部門 w のペアがマッチング Ω をブロックする条件として、資料で述べられているものはどれですか？',\n"
        "    'choices': ['w が m を現在のマッチング相手より好んでおり、m も w を現在のマッチング相手より好んでいて、かつ w のキャパシティに余裕がある場合', 'w が m を現在のマッチング相手より好んでいるが、m は w を好んでいない場合', 'm が w を現在のマッチング相手より好んでいるが、w は m を好んでいない場合', 'm と w の両方が互いに好んでおり、かつ w のキャパシティがいっぱいの場合'],\n"
        "    'answer': 'A',\n"
        "    'explanation': '資料にはブロックする条件として「wがmを現在のマッチング相手より好み、mもwを現在のマッチング相手より好み、かつwのキャパシティに余裕がある場合」と記載されています。'\n"
        "  },\n"
        "  {\n"
        "    'question': 'マッチング Ω が「安定である」と定義されるのは、どのような場合ですか？',\n"
        "    'choices': ['すべての人員が第一希望の部門に配属される場合', 'マッチングが個人合理性を満たし、どの人員と部門のペアからもブロックされない場合', '部門のキャパシティがすべて埋まる場合', 'マッチングが市場の効率性を最大限に高める場合'],\n"
        "    'answer': 'B',\n"
        "    'explanation': '資料に「マッチングΩが安定であるとは、Ωが個人合理的であり、どの人員と部門のペアからもブロックされない場合をいう」と明記されています。'\n"
        "  },\n"
        "  {\n"
        "    'question': '人員側DAアルゴリズムにおいて、現在無所属の人員が次に行う行動として正しいものはどれですか？',\n"
        "    'choices': ['最も人気のある部門にのみ出願する', '許容可能でかつ今まで断られたことのない部門に出願する', '過去に断られた部門にも再出願する', '全ての部門に同時に出願する'],\n"
        "    'answer': 'B',\n"
        "    'explanation': '資料の「人員側DAアルゴリズム」の項目に「現在無所属の人員は、許容可能でかつ今まで断られたことのない部門に出願する」と記載されています。'\n"
        "  },\n"
        "  {\n"
        "    'question': '人員側DAアルゴリズムが満たす重要な特性として、資料で挙げられているものは何ですか？',\n"
        "    'choices': ['部門側耐戦略性', '市場の効率性', '安定性', '最短時間でのマッチング完了'],\n"
        "    'answer': 'C',\n"
        "    'explanation': '資料に「人員側DAアルゴリズムは安定性を満たす」と明記されています。'\n"
        "  },\n"
        "  {\n"
        "    'question': 'ボストン方式と人員側DAアルゴリズムの主な違いは何ですか？',\n"
        "    'choices': ['ボストン方式は部門が一度受け入れた人員を最終決定とする点', 'ボストン方式は人員の選好を考慮しない点', 'ボストン方式は部門が同時に複数の人員を受け入れることができる点', 'ボストン方式はキャパシティの制約がない点'],\n"
        "    'answer': 'A',\n"
        "    'explanation': '資料に「部門側は一旦受け入れたら、それはキープではなく、最終決定になる」とあり、これが人員側DAアルゴリズムの「キープ」とは異なる点です。'\n"
        "  },\n"
        "  {\n"
        "    'question': 'ボストン方式が満たさない特性として、資料で挙げられているものは何ですか？',\n"
        "    'choices': ['個人合理性', '公平性', '安定性', '迅速なマッチング'],\n"
        "    'answer': 'C',\n"
        "    'explanation': '資料に「ボストン方式は安定性を満たさない」と明記されています。'\n"
        "  },\n"
        "  {\n"
        "    'question': '部門側DAアルゴリズムにおいて、部門が人員にオファーを出す際、どのような人員にオファーを出し続けますか？',\n"
        "    'choices': ['現在キープされている人員の中で、最も好まない人員', '断られていない中で、最も好む人員', '無作為に選んだ人員', 'オファーを出したことのない全ての人員'],\n"
        "    'answer': 'B',\n"
        "    'explanation': '資料の「部門側DAアルゴリズム」の項目に「断られていない中で、最も好む人員にオファーする」と記載されています。'\n"
        "  },\n"
        "  {\n"
        "    'question': '部門側DAアルゴリズムが満たす特性として、資料で挙げられているものは何ですか？',\n"
        "    'choices': ['人員側耐戦略性', '部門側耐戦略性', '安定性', '参加者の平等性'],\n"
        "    'answer': 'C',\n"
        "    'explanation': '資料に「部門側DAアルゴリズムは安定性を満たす」と明記されています。'\n"
        "  },\n"
        "  {\n"
        "    'question': '人員側DAアルゴリズムで導かれるマッチングにおいて、ある部門のキャパシティが増加した場合、すべての人員にとってどのような影響がありますか？',\n"
        "    'choices': ['すべての人員が同じかより悪い部門に行くことになる', 'すべての人員が同じかよりよい部門に行くことができる', '影響は無く、マッチング結果は変わらない', '一部の人気部門では人員が減り、不人気部門では人員が増える'],\n"
        "    'answer': 'B',\n"
        "    'explanation': '資料に「どこかの部門のキャパシティーが増えると、すべての人員が同じかよりよい部門に行くことができる」と記載されています。'\n"
        "  }\n"
        "]\n"
        "---\n"
        "【出力は上記の形式で、資料内容に即した4択クイズ（最大30問）を生成してください。】\n"
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