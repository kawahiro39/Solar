# デプロイメントガイド

## 前提条件
- Google Cloud Projectが設定済み
- gcloud CLIがインストール済み
- Google Maps JavaScript APIキーを取得済み
- Bubbleアカウントを持っている

## 1. Google Cloud設定

### 1.1 プロジェクト設定
```bash
# プロジェクトIDを設定
export PROJECT_ID=your-project-id
gcloud config set project $PROJECT_ID

# 必要なAPIを有効化
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### 1.2 Google Maps API設定
1. [Google Cloud Console](https://console.cloud.google.com)にアクセス
2. 「APIとサービス」→「認証情報」
3. 「認証情報を作成」→「APIキー」
4. キーの制限を設定（HTTPリファラーを制限）

## 2. Cloud Run APIのデプロイ

### 2.1 ビルドとデプロイ
```bash
cd api/

# Cloud Buildを使用してビルド&デプロイ
gcloud run deploy solar-panel-api \
    --source . \
    --platform managed \
    --region asia-northeast1 \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1
```

### 2.2 URLの取得
デプロイ完了後、表示されるService URLをメモしてください。
例: `https://solar-panel-api-xxxxx-an.a.run.app`

## 3. フロントエンド設定

### 3.1 APIキーとURLの設定
`frontend/index.html`を編集:
```javascript
// Google Maps APIキーを設定
<script async defer 
    src="https://maps.googleapis.com/maps/api/js?key=YOUR_ACTUAL_API_KEY&libraries=drawing,geometry&callback=initMap">
</script>
```

`frontend/script.js`を編集:
```javascript
// Cloud Run URLを設定
const API_BASE_URL = 'https://solar-panel-api-xxxxx-an.a.run.app';
```

### 3.2 フロントエンドファイルのホスティング
以下のオプションから選択:

#### Option A: GitHub Pages
1. GitHubリポジトリを作成
2. `frontend/`フォルダの内容をプッシュ
3. Settings → Pages でGitHub Pagesを有効化

#### Option B: Firebase Hosting
```bash
# Firebase CLIをインストール
npm install -g firebase-tools

# 初期化
firebase init hosting

# デプロイ
firebase deploy --only hosting
```

#### Option C: Cloud Storage (静的ホスティング)
```bash
# バケット作成
gsutil mb gs://your-bucket-name

# ファイルをアップロード
gsutil -m cp -r frontend/* gs://your-bucket-name/

# 公開設定
gsutil iam ch allUsers:objectViewer gs://your-bucket-name
```

## 4. Bubble統合

### 4.1 HTML要素の追加
1. Bubbleエディタを開く
2. 「HTML element」を追加
3. 以下のiframeコードを設定:

```html
<iframe 
    src="YOUR_FRONTEND_URL/index.html"
    width="100%" 
    height="800px"
    frameborder="0"
    allow="geolocation">
</iframe>
```

### 4.2 レスポンシブ設定
Bubble側の設定:
- HTML要素の幅を「100%」に設定
- 高さを固定または動的に設定
- モバイル対応の場合、条件付き表示を設定

## 5. セキュリティ設定

### 5.1 CORS設定
`api/main.py`のCORS設定を本番環境に合わせて調整:
```python
CORS(app, origins=['https://your-bubble-app.bubbleapps.io'])
```

### 5.2 API認証（オプション）
必要に応じてAPI認証を追加:
- Cloud Run IAM認証
- APIキー認証
- OAuth 2.0

## 6. モニタリング

### 6.1 Cloud Runメトリクス
```bash
# ログを確認
gcloud run services logs read solar-panel-api

# メトリクスを確認
gcloud run services describe solar-panel-api
```

### 6.2 エラーハンドリング
フロントエンドでエラーを適切に処理:
- ネットワークエラー
- API制限
- タイムアウト

## 7. 本番環境チェックリスト

- [ ] Google Maps APIキーが設定済み
- [ ] Cloud Run APIがデプロイ済み
- [ ] CORS設定が適切
- [ ] SSL証明書が有効
- [ ] エラーハンドリングが実装済み
- [ ] バックアップ設定済み
- [ ] 監視アラート設定済み

## トラブルシューティング

### 問題: CORSエラー
解決: `api/main.py`のCORS設定を確認し、Bubbleドメインを許可

### 問題: Google Maps APIエラー
解決: APIキーの制限設定とクォータを確認

### 問題: PDFが生成されない
解決: Cloud RunのメモリとCPU設定を増やす

### 問題: パネル配置が遅い
解決: アルゴリズムの最適化またはCloud RunのCPU設定を増やす

## サポート
問題が発生した場合:
1. Cloud Runログを確認
2. ブラウザコンソールを確認
3. ネットワークタブでAPIレスポンスを確認