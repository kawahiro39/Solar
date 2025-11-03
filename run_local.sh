#!/bin/bash

# ローカル開発環境起動スクリプト

echo "太陽光パネル配置シミュレーションシステム - ローカル開発環境"
echo "=================================================="

# APIサーバー起動
echo ""
echo "1. APIサーバーを起動しています..."
cd api
pip install -r requirements.txt
python main.py &
API_PID=$!
echo "   APIサーバー起動完了 (PID: $API_PID)"
echo "   URL: http://localhost:8080"

# フロントエンド用の簡易HTTPサーバー起動
echo ""
echo "2. フロントエンドサーバーを起動しています..."
cd ../frontend
python3 -m http.server 8000 &
FRONTEND_PID=$!
echo "   フロントエンドサーバー起動完了 (PID: $FRONTEND_PID)"
echo "   URL: http://localhost:8000"

echo ""
echo "=================================================="
echo "起動完了！"
echo ""
echo "アクセスURL:"
echo "  - フロントエンド: http://localhost:8000"
echo "  - API: http://localhost:8080"
echo ""
echo "停止するには Ctrl+C を押してください"
echo "=================================================="

# 終了時のクリーンアップ
trap "kill $API_PID $FRONTEND_PID 2>/dev/null; echo 'サーバーを停止しました'" EXIT

# 待機
wait