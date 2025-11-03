#!/bin/bash

# Cloud Run デプロイスクリプト
# APIディレクトリから直接デプロイする

echo "🚀 太陽光パネル配置シミュレーションAPI - Cloud Runデプロイ"
echo "=================================================="

# プロジェクトIDの確認
if [ -z "$PROJECT_ID" ]; then
    echo "プロジェクトIDを入力してください:"
    read PROJECT_ID
    export PROJECT_ID
fi

echo "プロジェクトID: $PROJECT_ID"
echo ""

# プロジェクト設定
gcloud config set project $PROJECT_ID

# 必要なAPIを有効化
echo "📦 必要なAPIを有効化しています..."
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
echo "✅ API有効化完了"
echo ""

# リージョン選択
REGION="asia-northeast1"
echo "📍 デプロイリージョン: $REGION"
echo ""

# APIディレクトリに移動
cd api/

# Cloud Runにデプロイ
echo "🏗️ Cloud Runにデプロイしています..."
echo "これには数分かかる場合があります..."
echo ""

gcloud run deploy solar-panel-api \
    --source . \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --timeout 60 \
    --max-instances 100

if [ $? -eq 0 ]; then
    echo ""
    echo "=================================================="
    echo "✅ デプロイ成功！"
    echo ""
    echo "サービスURL:"
    gcloud run services describe solar-panel-api --region $REGION --format 'value(status.url)'
    echo ""
    echo "次のステップ:"
    echo "1. 上記のURLをコピーしてください"
    echo "2. frontend/bubble-embed.html の API_BASE_URL を更新"
    echo "3. Google Maps APIキーを設定"
    echo "4. Bubbleに埋め込み"
    echo "=================================================="
else
    echo ""
    echo "❌ デプロイに失敗しました"
    echo "エラーログを確認してください"
fi