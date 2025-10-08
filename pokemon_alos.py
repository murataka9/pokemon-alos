"""
ポケモンALOsクラス: 各ポケモンのALOs表現とシミュレーション
"""
from typing import Dict, List, Tuple, Optional
import random
import numpy as np


class PokemonALOs:
    """個別のポケモンALOsを表現するクラス"""
    
    def __init__(self, pokemon_key: str, pokemon_data: Dict, alos_definition: Dict = None):
        """
        Args:
            pokemon_key: ポケモンの識別キー (pikachu, meowth, sprigatito)
            pokemon_data: ポケモンの基本データ
            alos_definition: ALOsシステムから生成された定義
        """
        self.key = pokemon_key
        self.name = pokemon_data['name']
        self.owner = pokemon_data['owner']
        self.species = pokemon_data['species']
        self.type = pokemon_data['type']
        self.personality = pokemon_data['personality']
        self.base_abilities = pokemon_data['abilities']
        
        # 状態管理
        self.position = self._random_position()
        self.hp = 100
        self.energy = 100
        self.mood = "normal"  # normal, happy, angry, tired, excited
        self.current_abilities = self.base_abilities.copy()
        self.relationships = {}  # {pokemon_key: friendship_level (-100 to 100)}
        self.inventory = []  # 持っているアイテム
        self.max_inventory = 3  # 最大所持数
        
        # ALOs定義
        self.alos_definition = alos_definition or {}
        
        # 履歴
        self.action_history = []
        
    def _random_position(self) -> Tuple[float, float]:
        """ランダムな初期位置を生成 (0-10の範囲)"""
        return (random.uniform(0, 10), random.uniform(0, 10))
    
    def update_position(self, dx: float, dy: float):
        """位置を更新（境界チェック付き）"""
        x, y = self.position
        x = max(0, min(10, x + dx))
        y = max(0, min(10, y + dy))
        self.position = (x, y)
    
    def move_towards(self, target_pos: Tuple[float, float], speed: float = 0.3):
        """ターゲット位置に向かって移動"""
        x, y = self.position
        tx, ty = target_pos
        
        dx = tx - x
        dy = ty - y
        dist = np.sqrt(dx**2 + dy**2)
        
        if dist > 0:
            dx = (dx / dist) * speed
            dy = (dy / dist) * speed
            self.update_position(dx, dy)
    
    def move_away(self, target_pos: Tuple[float, float], speed: float = 0.3):
        """ターゲット位置から離れる"""
        x, y = self.position
        tx, ty = target_pos
        
        dx = x - tx
        dy = y - ty
        dist = np.sqrt(dx**2 + dy**2)
        
        if dist > 0:
            dx = (dx / dist) * speed
            dy = (dy / dist) * speed
            self.update_position(dx, dy)
    
    def random_walk(self, speed: float = 0.2):
        """ランダムに移動"""
        dx = random.uniform(-speed, speed)
        dy = random.uniform(-speed, speed)
        self.update_position(dx, dy)
    
    def distance_to(self, other: 'PokemonALOs') -> float:
        """他のポケモンまでの距離を計算"""
        x1, y1 = self.position
        x2, y2 = other.position
        return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
    def take_damage(self, damage: int):
        """ダメージを受ける"""
        self.hp = max(0, self.hp - damage)
        self.energy = max(0, self.energy - 5)
        if self.hp < 30:
            self.mood = "tired"
        elif self.hp < 60:
            self.mood = "angry"
    
    def heal(self, amount: int):
        """回復する"""
        self.hp = min(100, self.hp + amount)
        if self.hp > 70:
            self.mood = "happy"
    
    def rest(self):
        """休憩する"""
        self.energy = min(100, self.energy + 10)
        self.hp = min(100, self.hp + 3)
        if self.energy > 80:
            self.mood = "normal"
    
    def learn_move(self, move_name: str):
        """新しい技を覚える"""
        if move_name not in self.current_abilities:
            self.current_abilities.append(move_name)
            self.mood = "excited"
    
    def update_relationship(self, other_key: str, change: int):
        """他のポケモンとの関係性を更新"""
        current = self.relationships.get(other_key, 0)
        self.relationships[other_key] = max(-100, min(100, current + change))
    
    def get_relationship(self, other_key: str) -> int:
        """他のポケモンとの関係性を取得"""
        return self.relationships.get(other_key, 0)
    
    def add_action(self, action: Dict):
        """行動履歴に追加"""
        self.action_history.append(action)
        # 履歴は最大50件まで
        if len(self.action_history) > 50:
            self.action_history.pop(0)
    
    def add_item(self, item) -> bool:
        """
        アイテムを追加
        
        Args:
            item: 追加するアイテム
            
        Returns:
            追加できたかどうか
        """
        if len(self.inventory) < self.max_inventory:
            self.inventory.append(item)
            return True
        return False
    
    def use_item(self, item_index: int = 0) -> Optional[str]:
        """
        アイテムを使用
        
        Args:
            item_index: 使用するアイテムのインデックス
            
        Returns:
            効果の説明文
        """
        if 0 <= item_index < len(self.inventory):
            item = self.inventory.pop(item_index)
            return item.use(self)
        return None
    
    def auto_use_item(self) -> Optional[str]:
        """
        必要に応じて自動でアイテムを使用
        
        Returns:
            使用した場合は効果の説明文
        """
        # HPが50以下でHP回復アイテムを持っていたら使う
        if self.hp <= 50:
            for i, item in enumerate(self.inventory):
                if item.effect_type == "hp" or item.effect_type == "mixed":
                    return self.use_item(i)
        
        # Energyが30以下でEnergy回復アイテムを持っていたら使う
        if self.energy <= 30:
            for i, item in enumerate(self.inventory):
                if item.effect_type == "energy" or item.effect_type == "mixed":
                    return self.use_item(i)
        
        # 気分が悪い時にmoodアイテムを持っていたら使う
        if self.mood in ["angry", "tired"]:
            for i, item in enumerate(self.inventory):
                if item.effect_type == "mood":
                    return self.use_item(i)
        
        return None
    
    def to_dict(self) -> Dict:
        """ALOsを辞書形式で出力"""
        return {
            "mainObj": self.name,
            "key": self.key,
            "subObjList": {
                "appearance": {
                    "species": self.species,
                    "type": self.type,
                    "owner": self.owner
                },
                "behavior": {
                    "personality": self.personality,
                    "mood": self.mood
                },
                "skills": {
                    "abilities": self.current_abilities
                },
                "state": {
                    "hp": self.hp,
                    "energy": self.energy,
                    "position": self.position
                },
                "relationships": self.relationships
            },
            "alos_definition": self.alos_definition
        }
    
    def get_color(self) -> str:
        """ポケモンのタイプに基づいた色を返す（可視化用）"""
        type_colors = {
            "でんき": "yellow",
            "ノーマル": "gray",
            "くさ": "green"
        }
        return type_colors.get(self.type, "gray")
    
    def get_mood_color(self) -> Tuple[float, float, float]:
        """ポケモンごとの固定色を返す（RGB, 0-1の範囲）
        
        HPに応じて明度が変化します
        """
        # ポケモンごとの基本色（RGB, 0-1の範囲）
        pokemon_colors = {
            "pikachu": (1.0, 0.9, 0.0),      # 黄色（ピカチュウ）
            "meowth": (0.7, 0.7, 0.7),       # 灰色（ニャース）
            "sprigatito": (0.2, 0.8, 0.3)    # 緑（ニャオハ）
        }
        
        base_color = pokemon_colors.get(self.key, (0.5, 0.5, 0.5))
        
        # HPに基づいて明度を調整（HPが低いと暗くなる）
        hp_factor = max(0.3, self.hp / 100.0)  # 最低でも30%の明度を保つ
        return tuple(c * hp_factor for c in base_color)
    
    def __repr__(self):
        return f"PokemonALOs({self.name}, HP:{self.hp}, Energy:{self.energy}, Mood:{self.mood})"

