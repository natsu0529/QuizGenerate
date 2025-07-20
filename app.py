import streamlit as st
import google.generativeai as genai
import json

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
    st.session_state.user_answers = []
if "grading" not in st.session_state:
    st.session_state.grading = False
if "explanations" not in st.session_state:
    st.session_state.explanations = None

# Quiz生成
if st.button("quiz生成"):
    if not bullets.strip():
        st.error("授業資料を入力してください。")
    else:
        with st.spinner('Quizを生成中...'):
            quiz_prompt = (
                "あなたは与えられた授業資料（lecture notes）の内容だけを使い、4択クイズ（最大10問）を自動生成するAIです。\n"
                "【重要】\n"
                "- 問題・選択肢・解説はすべて日本語で作成してください。\n"
                "- 問題文・選択肢・解説は必ず授業資料の内容だけを根拠にしてください。一般知識や資料外の内容は使わないでください。\n"
                "- 各問題は4つの選択肢（A〜D）を用意し、必ず1つだけ正解を含めてください。\n"
                "- 出力は必ずPythonのリスト形式のJSON（[]で囲む）で返してください。\n"
                "- 1問あたりのJSON要素は question, choices, answer, explanation の4つだけです。\n"
                "- answerはA/B/C/Dのいずれか1文字で指定してください。\n"
                "- choicesは4つの文字列からなるリストです。\n"
                "- 出力例の形式を厳密に守ってください。\n"
                "- 出力は10問以内にしてください。\n"
                "- JSONの前後に説明文は付けず、JSONのみを返してください。\n"
                "\n"
                "【入力例】\n"
                "• フォワーダーとは、実運送人に対し利用運送事業者（混載業者、貨物取扱業者）である。\n"
                "• 混載業者は小口貨物を集め大口貨物にまとめる。\n"
                "• 国際複合一貫運送業者は1つの運送契約を荷主と締結し、複合運送船荷証券を発行する。\n"
                "• コンテナ船は定期船サービスを提供し、決められた航路とスケジュールで運航する。\n"
                "• バルク船は不定期船として運航され、穀物や鉱石などのばら積み貨物を輸送する。\n"
                "\n"
                "【出力例】\n"
                "[\n"
                "  {\n"
                "    \"question\": \"フォワーダーの主な役割は何ですか？\",\n"
                "    \"choices\": [\"小口貨物を集め大口貨物にまとめる\", \"運送契約を結ばない\", \"貨物を保管するだけ\", \"運賃を決めるだけ\"],\n"
                "    \"answer\": \"A\",\n"
                "    \"explanation\": \"混載業者（フォワーダー）は小口貨物を集め大口貨物にまとめる役割があります。\"\n"
                "  },\n"
                "  {\n"
                "    \"question\": \"コンテナ船の運航方式はどれですか？\",\n"
                "    \"choices\": [\"不定期船として運航\", \"定期船サービスを提供\", \"チャーター船のみ\", \"季節運航のみ\"],\n"
                "    \"answer\": \"B\",\n"
                "    \"explanation\": \"コンテナ船は定期船サービスを提供し、決められた航路とスケジュールで運航します。\"\n"
                "  }\n"
                "]\n"
                "\n"
                "【出力は必ず上記の形式で、[]で囲んだJSONリストとして返してください。】\n"
                f"\n授業資料:\n{bullets}"
            )
            
            try:
                model = genai.GenerativeModel("models/gemini-1.5-flash")
                response = model.generate_content(quiz_prompt)
                
                # レスポンステキストのクリーニング
                response_text = response.text.strip()
                
                # JSONの抽出（```json で囲まれている場合の対応）
                if "```json" in response_text:
                    start = response_text.find("```json") + 7
                    end = response_text.find("```", start)
                    response_text = response_text[start:end].strip()
                elif "```" in response_text:
                    start = response_text.find("```") + 3
                    end = response_text.find("```", start)
                    response_text = response_text[start:end].strip()
                
                # JSONのパース
                quiz_data = json.loads(response_text)
                
                # データの検証
                if not isinstance(quiz_data, list) or len(quiz_data) < 1:
                    raise ValueError("Invalid quiz data format")
                
                # 各問題の構造を検証
                valid_quiz_data = []
                for q in quiz_data:
                    if (isinstance(q, dict) and 
                        "question" in q and 
                        "choices" in q and 
                        "answer" in q and 
                        "explanation" in q and
                        isinstance(q["choices"], list) and
                        len(q["choices"]) == 4 and
                        q["answer"] in ["A", "B", "C", "D"]):
                        valid_quiz_data.append(q)
                
                if not valid_quiz_data:
                    raise ValueError("No valid quiz questions found")
                
                st.session_state.quiz_data = valid_quiz_data[:10]  # 最大10問
                st.session_state.user_answers = [None] * len(st.session_state.quiz_data)
                st.session_state.grading = False
                st.session_state.explanations = None
                st.success(f"Quiz（{len(st.session_state.quiz_data)}問）を生成しました！")
                
            except json.JSONDecodeError as e:
                st.error(f"JSONの解析に失敗しました: {e}")
                st.text("生成されたレスポンス:")
                st.text(response.text)
            except Exception as e:
                st.error(f"Quizの生成に失敗しました: {e}")

# Quiz表示・解答
if st.session_state.quiz_data:
    st.markdown("---")
    st.header(f"4択Quiz ({len(st.session_state.quiz_data)}問)")
    
    for idx, q in enumerate(st.session_state.quiz_data):
        st.markdown(f"**問題{idx+1}**: {q.get('question', '')}")
        
        choices = q.get('choices', ['', '', '', ''])
        if len(choices) >= 4:
            # 現在の選択を取得
            current_selection = None
            if st.session_state.user_answers[idx] is not None:
                current_selection = ord(st.session_state.user_answers[idx]) - 65
            
            selected = st.radio(
                f"選択肢 (問題{idx+1})",
                options=[0, 1, 2, 3],
                format_func=lambda x: f"{'ABCD'[x]}: {choices[x]}",
                key=f"quiz_{idx}",
                index=current_selection
            )
            
            # 選択を文字に変換して保存（selectedがNoneでないことを確認）
            if selected is not None:
                st.session_state.user_answers[idx] = chr(65 + selected)
        
        st.markdown("---")

    # 全問題に回答済みかチェック
    all_answered = all(answer is not None for answer in st.session_state.user_answers)
    
    if st.button("回答を提出・採点", disabled=not all_answered):
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
                "explanation": q.get("explanation", ""),
                "is_correct": user_ans == correct_ans
            })
        
        st.session_state.grading = True
        st.session_state.explanations = explanations
        
        score_percentage = (correct / len(st.session_state.quiz_data)) * 100
        st.success(f"採点完了！ {correct} / {len(st.session_state.quiz_data)} 問正解 ({score_percentage:.1f}%)")
    
    if not all_answered:
        unanswered = sum(1 for answer in st.session_state.user_answers if answer is None)
        st.warning(f"未回答の問題があります（残り{unanswered}問）")

# 採点・解説表示
if st.session_state.grading and st.session_state.explanations:
    st.markdown("---")
    st.header("採点結果・解説")
    
    for idx, q in enumerate(st.session_state.quiz_data):
        exp = st.session_state.explanations[idx]
        
        # 正解/不正解の表示
        if exp["is_correct"]:
            st.success(f"**問題{idx+1}**: {q.get('question', '')}")
        else:
            st.error(f"**問題{idx+1}**: {q.get('question', '')}")
        
        choices = q.get('choices', ['', '', '', ''])
        st.write(f"**あなたの回答**: {exp['user']} - {choices[ord(exp['user'])-65] if exp['user'] and len(choices) > ord(exp['user'])-65 else ''}")
        st.write(f"**正解**: {exp['correct']} - {choices[ord(exp['correct'])-65] if exp['correct'] and len(choices) > ord(exp['correct'])-65 else ''}")
        
        st.info(f"**解説**: {exp['explanation']}")
        st.markdown("---")

# リセットボタン
if st.session_state.quiz_data:
    if st.button("新しいQuizを作成"):
        st.session_state.quiz_data = None
        st.session_state.user_answers = []
        st.session_state.grading = False
        st.session_state.explanations = None
        st.rerun()