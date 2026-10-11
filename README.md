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

```bash
git clone [https://github.com/your-username/weather-analysis-app.git](https://github.com/your-username/weather-analysis-app.git)
cd weather-analysis-app
```

### 2. 必要なライブラリのインストール

```bash
pip install -r requirements.txt
```

**`requirements.txt` の内容:**
```text
streamlit
requests
pandas
```

### 3. アプリの起動

```bash
streamlit run app.py
```

ブラウザで `http://localhost:8501` が自動的に開き、アプリが実行されます。

---

## 📖 使い方

1. **条件の設定（サイドバー）**
   - **地域を選択**: 主要都市（東京、大阪、札幌、福岡など）から選択します。
   - **期間を選択**: 分析したい開始日と終了日を選択します。（※過去気象データの仕様上、2日前まで選択可能です）
2. **集計結果と過去比較の確認**
   - 画面上部に指定期間の実績値、前年比、過去5年平均との差分が表示されます。

<!-- [スクショ挿入位置: 比較メトリクスカードの拡大表示] -->
<!-- 例: ![比較メトリクス](images/metrics.png) -->

3. **グラフでの推移確認**
   - タブを切り替えて、期間内の日別データの変化を可視化します。

<!-- [スクショ挿入位置: 日別推移グラフ画面] -->
<!-- 例: ![日別推移グラフ](images/graphs.png) -->

4. **データのダウンロード**
   - 画面下部の「詳細データ」から日別データを確認し、「📥 指定期間のデータをCSVダウンロード」ボタンからCSVファイルを取得できます。

---

## 📂 ディレクトリ構成

```text
.
├── app.py              # アプリケーションのメインプログラム
├── requirements.txt    # 依存ライブラリ一覧
├── README.md           # 本ドキュメント
└── images/             # README用スクリーンショット保存用フォルダ（任意）
    ├── top_summary.png
    ├── metrics.png
    └── graphs.png
```

---

## 🛠️ 使用技術

- **Frontend / Framework**: [Streamlit](https://streamlit.io/)
- **Data Processing**: [Pandas](https://pandas.pydata.org/)
- **Data Source**: [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api)
