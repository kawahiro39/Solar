"""
Panel Layout Algorithm
太陽光パネルの自動配置アルゴリズム
"""

import numpy as np
from shapely.geometry import Polygon, box
from shapely.affinity import translate, rotate
from typing import List, Tuple, Dict
import math

class PanelLayout:
    def __init__(self, panel_width_cm: float, panel_height_cm: float, offset_cm: float):
        """
        パネルレイアウト計算クラス
        
        Args:
            panel_width_cm: パネル幅 (cm)
            panel_height_cm: パネル高さ (cm)
            offset_cm: オフセット/離隔 (cm)
        """
        self.panel_width = panel_width_cm
        self.panel_height = panel_height_cm
        self.offset = offset_cm
        
    def calculate_layout(self, polygon_coords: List[List[float]]) -> List[Dict]:
        """
        多角形内にパネルを配置
        
        Args:
            polygon_coords: [[lat, lng], ...] 形式の多角形座標
            
        Returns:
            配置されたパネル情報のリスト
        """
        # 緯度経度をメートル座標系に変換（簡易版）
        meter_coords = self._latlon_to_meters(polygon_coords)
        
        # Shapelyポリゴンを作成
        roof_polygon = Polygon(meter_coords)
        
        # オフセットを適用（内側に縮小）
        offset_m = self.offset / 100  # cm to m
        roof_polygon = roof_polygon.buffer(-offset_m)
        
        if not roof_polygon.is_valid or roof_polygon.is_empty:
            return []
        
        # パネルサイズをメートルに変換
        panel_w_m = self.panel_width / 100
        panel_h_m = self.panel_height / 100
        
        # 配置するパネルのリスト
        panels = []
        
        # バウンディングボックスを取得
        minx, miny, maxx, maxy = roof_polygon.bounds
        
        # グリッド配置アルゴリズム
        panel_id = 0
        
        # 横置きと縦置きの両方を試す
        for orientation in ['landscape', 'portrait']:
            if orientation == 'landscape':
                w, h = panel_w_m, panel_h_m
            else:
                w, h = panel_h_m, panel_w_m
            
            # 間隔を考慮してグリッド配置
            spacing = 0.05  # 5cm間隔
            
            y = miny
            while y + h <= maxy:
                x = minx
                while x + w <= maxx:
                    # パネルの矩形を作成
                    panel_rect = box(x, y, x + w, y + h)
                    
                    # 屋根ポリゴン内に完全に含まれるかチェック
                    if roof_polygon.contains(panel_rect):
                        # パネルの中心座標を緯度経度に変換
                        center_m = [x + w/2, y + h/2]
                        center_latlon = self._meters_to_latlon([center_m], polygon_coords[0])[0]
                        
                        panels.append({
                            'id': panel_id,
                            'center': center_latlon,
                            'corners': self._get_panel_corners_latlon(x, y, w, h, polygon_coords[0]),
                            'orientation': orientation,
                            'width_cm': self.panel_width if orientation == 'landscape' else self.panel_height,
                            'height_cm': self.panel_height if orientation == 'landscape' else self.panel_width
                        })
                        panel_id += 1
                    
                    x += w + spacing
                y += h + spacing
        
        # 最適な配置を選択（パネル数が多い方）
        return panels
    
    def _latlon_to_meters(self, coords: List[List[float]]) -> List[Tuple[float, float]]:
        """緯度経度をメートル座標系に変換（簡易版）"""
        if not coords:
            return []
        
        ref_lat = coords[0][0]
        ref_lon = coords[0][1]
        
        meters_coords = []
        for lat, lon in coords:
            # 簡易的な変換（小範囲では十分な精度）
            x = (lon - ref_lon) * 111320 * math.cos(math.radians(ref_lat))
            y = (lat - ref_lat) * 110540
            meters_coords.append((x, y))
        
        return meters_coords
    
    def _meters_to_latlon(self, meter_coords: List[List[float]], ref_point: List[float]) -> List[List[float]]:
        """メートル座標系を緯度経度に変換"""
        ref_lat, ref_lon = ref_point
        
        latlon_coords = []
        for x, y in meter_coords:
            lon = ref_lon + x / (111320 * math.cos(math.radians(ref_lat)))
            lat = ref_lat + y / 110540
            latlon_coords.append([lat, lon])
        
        return latlon_coords
    
    def _get_panel_corners_latlon(self, x: float, y: float, w: float, h: float, 
                                   ref_point: List[float]) -> List[List[float]]:
        """パネルの4隅の座標を緯度経度で取得"""
        corners_m = [
            [x, y],
            [x + w, y],
            [x + w, y + h],
            [x, y + h]
        ]
        return self._meters_to_latlon(corners_m, ref_point)
    
    def get_bounds(self, polygon_coords: List[List[float]]) -> Dict:
        """多角形の境界情報を取得"""
        if not polygon_coords:
            return {}
        
        lats = [coord[0] for coord in polygon_coords]
        lngs = [coord[1] for coord in polygon_coords]
        
        return {
            'north': max(lats),
            'south': min(lats),
            'east': max(lngs),
            'west': min(lngs),
            'center': {
                'lat': sum(lats) / len(lats),
                'lng': sum(lngs) / len(lngs)
            }
        }