import streamlit as st
import google.generativeai as genai

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

st.title("箇条書き→レポート自動変換")

bullets = st.text_area("箇条書きの文章を入力してください", height=200)
if st.button("レポート生成"):
    prompt = f"以下の箇条書きを、まとまったレポート形式の日本語文章に変換してください。\n\n{bullets}"
    model = genai.GenerativeModel("models/gemini-1.5-flash")  # ここに使いたいモデル名
    response = model.generate_content(prompt)
    st.markdown("### レポート結果")
    st.write(response.text)