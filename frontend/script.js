/**
 * 太陽光パネル配置シミュレーション - メインJavaScript
 */

// API設定 - Cloud RunのURLに置き換える
const API_BASE_URL = 'https://your-cloud-run-url.run.app';  // TODO: デプロイ後に更新

// グローバル変数
let map;
let drawingManager;
let currentPolygon = null;
let panelMarkers = [];
let simulationData = null;

/**
 * Google Maps初期化
 */
function initMap() {
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
        drawingControl: false,
        polygonOptions: {
            fillColor: '#FF0000',
            fillOpacity: 0.3,
            strokeColor: '#FF0000',
            strokeWeight: 2,
            editable: true,
            draggable: false
        }
    });

    drawingManager.setMap(map);

    // ポリゴン完成時のイベント
    google.maps.event.addListener(drawingManager, 'polygoncomplete', function(polygon) {
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
            },
            () => {
                console.log('位置情報の取得に失敗しました');
            }
        );
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
    drawingManager.setDrawingMode(null);
    
    // ボタンの状態を更新
    document.getElementById('calculate-btn').disabled = false;
    document.getElementById('draw-mode-btn').textContent = '編集モード';
    
    // 頂点変更時のイベント
    google.maps.event.addListener(polygon.getPath(), 'set_at', updatePolygon);
    google.maps.event.addListener(polygon.getPath(), 'insert_at', updatePolygon);
    
    showStatus('屋根の形状を描画しました', 'success');
}

/**
 * ポリゴン更新時の処理
 */
function updatePolygon() {
    clearPanels();
    document.getElementById('generate-pdf-btn').disabled = true;
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
            address: '日本' // TODO: Geocoding APIで実際の住所を取得
        }
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/calculate-panels`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        });
        
        if (!response.ok) throw new Error('計算に失敗しました');
        
        const data = await response.json();
        simulationData = data;
        
        // パネルを地図上に表示
        displayPanels(data.panels);
        
        // 結果を表示
        displayResults(data);
        
        // PDFボタンを有効化
        document.getElementById('generate-pdf-btn').disabled = false;
        
        showStatus(`${data.panel_count}枚のパネルを配置しました`, 'success');
        
    } catch (error) {
        console.error('Error:', error);
        showStatus('パネル配置の計算に失敗しました', 'error');
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
        // Google Maps画像をキャプチャ（簡易版）
        // 実際にはGoogle Static Maps APIを使用する
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
            body: JSON.stringify(requestData)
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
    // 描画モードボタン
    document.getElementById('draw-mode-btn').addEventListener('click', function() {
        if (drawingManager.getDrawingMode()) {
            drawingManager.setDrawingMode(null);
            this.textContent = '屋根を描画';
        } else {
            drawingManager.setDrawingMode(google.maps.drawing.OverlayType.POLYGON);
            this.textContent = '描画中...';
        }
    });
    
    // クリアボタン
    document.getElementById('clear-polygon-btn').addEventListener('click', function() {
        if (currentPolygon) {
            currentPolygon.setMap(null);
            currentPolygon = null;
        }
        clearPanels();
        document.getElementById('calculate-btn').disabled = true;
        document.getElementById('generate-pdf-btn').disabled = true;
        document.getElementById('results').classList.add('hidden');
        showStatus('描画をクリアしました', 'info');
    });
    
    // パネル配置ボタン
    document.getElementById('calculate-btn').addEventListener('click', calculatePanels);
    
    // PDF生成ボタン
    document.getElementById('generate-pdf-btn').addEventListener('click', generatePDF);
});