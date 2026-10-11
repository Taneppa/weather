import datetime
import pandas as pd
import requests
import streamlit as st

# ページ基本設定
st.set_page_config(
    page_title="過去気象データ分析アプリ",
    page_icon="🌤️",
    layout="wide"
)

# 主要都市の緯度・経度リスト
LOCATIONS = {
    "札幌 (北海道)": {"lat": 43.0621, "lon": 141.3544},
    "仙台 (宮城)": {"lat": 38.2682, "lon": 140.8694},
    "東京 (東京都)": {"lat": 35.6895, "lon": 139.6917},
    "横浜 (神奈川)": {"lat": 35.4437, "lon": 139.6380},
    "金沢 (石川)": {"lat": 36.5947, "lon": 136.6256},
    "名古屋 (愛知)": {"lat": 35.1815, "lon": 136.9066},
    "大阪 (大阪府)": {"lat": 34.6937, "lon": 135.5023},
    "広島 (広島)": {"lat": 34.3853, "lon": 132.4553},
    "高松 (香川)": {"lat": 34.3401, "lon": 134.0433},
    "福岡 (福岡)": {"lat": 33.5904, "lon": 130.4017},
    "鹿児島 (鹿児島)": {"lat": 31.5966, "lon": 130.5571},
    "那覇 (沖縄)": {"lat": 26.2124, "lon": 127.6809},
}

# うるう年を考慮して「〇年前」の日付を計算する関数
def safe_replace_year(date_obj, year_offset):
    try:
        return date_obj.replace(year=date_obj.year + year_offset)
    except ValueError:
        # うるう年の2/29で、移動先が平年の場合は2/28に調整
        return date_obj.replace(year=date_obj.year + year_offset, day=28)


# --- Open-Meteo Archive API からデータ取得 ---
@st.cache_data(ttl=3600)
def fetch_weather_data(lat: float, lon: float, start_date: datetime.date, end_date: datetime.date):
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "daily": [
            "temperature_2m_mean",
            "precipitation_sum",
            "sunshine_duration",
            "relative_humidity_2m_mean"
        ],
        "timezone": "Asia/Tokyo"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            daily = data.get("daily", {})
            
            # 秒単位で返る日照時間を時間に変換 (秒 / 3600)
            sunshine_hours = [
                round(s / 3600, 1) if s is not None else 0.0 
                for s in daily.get("sunshine_duration", [])
            ]
            
            df = pd.DataFrame({
                "日付": daily.get("time", []),
                "平均気温 (°C)": daily.get("temperature_2m_mean", []),
                "降水量 (mm)": daily.get("precipitation_sum", []),
                "日照時間 (時間)": sunshine_hours,
                "平均湿度 (%)": daily.get("relative_humidity_2m_mean", [])
            })
            df["日付"] = pd.to_datetime(df["日付"]).dt.date
            return df
        else:
            return None
    except Exception:
        return None


# --- 指定期間のサマリー（合計・平均）を算出する関数 ---
def calculate_summary(df):
    if df is None or df.empty:
        return None
    return {
        "precip": df["降水量 (mm)"].sum(),
        "sun": df["日照時間 (時間)"].sum(),
        "temp": df["平均気温 (°C)"].mean(),
        "humid": df["平均湿度 (%)"].mean()
    }


# --- サイドバー (条件設定) ---
st.sidebar.header("⚙️ 取得条件")

selected_location = st.sidebar.selectbox("地域を選択", list(LOCATIONS.keys()))
lat = LOCATIONS[selected_location]["lat"]
lon = LOCATIONS[selected_location]["lon"]

# 過去気象APIの確定データの都合上、2日前までをデフォルト上限に設定
today = datetime.date.today()
max_allowed_date = today - datetime.timedelta(days=2)
default_start = max_allowed_date - datetime.timedelta(days=30)

date_range = st.sidebar.date_input(
    "期間を選択",
    value=(default_start, max_allowed_date),
    max_value=max_allowed_date
)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    st.info("開始日と終了日の両方を選択してください。")
    st.stop()


# --- メインコンテンツ ---
st.title("🌤️ 過去気象データ分析アプリ (過去比較付き)")
st.caption(f"選択地域: **{selected_location}** （{start_date} ～ {end_date}）")

# データ取得・計算処理
with st.spinner("指定期間、および過去5年分の気象データを取得・計算しています..."):
    # 1. 指定期間（当年）
    current_df = fetch_weather_data(lat, lon, start_date, end_date)
    current_summary = calculate_summary(current_df)

    if current_df is None or current_df.empty:
        st.error("指定された期間のデータを取得できませんでした。条件を変更してください。")
        st.stop()

    # 2. 1年前の同期間
    start_1yr = safe_replace_year(start_date, -1)
    end_1yr = safe_replace_year(end_date, -1)
    df_1yr = fetch_weather_data(lat, lon, start_1yr, end_1yr)
    summary_1yr = calculate_summary(df_1yr)

    # 3. 過去5年間 (1〜5年前) の同期間平均
    past_5_summaries = []
    for i in range(1, 6):
        s_date = safe_replace_year(start_date, -i)
        e_date = safe_replace_year(end_date, -i)
        df_i = fetch_weather_data(lat, lon, s_date, e_date)
        sum_i = calculate_summary(df_i)
        if sum_i:
            past_5_summaries.append(sum_i)
    
    if past_5_summaries:
        summary_5yr = {
            "precip": sum(x["precip"] for x in past_5_summaries) / len(past_5_summaries),
            "sun": sum(x["sun"] for x in past_5_summaries) / len(past_5_summaries),
            "temp": sum(x["temp"] for x in past_5_summaries) / len(past_5_summaries),
            "humid": sum(x["humid"] for x in past_5_summaries) / len(past_5_summaries)
        }
    else:
        summary_5yr = None


# --- 1. データサマリー (比較表示) ---
st.subheader("📊 期間内の集計結果と過去比較")

# UI描画用のヘルパー関数
def render_metric(col, icon, label, key, unit):
    val_current = current_summary[key]
    val_1yr = summary_1yr[key] if summary_1yr else None
    val_5yr = summary_5yr[key] if summary_5yr else None

    with col:
        # 1年前との差分表示
        if val_1yr is not None:
            delta_1yr = val_current - val_1yr
            delta_str = f"昨年比: {delta_1yr:+.1f} {unit}"
        else:
            delta_str = "昨年データなし"

        # メイン指標の描画 (delta_color="off" で色の意味付けをなくす)
        st.metric(
            label=f"{icon} {label}",
            value=f"{val_current:.1f} {unit}",
            delta=delta_str,
            delta_color="off"
        )
        
        # 過去5年平均との差分表示
        if val_5yr is not None:
            delta_5yr = val_current - val_5yr
            st.caption(f"過去5年平均: {val_5yr:.1f} {unit}")
            st.caption(f"（平均との差: {delta_5yr:+.1f} {unit}）")
        else:
            st.caption("過去5年平均データなし")

col1, col2, col3, col4 = st.columns(4)
render_metric(col1, "🌧️", "降水量 (合計)", "precip", "mm")
render_metric(col2, "☀️", "日照時間 (合計)", "sun", "時間")
render_metric(col3, "🌡️", "平均気温", "temp", "°C")
render_metric(col4, "💧", "平均湿度", "humid", "%")

st.divider()

# --- 2. 日別推移グラフ (指定期間) ---
st.subheader("📈 指定期間の日別推移グラフ")

tab1, tab2, tab3 = st.tabs(["気温・湿度", "降水量", "日照時間"])

with tab1:
    st.line_chart(current_df.set_index("日付")[["平均気温 (°C)", "平均湿度 (%)"]])

with tab2:
    st.bar_chart(current_df.set_index("日付")["降水量 (mm)"])

with tab3:
    st.bar_chart(current_df.set_index("日付")["日照時間 (時間)"])

st.divider()

# --- 3. 詳細データテーブル & ダウンロード ---
st.subheader("📋 詳細データ")

st.dataframe(current_df, use_container_width=True)

csv_data = current_df.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    label="📥 指定期間のデータをCSVダウンロード",
    data=csv_data,
    file_name=f"weather_{selected_location}_{start_date}_{end_date}.csv",
    mime="text/csv"
)
