"""
アイテムシステム: きのみなどのアイテム管理
"""
from typing import Dict, Tuple, Optional
import random


class Item:
    """アイテムの基本クラス"""
    
    def __init__(self, name: str, item_type: str, effect_type: str, effect_value: int):
        """
        Args:
            name: アイテム名
            item_type: アイテムの種類（berry, potion, etc.）
            effect_type: 効果のタイプ（hp, energy, mood）
            effect_value: 効果の値
        """
        self.name = name
        self.item_type = item_type
        self.effect_type = effect_type
        self.effect_value = effect_value
        self.position = None
    
    def get_color(self) -> Tuple[float, float, float]:
        """アイテムの色を返す（RGB, 0-1の範囲）"""
        # アイテムタイプに応じた色
        colors = {
            "hp": (1.0, 0.4, 0.4),      # 赤系（HP回復）
            "energy": (0.4, 0.8, 1.0),  # 青系（Energy回復）
            "mood": (1.0, 0.8, 0.4),    # 黄系（気分改善）
            "mixed": (0.8, 0.4, 1.0)    # 紫系（複合効果）
        }
        return colors.get(self.effect_type, (0.5, 0.5, 0.5))
    
    def get_emoji(self) -> str:
        """アイテムの絵文字を返す"""
        emojis = {
            "hp": "🍎",
            "energy": "🍇",
            "mood": "🍌",
            "mixed": "🍊"
        }
        return emojis.get(self.effect_type, "🍓")
    
    def use(self, pokemon) -> str:
        """
        アイテムを使用
        
        Args:
            pokemon: 使用するポケモン
            
        Returns:
            効果の説明文
        """
        if self.effect_type == "hp":
            old_hp = pokemon.hp
            pokemon.heal(self.effect_value)
            return f"{pokemon.name}はHPが{pokemon.hp - old_hp:.0f}回復した！"
        
        elif self.effect_type == "energy":
            old_energy = pokemon.energy
            pokemon.energy = min(100, pokemon.energy + self.effect_value)
            return f"{pokemon.name}はEnergyが{pokemon.energy - old_energy:.0f}回復した！"
        
        elif self.effect_type == "mood":
            if pokemon.mood in ["angry", "tired"]:
                pokemon.mood = "happy"
                return f"{pokemon.name}の気分が良くなった！"
            else:
                pokemon.mood = "excited"
                return f"{pokemon.name}は元気になった！"
        
        elif self.effect_type == "mixed":
            pokemon.heal(self.effect_value // 2)
            pokemon.energy = min(100, pokemon.energy + self.effect_value // 2)
            return f"{pokemon.name}は元気を取り戻した！"
        
        return f"{pokemon.name}は{self.name}を使った"
    
    def __repr__(self):
        return f"Item({self.name}, {self.effect_type}+{self.effect_value})"


# きのみの定義
BERRY_TYPES = {
    "オレンのみ": {
        "type": "berry",
        "effect_type": "hp",
        "effect_value": 20,
        "description": "HPを20回復する"
    },
    "オボンのみ": {
        "type": "berry",
        "effect_type": "hp",
        "effect_value": 40,
        "description": "HPを40回復する"
    },
    "チーゴのみ": {
        "type": "berry",
        "effect_type": "energy",
        "effect_value": 30,
        "description": "Energyを30回復する"
    },
    "モモンのみ": {
        "type": "berry",
        "effect_type": "mood",
        "effect_value": 1,
        "description": "気分を良くする"
    },
    "ナナのみ": {
        "type": "berry",
        "effect_type": "mixed",
        "effect_value": 30,
        "description": "HPとEnergyを少し回復"
    },
    "キーのみ": {
        "type": "berry",
        "effect_type": "energy",
        "effect_value": 50,
        "description": "Energyを大きく回復"
    },
    "ヒメリのみ": {
        "type": "berry",
        "effect_type": "hp",
        "effect_value": 15,
        "description": "HPを少し回復"
    }
}


class ItemManager:
    """アイテムを管理するクラス"""
    
    def __init__(self, field_size: Tuple[float, float] = (10.0, 10.0)):
        """
        Args:
            field_size: フィールドのサイズ (width, height)
        """
        self.field_size = field_size
        self.items_on_field = []  # フィールド上のアイテム
        self.spawn_probability = 0.03  # アイテム出現確率（ステップあたり）
        self.max_items_on_field = 5  # フィールド上の最大アイテム数
    
    def create_random_berry(self) -> Item:
        """ランダムなきのみを生成"""
        berry_name = random.choice(list(BERRY_TYPES.keys()))
        berry_data = BERRY_TYPES[berry_name]
        
        item = Item(
            name=berry_name,
            item_type=berry_data["type"],
            effect_type=berry_data["effect_type"],
            effect_value=berry_data["effect_value"]
        )
        
        return item
    
    def spawn_item(self):
        """フィールドにアイテムを出現させる"""
        if len(self.items_on_field) >= self.max_items_on_field:
            return None
        
        if random.random() < self.spawn_probability:
            item = self.create_random_berry()
            # ランダムな位置に配置
            x = random.uniform(0.5, self.field_size[0] - 0.5)
            y = random.uniform(0.5, self.field_size[1] - 0.5)
            item.position = (x, y)
            self.items_on_field.append(item)
            return item
        
        return None
    
    def check_pickup(self, pokemon, pickup_distance: float = 0.5) -> Optional[Item]:
        """
        ポケモンがアイテムを拾えるかチェック
        
        Args:
            pokemon: ポケモン
            pickup_distance: 拾える距離
            
        Returns:
            拾ったアイテム、なければNone
        """
        px, py = pokemon.position
        
        for item in self.items_on_field[:]:
            if item.position:
                ix, iy = item.position
                distance = ((px - ix) ** 2 + (py - iy) ** 2) ** 0.5
                
                if distance < pickup_distance:
                    # アイテムを拾う
                    self.items_on_field.remove(item)
                    return item
        
        return None
    
    def get_items_state(self) -> list:
        """フィールド上のアイテムの状態を取得"""
        return [
            {
                "name": item.name,
                "position": item.position,
                "color": item.get_color(),
                "emoji": item.get_emoji(),
                "effect_type": item.effect_type
            }
            for item in self.items_on_field
        ]
    
    def clear_all_items(self):
        """全てのアイテムをクリア"""
        self.items_on_field.clear()

