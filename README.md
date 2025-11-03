# 太陽光パネル配置シミュレーションシステム

## 概要
Google Maps航空写真上で屋根の形状を描画し、太陽光パネルの配置と発電量をシミュレーションするシステムです。

## システム構成
- **バックエンド**: Python Flask API (Cloud Runで動作)
- **フロントエンド**: HTML/JavaScript (Bubble HTML埋め込み)
- **主要機能**:
  - Google Maps航空写真上での多角形描画
  - パネル自動配置アルゴリズム
  - 発電量シミュレーション
  - PDF資料生成

## ディレクトリ構造
```
/webapp
├── api/                  # Cloud Run APIサーバー
│   ├── main.py          # Flask アプリケーション
│   ├── panel_layout.py  # パネル配置アルゴリズム
│   ├── solar_calc.py    # 日射量・発電量計算
│   ├── pdf_generator.py # PDF生成
│   ├── requirements.txt # Python依存関係
│   └── Dockerfile       # Cloud Run用Dockerfile
│
└── frontend/            # Bubble埋め込み用HTML
    ├── index.html      # メインHTML
    ├── script.js       # JavaScript
    └── style.css       # スタイル

```

## 機能詳細

### 1. 屋根形状の描画
- Google Maps航空写真上でクリックして多角形を作成
- 作成した多角形の編集・削除機能

### 2. パネル配置
- 指定されたパネルサイズで多角形内に自動配置
- オフセット（離隔）の設定可能

### 3. 発電量シミュレーション
- 設置地点の緯度経度から日射量を計算
- 年間発電量の予測

### 4. PDF資料生成
- 1ページ目: レイアウト図（航空写真+パネル配置）
- 2ページ目: 発電量シミュレーション結果

## 使用技術
- Google Maps JavaScript API
- Python Flask
- ReportLab (PDF生成)
- Cloud Run
- Bubble (HTML埋め込み)