import streamlit as st
import pandas as pd
import urllib.parse

# 1. ページ設定（※必ず一番最初に書く！）
st.set_page_config(page_title="1週間の計画アプリ", layout="wide")

# ==========================================
# 🔐 ログイン機能
# ==========================================
# パスワードを「0126」に設定しました
MY_PASSWORD = "0126"

def check_password():
    """パスワードが正しいか判定する関数"""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.title("🔒 ログイン")
        # type="password" にすると入力した文字が黒丸(●●●)で隠れます
        password_input = st.text_input("パスワードを入力してください", type="password")
        
        if st.button("ログイン"):
            if password_input == MY_PASSWORD:
                st.session_state.logged_in = True
                st.rerun() 
            else:
                st.error("パスワードが違います！")
        return False
    
    return True

# ==========================================
# 📅 カレンダー連携用の関数
# ==========================================
def make_gcal_url(task_name):
    """タスク名からGoogleカレンダー登録用のURLを作成する"""
    base_url = "https://calendar.google.com/calendar/render?action=TEMPLATE"
    title = urllib.parse.quote(task_name)
    return f"{base_url}&text={title}"

# ==========================================
# 🚀 メインアプリ（ログイン成功時のみここから下が実行される）
# ==========================================
if check_password():
    
    # --- データの初期化 ---
    if 'weekly_goal' not in st.session_state:
        st.session_state.weekly_goal = ""
    if 'tasks' not in st.session_state:
        st.session_state.tasks = []  
    if 'wants' not in st.session_state:
        st.session_state.wants = []  

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
        goal = st.text_area("今週の目標", value=st.session_state.weekly_goal)
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
                st.session_state.tasks[i]["goal_priority"] = goal_p
                st.session_state.tasks[i]["general_priority"] = gen_p
                st.divider()
            st.success("自動的に保存されています！次のステップへ進みましょう。")

    # --- ステップ4: やりたいこと(Want to)を洗い出す ---
    elif step == "4. やりたいこと(Want to)を洗い出す":
        st.title("✨ ステップ4: やりたいこと(Want to)の整理")
        
        with st.form("add_want_form", clear_on_submit=True):
            new_want = st.text_input("やりたいことを入力")
            submitted = st.form_submit_button("リストに追加")
            if submitted and new_want:
                st.session_state.wants.append({
                    "id": len(st.session_state.wants),
                    "name": new_want,
                    "type": "Want to",
                    "day": "未定"
                })
                st.rerun()

        st.subheader("現在のやり
