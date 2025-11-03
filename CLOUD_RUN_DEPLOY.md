# Cloud Run デプロイガイド

## 🚀 クイックデプロイ（3つの方法）

### 方法1: デプロイスクリプトを使用（最も簡単）
```bash
# デプロイスクリプトを実行
./deploy.sh

# プロジェクトIDを入力して実行
```

### 方法2: APIディレクトリから直接デプロイ
```bash
# APIディレクトリに移動
cd api/

# Cloud Runにデプロイ
gcloud run deploy solar-panel-api \
    --source . \
    --platform managed \
    --region asia-northeast1 \
    --allow-unauthenticated \
    --memory 1Gi
```

### 方法3: ルートディレクトリからデプロイ
```bash
# プロジェクトルートから実行（Dockerfileがルートにある場合）
gcloud run deploy solar-panel-api \
    --source . \
    --platform managed \
    --region asia-northeast1 \
    --allow-unauthenticated \
    --memory 1Gi
```

## 📝 デプロイ前のチェックリスト

### 1. Google Cloud CLIの準備
```bash
# gcloudがインストールされているか確認
gcloud version

# ログイン
gcloud auth login

# プロジェクト設定
gcloud config set project YOUR_PROJECT_ID
```

### 2. 必要なAPIの有効化
```bash
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

## 🎯 デプロイ後の設定

### 1. サービスURLの取得
```bash
gcloud run services describe solar-panel-api \
    --region asia-northeast1 \
    --format 'value(status.url)'
```

### 2. frontend/bubble-embed.htmlを更新
```javascript
// Cloud Run URLを設定
const API_BASE_URL = 'https://solar-panel-api-xxxxx-an.a.run.app';
```

### 3. Google Maps APIキーを設定
```html
<script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&...">
```

## 🔧 トラブルシューティング

### エラー: Dockerfileが見つからない
**原因**: Cloud BuildがDockerfileを見つけられない

**解決方法**:
1. `cd api/` してからデプロイ
2. または、ルートディレクトリにDockerfileを配置（作成済み）
3. または、deploy.shスクリプトを使用

### エラー: ビルド失敗
**原因**: 依存関係のインストールエラー

**解決方法**:
```bash
# ローカルでテスト
cd api/
docker build -t test .
docker run -p 8080:8080 test
```

### エラー: 認証エラー
**原因**: Cloud Run APIが有効でない、または権限不足

**解決方法**:
```bash
# APIを有効化
gcloud services enable run.googleapis.com

# 権限を確認
gcloud projects get-iam-policy YOUR_PROJECT_ID
```

## 📊 デプロイステータスの確認

### サービス一覧
```bash
gcloud run services list --region asia-northeast1
```

### ログ確認
```bash
gcloud run services logs read solar-panel-api \
    --region asia-northeast1 \
    --limit 50
```

### メトリクス確認
```bash
gcloud run services describe solar-panel-api \
    --region asia-northeast1
```

## 🔄 更新デプロイ

コードを更新した後：
```bash
# GitHubから最新を取得
git pull origin main

# 再デプロイ（方法1）
./deploy.sh

# または（方法2）
cd api/
gcloud run deploy solar-panel-api --source .
```

## 💡 Tips

1. **コールドスタート対策**: 最小インスタンス数を1に設定
   ```bash
   gcloud run services update solar-panel-api \
       --min-instances 1 \
       --region asia-northeast1
   ```

2. **カスタムドメイン設定**
   ```bash
   gcloud run domain-mappings create \
       --service solar-panel-api \
       --domain your-domain.com \
       --region asia-northeast1
   ```

3. **環境変数の設定**
   ```bash
   gcloud run services update solar-panel-api \
       --set-env-vars KEY=VALUE \
       --region asia-northeast1
   ```