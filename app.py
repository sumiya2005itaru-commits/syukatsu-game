import streamlit as st
import pandas as pd
import plotly.express as px

# ページ設定
st.set_page_config(page_title="就活ゲーム化アプリ", layout="wide")

# --- 1. 定義・設定セクション ---

# 行動とポイントの定義辞書
ACTIONS = {
    "面接（本番）": 30,
    "ES提出（1社）": 20,
    "ケース問題（1問完答）": 20,
    "OB/OG訪問": 15,
    "Webテスト受検": 10,
    "説明会参加": 10,
    "業界研究・ニュース": 5,
    "自己分析・振り返り": 5
}

# ランク判定関数
def get_rank(score):
    if score >= 200:
        return "SSS (神)", "🔥 圧倒的です！この調子なら無双できます。", "red"
    elif score >= 150:
        return "S (トップ層)", "✨ 素晴らしい行動量です。自信を持ってください。", "orange"
    elif score >= 100:
        return "A (合格点)", "✅ 順調です。質も意識していきましょう。", "green"
    elif score >= 50:
        return "B (要改善)", "⚠️ もう少しギアを上げられます。行動あるのみ！", "blue"
    else:
        return "C (危機)", "💀 まずはパソコンを開くところから始めましょう。", "gray"

# --- 2. UI・入力セクション ---

st.title("🎮 就活・努力ゲーム化アプリ")
st.markdown("今の行動をポイントに換算し、**「今週のランク」**を判定します。")

st.sidebar.header("今週の行動入力")
st.sidebar.write("今週行った回数を入力してください")

# 入力フォームの自動生成と集計
input_data = {}
total_score = 0

for action, point in ACTIONS.items():
    # スライダーで回数を入力（0〜10回）
    count = st.sidebar.number_input(f"{action} ({point}pt)", min_value=0, max_value=20, value=0)
    subtotal = count * point
    total_score += subtotal
    
    if subtotal > 0:
        input_data[action] = subtotal

# --- 3. 結果表示セクション ---

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("🏆 Current Rank")
    rank, comment, color = get_rank(total_score)
    
    # ランク表示
    st.markdown(f"""
    <div style="border: 3px solid {color}; border-radius: 10px; padding: 20px; text-align: center;">
        <h1 style="color: {color}; font-size: 60px; margin: 0;">{rank.split()[0]}</h1>
        <h3 style="color: {color};">{rank.split()[1]}</h3>
        <p>{comment}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.metric(label="今週の獲得ポイント", value=f"{total_score} pt")

with col2:
    st.subheader("📊 ポイントの内訳 (努力の可視化)")
    
    if total_score > 0:
        # データフレーム作成
        df = pd.DataFrame(list(input_data.items()), columns=["行動", "獲得ポイント"])
        
        # ドーナツチャートで内訳表示
        fig = px.pie(df, values='獲得ポイント', names='行動', hole=0.4,
                     title="何でポイントを稼いだか？")
        st.plotly_chart(fig, use_container_width=True)
        
        # バーチャートでポイントの高さ順表示
        st.bar_chart(df.set_index("行動"))
        
    else:
        st.info("左側のサイドバーから行動を入力すると、ここに分析結果が表示されます。")

# --- 4. 目標・進捗バー ---
st.divider()
st.subheader("📈 次のランクへの進捗")

# 次のランクまでの計算
if total_score < 50:
    target, next_rank = 50, "B"
elif total_score < 100:
    target, next_rank = 100, "A"
elif total_score < 150:
    target, next_rank = 150, "S"
elif total_score < 200:
    target, next_rank = 200, "SSS"
else:
    target, next_rank = 300, "LEGEND"

progress = min(total_score / target, 1.0)
st.progress(progress)
st.caption(f"次のランク {next_rank} まで、あと {max(0, target - total_score)} pt")