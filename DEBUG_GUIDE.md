# デバッグガイド - 屋根描画ボタンが動作しない場合

## 問題の確認手順

### 1. ブラウザコンソールを開く
- Chrome/Edge: F12キー または 右クリック → 検証
- Console タブを選択

### 2. エラーメッセージを確認

#### ケース1: Google Maps APIエラー
```
Google Maps JavaScript API error: InvalidKeyMapError
```
**解決方法**: 
- Google Maps APIキーが正しいか確認
- APIキーに Maps JavaScript API が有効になっているか確認
- HTTPリファラー制限を確認

#### ケース2: Drawing ライブラリが読み込まれていない
```
google.maps.drawing is undefined
```
**解決方法**:
- URLに `&libraries=drawing,geometry` が含まれているか確認
- APIキーの設定を確認

#### ケース3: CORS エラー
```
Access to fetch at 'https://...' from origin 'null' has been blocked by CORS policy
```
**解決方法**:
- Cloud Run APIのCORS設定を確認
- `api/main.py` の CORS設定でBubbleドメインを許可

## 修正版HTMLの使用方法

### 1. 最新の修正版を使用
`frontend/bubble-embed-fixed.html` を使用してください。

### 2. 設定箇所（2箇所のみ）
```javascript
// 523行目付近
const API_BASE_URL = 'https://your-cloud-run-url.run.app';

// 524行目付近  
const GOOGLE_MAPS_API_KEY = 'YOUR_GOOGLE_MAPS_API_KEY';
```

### 3. Bubbleでの設定
- HTML要素の「Run mode」を「Every time element is visible」に設定
- 高さを最小800pxに設定

## 動作確認チェックリスト

### ✅ 初期表示
- [ ] マップが表示される
- [ ] 衛星写真モードになっている
- [ ] 「API接続: 正常」が表示される（一時的）

### ✅ 描画機能
- [ ] 「屋根を描画」ボタンをクリックできる
- [ ] クリック後、マップの枠が青く光る
- [ ] マップ上をクリックすると赤い点が表示される
- [ ] 3点以上クリックで多角形が作成される
- [ ] 最後の点をクリックで描画完了

### ✅ パネル配置
- [ ] 「パネル配置」ボタンが有効になる
- [ ] クリックで青いパネルが表示される
- [ ] 結果が下部に表示される

## トラブルシューティング

### 問題: ボタンをクリックしても何も起きない

**確認事項**:
1. コンソールにエラーが出ていないか
2. `initMap` 関数が呼ばれているか（コンソールに「Google Maps初期化開始」が表示されるか）

**デバッグコード追加**:
```javascript
// ボタンクリックの確認
document.getElementById('draw-mode-btn').addEventListener('click', function() {
    console.log('ボタンがクリックされました');
    console.log('drawingManager:', drawingManager);
    console.log('isDrawingMode:', isDrawingMode);
});
```

### 問題: マップは表示されるが描画できない

**確認事項**:
1. Drawing ライブラリが読み込まれているか
```javascript
console.log('Drawing API:', typeof google.maps.drawing);
```

2. DrawingManagerが初期化されているか
```javascript
console.log('DrawingManager:', drawingManager);
```

### 問題: 描画はできるがAPIエラーになる

**確認事項**:
1. Cloud Run URLが正しいか
2. Cloud Runサービスが起動しているか
3. CORS設定が正しいか

**テストコード**:
```javascript
// API接続テスト
fetch('https://your-cloud-run-url.run.app/health')
    .then(r => r.json())
    .then(d => console.log('API応答:', d))
    .catch(e => console.error('APIエラー:', e));
```

## ログ出力の見方

正常な動作時のログ順序:
1. `DOM読み込み完了`
2. `Google Maps初期化開始`
3. `Google Maps初期化完了`
4. `描画ボタンクリック`
5. `描画モード開始`
6. `ポリゴン描画完了`
7. `計算ボタンクリック`
8. `パネル配置計算結果: {データ}`

## 最終手段

それでも動作しない場合:

1. **シンプルなテスト**:
```html
<!DOCTYPE html>
<html>
<head>
    <script>
        function initMap() {
            var map = new google.maps.Map(document.getElementById('map'), {
                center: {lat: 35.6762, lng: 139.6503},
                zoom: 15
            });
            console.log('マップ初期化成功');
        }
    </script>
</head>
<body>
    <div id="map" style="height: 400px;"></div>
    <script async defer
        src="https://maps.googleapis.com/maps/api/js?key=YOUR_KEY&callback=initMap">
    </script>
</body>
</html>
```

2. **サポート連絡先**:
- Google Maps APIの問題: [Google Maps Platform Support](https://developers.google.com/maps/support)
- Cloud Runの問題: [Google Cloud Support](https://cloud.google.com/support)
- Bubbleの問題: [Bubble Forum](https://forum.bubble.io/)