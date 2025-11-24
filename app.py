import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_gsheets import GSheetsConnection

# --- 1. 設定 ---
st.set_page_config(page_title="就活Quest", layout="wide")

# --- 2. スプレッドシート接続（ここが連携の入り口です） ---
# ここでは「gsheets」という名前で接続を作ります。
# 実際のURLやパスワードは secrets.toml から自動で読み込まれます。
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 3. デザイン（CSS） ---
st.markdown("""
<style>
    .stApp {
        background-color: #000000;
        max-width: 600px;
        margin: 0 auto;
    }
    .rank-card {
        background-color: #222222;
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 4px 15px rgba(255,255,255,0.1);
        text-align: center;
        margin-bottom: 20px;
        border: 2px solid #e0e0e0;
    }
    .rank-title {
        font-size: 1.2rem;
        color: #ffffff;
        margin-bottom: 5px;
    }
    .rank-name {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0;
        color: #ffffff;
    }
    .total-point {
        font-size: 1.5rem;
        font-weight: bold;
        color: #ffffff;
        margin-top: 10px;
    }
    .stNumberInput {
        max-width: 150px;
        margin-left: auto;
    }
    header {
        visibility: hidden;
        height: 0px;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. データ管理（セッション） ---
if 'total_score' not in st.session_state:
    st.session_state['total_score'] = 0
if 'input_data' not in st.session_state:
    st.session_state['input_data'] = {}
for action in ["面接（本番）", "ES提出", "ケース問題", "OB/OG訪問", "説明会参加", "Webテスト", "業界研究", "自己分析"]:
    if action not in st.session_state:
        st.session_state[action] = 0

# ポイント定義
ACTIONS = {
    "面接（本番）": 30,
    "ES提出": 20,
    "ケース問題": 20,
    "OB/OG訪問": 15,
    "説明会参加": 10,
    "Webテスト": 10,
    "業界研究": 5,
    "自己分析": 5
}

# --- 5. 関数定義 ---

def get_rank_info(score):
    if score >= 200:
        return "DIAMOND", "💎", "#b9f2ff"
    elif score >= 150:
        return "PLATINUM", "🏆", "#e5e4e2"
    elif score >= 100:
        return "GOLD", "🥇", "#ffd700"
    elif score >= 50:
        return "SILVER", "🥈", "#c0c0c0"
    else:
        return "BRONZE", "🥉", "#cd7f32"

def load_ranking():
    """シートからランキングデータを読み込む"""
    try:
        # ttl=0 でキャッシュを無効化し、常に最新を取得
        df = conn.read(ttl=0)
        return df
    except Exception:
        # エラー時や空のときは空のデータフレームを返す
        return pd.DataFrame()

def save_score(name, score):
    """名前とスコアをシートに保存する"""
    try:
        df = load_ranking()
        # 新しい行を作成
        new_data = pd.DataFrame([{"名前": name, "スコア": score}])
        # 既存データと合体
        updated_df = pd.concat([df, new_data], ignore_index=True)
        # 更新を実行
        conn.update(data=updated_df)
        return True
    except Exception as e:
        st.error(f"保存エラー: {e}")
        return False

# --- 6. 画面ごとの表示内容 ---

def render_point_input_screen():
    st.header("📝 今週の行動記録")
    st.caption("回数を入力してください")
    
    total_score = 0
    input_data = {}
    
    for action, point in ACTIONS.items():
        col_label, col_input = st.columns([0.6, 0.4])
        with col_label:
            st.write(f"{action} ({point}pt/回)")
        with col_input:
            count = st.number_input("", 
                                    min_value=0, max_value=100, 
                                    value=st.session_state[action], 
                                    step=1, 
                                    key=f"input_{action}",
                                    label_visibility="collapsed")
            st.session_state[action] = count
            
        subtotal = count * point
        total_score += subtotal
        if subtotal > 0:
            input_data[action] = subtotal
            
    st.session_state['total_score'] = total_score
    st.session_state['input_data'] = input_data
    st.subheader(f"合計ポイント: {total_score} pt")

def render_rank_display_screen():
    st.header("👑 My Status")
    current_score = st.session_state.get('total_score', 0)
    current_data = st.session_state.get('input_data', {})
    rank_name, icon, color = get_rank_info(current_score)
    
    st.markdown(f"""
    <div class="rank-card">
        <div class="rank-title">CURRENT RANK</div>
        <div class="rank-name" style="color: {color};">
            {icon} {rank_name}
        </div>
        <div class="total-point">
            {current_score} <span style="font-size: 1rem;">pt</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("📊 ポイント内訳")
    if current_score > 0:
        df = pd.DataFrame(list(current_data.items()), columns=["行動", "ポイント"])
        fig = px.pie(df, values='ポイント', names='行動', hole=0.5)
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=300)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("まだ記録がありません。")

def render_national_rank_screen():
    st.header("🏆 国内ランキング")
    my_score = st.session_state.get('total_score', 0)

    # 登録フォーム
    st.markdown("##### 🏅 ランキングに登録")
    if my_score == 0:
        st.warning("スコアが0なので登録できません。")
    else:
        with st.form("ranking_form"):
            st.write(f"あなたのスコア: **{my_score} pt**")
            name = st.text_input("ニックネーム")
            submitted = st.form_submit_button("登録する")

            if submitted:
                if not name:
                    st.error("名前を入力してください")
                else:
                    success = save_score(name, my_score)
                    if success:
                        st.success("登録しました！")

    # ランキング表
    st.markdown("---")
    st.markdown("##### 📊 トップランカー")
    df_ranking = load_ranking()

    if not df_ranking.empty:
        if 'スコア' in df_ranking.columns:
            # 数値変換とソート
            df_ranking['スコア'] = pd.to_numeric(df_ranking['スコア'], errors='coerce')
            df_ranking = df_ranking.sort_values(by="スコア", ascending=False)
            df_ranking = df_ranking.reset_index(drop=True)
            df_ranking.index = df_ranking.index + 1
            st.dataframe(df_ranking, use_container_width=True)
    else:
        st.info("まだデータがありません。")

# --- 7. メイン処理（タブ切り替え） ---

tab_titles = ["📝 ポイント取得", "👑 自分のランク", "🏆 国内ランク"]
if 'tab_index' not in st.session_state:
    st.session_state['tab_index'] = 0

cols = st.columns(len(tab_titles))
for i, title in enumerate(tab_titles):
    if cols[i].button(title, use_container_width=True, type="primary" if st.session_state['tab_index'] == i else "secondary"):
        st.session_state['tab_index'] = i

st.markdown("---") 

if st.session_state['tab_index'] == 0:
    render_point_input_screen()
elif st.session_state['tab_index'] == 1:
    render_rank_display_screen()
elif st.session_state['tab_index'] == 2:
    render_national_rank_screen()