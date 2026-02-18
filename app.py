import streamlit as st
import pandas as pd
import numpy as np
from scipy.optimize import minimize
import plotly.express as px

# ページ設定
st.set_page_config(page_title="TV Reach Maximize Tool", layout="wide")

st.title("📺 テレビ出稿 最適化ダッシュボード")
st.caption("タイム（固定枠）をベースに、残予算をスポットへ最適配分してリーチを最大化します。")

# --- 設定サイドバー ---
with st.sidebar:
    st.header("⚙️ 基本設定")
    total_budget = st.number_input("総予算 (円)", value=150000000, step=1000000)
    num_brands = st.slider("ブランド数", 1, 3, 1)
    brands = [st.text_input(f"ブランド名 {i+1}", f"Brand {chr(65+i)}") for i in range(num_brands)]

# エリア情報
areas = ["関東", "関西", "中部", "九州", "その他"]
area_master = {
    "関東": {"price": 150000, "pop": 0.35, "m": 90, "a": 0.002},
    "関西": {"price": 80000,  "pop": 0.15, "m": 88, "a": 0.0025},
    "中部": {"price": 60000,  "pop": 0.10, "m": 85, "a": 0.003},
    "九州": {"price": 40000,  "pop": 0.10, "m": 85, "a": 0.0035},
    "その他": {"price": 30000, "pop": 0.30, "m": 80, "a": 0.004}
}

# --- 画面構成 ---
tab1, tab2 = st.tabs(["📝 条件入力", "📊 最適化レポート"])

with tab1:
    st.subheader("1. タイム枠（30秒）の既決定分入力")
    input_rows = []
    for b in brands:
        st.markdown(f"**【{b}】**")
        cols = st.columns(5)
        for idx, a in enumerate(areas):
            grp = cols[idx].number_input(f"{a} GRP", key=f"t_grp_{b}_{a}", min_value=0)
            cost = cols[idx].number_input(f"{a} 金額", key=f"t_cost_{b}_{a}", min_value=0)
            input_rows.append({"brand": b, "area": a, "t_grp": grp, "t_cost": cost})

with tab2:
    time_total_cost = sum(r['t_cost'] for r in input_rows)
    spot_budget = total_budget - time_total_cost
    
    if spot_budget < 0:
        st.error("予算不足です。総予算を増やすか、タイム枠を減らしてください。")
    elif st.button("🚀 最適化計算を実行"):
        # 最適化ロジック
        def objective(x):
            s_grps = x.reshape(len(brands), len(areas))
            score = 0
            for i, b in enumerate(brands):
                for j, a in enumerate(areas):
                    t_grp = next(r['t_grp'] for r in input_rows if r['brand']==b and r['area']==a)
                    m, alpha = area_master[a]['m'], area_master[a]['a']
                    reach = m * (1 - np.exp(-alpha * (t_grp + s_grps[i, j])))
                    score += reach * area_master[a]['pop']
            return -score

        cons = {'type': 'ineq', 'fun': lambda x: spot_budget - sum(x[i*len(areas)+j] * area_master[areas[j]]['price'] for i in range(len(brands)) for j in range(len(areas)))}
        res = minimize(objective, np.zeros(len(brands)*len(areas)), bounds=[(0, None)]*(len(brands)*len(areas)), constraints=cons)
        
        st.success("最適化が完了しました！")
        spot_res = res.x.reshape(len(brands), len(areas))
        
        # グラフ作成
        res_data = []
        for i, b in enumerate(brands):
            for j, a in enumerate(areas):
                res_data.append({"ブランド": b, "エリア": a, "スポットGRP": round(spot_res[i,j], 1), "コスト": int(spot_res[i,j]*area_master[a]['price'])})
        
        df_res = pd.DataFrame(res_data)
        st.plotly_chart(px.bar(df_res, x="エリア", y="スポットGRP", color="ブランド", barmode="group"), use_container_width=True)
        st.write("### エリア別スポット配分詳細")
        st.table(df_res)