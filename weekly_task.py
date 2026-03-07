import streamlit as st
import pandas as pd

# ページ設定
st.set_page_config(page_title="1週間の計画アプリ", layout="wide")

# --- データの初期化（無料でセッションに保存） ---
if 'weekly_goal' not in st.session_state:
    st.session_state.weekly_goal = ""
if 'tasks' not in st.session_state:
    st.session_state.tasks = []  # Have to のリスト
if 'wants' not in st.session_state:
    st.session_state.wants = []  # Want to のリスト

# --- サイドバーでステップを管理 ---
st.sidebar.title("🧭 計画のステップ")
st.sidebar.info("上から順番に進めていくだけで、1週間の計画が完成します！")
step = st.sidebar.radio(
    "現在のステップ",
    [
        "1. 1週間の目標を決める",
        "2. タスク(Have to)を洗い出す",
        "3. タスクの優先順位を決める",
        "4. やりたいこと(Want to)を洗い出す",
        "5. 全体の整理・確認",
        "6. 1週間のスケジュールに割り当てる"
    ]
)

# --- ステップ1: 1週間の目標を決める ---
if step == "1. 1週間の目標を決める":
    st.title("🎯 ステップ1: 1週間の目標")
    st.write("まずは、今週をどんな1週間にしたいか（何を達成したいか）を決めましょう。")
    goal = st.text_area("今週の目標（例：〇〇のプロジェクトを終わらせる、ゆっくり休む、など）", value=st.session_state.weekly_goal)
    if st.button("目標を保存"):
        st.session_state.weekly_goal = goal
        st.success("目標を保存しました！左のメニューから次のステップに進んでください。")

# --- ステップ2: タスク(Have to)を洗い出す ---
elif step == "2. タスク(Have to)を洗い出す":
    st.title("📝 ステップ2: 抱えているタスク(Have to)の整理")
    st.write("今週「やらなければならないこと」を思いつく限り書き出しましょう。")
    
    with st.form("add_task_form", clear_on_submit=True):
        new_task = st.text_input("タスクを入力")
        submitted = st.form_submit_button("リストに追加")
        if submitted and new_task:
            # タスクのデータ構造
            st.session_state.tasks.append({
                "id": len(st.session_state.tasks),
                "name": new_task,
                "goal_priority": "未設定",
                "general_priority": "未設定",
                "day": "未定"
            })
            st.rerun()

    st.subheader("現在のタスク一覧")
    for t in st.session_state.tasks:
        st.write(f"・ {t['name']}")

# --- ステップ3: タスクの優先順位を決める ---
elif step == "3. タスクの優先順位を決める":
    st.title("⚖️ ステップ3: 優先順位づけ")
    if st.session_state.weekly_goal:
        st.info(f"💡 今週の目標: {st.session_state.weekly_goal}")
    
    st.write("ステップ2で出したタスクに優先順位をつけます。")
    
    if not st.session_state.tasks:
        st.warning("先にステップ2でタスクを追加してください。")
    else:
        for i, task in enumerate(st.session_state.tasks):
            st.markdown(f"### 📌 {task['name']}")
            col1, col2 = st.columns(2)
            with col1:
                goal_p = st.selectbox(
                    "今週の目標に沿った優先度", 
                    ["高 (目標達成に必須)", "中 (できればやる)", "低 (目標とは無関係)"], 
                    key=f"goal_{i}",
                    index=["高 (目標達成に必須)", "中 (できればやる)", "低 (目標とは無関係)", "未設定"].index(task.get("goal_priority", "未設定")) if task.get("goal_priority") in ["高 (目標達成に必須)", "中 (できればやる)", "低 (目標とは無関係)"] else 0
                )
            with col2:
                gen_p = st.selectbox(
                    "目標とは関係ない絶対的な優先度(期限など)", 
                    ["高 (絶対今週やる)", "中 (なるべく今週)", "低 (来週以降でも可)"], 
                    key=f"gen_{i}",
                    index=["高 (絶対今週やる)", "中 (なるべく今週)", "低 (来週以降でも可)", "未設定"].index(task.get("general_priority", "未設定")) if task.get("general_priority") in ["高 (絶対今週やる)", "中 (なるべく今週)", "低 (来週以降でも可)"] else 0
                )
            # 値を更新
            st.session_state.tasks[i]["goal_priority"] = goal_p
            st.session_state.tasks[i]["general_priority"] = gen_p
            st.divider()
        st.success("自動的に保存されています！次のステップへ進みましょう。")

# --- ステップ4: やりたいこと(Want to)を洗い出す ---
elif step == "4. やりたいこと(Want to)を洗い出す":
    st.title("✨ ステップ4: やりたいこと(Want to)の整理")
    st.write("「やらなきゃいけないこと」だけでなく、今週「やりたいこと・楽しみたいこと」も書き出しましょう！")
    
    with st.form("add_want_form", clear_on_submit=True):
        new_want = st.text_input("やりたいことを入力（例：映画を見る、サウナに行く）")
        submitted = st.form_submit_button("リストに追加")
        if submitted and new_want:
            st.session_state.wants.append({
                "id": len(st.session_state.wants),
                "name": new_want,
                "type": "Want to",
                "day": "未定"
            })
            st.rerun()

    st.subheader("現在のやりたいこと一覧")
    for w in st.session_state.wants:
        st.write(f"・ {w['name']}")

# --- ステップ5: 全体の整理・確認 ---
elif step == "5. 全体の整理・確認":
    st.title("📊 ステップ5: タスクとやりたいことの全体像")
    st.write("ここまでに出したすべての項目を確認します。")
    
    # テーブル表示のためにデータを整形
    all_items = []
    for t in st.session_state.tasks:
        all_items.append({
            "種類": "🔴 Have to (タスク)",
            "内容": t["name"],
            "目標優先度": t["goal_priority"],
            "絶対優先度": t["general_priority"]
        })
    for w in st.session_state.wants:
        all_items.append({
            "種類": "🔵 Want to (やりたい事)",
            "内容": w["name"],
            "目標優先度": "-",
            "絶対優先度": "-"
        })
    
    if all_items:
        df = pd.DataFrame(all_items)
        st.dataframe(df, use_container_width=True)
    else:
        st.write("まだアイテムがありません。")

# --- ステップ6: 1週間のスケジュールに割り当てる ---
elif step == "6. 1週間のスケジュールに割り当てる":
    st.title("📅 ステップ6: 1週間に割り当てる")
    st.write("最後に、それぞれのタスク・やりたいことを何曜日にやるか決めましょう！")
    
    days_of_week = ["未定", "月", "火", "水", "木", "金", "土", "日"]
    
    st.subheader("🔴 Have to (タスク)")
    for i, task in enumerate(st.session_state.tasks):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**{task['name']}** (目標: {task['goal_priority'][:1]} / 絶対: {task['general_priority'][:1]})")
        with col2:
            st.session_state.tasks[i]["day"] = st.selectbox("曜日", days_of_week, key=f"task_day_{i}", index=days_of_week.index(task.get("day", "未定")))
            
    st.subheader("🔵 Want to (やりたい事)")
    for i, want in enumerate(st.session_state.wants):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**{want['name']}**")
        with col2:
            st.session_state.wants[i]["day"] = st.selectbox("曜日", days_of_week, key=f"want_day_{i}", index=days_of_week.index(want.get("day", "未定")))

    st.divider()
    st.title("🎉 今週の完成スケジュール")
    
    # 曜日ごとに表示
    columns = st.columns(7)
    for idx, day in enumerate(days_of_week[1:]): # 未定を除く月〜日
        with columns[idx]:
            st.markdown(f"### {day}")
            # タスク
            day_tasks = [t for t in st.session_state.tasks if t["day"] == day]
            for t in day_tasks:
                st.markdown(f"🔴 {t['name']}")
            # やりたいこと
            day_wants = [w for w in st.session_state.wants if w["day"] == day]
            for w in day_wants:
                st.markdown(f"🔵 {w['name']}")
import urllib.parse

# タスク名からGoogleカレンダー用のURLを作る関数
def make_gcal_url(task_name):
    base_url = "https://calendar.google.com/calendar/render?action=TEMPLATE"
    title = urllib.parse.quote(task_name)
    return f"{base_url}&text={title}"

# Streamlitでの表示例
task_name = "プログラミングの勉強"
url = make_gcal_url(task_name)
st.markdown(f"[📅 カレンダーに『{task_name}』を追加する]({url})")