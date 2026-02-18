import streamlit as st
import pandas as pd
import numpy as np
from scipy.optimize import minimize
import plotly.express as px
import plotly.graph_objects as go

# ページ設定：ダークモード風のカスタムCSS
st.set_page_config(page_title="TV Optimizer Pro", layout="wide")

st.markdown("""
    <style>
    .main {
        background-color: #0f0f0f;
    }
    .stMetric {
        background-color: #1e1e1e;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #333;
    }
    div[data-testid="stExpander"] {
        border: none !important;
        background-color: #1e1e1e !important;
    }
    </style>
    """, unsafe_content_html=True)

# ヘッダーエリア
st.title("📊 TV Analytics Pro")
st.caption("YouTube Studio Style Marketing Dashboard")

# エリア設定
areas = ["関東", "関西", "中部", "九州", "その他"]
area_master = {
    "関東": {"price": 150000, "pop": 0.35, "m": 90, "a": 0.002},
    "関西": {"price": 80000,  "pop": 0.15, "m": 88, "a": 0.0025},
    "中部": {"price": 60000,  "pop": 0.10, "m": 85, "a": 0.003},
    "九州": {"price": 40000,  "pop": 0.10, "m": 85, "a": 0.0035},
    "その他": {"price": 30000, "pop": 0.30, "m": 80, "a": 0.004}
}

# サイドバー設定
with st.sidebar:
    st.image("https://img.icons8.com/fluent/100/000000/combo-chart.png", width=50)
    st.header("Campaign Settings")
    total_budget = st.number_input("Total Budget (JPY)", value=100000000, step=1000000)
    brand = st.text_input("Project Name", "Quarterly Campaign")
    st.divider()
    st.info("設定を変更すると、右側の数値がリアルタイムに更新準備に入ります。")

# メインコンテンツ
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Estimated Reach", value="85.4%", delta="+2.1%")
with col2:
    st.metric(label="Budget Usage", value=f"¥{total_budget:,}")
with col3:
    st.metric(label="Active Regions", value=len(areas))

st.divider()

# 入力セクション（カード型）
with st.expander("📍 地域別データ入力 (Current GRP & Cost)", expanded=True):
    cols = st.columns(len(areas))
    t_inputs = []
    for idx, a in enumerate(areas):
        with cols[idx]:
            grp = st.number_input(f"{a} GRP", value=0, key=f"g_{a}")
            cost = st.number_input(f"{a} Cost", value=0, key=f"c_{a}")
            t_inputs.append({"area": a, "t_grp": grp, "t_cost": cost})

# 計算ボタンと結果
if st.button("RUN OPTIMIZATION", use_container_width=True, type="primary"):
    time_cost = sum(i['t_cost'] for i in t_inputs)
    spot_budget = total_budget - time_cost
    
    if spot_budget < 0:
        st.error("Budget Exceeded! Please adjust your settings.")
    else:
        # 最適化計算
        def obj(x):
            score = 0
            for i, a in enumerate(areas):
                m, alpha = area_master[a]['m'], area_master[a]['a']
                score += m * (1 - np.exp(-alpha * (t_inputs[i]['t_grp'] + x[i]))) * area_master[a]['pop']
            return -score
        
        cons = ({'type': 'ineq', 'fun': lambda x: spot_budget - sum(x[i] * area_master[areas[i]]['price'] for i in range(len(areas)))})
        res = minimize(obj, np.zeros(len(areas)), bounds=[(0, None)]*len(areas), constraints=cons)
        
        # 結果表示
        chart_col, table_col = st.columns([2, 1])
        
        df = pd.DataFrame({"Region": areas, "Optimized GRP": res.x.round(1)})
        
        with chart_col:
            fig = px.bar(df, x="Region", y="Optimized GRP", 
                         title="Allocation Strategy",
                         color="Optimized GRP",
                         color_continuous_scale="Viridis")
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig, use_container_width=True)
            
        with table_col:
            st.write("Allocation List")
            st.dataframe(df, use_container_width=True, hide_index=True)
