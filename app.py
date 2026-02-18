import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# 1. ページ設定
st.set_page_config(page_title="TV Strategy Planner", layout="wide")

# --- ダミーデータの生成 (裏側で保持するデータ) ---
def get_dummy_data():
    # タイム番組リスト
    programs = pd.DataFrame({
        "番組名": ["朝のニュースワイド", "ゴールデン歌謡祭", "日曜ドラマ特選", "深夜のアニメ枠", "土曜スポーツLIVE"],
        "エリア": ["関東", "関西", "名古屋", "関東", "名古屋"],
        "視聴率(想定)": [5.2, 12.5, 10.8, 2.1, 4.5],
        "コスト(万円)": [150, 500, 450, 50, 100],
        "ターゲット適合度": ["High", "High", "Mid", "Low", "Mid"]
    })
    # スポット過去実績
    past_spots = pd.DataFrame({
        "枠名": ["全日", "逆L", "コの字", "ヨの字"],
        "平均コスト単価": [25000, 35000, 45000, 55000],
        "期待リーチ率": [15.2, 22.5, 28.0, 35.5]
    })
    return programs, past_spots

programs_df, spots_df = get_dummy_data()

# --- メイン画面 ---
st.title("🚀 TV Media Mix Strategy")
st.caption("Multiple Brands & Regional Optimization Dashboard")

# 2. 基本設定（サイドバー）
with st.sidebar:
    st.header("🏢 基本設定")
    num_brands = st.number_input("管理ブランド数", min_value=1, max_value=5, value=2)
    selected_areas = st.multiselect("対象エリア", ["関東", "関西", "名古屋", "福岡", "札幌"], default=["関東", "関西", "名古屋"])
    
    st.divider()
    st.info("ブランドごとの詳細を設定してください。")

# 3. ブランド別詳細入力
st.subheader("📋 ブランド別・プランニング詳細")
brand_configs = []

for i in range(num_brands):
    with st.expander(f"ブランド {i+1} の設定", expanded=True):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            name = st.text_input(f"ブランド名", value=f"Brand {chr(65+i)}", key=f"bn_{i}")
            budget = st.number_input(f"月間予算 (円)", value=50000000, step=1000000, key=f"bb_{i}")
        with c2:
            length = st.selectbox(f"素材秒数", [15, 30], key=f"bl_{i}")
            target = st.selectbox(f"ターゲット", ["F1-F2", "M1-M2", "ALL", "Teen"], key=f"bt_{i}")
        with c3:
            kpi = st.radio(f"KPI設定", ["TRP", "Reach"], key=f"bk_{i}")
        with c4:
            ratio = st.slider(f"タイム比率 (%)", 0, 100, 40, key=f"br_{i}")
            
        brand_configs.append({
            "name": name, "budget": budget, "length": length, 
            "target": target, "kpi": kpi, "time_ratio": ratio
        })

# 4. 最適化実行
st.write("")
if st.button("STRATEGY GENERATE (プラン実行)", use_container_width=True, type="primary"):
    
    for b in brand_configs:
        st.divider()
        st.header(f"✨ Result: {b['name']}")
        
        # 予算計算
        time_budget = b['budget'] * (b['time_ratio'] / 100)
        spot_budget = b['budget'] - time_budget
        
        # アウトプット表示
        m1, m2 = st.columns(2)
        m1.metric("タイム配分予算", f"¥{int(time_budget):,}")
        m2.metric("スポット配分予算", f"¥{int(spot_budget):,}")
        
        tab1, tab2 = st.tabs(["📺 推奨タイム番組", "🎯 スポット出稿プラン"])
        
        with tab1:
            st.write("### 購入すべきテレビタイム番組 (シミュレーション)")
            # 予算とエリアに合う番組を抽出
            rec_programs = programs_df[programs_df['エリア'].isin(selected_areas)].copy()
            rec_programs['推奨
