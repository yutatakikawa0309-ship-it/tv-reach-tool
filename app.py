import streamlit as st
import pandas as pd
import numpy as np
from scipy.optimize import minimize
import plotly.express as px

# 1. ページ設定（ダークモード設定はStreamlitの基本設定に任せる）
st.set_page_config(page_title="TV Analytics Pro", layout="wide")

# 2. ヘッダー（シンプルかつモダンに）
st.title("📊 TV Analytics Pro")
st.caption("Marketing Dashboard for Strategic Optimization")

# エリアデータ
areas = ["関東", "関西", "中部", "九州", "その他"]
area_master = {
    "関東": {"price": 150000, "pop": 0.35, "m": 90, "a": 0.002},
    "関西": {"price": 80000,  "pop": 0.15, "m": 88, "a": 0.0025},
    "中部": {"price": 60000,  "pop": 0.10, "m": 85, "a": 0.003},
    "九州": {"price": 40000,  "pop": 0.10, "m": 85, "a": 0.0035},
    "その他": {"price": 30000, "pop": 0.30, "m": 80, "a": 0.004}
}

# 3. サイドバー
with st.sidebar:
    st.header("Campaign Settings")
    total_budget = st.number_input("Total Budget (JPY)", value=100000000, step=1000000)
    brand = st.text_input("Project Name", "Quarterly Campaign")
    st.divider()
    st.info("数値を入力後、中央のボタンを押してください。")

# 4. メイン指標（YouTube Studio風のカードレイアウト）
# ボーダー付きのコンテナで囲むことで、デザインをスマートに見せます
with st.container(border=True):
    col1, col2, col3 = st.columns(3)
    col1.metric("Target Audience", "42.5M", "High")
    col2.metric("Total Budget", f"¥{total_budget:,}")
    col3.metric("Regions", len(areas))

st.write("") # スペース空け

# 5. 入力エリア
st.subheader("📍 Input Data")
with st.expander("詳細データを入力する", expanded=True):
    t_inputs = []
    # 2段に分けてスッキリさせる
    rows = [areas[:3], areas[3:]]
    for row in rows:
        cols = st.columns(len(row))
        for idx, a in enumerate(row):
            with cols[idx]:
                grp = st.number_input(f"{a} GRP", value=0, key=f"g_{a}")
                cost = st.number_input(f"{a} Cost", value=0, key=f"c_{a}")
                # リストに追加するために元のエリア名を保持
                area_idx = areas.index(a)
                t_inputs.append({"area": a, "t_grp": grp, "t_cost": cost, "order": area_idx})

# データの並び順を元に戻す
t_inputs = sorted(t_inputs, key=lambda x: x['order'])

# 6. 計算実行
st.write("")
if st.button("RUN OPTIMIZATION", use_container_width=True, type="primary"):
    time_cost = sum(i['t_cost'] for i in t_inputs)
    spot_budget = total_budget - time_cost
    
    if spot_budget < 0:
        st.error("Budget Exceeded! Please adjust your settings.")
    else:
        def obj(x):
            score = 0
            for i, a in enumerate(areas):
                m, alpha = area_master[a]['m'], area_master[a]['a']
                score += m * (1 - np.exp(-alpha * (t_inputs[i]['t_grp'] + x[i]))) * area_master[a]['pop']
            return -score
        
        cons = ({'type': 'ineq', 'fun': lambda x: spot_budget - sum(x[i] * area_master[areas[i]]['price'] for i in range(len(areas)))})
        res = minimize(obj, np.zeros(len(areas)), bounds=[(0, None)]*len(areas), constraints=cons)
        
        # グラフと表
        st.subheader("📊 Optimization Result")
        df = pd.DataFrame({"Region": areas, "Optimized GRP": res.x.round(1)})
        
        chart_col, table_col = st.columns([2, 1])
        with chart_col:
            fig = px.bar(df, x="Region", y="Optimized GRP", 
                         color="Optimized GRP",
                         color_continuous_scale="Reds", # YouTube風の赤系
                         template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
            
        with table_col:
            st.dataframe(df, use_container_width=True, hide_index=True)
