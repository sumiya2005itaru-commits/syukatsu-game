import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_gsheets import GSheetsConnection
import random # ガチャ用に乱数機能を追加

# --- 1. 設定 ---
st.set_page_config(page_title="就活Quest", layout="wide")

# --- 2. スプレッドシート接続 ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 3. デザイン（CSS） ---
# スマホ見やすさ重視のCSS
st.markdown("""
<style>
    .stApp {
        background-color: #000000;
        max-width: 600px;
        margin: 0 auto;
    }
    .rank-card {
        background-color: #999999;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 10px rgba(255, 255, 255, 0.1);
        text-align: center;
        margin-bottom: 20px;
        border: 1px solid #333;
    }
    .rank-title {
        font-size: 1.0rem;
        color: #999999;
        letter-spacing: 2px;
    }
    .rank-name {
        font-size: 2.2rem;
        font-weight: bold;
        margin: 10px 0;
        text-shadow: 0 0 10px rgba(255,255,255,0.3);
    }
    .rank-sub {
        font-size: 1.0rem;
        color: #999999;
        margin-bottom: 10px;
        font-weight: bold;
    }
    .total-point {
        font-size: 1.8rem;
        font-weight: bold;
        color: #999999;
    }
    .gacha-box {
        background-color: #999999;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        border: 2px dashed #555;
        margin-top: 20px;
    }
    /* ヘッダー削除 */
    header {visibility: hidden; height: 0px;}
</style>
""", unsafe_allow_html=True)

# --- 4. データ管理（セッション） ---
if 'total_score' not in st.session_state:
    st.session_state['total_score'] = 0
if 'input_data' not in st.session_state:
    st.session_state['input_data'] = {}
if 'gacha_history' not in st.session_state:
    st.session_state['gacha_history'] = []

# アクション定義（メンタルケア項目を追加！）
ACTIONS = {
    "面接（本番）": 30,
    "お祈りメール受信": 50,  # 🆕 失敗を資産に変える！
    "ES提出": 20,
    "ケース問題": 20,
    "OB/OG訪問": 15,
    "説明会参加": 10,
    "Webテスト": 10,
    "業界研究": 5,
    "自己分析": 5,
    "完全休息日": 10      # 🆕 休むのも仕事！
}

# --- 5. 関数定義 ---

def get_rank_info(score):
    # ランクと「称号」を返す
    if score >= 500:
        return "LEGEND", "👑 就活王", "🌈", "#ff00ff"
    elif score >= 300:
        return "DIAMOND", "⚔️ 内定ハンター", "💎", "#b9f2ff"
    elif score >= 150:
        return "PLATINUM", "🛡️ 歴戦の猛者", "🏆", "#e5e4e2"
    elif score >= 100:
        return "GOLD", "🗡️ 上級就活生", "🥇", "#ffd700"
    elif score >= 50:
        return "SILVER", "🪵 見習い勇者", "🥈", "#c0c0c0"
    else:
        return "BRONZE", "🥚 旅立ちの時", "🥉", "#cd7f32"

def load_ranking():
    try:
        df = conn.read(ttl=0)
        return df
    except Exception:
        return pd.DataFrame()

def save_score(name, score):
    try:
        df = load_ranking()
        new_data = pd.DataFrame([{"名前": name, "スコア": score}])
        updated_df = pd.concat([df, new_data], ignore_index=True)
        conn.update(data=updated_df)
        return True
    except Exception as e:
        st.error(f"保存エラー: {e}")
        return False

# --- 6. 画面ごとの表示内容 ---

def render_point_input_screen():
    st.header("📝 クエストボード")
    st.info("💡 失敗しても大丈夫。「お祈りメール」は高得点です！")
    
    total_score = 0
    input_data = {}
    
    for action, point in ACTIONS.items():
        # スマホで見やすいよう、カード風に表示
        with st.container():
            col1, col2 = st.columns([0.7, 0.3])
            with col1:
                st.write(f"**{action}**")
                st.caption(f"報酬: {point} pt")
            with col2:
                count = st.number_input(f"{action}", 
                                        min_value=0, max_value=100, 
                                        value=st.session_state.get(action, 0), 
                                        step=1, 
                                        key=f"input_{action}",
                                        label_visibility="collapsed")
                st.session_state[action] = count
            st.markdown("---") # 区切り線
            
        subtotal = count * point
        total_score += subtotal
        if subtotal > 0:
            input_data[action] = subtotal
            
    st.session_state['total_score'] = total_score
    st.session_state['input_data'] = input_data
    
    # 固定フッター風の合計表示
    st.markdown(f"""
    <div style="position:fixed; bottom:0; left:0; width:100%; background-color:#333; padding:10px; text-align:center; z-index:999;">
        <span style="color:white; font-weight:bold;">現在の獲得経験値: {total_score} pt</span>
    </div>
    <div style="height:50px;"></div> """, unsafe_allow_html=True)

def render_rank_display_screen():
    st.header("👑 ステータス")
    
    current_score = st.session_state.get('total_score', 0)
    current_data = st.session_state.get('input_data', {})
    rank_eng, rank_title, icon, color = get_rank_info(current_score)
    
    # ランクカード表示
    st.markdown(f"""
    <div class="rank-card">
        <div class="rank-title">CURRENT RANK</div>
        <div class="rank-name" style="color: {color};">{icon} {rank_eng}</div>
        <div class="rank-sub">{rank_title}</div>
        <div class="total-point">{current_score} <span style="font-size:1rem">pt</span></div>
    </div>
    """, unsafe_allow_html=True)

    # 次のランクまで
    next_goal = 0
    if current_score < 50: next_goal = 50
    elif current_score < 100: next_goal = 100
    elif current_score < 150: next_goal = 150
    elif current_score < 300: next_goal = 300
    elif current_score < 500: next_goal = 500
    
    if next_goal > 0:
        needed = next_goal - current_score
        st.progress(min(current_score / next_goal, 1.0))
        st.caption(f"次のランクまであと **{needed} pt**")

    # 円グラフ
    st.subheader("📊 経験値の内訳")
    if current_score > 0:
        df = pd.DataFrame(list(current_data.items()), columns=["行動", "ポイント"])
        # 黒背景に映える色セット
        fig = px.pie(df, values='ポイント', names='行動', hole=0.5, color_discrete_sequence=px.colors.qualitative.Pastel)
        fig.update_layout(
            margin=dict(t=0, b=0, l=0, r=0), 
            height=300,
            paper_bgcolor='rgba(0,0,0,0)', # 背景透明
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color="white")
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("まだ記録がありません。クエストボードで入力を！")

def render_gacha_screen():
    """新機能：就活ガチャ"""
    st.header("🔮 就活ガチャ")
    st.caption("疲れた時は運試し。何かいいアイテムが出るかも？")
    
    st.markdown("""
    <div class="gacha-box">
        <h3>1回 100pt (※今は無料CP中)</h3>
        <p>SSRアイテムをゲットしよう！</p>
    </div>
    """, unsafe_allow_html=True)
    
    # ガチャの中身リスト
    items = [
        {"レア": "N", "名": "ただの消しゴム", "言": "よく消える。過去のミスも消したい。"},
        {"レア": "N", "名": "栄養ドリンク", "言": "元気の前借り。ご利用は計画的に。"},
        {"レア": "R", "名": "ラッキーネクタイ(赤)", "言": "勝負運アップ！ここぞという時に。"},
        {"レア": "R", "名": "Webカメラのライト", "言": "顔色が良く見える。面接官の印象UP。"},
        {"レア": "SR", "名": "内定者のエントリーシート", "言": "伝説の遺物。読むだけで偏差値が上がる気がする。"},
        {"レア": "SR", "名": "圧迫面接ガード", "言": "心の防御力が上昇するお守り。"},
        {"レア": "SSR", "名": "最終面接フリーパス", "言": "※そんなものはない。実力で掴め！"},
        {"レア": "SSR", "名": "採用通知", "言": "いつか必ず手に入る。信じて進め！"}
    ]
    
    if st.button("ガチャを回す！", type="primary", use_container_width=True):
        result = random.choice(items)
        st.balloons() # 風船のエフェクト
        
        # 結果表示
        color = "#ffffff"
        if result["レア"] == "SR": color = "#ffd700"
        if result["レア"] == "SSR": color = "#ff00ff"
        
        st.markdown(f"""
        <div style="text-align:center; padding:20px; border:2px solid {color}; border-radius:10px; margin-top:10px;">
            <h2 style="color:{color};">[{result['レア']}] {result['名']}</h2>
            <p style="font-size:1.2rem;">{result['言']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 履歴に追加
        st.session_state['gacha_history'].insert(0, result)

    # 履歴表示
    if st.session_state['gacha_history']:
        st.markdown("---")
        st.caption("獲得履歴")
        for item in st.session_state['gacha_history'][:5]: # 最新5件
            st.write(f"・[{item['レア']}] {item['名']}")

def render_national_rank_screen():
    st.header("🏆 全国ランキング")
    my_score = st.session_state.get('total_score', 0)

    # 登録フォーム
    if my_score > 0:
        with st.form("ranking_form"):
            st.write(f"現在のスコア: **{my_score} pt**")
            name = st.text_input("エントリーネーム")
            submitted = st.form_submit_button("ランキングに登録")
            if submitted and name:
                save_score(name, my_score)
                st.success("登録完了！")
    else:
        st.info("ポイントを獲得すると参加できます。")

    # ランキング表
    st.markdown("---")
    df_ranking = load_ranking()
    if not df_ranking.empty and 'スコア' in df_ranking.columns:
        df_ranking['スコア'] = pd.to_numeric(df_ranking['スコア'], errors='coerce')
        df_ranking = df_ranking.sort_values(by="スコア", ascending=False).reset_index(drop=True)
        df_ranking.index = df_ranking.index + 1
        st.dataframe(df_ranking, use_container_width=True)
    else:
        st.write("ランキング読み込み中...")

# --- 7. メイン処理（タブ切り替え） ---

# タブのアイコン化
tab1, tab2, tab3, tab4 = st.tabs(["📝 クエスト", "👑 ステータス", "🔮 ガチャ", "🏆 ランキング"])

with tab1:
    render_point_input_screen()
with tab2:
    render_rank_display_screen()
with tab3:
    render_gacha_screen()
with tab4:
    render_national_rank_screen()