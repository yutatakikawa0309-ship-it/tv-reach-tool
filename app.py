import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# 1. ページ設定
st.set_page_config(page_title="TV Strategy Planner", layout="wide")

# --- ダミーデータの生成 ---
def get_dummy_data():
    # タイム番組リスト (カラム名を英語にすることでエラーを回避)
    programs = pd.DataFrame({
        "Program": ["Morning News", "Golden Music Fest", "Sunday Drama", "Late Night Anime", "Saturday Sports"],
        "Area": ["関東", "関西", "名古屋", "関東", "名古屋"],
        "Rating": [5.2, 12.5, 10.8, 2.1, 4.5],
        "Cost_M": [150, 500, 450, 50, 100],
        "Match": ["High", "High", "Mid", "Low", "Mid"]
    })
    # スポット構成
    spots = pd.DataFrame({
        "Pattern": ["All Day", "Reverse L", "U-Shape", "Y-Shape"],
        "Unit_Cost": [25000, 35000, 45000, 55000],
        "Reach_Exp": [15.2, 22.5, 28.0, 35.5]
    })
    return programs, spots

programs_df, spots_df = get_dummy_data()

# --- メイン画面 ---
st.title("🚀 TV Media Mix Strategy")
st.caption("Strategic Planning Dashboard")

# 2. 基本設定
with st.sidebar:
    st.header("🏢 Basic Settings")
    num_brands = st.number_input("Number of Brands", min_value=1, max_value=5, value=2)
    selected_areas = st.multiselect("Target Areas", ["関東", "関西", "名古屋", "福岡", "札幌"], default=["関東", "関西", "名古屋"])
    st.divider()

# 3. ブランド別入力
brand_configs = []
for i in range(num_brands):
    with st.expander(f"Brand {i+1} Configuration", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            name = st.text_input(f"Brand Name", value=f"Brand {chr(65+i)}", key=f"bn_{i}")
            budget = st.number_input(f"Monthly Budget (JPY)", value=50000000, step=1000000, key=f"bb_{i}")
        with c2:
            length = st.selectbox(f"Length", [15, 30], key=f"bl_{i}")
            kpi = st.radio(f"KPI Type", ["TRP", "Reach"], key=f"bk_{i}")
        with c3:
            target = st.selectbox(f"Target", ["F1-F2", "M1-M2", "ALL", "Teen"], key=f"bt_{i}")
            ratio = st.slider(f"Time Ratio (%)", 0, 100, 40, key=f"br_{i}")
            
        brand_configs.append({"name": name, "budget": budget, "ratio": ratio, "kpi": kpi, "target": target})

# 4. 実行ボタン
if st.button("GENERATE STRATEGY", use_container_width=True, type="primary"):
    for b in brand_configs:
        st.divider()
        st.header(f"✨ Result: {b['name']}")
        
        t_bud = b['budget'] * (b['ratio'] / 100)
        s_bud = b['budget'] - t_bud
        
        col_m1, col_m2 = st.columns(2)
        col_m1.metric("Time Budget", f"¥{int(t_bud):,}")
        col_m2.metric("Spot Budget", f"¥{int(s_bud):,}")
        
        t1, t2 = st.tabs(["📺 Time Program Recommendation", "🎯 Spot Plan"])
        
        with t1:
            st.write("### Recommended Programs")
            rec = programs_df[programs_df['Area'].isin(selected_areas)].copy()
            rec['Score'] = np.random.randint(70, 99, len(rec))
            st.dataframe(rec.sort_values("Score", ascending=False), use_container_width=True, hide_index=True)
            
        with t2:
            st.write("### Spot Distribution")
            fig = px.pie(spots_df, values='Reach_Exp', names='Pattern', 
                         title=f"Recommended Pattern for {b['kpi']}",
                         hole=0.4, template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
        
