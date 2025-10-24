# Solar Layout Simulation System

このリポジトリは Google Cloud Run 上で動作する FastAPI ベースの API と、Bubble アプリに埋め込める HTML スニペットを利用した太陽光パネル設置シミュレーションのリファレンス実装です。ユーザーは対象となる住宅の屋根形状を描画し、パネルタイプと配置基準を選択すると、API が配置レイアウトと年間発電量を計算し、PDF レポートを生成します。

## 構成概要

- **FastAPI サービス** (`app/`)
  - `GET /panel-types`: 登録済みパネル一覧 (初期値 5 パターン)
  - `POST /simulate`: 屋根形状と配置条件からレイアウトと年間発電量を計算
  - `POST /report`: シミュレーション結果から 2 ページ構成の PDF を生成 (1 ページ目: 屋根レイアウト、2 ページ目: 年間発電シミュレーション)
- **Dockerfile**: Cloud Run へデプロイ可能なコンテナイメージを作成
- **Bubble 用 HTML**: Leaflet を使った地図 UI、屋根ポリゴンの描画、パネル・配置基準の選択、レイアウト表示、PDF レポート取得が可能

## ローカル実行

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

`http://127.0.0.1:8000/docs` で自動生成された API ドキュメントを確認できます。

## Cloud Run へのデプロイ手順

1. プロジェクト ID とリージョンを設定
   ```bash
   export PROJECT_ID="your-gcp-project"
   export REGION="asia-northeast1"
   gcloud config set project "$PROJECT_ID"
   gcloud config set run/region "$REGION"
   ```
2. コンテナイメージのビルドと Artifact Registry への push
   ```bash
   gcloud builds submit --tag "asia-northeast1-docker.pkg.dev/$PROJECT_ID/solar-sim/app"
   ```
3. Cloud Run へデプロイ
   ```bash
   gcloud run deploy solar-sim \
     --image="asia-northeast1-docker.pkg.dev/$PROJECT_ID/solar-sim/app" \
     --allow-unauthenticated \
     --port=8080
   ```
   デプロイ後に表示される URL (`https://solar-sim-xxxxxx-uc.a.run.app` など) を Bubble 側の HTML から利用します。

## API リクエスト例

```bash
curl -X POST "https://<cloud-run-host>/simulate" \
  -H "Content-Type: application/json" \
  -d '{
    "roof_polygon": [
      {"x": 0, "y": 0},
      {"x": 8, "y": 0},
      {"x": 8, "y": 6},
      {"x": 2, "y": 6},
      {"x": 0, "y": 3}
    ],
    "panel_type_id": "standard",
    "alignment": "center"
  }'
```

## Bubble で利用する HTML

以下の HTML を Bubble の HTML 要素に貼り付け、`CLOUD_RUN_BASE_URL` をデプロイ済み API の URL に置き換えてください。

```html
<div id="solar-app" style="font-family: 'Noto Sans JP', sans-serif;">
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <link rel="stylesheet" href="https://unpkg.com/leaflet-draw@1.0.4/dist/leaflet.draw.css" />
  <style>
    #map { height: 400px; margin-bottom: 1rem; }
    .controls { display: flex; flex-wrap: wrap; gap: 1rem; }
    .controls label { display: block; font-weight: 600; margin-bottom: 0.25rem; }
    .controls select, .controls button { padding: 0.5rem; min-width: 160px; }
    .results { margin-top: 1rem; background: #f8f9fa; padding: 1rem; border-radius: 8px; }
    .panel { fill: rgba(76, 175, 80, 0.7); stroke: #2e7d32; stroke-width: 1; }
  </style>
  <div id="map"></div>
  <div class="controls">
    <div>
      <label for="manufacturer-select">メーカー</label>
      <select id="manufacturer-select"></select>
    </div>
    <div>
      <label for="series-select">シリーズ</label>
      <select id="series-select"></select>
    </div>
    <div>
      <label for="panel-select">パネル</label>
      <select id="panel-select"></select>
    </div>
    <div>
      <label for="alignment-select">配置基準</label>
      <select id="alignment-select">
        <option value="left">左寄せ</option>
        <option value="center" selected>中央</option>
        <option value="right">右寄せ</option>
      </select>
    </div>
    <div style="align-self: flex-end;">
      <button id="simulate-btn">配置</button>
      <button id="report-btn" disabled>レポート生成</button>
    </div>
  </div>
  <div class="results" id="results" hidden>
    <div>パネル枚数: <span id="panel-count"></span></div>
    <div>総容量 (kW): <span id="capacity"></span></div>
    <div>推定年間発電量 (kWh): <span id="annual"></span></div>
    <a id="report-link" download="solar-simulation-report.pdf">PDFをダウンロード</a>
  </div>
</div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://unpkg.com/leaflet-draw@1.0.4/dist/leaflet.draw.js"></script>
<script>
  const CLOUD_RUN_BASE_URL = 'https://your-cloud-run-url';
  const map = L.map('map').setView([35.6804, 139.7690], 18);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 22,
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map);

  const drawnItems = new L.FeatureGroup();
  map.addLayer(drawnItems);
  const panelLayer = L.layerGroup().addTo(map);

  const drawControl = new L.Control.Draw({
    draw: {
      marker: false,
      circle: false,
      circlemarker: false,
      polyline: false,
      rectangle: false,
      polygon: { allowIntersection: false, showArea: true }
    },
    edit: {
      featureGroup: drawnItems
    }
  });
  map.addControl(drawControl);

  let currentSimulation = null;
  const DEFAULT_PANEL_CATALOG = {
    "canadian-solar": {
      id: "canadian-solar",
      name: "カナディアンソーラー",
      series: {
        tophiku6: {
          id: "tophiku6",
          name: "TOPHiKu6",
          allow_mixing_within_series: true,
          panels: {
            "CS6.2-48TM-455": {
              id: "CS6.2-48TM-455",
              name: "CS6.2-48TM-455",
              width: 1.134,
              height: 1.762,
              capacity_kw: 0.455
            },
            "CS6.2-36TM-340": {
              id: "CS6.2-36TM-340",
              name: "CS6.2-36TM-340",
              width: 1.134,
              height: 1.334,
              capacity_kw: 0.34
            },
            "CS6.2-32TM-300": {
              id: "CS6.2-32TM-300",
              name: "CS6.2-32TM-300",
              width: 0.767,
              height: 1.762,
              capacity_kw: 0.3
            }
          }
        }
      }
    },
    generic: {
      id: "generic",
      name: "汎用パネル",
      series: {
        reference: {
          id: "reference",
          name: "リファレンス",
          allow_mixing_within_series: true,
          panels: {
            compact: {
              id: "compact",
              name: "Compact 320W",
              width: 0.99,
              height: 1.65,
              capacity_kw: 0.32
            },
            standard: {
              id: "standard",
              name: "Standard 400W",
              width: 1.0,
              height: 1.7,
              capacity_kw: 0.4
            },
            premium: {
              id: "premium",
              name: "Premium 450W",
              width: 1.05,
              height: 1.8,
              capacity_kw: 0.45
            },
            wide: {
              id: "wide",
              name: "Wide 500W",
              width: 1.2,
              height: 1.6,
              capacity_kw: 0.5
            },
            ultra: {
              id: "ultra",
              name: "Ultra 550W",
              width: 1.1,
              height: 2.1,
              capacity_kw: 0.55
            }
          }
        }
      }
    }
  };
  let panelCatalog = JSON.parse(JSON.stringify(DEFAULT_PANEL_CATALOG));
  let selectedPanelId = null;

  function formatPanelLabel(panel) {
    const heightMm = Math.round(panel.height * 1000);
    const widthMm = Math.round(panel.width * 1000);
    const capacityW = Math.round(panel.capacity_kw * 1000);
    return `${panel.name} (${heightMm}mm×${widthMm}mm ${capacityW}W)`;
  }

  function updatePanelOptions(series, preferredPanelId) {
    const panelSelect = document.getElementById('panel-select');
    panelSelect.innerHTML = '';

    Object.values(series.panels).forEach(panel => {
      const option = document.createElement('option');
      option.value = panel.id;
      option.textContent = formatPanelLabel(panel);
      panelSelect.appendChild(option);
    });

    const defaultPanelId = preferredPanelId && series.panels[preferredPanelId]
      ? preferredPanelId
      : (series.panels['CS6.2-48TM-455'] ? 'CS6.2-48TM-455' : (panelSelect.options[0] ? panelSelect.options[0].value : null));
    if (defaultPanelId) {
      panelSelect.value = defaultPanelId;
    }
    selectedPanelId = panelSelect.value || null;
  }

  function updateSeriesOptions(manufacturer, preferences = {}) {
    const seriesSelect = document.getElementById('series-select');
    seriesSelect.innerHTML = '';

    Object.values(manufacturer.series).forEach(series => {
      const option = document.createElement('option');
      option.value = series.id;
      option.textContent = series.name;
      seriesSelect.appendChild(option);
    });

    const defaultSeriesId = preferences.seriesId && manufacturer.series[preferences.seriesId]
      ? preferences.seriesId
      : (manufacturer.series['tophiku6'] ? 'tophiku6' : (seriesSelect.options[0] ? seriesSelect.options[0].value : null));
    if (defaultSeriesId) {
      seriesSelect.value = defaultSeriesId;
    }

    const selectedSeries = manufacturer.series[seriesSelect.value];
    if (selectedSeries) {
      updatePanelOptions(selectedSeries, preferences.panelId);
    }
  }

  function populateManufacturerOptions(preferences = {}) {
    const manufacturerSelect = document.getElementById('manufacturer-select');
    manufacturerSelect.innerHTML = '';

    Object.values(panelCatalog).forEach(manufacturer => {
      const option = document.createElement('option');
      option.value = manufacturer.id;
      option.textContent = manufacturer.name;
      manufacturerSelect.appendChild(option);
    });

    const defaultManufacturerId = preferences.manufacturerId && panelCatalog[preferences.manufacturerId]
      ? preferences.manufacturerId
      : (panelCatalog['canadian-solar'] ? 'canadian-solar' : (manufacturerSelect.options[0] ? manufacturerSelect.options[0].value : null));
    if (defaultManufacturerId) {
      manufacturerSelect.value = defaultManufacturerId;
    }

    const selectedManufacturer = panelCatalog[manufacturerSelect.value];
    if (selectedManufacturer) {
      updateSeriesOptions(selectedManufacturer, preferences);
    }
  }

  async function fetchPanelTypes() {
    try {
      const res = await fetch(`${CLOUD_RUN_BASE_URL}/panel-types`);
      if (!res.ok) {
        throw new Error(`Failed to fetch panel catalog: ${res.status}`);
      }
      const fetchedCatalog = await res.json();
      const preferences = {
        manufacturerId: document.getElementById('manufacturer-select').value,
        seriesId: document.getElementById('series-select').value,
        panelId: document.getElementById('panel-select').value
      };
      panelCatalog = fetchedCatalog;
      populateManufacturerOptions(preferences);
    } catch (error) {
      console.warn('パネル情報の取得に失敗したため、標準パネルを利用します。', error);
      panelCatalog = JSON.parse(JSON.stringify(DEFAULT_PANEL_CATALOG));
      populateManufacturerOptions();
    }
  }

  document.getElementById('manufacturer-select').addEventListener('change', (event) => {
    const manufacturer = panelCatalog[event.target.value];
    if (manufacturer) {
      updateSeriesOptions(manufacturer);
    }
  });

  document.getElementById('series-select').addEventListener('change', (event) => {
    const manufacturerId = document.getElementById('manufacturer-select').value;
    const manufacturer = panelCatalog[manufacturerId];
    if (!manufacturer) return;
    const series = manufacturer.series[event.target.value];
    if (series) {
      updatePanelOptions(series);
    }
  });

  document.getElementById('panel-select').addEventListener('change', (event) => {
    selectedPanelId = event.target.value;
  });

  function getPolygonLatLngs() {
    if (drawnItems.getLayers().length === 0) return null;
    return drawnItems.getLayers()[0].getLatLngs()[0];
  }

  function transformToMeters(latLngs) {
    if (!latLngs) return null;
    const origin = latLngs[0];
    return latLngs.map(pt => {
      const dx = (pt.lng - origin.lng) * 111320 * Math.cos(origin.lat * Math.PI / 180);
      const dy = (pt.lat - origin.lat) * 110540;
      return { x: dx, y: dy };
    });
  }

  function metersToLatLng(origin, dx, dy) {
    const lng = origin.lng + (dx / 111320) / Math.cos(origin.lat * Math.PI / 180);
    const lat = origin.lat + (dy / 110540);
    return [lat, lng];
  }

  async function simulate() {
    const latLngs = getPolygonLatLngs();
    const polygon = transformToMeters(latLngs);
    if (!polygon || polygon.length < 3) {
      alert('屋根のポリゴンを描画してください');
      return;
    }
    if (!selectedPanelId) {
      alert('パネルを選択してください');
      return;
    }
    const payload = {
      roof_polygon: polygon,
      panel_type_id: selectedPanelId,
      alignment: document.getElementById('alignment-select').value
    };
    const res = await fetch(`${CLOUD_RUN_BASE_URL}/simulate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      alert('シミュレーションに失敗しました');
      return;
    }
    currentSimulation = await res.json();
    renderPanels(latLngs[0], currentSimulation);
    updateResults(currentSimulation);
    document.getElementById('report-btn').disabled = false;
  }

  function renderPanels(originLatLng, simulation) {
    panelLayer.clearLayers();
    const panelWidth = simulation.panel_width;
    const panelHeight = simulation.panel_height;
    simulation.placements.forEach(placement => {
      const topLeft = metersToLatLng(originLatLng, placement.origin.x, placement.origin.y);
      const bottomRight = metersToLatLng(originLatLng, placement.origin.x + panelWidth, placement.origin.y + panelHeight);
      L.rectangle([topLeft, bottomRight], { className: 'panel-layer panel' }).addTo(panelLayer);
    });
  }

  function updateResults(sim) {
    document.getElementById('results').hidden = false;
    document.getElementById('panel-count').textContent = sim.panel_count;
    document.getElementById('capacity').textContent = sim.total_capacity_kw.toFixed(2);
    document.getElementById('annual').textContent = sim.estimated_annual_output_kwh.toFixed(1);
  }

  async function generateReport() {
    if (!currentSimulation) return;
    const polygon = transformToMeters(getPolygonLatLngs());
    if (!selectedPanelId) {
      alert('パネルを選択してください');
      return;
    }
    const payload = {
      simulation: {
        roof_polygon: polygon,
        panel_type_id: selectedPanelId,
        alignment: document.getElementById('alignment-select').value
      },
      panel_count: currentSimulation.panel_count,
      estimated_annual_output_kwh: currentSimulation.estimated_annual_output_kwh,
      placements: currentSimulation.placements
    };
    const res = await fetch(`${CLOUD_RUN_BASE_URL}/report`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      alert('レポート生成に失敗しました');
      return;
    }
    const data = await res.json();
    document.getElementById('report-link').href = `data:${data.content_type};base64,${data.data_base64}`;
  }

  map.on(L.Draw.Event.CREATED, event => {
    drawnItems.clearLayers();
    panelLayer.clearLayers();
    drawnItems.addLayer(event.layer);
    currentSimulation = null;
    document.getElementById('report-btn').disabled = true;
    document.getElementById('results').hidden = true;
  });

  document.getElementById('simulate-btn').addEventListener('click', simulate);
  document.getElementById('report-btn').addEventListener('click', generateReport);
  populateManufacturerOptions();
  fetchPanelTypes();
</script>
```

> **注意**: Leaflet で描いたポリゴン座標を簡易的にメートルへ変換するため、緯度・経度からの概算式を利用しています。高い精度が必要な場合は、サーバーサイドでの座標変換や測地系ライブラリの利用を検討してください。

## ライセンス

このリファレンス実装は MIT ライセンスで提供されます。
