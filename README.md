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
    ├── style.css       # スタイル
    └── bubble-embed.html # Bubble埋め込み用統合版

```

## 🚀 Bubble埋め込み用HTMLコード

Bubbleに埋め込む際は、以下の手順で設定してください：

### 1. 事前準備
1. Google Maps JavaScript APIキーを取得
2. Cloud Run APIをデプロイしてURLを取得

### 2. Bubble埋め込み手順

1. **Bubbleエディタで「HTML」要素を追加**

2. **以下のHTMLコードをコピーして貼り付け**
   - `frontend/bubble-embed.html` の内容を使用
   - または以下の設定箇所のみを編集：

```javascript
// ============================================
// 設定 - ここを編集してください
// ============================================

// 1. Cloud RunのAPIエンドポイントURLを設定
const API_BASE_URL = 'https://your-cloud-run-url.run.app';

// 2. Google Maps APIキーを設定
// HTMLの下部にある以下の行を編集：
<script async defer 
    src="https://maps.googleapis.com/maps/api/js?key=YOUR_GOOGLE_MAPS_API_KEY&libraries=drawing,geometry&callback=initMap">
</script>
```

### 3. 設定が必要な2箇所

#### ① API URLの設定（JavaScript内）
```javascript
const API_BASE_URL = 'https://your-cloud-run-url.run.app';  
// ↑ あなたのCloud Run URLに置き換える
```

#### ② Google Maps APIキーの設定（HTML内）
```html
src="https://maps.googleapis.com/maps/api/js?key=YOUR_GOOGLE_MAPS_API_KEY&libraries=drawing,geometry&callback=initMap"
// ↑ YOUR_GOOGLE_MAPS_API_KEY を実際のAPIキーに置き換える
```

### 4. Bubbleでの設定推奨値

- **HTML要素の幅**: 100%（レスポンシブ対応）
- **HTML要素の高さ**: 最小800px推奨
- **「Run mode」**: 「Every time element is visible」に設定

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

## 📝 簡単セットアップ用コード

最小限の設定で動作確認したい場合は、以下のコードをBubbleのHTML要素に貼り付けて、2箇所の設定を変更するだけです：

```html
<!-- bubble-embed.htmlの内容をここにコピー -->
<!-- 設定箇所1: API_BASE_URL を変更 -->
<!-- 設定箇所2: YOUR_GOOGLE_MAPS_API_KEY を変更 -->
```

`frontend/bubble-embed.html` ファイルに完全なコードが含まれています。

## トラブルシューティング

### CORS エラーが発生する場合
- Cloud Run APIの `main.py` で CORS設定を確認
- BubbleアプリのドメインがCORS許可リストに含まれているか確認

### Google Maps が表示されない場合
- APIキーが正しく設定されているか確認
- APIキーの制限設定（HTTPリファラー）を確認
- Google Cloud ConsoleでMaps JavaScript APIが有効になっているか確認

### パネル配置が動作しない場合
- Cloud Run APIが正常に起動しているか確認
- ブラウザの開発者ツールでネットワークエラーを確認
- API URLが正しく設定されているか確認

## 使用技術
- Google Maps JavaScript API
- Python Flask
- ReportLab (PDF生成)
- Cloud Run
- Bubble (HTML埋め込み)