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
    ├── bubble-embed.html # Bubble埋め込み用統合版（旧版）
    └── bubble-embed-fixed.html # 修正版（描画機能修正済み）

```

## 🚀 Bubble埋め込み用HTMLコード

Bubbleに埋め込む際は、以下の手順で設定してください：

### 1. 事前準備
1. Google Maps JavaScript APIキーを取得
2. Cloud Run APIをデプロイしてURLを取得

### 2. Bubble埋め込み手順

1. **Bubbleエディタで「HTML」要素を追加**

2. **以下のHTMLコードをコピーして貼り付け**
   - 下記の完全なHTMLコードを使用
   - 設定が必要な箇所は2つだけ

### 3. 設定が必要な2箇所

#### ① API URLの設定（562行目付近）
```javascript
const API_BASE_URL = 'https://your-cloud-run-url.run.app';  
// ↑ あなたのCloud Run URLに置き換える
```

#### ② Google Maps APIキーの設定（563行目付近）
```javascript
const GOOGLE_MAPS_API_KEY = 'YOUR_GOOGLE_MAPS_API_KEY';
// ↑ あなたのGoogle Maps APIキーに置き換える
```

### 4. Bubbleでの設定推奨値

- **HTML要素の幅**: 100%（レスポンシブ対応）
- **HTML要素の高さ**: 最小800px推奨
- **「Run mode」**: 「Every time element is visible」に設定

## 📝 Bubble埋め込み用完全HTMLコード（修正版）

以下の完全なHTMLコードをBubbleのHTML要素にコピー&ペーストして、2箇所の設定を変更するだけです：

<details>
<summary>👉 クリックして完全なHTMLコード（修正版）を表示</summary>

```html<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>太陽光パネル配置シミュレーション</title>
    
    <style>
        /* Reset & Base Styles */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }

        #app {
            max-width: 100%;
            margin: 0 auto;
            padding: 20px;
        }

        /* Header */
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
            animation: fadeIn 0.8s ease-out;
        }

        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }

        .subtitle {
            font-size: 1.1em;
            opacity: 0.95;
        }

        /* Control Panel */
        .control-panel {
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 25px;
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            animation: slideUp 0.6s ease-out;
        }

        .control-section {
            padding: 0 15px;
            border-right: 1px solid #e0e0e0;
        }

        .control-section:last-child {
            border-right: none;
        }

        .control-section h3 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.1em;
        }

        .control-group {
            margin-bottom: 15px;
        }

        .control-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: 500;
            color: #555;
            font-size: 0.9em;
        }

        .control-group input[type="number"] {
            width: 100%;
            padding: 8px 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 1em;
            transition: border-color 0.3s;
        }

        .control-group input[type="number"]:focus {
            outline: none;
            border-color: #667eea;
        }

        /* Buttons */
        .btn {
            width: 100%;
            padding: 12px 20px;
            margin-bottom: 10px;
            border: none;
            border-radius: 8px;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }

        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        .btn-primary:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102,126,234,0.4);
        }

        .btn-secondary {
            background: #f5f5f5;
            color: #333;
        }

        .btn-secondary:hover:not(:disabled) {
            background: #e8e8e8;
        }

        .btn-success {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
        }

        .btn-success:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(17,153,142,0.4);
        }

        .btn-info {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
        }

        .btn-info:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(240,147,251,0.4);
        }

        .icon {
            width: 20px;
            height: 20px;
            fill: currentColor;
        }

        /* Hints */
        .hints {
            list-style: none;
            padding: 0;
        }

        .hints li {
            padding: 5px 0;
            padding-left: 20px;
            position: relative;
            font-size: 0.85em;
            color: #666;
        }

        .hints li:before {
            content: "•";
            position: absolute;
            left: 0;
            color: #667eea;
            font-weight: bold;
        }

        /* Map Container */
        #map-container {
            position: relative;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
            margin-bottom: 25px;
            animation: fadeIn 0.8s ease-out;
        }

        #map {
            width: 100%;
            height: 600px;
        }

        /* Map Overlay */
        #map-overlay {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(255,255,255,0.95);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
        }

        #map-overlay.hidden {
            display: none;
        }

        .overlay-content {
            text-align: center;
        }

        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }

        /* API Status */
        .api-status {
            background: #fff3cd;
            border: 1px solid #ffc107;
            border-radius: 8px;
            padding: 10px;
            margin-bottom: 15px;
            display: none;
        }

        .api-status.error {
            background: #f8d7da;
            border-color: #f5c6cb;
        }

        .api-status.success {
            background: #d4edda;
            border-color: #c3e6cb;
        }

        /* Results Section */
        .results {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            animation: fadeIn 0.5s ease-out;
        }

        .results.hidden {
            display: none;
        }

        .results h2 {
            color: #667eea;
            margin-bottom: 25px;
            text-align: center;
        }

        .result-cards {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }

        .result-card {
            background: #f8f9fa;
            border-radius: 12px;
            padding: 20px;
            border: 1px solid #e9ecef;
        }

        .result-card.full-width {
            grid-column: 1 / -1;
        }

        .result-card h3 {
            color: #495057;
            margin-bottom: 15px;
            font-size: 1.1em;
        }

        .stat-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            padding: 8px 0;
            border-bottom: 1px solid #dee2e6;
        }

        .stat-label {
            color: #6c757d;
            font-weight: 500;
        }

        .stat-value {
            color: #212529;
            font-weight: 600;
            font-size: 1.1em;
        }

        #monthly-chart {
            width: 100%;
            height: 250px;
            margin-top: 10px;
        }

        /* Status Message */
        .status-message {
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: #333;
            color: white;
            padding: 12px 24px;
            border-radius: 30px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
            z-index: 2000;
            animation: slideUp 0.3s ease-out;
        }

        .status-message.hidden {
            display: none;
        }

        .status-message.success {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        }

        .status-message.error {
            background: linear-gradient(135deg, #f5576c 0%, #f093fb 100%);
        }

        /* Animations */
        @keyframes fadeIn {
            from {
                opacity: 0;
            }
            to {
                opacity: 1;
            }
        }

        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        /* Responsive Design */
        @media (max-width: 1024px) {
            .control-panel {
                grid-template-columns: 1fr;
                gap: 20px;
            }
            
            .control-section {
                border-right: none;
                border-bottom: 1px solid #e0e0e0;
                padding-bottom: 20px;
            }
            
            .control-section:last-child {
                border-bottom: none;
            }
        }

        @media (max-width: 768px) {
            .header h1 {
                font-size: 1.8em;
            }
            
            .result-cards {
                grid-template-columns: 1fr;
            }
            
            #map {
                height: 400px;
            }
        }

        /* 描画モード時のスタイル */
        .drawing-mode {
            border: 2px solid #667eea !important;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0% {
                box-shadow: 0 0 0 0 rgba(102, 126, 234, 0.7);
            }
            70% {
                box-shadow: 0 0 0 10px rgba(102, 126, 234, 0);
            }
            100% {
                box-shadow: 0 0 0 0 rgba(102, 126, 234, 0);
            }
        }
    </style>
</head>
<body>
    <div id="app">
        <!-- ヘッダー -->
        <div class="header">
            <h1>太陽光パネル配置シミュレーション</h1>
            <p class="subtitle">屋根の形状を描画してパネル配置をシミュレート</p>
        </div>

        <!-- API状態表示 -->
        <div id="api-status" class="api-status">
            <span id="api-status-text">API接続確認中...</span>
        </div>

        <!-- コントロールパネル -->
        <div class="control-panel">
            <div class="control-section">
                <h3>パネル設定</h3>
                <div class="control-group">
                    <label for="panel-width">パネル幅 (cm):</label>
                    <input type="number" id="panel-width" value="165" min="50" max="300">
                </div>
                <div class="control-group">
                    <label for="panel-height">パネル高さ (cm):</label>
                    <input type="number" id="panel-height" value="100" min="50" max="200">
                </div>
                <div class="control-group">
                    <label for="offset">オフセット/離隔 (cm):</label>
                    <input type="number" id="offset" value="10" min="0" max="50">
                </div>
            </div>

            <div class="control-section">
                <h3>操作</h3>
                <button id="draw-mode-btn" class="btn btn-primary">
                    <svg class="icon" viewBox="0 0 24 24">
                        <path d="M3,17.25V21h3.75L17.81,9.94l-3.75-3.75L3,17.25z M20.71,7.04c0.39-0.39,0.39-1.02,0-1.41l-2.34-2.34c-0.39-0.39-1.02-0.39-1.41,0l-1.83,1.83 3.75,3.75 1.83-1.83z"/>
                    </svg>
                    屋根を描画
                </button>
                <button id="clear-polygon-btn" class="btn btn-secondary">
                    <svg class="icon" viewBox="0 0 24 24">
                        <path d="M19,6.41L17.59,5 12,10.59 6.41,5 5,6.41 10.59,12 5,17.59 6.41,19 12,13.41 17.59,19 19,17.59 13.41,12z"/>
                    </svg>
                    描画をクリア
                </button>
                <button id="calculate-btn" class="btn btn-success" disabled>
                    <svg class="icon" viewBox="0 0 24 24">
                        <path d="M19,3H5c-1.1,0-2,0.9-2,2v14c0,1.1,0.9,2,2,2h14c1.1,0,2-0.9,2-2V5C21,3.9,20.1,3,19,3z M9,17H7v-7h2V17z M13,17h-2V7h2V17z M17,17h-2v-4h2V17z"/>
                    </svg>
                    パネル配置
                </button>
                <button id="generate-pdf-btn" class="btn btn-info" disabled>
                    <svg class="icon" viewBox="0 0 24 24">
                        <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z"/>
                    </svg>
                    資料作成
                </button>
            </div>

            <div class="control-section">
                <h3>描画ヒント</h3>
                <ul class="hints">
                    <li>「屋根を描画」ボタンをクリックして描画モード開始</li>
                    <li>マップをクリックして屋根の角を順番に指定</li>
                    <li>最低3点以上で多角形を作成</li>
                    <li>最後の点をクリックまたはダブルクリックで描画完了</li>
                    <li>描画完了後、頂点をドラッグして調整可能</li>
                </ul>
            </div>
        </div>

        <!-- Google Maps -->
        <div id="map-container">
            <div id="map"></div>
            <div id="map-overlay" class="hidden">
                <div class="overlay-content">
                    <div class="spinner"></div>
                    <p>処理中...</p>
                </div>
            </div>
        </div>

        <!-- 結果表示エリア -->
        <div id="results" class="results hidden">
            <h2>シミュレーション結果</h2>
            
            <div class="result-cards">
                <div class="result-card">
                    <h3>パネル配置</h3>
                    <div class="result-content">
                        <div class="stat-item">
                            <span class="stat-label">パネル枚数:</span>
                            <span class="stat-value" id="panel-count">-</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">総面積:</span>
                            <span class="stat-value" id="total-area">-</span>
                        </div>
                    </div>
                </div>

                <div class="result-card">
                    <h3>発電量予測</h3>
                    <div class="result-content">
                        <div class="stat-item">
                            <span class="stat-label">年間発電量:</span>
                            <span class="stat-value" id="yearly-generation">-</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">システム容量:</span>
                            <span class="stat-value" id="system-capacity">-</span>
                        </div>
                    </div>
                </div>

                <div class="result-card full-width">
                    <h3>月別発電量予測</h3>
                    <canvas id="monthly-chart"></canvas>
                </div>
            </div>
        </div>

        <!-- ステータスメッセージ -->
        <div id="status-message" class="status-message hidden">
            <span id="status-text"></span>
        </div>
    </div>

    <!-- Main JavaScript -->
    <script>
        // ============================================
        // 設定 - ここを編集してください
        // ============================================
        const API_BASE_URL = 'https://your-cloud-run-url.run.app';  // Cloud RunのURLに置き換える
        const GOOGLE_MAPS_API_KEY = 'YOUR_GOOGLE_MAPS_API_KEY';  // Google Maps APIキーに置き換える

        // ============================================
        // メインアプリケーションコード
        // ============================================
        
        // グローバル変数
        let map;
        let drawingManager;
        let currentPolygon = null;
        let panelMarkers = [];
        let simulationData = null;
        let isDrawingMode = false;

        // Google Maps APIを動的にロード
        function loadGoogleMaps() {
            const script = document.createElement('script');
            script.src = `https://maps.googleapis.com/maps/api/js?key=${GOOGLE_MAPS_API_KEY}&libraries=drawing,geometry&callback=initMap`;
            script.async = true;
            script.defer = true;
            script.onerror = function() {
                console.error('Google Maps APIの読み込みに失敗しました');
                showStatus('Google Maps APIの読み込みに失敗しました。APIキーを確認してください。', 'error');
                document.getElementById('api-status').style.display = 'block';
                document.getElementById('api-status').className = 'api-status error';
                document.getElementById('api-status-text').textContent = 'Google Maps APIエラー: APIキーを確認してください';
            };
            document.head.appendChild(script);
        }

        /**
         * Google Maps初期化
         */
        window.initMap = function() {
            console.log('Google Maps初期化開始');
            
            try {
                // 東京を中心に地図を初期化
                map = new google.maps.Map(document.getElementById('map'), {
                    center: { lat: 35.6762, lng: 139.6503 },
                    zoom: 20,
                    mapTypeId: 'satellite',
                    tilt: 0,
                    mapTypeControl: true,
                    mapTypeControlOptions: {
                        mapTypeIds: ['satellite', 'hybrid'],
                        position: google.maps.ControlPosition.TOP_RIGHT
                    }
                });

                // Drawing Managerを初期化
                drawingManager = new google.maps.drawing.DrawingManager({
                    drawingMode: null,
                    drawingControl: false,  // デフォルトのコントロールは非表示
                    polygonOptions: {
                        fillColor: '#FF0000',
                        fillOpacity: 0.3,
                        strokeColor: '#FF0000',
                        strokeWeight: 2,
                        clickable: true,
                        editable: true,
                        draggable: false
                    }
                });

                drawingManager.setMap(map);

                // ポリゴン完成時のイベント
                google.maps.event.addListener(drawingManager, 'polygoncomplete', function(polygon) {
                    console.log('ポリゴン描画完了');
                    handlePolygonComplete(polygon);
                });

                // 現在地を取得して移動
                if (navigator.geolocation) {
                    navigator.geolocation.getCurrentPosition(
                        (position) => {
                            const pos = {
                                lat: position.coords.latitude,
                                lng: position.coords.longitude
                            };
                            map.setCenter(pos);
                            console.log('現在地に移動:', pos);
                        },
                        () => {
                            console.log('位置情報の取得に失敗しました');
                        }
                    );
                }

                // API接続テスト
                testAPIConnection();
                
                console.log('Google Maps初期化完了');
                showStatus('マップの準備ができました', 'success');
                
            } catch (error) {
                console.error('Google Maps初期化エラー:', error);
                showStatus('マップの初期化に失敗しました', 'error');
            }
        }

        /**
         * API接続テスト
         */
        async function testAPIConnection() {
            try {
                const response = await fetch(`${API_BASE_URL}/health`, {
                    method: 'GET',
                    mode: 'cors'
                });
                
                if (response.ok) {
                    document.getElementById('api-status').style.display = 'block';
                    document.getElementById('api-status').className = 'api-status success';
                    document.getElementById('api-status-text').textContent = '✓ API接続: 正常';
                    setTimeout(() => {
                        document.getElementById('api-status').style.display = 'none';
                    }, 3000);
                }
            } catch (error) {
                document.getElementById('api-status').style.display = 'block';
                document.getElementById('api-status').className = 'api-status error';
                document.getElementById('api-status-text').textContent = '⚠ API接続エラー: Cloud Run URLを確認してください';
            }
        }

        /**
         * 描画モードの切り替え
         */
        function toggleDrawingMode() {
            if (!drawingManager) {
                showStatus('マップが初期化されていません', 'error');
                return;
            }

            const btn = document.getElementById('draw-mode-btn');
            const mapContainer = document.getElementById('map-container');
            
            if (isDrawingMode) {
                // 描画モードを終了
                drawingManager.setDrawingMode(null);
                btn.innerHTML = `
                    <svg class="icon" viewBox="0 0 24 24">
                        <path d="M3,17.25V21h3.75L17.81,9.94l-3.75-3.75L3,17.25z M20.71,7.04c0.39-0.39,0.39-1.02,0-1.41l-2.34-2.34c-0.39-0.39-1.02-0.39-1.41,0l-1.83,1.83 3.75,3.75 1.83-1.83z"/>
                    </svg>
                    屋根を描画
                `;
                mapContainer.classList.remove('drawing-mode');
                isDrawingMode = false;
                console.log('描画モード終了');
            } else {
                // 描画モードを開始
                drawingManager.setDrawingMode(google.maps.drawing.OverlayType.POLYGON);
                btn.innerHTML = `
                    <svg class="icon" viewBox="0 0 24 24">
                        <path d="M19,6.41L17.59,5 12,10.59 6.41,5 5,6.41 10.59,12 5,17.59 6.41,19 12,13.41 17.59,19 19,17.59 13.41,12z"/>
                    </svg>
                    描画を終了
                `;
                mapContainer.classList.add('drawing-mode');
                isDrawingMode = true;
                showStatus('マップ上をクリックして屋根の形状を描画してください', 'info');
                console.log('描画モード開始');
            }
        }

        /**
         * ポリゴン描画完了時の処理
         */
        function handlePolygonComplete(polygon) {
            // 既存のポリゴンを削除
            if (currentPolygon) {
                currentPolygon.setMap(null);
            }
            
            currentPolygon = polygon;
            
            // 描画モードを終了
            drawingManager.setDrawingMode(null);
            isDrawingMode = false;
            document.getElementById('map-container').classList.remove('drawing-mode');
            
            // ボタンの状態を更新
            document.getElementById('calculate-btn').disabled = false;
            document.getElementById('draw-mode-btn').innerHTML = `
                <svg class="icon" viewBox="0 0 24 24">
                    <path d="M3,17.25V21h3.75L17.81,9.94l-3.75-3.75L3,17.25z M20.71,7.04c0.39-0.39,0.39-1.02,0-1.41l-2.34-2.34c-0.39-0.39-1.02-0.39-1.41,0l-1.83,1.83 3.75,3.75 1.83-1.83z"/>
                </svg>
                屋根を描画
            `;
            
            // 頂点変更時のイベント
            google.maps.event.addListener(polygon.getPath(), 'set_at', updatePolygon);
            google.maps.event.addListener(polygon.getPath(), 'insert_at', updatePolygon);
            
            showStatus('屋根の形状を描画しました。頂点をドラッグして調整できます。', 'success');
        }

        /**
         * ポリゴン更新時の処理
         */
        function updatePolygon() {
            clearPanels();
            document.getElementById('generate-pdf-btn').disabled = true;
            console.log('ポリゴン更新');
        }

        /**
         * パネルをクリア
         */
        function clearPanels() {
            panelMarkers.forEach(marker => {
                marker.setMap(null);
            });
            panelMarkers = [];
        }

        /**
         * ポリゴン座標を取得
         */
        function getPolygonCoordinates() {
            if (!currentPolygon) return [];
            
            const path = currentPolygon.getPath();
            const coordinates = [];
            
            for (let i = 0; i < path.getLength(); i++) {
                const point = path.getAt(i);
                coordinates.push([point.lat(), point.lng()]);
            }
            
            return coordinates;
        }

        /**
         * パネル配置計算
         */
        async function calculatePanels() {
            if (!currentPolygon) {
                showStatus('先に屋根の形状を描画してください', 'error');
                return;
            }
            
            showLoading(true);
            clearPanels();
            
            const coordinates = getPolygonCoordinates();
            const panelWidth = parseFloat(document.getElementById('panel-width').value);
            const panelHeight = parseFloat(document.getElementById('panel-height').value);
            const offset = parseFloat(document.getElementById('offset').value);
            
            const requestData = {
                polygon: coordinates,
                panel_width: panelWidth,
                panel_height: panelHeight,
                offset: offset,
                location: {
                    lat: map.getCenter().lat(),
                    lng: map.getCenter().lng(),
                    address: '日本'
                }
            };
            
            console.log('パネル配置計算リクエスト:', requestData);
            
            try {
                const response = await fetch(`${API_BASE_URL}/api/calculate-panels`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(requestData),
                    mode: 'cors'
                });
                
                if (!response.ok) throw new Error('計算に失敗しました');
                
                const data = await response.json();
                simulationData = data;
                
                console.log('パネル配置計算結果:', data);
                
                // パネルを地図上に表示
                displayPanels(data.panels);
                
                // 結果を表示
                displayResults(data);
                
                // PDFボタンを有効化
                document.getElementById('generate-pdf-btn').disabled = false;
                
                showStatus(`${data.panel_count}枚のパネルを配置しました`, 'success');
                
            } catch (error) {
                console.error('Error:', error);
                showStatus('パネル配置の計算に失敗しました。API接続を確認してください。', 'error');
            } finally {
                showLoading(false);
            }
        }

        /**
         * パネルを地図上に表示
         */
        function displayPanels(panels) {
            panels.forEach(panel => {
                // パネルの多角形を作成
                const panelPolygon = new google.maps.Polygon({
                    paths: panel.corners.map(coord => ({lat: coord[0], lng: coord[1]})),
                    strokeColor: '#0000FF',
                    strokeOpacity: 0.8,
                    strokeWeight: 1,
                    fillColor: '#0000FF',
                    fillOpacity: 0.4,
                    map: map
                });
                
                panelMarkers.push(panelPolygon);
            });
        }

        /**
         * 結果を表示
         */
        function displayResults(data) {
            // 結果セクションを表示
            document.getElementById('results').classList.remove('hidden');
            
            // パネル情報
            document.getElementById('panel-count').textContent = `${data.panel_count}枚`;
            document.getElementById('total-area').textContent = `${data.total_area.toFixed(1)} m²`;
            
            // 発電量情報
            document.getElementById('yearly-generation').textContent = 
                `${data.power_estimation.yearly_total_kwh.toLocaleString()} kWh`;
            document.getElementById('system-capacity').textContent = 
                `${data.power_estimation.panel_info.total_rated_power_kw} kW`;
            
            // 月別グラフを描画
            drawMonthlyChart(data.power_estimation.monthly_data);
        }

        /**
         * 月別発電量グラフを描画
         */
        function drawMonthlyChart(monthlyData) {
            const canvas = document.getElementById('monthly-chart');
            const ctx = canvas.getContext('2d');
            
            // キャンバスをクリア
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // グラフ描画エリア
            const padding = 40;
            const chartWidth = canvas.width - padding * 2;
            const chartHeight = canvas.height - padding * 2;
            
            // 最大値を取得
            const maxValue = Math.max(...monthlyData.map(d => d.generation_kwh));
            
            // 月名
            const months = ['1月', '2月', '3月', '4月', '5月', '6月', 
                           '7月', '8月', '9月', '10月', '11月', '12月'];
            
            // バーを描画
            const barWidth = chartWidth / 12;
            
            monthlyData.forEach((data, index) => {
                const barHeight = (data.generation_kwh / maxValue) * chartHeight;
                const x = padding + index * barWidth;
                const y = padding + chartHeight - barHeight;
                
                // グラデーション
                const gradient = ctx.createLinearGradient(0, y, 0, y + barHeight);
                gradient.addColorStop(0, '#667eea');
                gradient.addColorStop(1, '#764ba2');
                
                // バーを描画
                ctx.fillStyle = gradient;
                ctx.fillRect(x + barWidth * 0.1, y, barWidth * 0.8, barHeight);
                
                // 値を表示
                ctx.fillStyle = '#333';
                ctx.font = '10px Arial';
                ctx.textAlign = 'center';
                ctx.fillText(Math.round(data.generation_kwh).toString(), 
                            x + barWidth / 2, y - 5);
                
                // 月名を表示
                ctx.fillText(months[index], x + barWidth / 2, 
                            padding + chartHeight + 15);
            });
        }

        /**
         * PDF生成
         */
        async function generatePDF() {
            if (!simulationData || !currentPolygon) {
                showStatus('先にパネル配置を実行してください', 'error');
                return;
            }
            
            showLoading(true);
            
            try {
                const mapImage = ''; // TODO: Static Maps APIで取得
                
                const requestData = {
                    polygon: getPolygonCoordinates(),
                    panels: simulationData.panels,
                    power_data: simulationData.power_estimation,
                    map_image: mapImage,
                    location: {
                        lat: map.getCenter().lat(),
                        lng: map.getCenter().lng(),
                        address: '日本'
                    },
                    panel_specs: {
                        width: document.getElementById('panel-width').value,
                        height: document.getElementById('panel-height').value,
                        offset: document.getElementById('offset').value
                    }
                };
                
                const response = await fetch(`${API_BASE_URL}/api/generate-pdf`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(requestData),
                    mode: 'cors'
                });
                
                if (!response.ok) throw new Error('PDF生成に失敗しました');
                
                // PDFダウンロード
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `solar_simulation_${new Date().getTime()}.pdf`;
                a.click();
                window.URL.revokeObjectURL(url);
                
                showStatus('PDFを生成しました', 'success');
                
            } catch (error) {
                console.error('Error:', error);
                showStatus('PDF生成に失敗しました', 'error');
            } finally {
                showLoading(false);
            }
        }

        /**
         * 描画をクリア
         */
        function clearDrawing() {
            if (currentPolygon) {
                currentPolygon.setMap(null);
                currentPolygon = null;
            }
            clearPanels();
            document.getElementById('calculate-btn').disabled = true;
            document.getElementById('generate-pdf-btn').disabled = true;
            document.getElementById('results').classList.add('hidden');
            
            // 描画モードも終了
            if (isDrawingMode) {
                toggleDrawingMode();
            }
            
            showStatus('描画をクリアしました', 'info');
        }

        /**
         * ローディング表示
         */
        function showLoading(show) {
            const overlay = document.getElementById('map-overlay');
            if (show) {
                overlay.classList.remove('hidden');
            } else {
                overlay.classList.add('hidden');
            }
        }

        /**
         * ステータスメッセージ表示
         */
        function showStatus(message, type = 'info') {
            const statusEl = document.getElementById('status-message');
            const textEl = document.getElementById('status-text');
            
            textEl.textContent = message;
            statusEl.className = `status-message ${type}`;
            statusEl.classList.remove('hidden');
            
            setTimeout(() => {
                statusEl.classList.add('hidden');
            }, 3000);
        }

        /**
         * イベントリスナー設定
         */
        document.addEventListener('DOMContentLoaded', function() {
            console.log('DOM読み込み完了');
            
            // 描画モードボタン
            document.getElementById('draw-mode-btn').addEventListener('click', function() {
                console.log('描画ボタンクリック');
                toggleDrawingMode();
            });
            
            // クリアボタン
            document.getElementById('clear-polygon-btn').addEventListener('click', function() {
                console.log('クリアボタンクリック');
                clearDrawing();
            });
            
            // パネル配置ボタン
            document.getElementById('calculate-btn').addEventListener('click', function() {
                console.log('計算ボタンクリック');
                calculatePanels();
            });
            
            // PDF生成ボタン
            document.getElementById('generate-pdf-btn').addEventListener('click', function() {
                console.log('PDF生成ボタンクリック');
                generatePDF();
            });
            
            // Google Maps APIを読み込み
            loadGoogleMaps();
        });
    </script>
</body>
</html>```

</details>

### ⚠️ 重要な設定箇所（2箇所のみ）

1. **562行目付近** - Cloud Run APIのURL：
```javascript
const API_BASE_URL = "https://your-cloud-run-url.run.app";  // あなたのCloud Run URLに変更
```

2. **563行目付近** - Google Maps APIキー：
```javascript
const GOOGLE_MAPS_API_KEY = "YOUR_GOOGLE_MAPS_API_KEY";  // あなたのGoogle Maps APIキーに変更
```

### 🔧 修正版の改善点
- 描画ボタンの動作問題を修正
- Google Maps APIの動的ロード
- エラーハンドリングの強化
- API接続状態の表示
- デバッグログの追加

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
