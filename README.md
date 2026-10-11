# 🌤️ 過去気象データ分析アプリ (過去比較付き)
https://app-g2llshtblgu.streamlit.app/

指定した地域・期間の過去気象データ（降水量・日照時間・平均気温・平均湿度）を取得・集計し、**「1年前の同期間」** や **「過去5年間の同期間平均」** との自動比較が行えるStreamlitアプリケーションです。

単年のデータだけでなく、例年や前年と比較することで、気候の傾向や異常気象の把握が容易になります。

<!-- [<img width="2830" height="1478" alt="image" src="https://github.com/user-attachments/assets/e28ed6fc-9c97-4839-9019-eaade6e2eb5c" />
: トップ画面全体（集計結果・比較メトリクスが表示されている状態）] -->
<!-- 例: ![トップ画面](images/top_summary.png) または <img src="images/top_summary.png" width="700"> -->

---

## 🌟 主な特徴

- **APIキー不要・完全無料**: Open-Meteo Archive APIを使用しているため、複雑なAPIキー設定なしで即座に利用可能。
- **4つの主要気象指標を集計**: 降水量 (mm)、日照時間 (時間)、平均気温 (°C)、平均湿度 (%) の合計値および平均値を自動算出。
- **過去データとの自動比較**:
  - **前年比較**: 1年前の同期間データとの差分（昨年比）を表示。
  - **過去5年平均比較**: 1〜5年前の同期間平均値および平均との差分を表示。
- **ビジュアルグラフ機能**: タブ切り替えで「気温・湿度」「降水量」「日照時間」の日別推移をグラフ表示。
- **CSVダウンロード**: 取得した日別データをCSVファイル形式で保存可能。
- **高速表示**: セッションキャッシュ処理により、同一条件での再読み込みを高速化。

---

## ⚙️ セットアップ & 実行方法

### 1. リポジトリのクローン / ファイルの準備

```bash
git clone [https://github.com/your-username/weather-analysis-app.git](https://github.com/your-username/weather-analysis-app.git)
cd weather-analysis-app
