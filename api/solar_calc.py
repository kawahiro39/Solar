"""
Solar Calculation Module
日射量計算と発電量シミュレーション
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import math

class SolarCalculator:
    def __init__(self):
        """太陽光発電量計算クラス"""
        # システム効率係数
        self.system_efficiency = 0.85  # システム全体の効率（85%）
        self.panel_efficiency = 0.20   # パネル効率（20%）
        self.temperature_coefficient = -0.004  # 温度係数（-0.4%/℃）
        self.standard_temperature = 25  # 標準テスト条件温度（℃）
        
    def calculate_power(self, latitude: float, longitude: float, 
                       panel_count: int, panel_area_m2: float) -> Dict:
        """
        発電量を計算
        
        Args:
            latitude: 緯度
            longitude: 経度  
            panel_count: パネル枚数
            panel_area_m2: 1枚あたりのパネル面積（m²）
            
        Returns:
            発電量データ
        """
        # 年間の月別データを計算
        monthly_data = []
        yearly_total = 0
        
        for month in range(1, 13):
            # 月別の平均日射量を取得（簡易計算）
            daily_irradiance = self._get_monthly_irradiance(latitude, month)
            
            # 月の日数
            days_in_month = self._get_days_in_month(month)
            
            # 月間発電量計算
            # 発電量 = 日射量 × パネル面積 × パネル枚数 × パネル効率 × システム効率 × 日数
            monthly_generation = (
                daily_irradiance * 
                panel_area_m2 * 
                panel_count * 
                self.panel_efficiency * 
                self.system_efficiency * 
                days_in_month
            )
            
            monthly_data.append({
                'month': month,
                'generation_kwh': round(monthly_generation / 1000, 2),  # Wh to kWh
                'daily_irradiance': round(daily_irradiance, 2)
            })
            
            yearly_total += monthly_generation
        
        # パネル1枚あたりの定格出力（W）
        panel_rated_power = panel_area_m2 * 1000 * self.panel_efficiency  # 1000W/m² × 面積 × 効率
        
        return {
            'yearly_total_kwh': round(yearly_total / 1000, 2),
            'monthly_data': monthly_data,
            'panel_info': {
                'count': panel_count,
                'total_area_m2': round(panel_area_m2 * panel_count, 2),
                'rated_power_per_panel_w': round(panel_rated_power, 0),
                'total_rated_power_kw': round(panel_rated_power * panel_count / 1000, 2)
            },
            'assumptions': {
                'system_efficiency': f'{self.system_efficiency * 100}%',
                'panel_efficiency': f'{self.panel_efficiency * 100}%',
                'location': {
                    'latitude': latitude,
                    'longitude': longitude
                }
            }
        }
    
    def get_irradiance_data(self, latitude: float, longitude: float) -> Dict:
        """
        指定地点の年間日射量データを取得
        
        Args:
            latitude: 緯度
            longitude: 経度
            
        Returns:
            日射量データ
        """
        monthly_irradiance = []
        
        for month in range(1, 13):
            irradiance = self._get_monthly_irradiance(latitude, month)
            monthly_irradiance.append({
                'month': month,
                'month_name': self._get_month_name(month),
                'daily_average_kwh_m2': round(irradiance / 1000, 3)
            })
        
        # 年間平均
        yearly_average = sum([m['daily_average_kwh_m2'] for m in monthly_irradiance]) / 12
        
        return {
            'location': {
                'latitude': latitude,
                'longitude': longitude
            },
            'monthly_data': monthly_irradiance,
            'yearly_average_daily_kwh_m2': round(yearly_average, 3),
            'annual_total_kwh_m2': round(yearly_average * 365, 1)
        }
    
    def _get_monthly_irradiance(self, latitude: float, month: int) -> float:
        """
        月別の平均日射量を取得（Wh/m²/day）
        簡易的な計算式を使用（実際にはNEDO等のデータベースを使用すべき）
        """
        # 日本の緯度に基づく簡易計算
        # 基準値（東京付近、年間平均）
        base_irradiance = 3800  # Wh/m²/day
        
        # 季節変動係数
        seasonal_factors = {
            1: 0.7,   # 1月
            2: 0.8,   # 2月
            3: 0.95,  # 3月
            4: 1.1,   # 4月
            5: 1.2,   # 5月
            6: 1.0,   # 6月（梅雨）
            7: 1.1,   # 7月
            8: 1.15,  # 8月
            9: 0.95,  # 9月
            10: 0.85, # 10月
            11: 0.75, # 11月
            12: 0.65  # 12月
        }
        
        # 緯度による補正（北に行くほど減少）
        latitude_factor = 1.0 - (abs(latitude - 35.0) * 0.02)
        latitude_factor = max(0.7, min(1.3, latitude_factor))
        
        # 最終的な日射量
        monthly_irradiance = base_irradiance * seasonal_factors[month] * latitude_factor
        
        return monthly_irradiance
    
    def _get_days_in_month(self, month: int) -> int:
        """月の日数を取得"""
        days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        return days[month - 1]
    
    def _get_month_name(self, month: int) -> str:
        """月名を取得"""
        months = ['January', 'February', 'March', 'April', 'May', 'June',
                 'July', 'August', 'September', 'October', 'November', 'December']
        return months[month - 1]
    
    def calculate_roi(self, installation_cost: float, yearly_generation_kwh: float,
                     electricity_price_per_kwh: float = 30) -> Dict:
        """
        投資回収期間を計算
        
        Args:
            installation_cost: 設置費用（円）
            yearly_generation_kwh: 年間発電量（kWh）
            electricity_price_per_kwh: 電力単価（円/kWh）
            
        Returns:
            投資回収データ
        """
        yearly_savings = yearly_generation_kwh * electricity_price_per_kwh
        payback_period = installation_cost / yearly_savings if yearly_savings > 0 else float('inf')
        
        # 20年間の累積データ
        cumulative_data = []
        for year in range(1, 21):
            # 経年劣化を考慮（年0.5%低下）
            degradation_factor = (1 - 0.005) ** (year - 1)
            yearly_generation_adjusted = yearly_generation_kwh * degradation_factor
            yearly_savings_adjusted = yearly_generation_adjusted * electricity_price_per_kwh
            
            cumulative_savings = sum([
                yearly_generation_kwh * ((1 - 0.005) ** y) * electricity_price_per_kwh
                for y in range(year)
            ])
            
            cumulative_data.append({
                'year': year,
                'generation_kwh': round(yearly_generation_adjusted, 0),
                'savings_yen': round(yearly_savings_adjusted, 0),
                'cumulative_savings_yen': round(cumulative_savings, 0),
                'net_benefit_yen': round(cumulative_savings - installation_cost, 0)
            })
        
        return {
            'payback_period_years': round(payback_period, 1),
            'yearly_savings_yen': round(yearly_savings, 0),
            'twenty_year_total_savings_yen': round(cumulative_data[-1]['cumulative_savings_yen'], 0),
            'twenty_year_net_benefit_yen': round(cumulative_data[-1]['net_benefit_yen'], 0),
            'yearly_data': cumulative_data[:10]  # 最初の10年分のみ返す
        }