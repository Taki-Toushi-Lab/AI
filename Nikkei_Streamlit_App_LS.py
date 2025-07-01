import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
from datetime import datetime
import matplotlib.pyplot as plt

# --- 定数とパス ---
MODEL_PATH = r"C:\\Users\\yasuyuki\\OneDrive - Questindustries\\デスクトップ\\Nikkei_Python\\ls_model.pkl"
THRESHOLDS_PATH = r"C:\\Users\\yasuyuki\\OneDrive - Questindustries\\デスクトップ\\Nikkei_Python\\ls_thresholds.pkl"
CSV_LOG_PATH = r"C:\\Users\\yasuyuki\\OneDrive - Questindustries\\デスクトップ\\Nikkei_Python\\ls_log.csv"
SCORE_LOG_PATH = r"C:\\Users\\yasuyuki\\OneDrive - Questindustries\\デスクトップ\\Nikkei_Python\\ls_score_log.csv"
FEATURE_COLUMNS = [
    "EPS", "PER", "海外", "個人", "証券自己", "信用倍率", "評価損益率",
    "売り残", "買い残", "騰落6日", "騰落10日", "騰落25日",
    "日経レバ倍率", "空売り比率", "VIX", "USDJPY", "SOX"
]
JUDGMENT_THRESHOLDS = [80, 60, 40, 20]

# --- 関数定義 ---
def get_judgment(score, thresholds):
    t1, t2, t3, t4 = thresholds
    if score >= t1:
        return "強気（上昇確率：80%以上）"
    elif score >= t2:
        return "やや強気（上昇確率：60〜70%）"
    elif score >= t3:
        return "中立（拮抗）"
    elif score >= t4:
        return "やや弱気（下落確率：60〜70%）"
    else:
        return "弱気（下落確率：80%以上）"

def safe(val):
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return "ー"
    if isinstance(val, (np.floating, np.integer, np.bool_)):
        val = val.item()
    return round(val, 2) if isinstance(val, (int, float)) else val

# --- Streamlit UI ---
st.markdown("""
<div style='text-align:center'>
    <h1>📈 AI日経診断 (Takiの投資ラボ)</h1>
</div>
""", unsafe_allow_html=True)

st.markdown("""
### 🧠 AIによる日経平均診断
日付を選んで、診断スコア・判定を確認できます。
""")

# --- モデル・データの読み込み ---
model = joblib.load(MODEL_PATH)
thresholds = list(map(int, joblib.load(THRESHOLDS_PATH))) if os.path.exists(THRESHOLDS_PATH) else JUDGMENT_THRESHOLDS

if not os.path.exists(SCORE_LOG_PATH):
    st.error("スコアログCSVが見つかりません。")
    st.stop()

score_df = pd.read_csv(SCORE_LOG_PATH)
score_df["日付"] = pd.to_datetime(score_df["日付"], errors="coerce")
score_df = score_df.dropna(subset=["日付", "スコア"])
latest_date = score_df["日付"].max()
st.sidebar.markdown("### 🔍 日付を選択")
selected_date = st.sidebar.date_input("診断日", latest_date)

row = score_df[score_df["日付"] == pd.to_datetime(selected_date)]
if row.empty:
    st.warning("この日付の診断データはありません。")
    st.stop()

score = row["スコア"].values[0]
judgment = get_judgment(score, thresholds)
result = row["判定"].values[0]

st.subheader(f"🗓 診断日：{selected_date.strftime('%Y-%m-%d')}")
st.metric("スコア", f"{score:.2f}")
st.metric("診断", judgment)
st.metric("判定結果", result)

# --- 📈 スコア推移グラフ ---
st.markdown("### 📈 スコア推移グラフ")
fig, ax = plt.subplots(figsize=(8, 3))
plot_df = score_df.sort_values("日付")
ax.plot(plot_df["日付"], plot_df["スコア"], label="スコア", marker='o')
ax.axhline(thresholds[0], color='green', linestyle='--', label='強気しきい値')
ax.axhline(thresholds[1], color='orange', linestyle='--', label='中立しきい値')
ax.axhline(thresholds[2], color='orange', linestyle='--', label='中立しきい値')
ax.axhline(thresholds[3], color='red', linestyle='--', label='弱気しきい値')
ax.set_ylabel("スコア")
ax.set_xlabel("日付")
ax.legend()
ax.grid(True)
st.pyplot(fig)

# --- 補足情報 ---
st.markdown("""
---
#### 📎 免責事項（Disclaimer）

本サービスは、過去の市場データおよび統計的なアルゴリズムに基づき、スコアおよび参考情報を提供するものであり、
将来の株価・市場動向・投資成果を保証するものではありません。

本サービスが提供する情報は、**投資判断の参考資料であり、最終的な意思決定はご利用者ご自身の責任において行っていただく必要があります**。
当方は、本サービスの利用に関連して発生した損失・損害について、一切の責任を負いかねます。

なお、本サービスは**金融商品取引法に基づく投資助言・代理業には該当しない情報提供サービス**であり、
特定の銘柄や売買タイミングを推奨・助言するものではありません。

また、一部の情報は外部データソースから取得されており、**その正確性・完全性・最新性について保証するものではありません**。
表示される情報には遅延・欠損・変動が生じる可能性があることを予めご了承ください。

本サービスに含まれるロジック、分析手法、スコア計算モデル、UIデザイン、およびその他の知的財産は、
すべて開発者に帰属し、**無断複製・転載・再配布・商用転用を一切禁じます**。
商用利用または法人への展開をご希望の場合は、必ず事前にご連絡ください。

> 本免責事項の内容は、予告なく変更される場合があります。常に最新の内容をご確認ください。
""")
