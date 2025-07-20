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
        "あなたは与えられた授業資料から4択問題を生成し、ユーザの解答を採点し、正解を解説するAIです。以下に例を示すのでこのようにしてください\n"
        "## 使用例\n"
        "**入力（箇条書き）：**\n"
        "- 8章 1対多マッチング\n"
        " 研修医と病院の問題(https://www.jrmp.jp/)\n"
        " 新入社員と部署，労働者と会社，学生と学校，学生とゼミ\n"
        " 教科書では人員と部門とよんでいる\n"
        " 部門にはキャパシティ（受け入れ可能な枠）がある（3人まで受け入れ可能など）\n"
        " マッチングの記述： 部門wについてwは人員の集合の部分集合\n"
        "w  1, 2,, M。異なる部門w, wについて，w  w 。（人員は一つの部門にしか所属できない）\n"
        " 感応選好，許容可能，個人合理性，安定性\n"
        "1 : 8 9  8 : 3 2 6 4 5  7 1\n"
        "2 : 9 8  9 : 3 1 6 5 7 4  2\n"
        "3 : 8  9 c8  2, c9  2\n"
        "4 : 8  9\n"
        "5 : 8 9 \n"
        "6 : 9 8 \n"
        "7 :  9 8\n"
        " 人員と部門のペアm, wがマッチングをブロックするとは以下の（１），（２）のどちらか（あるいは両方）が成り立つ場合をいう\n"
        "- (1) w m m, m w かつ|w|  cw\n"
        "* mがwに入りたくて，wもmを取りたくて，さらにキャパシティーもいっぱいでない\n"
        "- (2) w m mかつm w mで，あるようなm  wが存在\n"
        "* mがwに入りたくて，wがより好まないようなmがmに割り当てられている。\n"
        " マッチングが安定であるとは，が個人合理的であり，どの人員と部門のペアからもブロックされない 場合をいう。\n"
        "人員側DAアルゴリズム\n"
        " 現在無所属の人員は，許容可能でかつ今まで断られたことのない部門に出願する。\n"
        "部門は，出願してきた人員が許容可能でなければ断る。出願してきた許容可能な人員を，キャパシティーに余裕があるかぎりキープするが，キャパシティーに余裕が無い時は，キャパシティーいっぱいまで好きな順にキープし，他は断る。全員が，キープされるか出願する部門が無くなればアルゴリズム終了。\n"
        " 人員側DAアルゴリズムは安定性を満たす\n"
        " 人員側DAアルゴリズムは人員側耐戦略性を満たす\n"
        "- ただし部門側耐戦略性は満たさない\n"
        "ボストン方式\n"
        " 人員側DAアルゴリズムに近いが少し違う\n"
        " 部門側は一旦受け入れたら，それはキープではなく，最終決定になる\n"
        " 一旦受け入れた後にさらによい人員が来ても断らなければならない\n"
        " ボストン方式は安定性を満たさない\n"
        " ボストン方式は人員側耐戦略性を満たさない\n"
        "部門側DAアルゴリズム\n"
        " 部門側DAアルゴリズム： 部門側が人員にオファーを出す。人員側は，許容可能なオファーをキープするが，２つ以上オファーがきたら１つ以外すべて断る。部門側は，キープされているオファーの数がキャパシティーと同数になるか，断られていない許容可能な人員がいなくなるまで，オファーを出し続ける。その際，部門は，断られていない中で，最も好む人員にオファーする。すべての部門にオファーする人員がいなくなったらアルゴリズムは終了し，人員はその時点でオファーをキープしている部門に行く。\n"
        " 部門側DAアルゴリズムは安定性を満たす\n"
        " 部門側DAアルゴリズムは部門側耐戦略性を満たさない。\n"
        "人員側DAアルゴリズム（再）\n"
        " 人員側DAアルゴリズムによって導かれるマッチングを考える。どこかの部門のキャパシティーが増えると，すべての人員が同じかよりよい部門に行くことができる。新しい人員が入ってくると，既存のすべての人員が同じかより悪い部門に行くことになる。\n"
        "- 辞退がでて空きが出たりキャパシティーが増えたりした場合，人員側DAアルゴリズムでもう一度決め直したとしても，人員側からはクレームが無い。\n"
        "- 新しい人員が入ってきて，人員側DAアルゴリズムでもう一度決め直すと，人員側からはクレームがあるかも。\n"
        "例１： 教科書（p.143）の例でc8  3になったとして，人員側DAアルゴリズムを再度行う。\n"
        "例２： 教科書（p.143）の例で，新しい人員 x : 9 8  があらわれ，各部門は誰よりもxをとりたいとする。\n"
        "外部性の問題\n"
        " DAアルゴリズムがうまくいかなくなる場合（外部性の問題）\n"
        "- ある人員が別の人員と同じ部門に行きたいと思っていた場合（matching with couple）\n"
        "- ある人員が別の人員とは異なる部門に行きたいと思っていた場合\n"
        "- 部門側がある2人の人員を同時にとりたいが，1人だけならどちらもいらないと考えている場合\n"
        " カップル用NRMPアルゴリズム 1998年にアメリカで採用され問題を解決した\n"
        "- ハーリンジャ―著 2020 『マーケットデザイン：オークションとマッチングの理論・実践』 中央経済社 （第１０章）\n"
        "マッチングシステムと安定性\n"
        " （集権的な）マッチングシステムがない労働市場\n"
        " 学生と企業の就活市場\n"
        " 全体的に時期が前倒しになりがち（青田買い）\n"
        " １９８０年代のアメリカの医学生と病院のマッチング\n"
        " 学生の意欲の低下\n"
        " （集権的な）マッチングシステムの導入が重要\n"
        " 安定なマッチングを導かないマッチングルールの問題点\n"
        " イギリスの研修医マッチング市場\n"
        " 地域ごとにマッチングルールが異なる\n"
        " 安定的なマッチングを導くルールの地域はルールが続いた\n"
        "- エジンバラ，カーディフ\n"
        " 安定的なマッチングを導かないルールの地域は６地域中，２地域しかルールが続いていない\n"
        "- ロンドンなど\n"
        " なぜか？\n"
        " 医学生と病院でブロックされるようなマッチングとなるかも\n"
        " 医学生・病院はマッチングルールを介さずに相手を下がるようになる\n"
        " 青田買いが発生してしまう 集権的なマッチングシステムが崩壊\n"
        " ハーリンジャー（２０２０）の第１０章\n"
        "１対１マッチングとの対応関係\n"
        " 人員を男性だと考える\n"
        " 各部門のキャパシティー人の女性を考える\n"
        " 部門wから派生した女性の選好はwと同じ\n"
        " mのwから派生した女性に対する選好\n"
        "- より好む部門から派生した女性を好む\n"
        "- 同じ部門から派生した女性では，番号が少ない方をより好む。\n"
        "1 : 6  5 5 : 1 2 3 4 \n"
        "2 : 6 5  6 : 2 3 1 4 \n"
        "3 : 6 5 \n"
        "4 : 5  6\n"
        " この場合の１対１マッチングの安定マッチングを求める\n"
        " その安定マッチングでwから派生した女性とマッチした人員はwに所属すると１対多マッチングの安定マッチングが求まる\n"
        " １対多マッチングの安定マッチング求める\n"
        " wに所属する人員をwから派生した女性とマッチさせると，１対１マッチングの安定マッチングになる\n"
        " ２つの問題は同じ問題となる\n"
        "僻地病院定理\n"
        " 僻地病院定理： ある安定マッチングにおいて，ある部門に所属する人員の数は，別の安定マッチングを考えたとしても変わらない\n"
        " ある安定マッチングにおいて，人が集まらない（定員が埋まらない）病院には別の安定マッチングを考えたとしても人が集まらない（定員が埋まらない）\n"
        "- １対多マッチングをうえの方法で，1対１マッチングにする。1対１マッチングにおいて，あるマッチングでペアになれなかった人は別の安定マッチングでもペアになれない僻地病院定理\n"
        " 実際の研修医マッチング(JRMP)でも地方の病院に人が集まらないという問題が生じた地方が人手不足にならないマッチングの決め方\n"
        " 鎌田他 （２０１１）「マッチング理論とその応用： 研修医の「地域偏在」とその解決策」『医療経済研究』 23(1), 5-20\n"
        " Kamada, Y., Kojima, F. 2015. Efficient Matching under Distributional Constraints: Theory and Application American Economic Review 105(1), (pp. 67–99)\n"
        "部門側の選好の一般化\n"
        " 今までの部門側の選好はキャパシティーが埋まらない限り，受け入れ可能な人は変わらず受け入れたい\n"
        " 1人しか取れないならば人員mでも取りたいが，3人の人員が入ってくれるならば，mをとりたくないといった選好も考えられる。\n"
        " このような選好を含む一般的な場合でもDAアルゴリズムをつかって安定なマッチングを導くことができる\n"
        " 具体的には部門の選好が代替（だいたい）性を満たすならばDAアルゴリズムをつかって安定なマッチングを導くことができる\n"
        " 部門5が人員1,2,3の中から選ぶことができるときに，人員1が選ばれるとする。その場合，部門5が人員1,2（あるいは1,3）の中から選ぶことができるときにも人員1が選ばれる。\n"
        " 人が少ないときの方が人員は必要（人は別の人の代わりとなって働くことができる）\n"
        " 一般的な代替性の定義： m  S  S  1,, Mとする。部門wによって,人員の部分集合Sの中からmが選ばれるならば，Sの中からでも必ずmが選ばれるとき，部門wの選好は代替性を満たすという。\n"
        " 人員側DAのときの部門側の行動\n"
        " 部門側は「出願してきた人員＋キープしている人員」の中で不要な人員を断る\n"
        " 代替性を満たすとすると，キープしている人員は後半になるほど大きくなる\n"
        " 前に一度断った人をやはり受け入れたいということがない安定性\n"
        "\n**出力（4択選択機能付き）：**\n本日は天候に恵まれ、清々しい晴天の下で外出する機会を得ることができた。このような好天を活用し、近所の公園へ散歩に出かけることにした。公園に到着すると、季節の花々が美しく咲き誇っており、自然の美しさを堪能することができた。この散歩を通じて、日頃の疲れやストレスから解放され、心身ともにリフレッシュすることができた。\n"
        "\n**入力(4択から選択して回答を提出ボタンを押す)**\n" 
        # ...existing code...
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