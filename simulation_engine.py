"""
シミュレーションエンジン: ポケモンのインタラクションとイベント管理
"""
from typing import List, Dict, Tuple, Optional
import random
from pokemon_alos import PokemonALOs
from alos_system import ALOsSystem
from rag_system import PokemonRAG
from items import ItemManager


class SimulationEngine:
    """ポケモンシミュレーションのメインエンジン"""
    
    def __init__(
        self,
        pokemons: List[PokemonALOs],
        alos_system: ALOsSystem,
        rag_system: PokemonRAG
    ):
        """
        Args:
            pokemons: シミュレーションに参加するポケモンのリスト
            alos_system: ALOsシステム
            rag_system: RAGシステム
        """
        self.pokemons = {p.key: p for p in pokemons}
        self.alos_system = alos_system
        self.rag_system = rag_system
        
        self.step_count = 0
        self.event_log = []
        self.current_scenario = None
        
        # アイテムマネージャー
        self.item_manager = ItemManager(field_size=(10.0, 10.0))
        
        # イベント確率
        self.battle_probability = 0.15
        self.friendship_probability = 0.2
        self.learn_probability = 0.1
        self.random_event_probability = 0.1
    
    def log_event(self, event: str):
        """イベントをログに記録"""
        log_entry = f"[Step {self.step_count}] {event}"
        self.event_log.append(log_entry)
        print(log_entry)
        
        # ログは最大200件まで
        if len(self.event_log) > 200:
            self.event_log.pop(0)
    
    def get_recent_logs(self, n: int = 10) -> List[str]:
        """最近のログを取得"""
        return self.event_log[-n:]
    
    def step(self) -> Dict:
        """シミュレーションの1ステップを実行"""
        self.step_count += 1
        step_events = []
        
        # アイテムの出現
        new_item = self.item_manager.spawn_item()
        if new_item:
            self.log_event(f"🍓 {new_item.name}が出現した！")
        
        # 全てのポケモンのペアをチェック
        pokemon_list = list(self.pokemons.values())
        
        for i, pokemon1 in enumerate(pokemon_list):
            for pokemon2 in pokemon_list[i+1:]:
                distance = pokemon1.distance_to(pokemon2)
                
                # 近接時のインタラクション
                if distance < 1.5:
                    event = self._handle_interaction(pokemon1, pokemon2)
                    if event:
                        step_events.append(event)
                elif distance < 3.0:
                    # 中距離：互いに気づいている
                    self._handle_awareness(pokemon1, pokemon2)
        
        # 個別の行動
        for pokemon in pokemon_list:
            self._handle_individual_action(pokemon)
            
            # アイテムを拾う
            picked_item = self.item_manager.check_pickup(pokemon, pickup_distance=0.6)
            if picked_item:
                if pokemon.add_item(picked_item):
                    self.log_event(f"📦 {pokemon.name}は{picked_item.name}を拾った！")
                else:
                    # インベントリがいっぱいなら自動使用
                    result = picked_item.use(pokemon)
                    self.log_event(f"💊 {result}")
            
            # 自動でアイテムを使用
            auto_use_result = pokemon.auto_use_item()
            if auto_use_result:
                self.log_event(f"💊 {auto_use_result}")
        
        # ランダムイベント
        if random.random() < self.random_event_probability:
            event = self._trigger_random_event()
            if event:
                step_events.append(event)
        
        return {
            "step": self.step_count,
            "events": step_events,
            "pokemons_state": {k: v.to_dict() for k, v in self.pokemons.items()}
        }
    
    def _handle_interaction(self, pokemon1: PokemonALOs, pokemon2: PokemonALOs) -> Optional[str]:
        """2匹のポケモン間のインタラクションを処理"""
        relationship1 = pokemon1.get_relationship(pokemon2.key)
        relationship2 = pokemon2.get_relationship(pokemon1.key)
        
        # 関係性に基づいてインタラクションタイプを決定
        if relationship1 < -30 or relationship2 < -30:
            # 敵対的：バトルの可能性が高い
            if random.random() < self.battle_probability * 2:
                return self._simulate_battle(pokemon1, pokemon2)
        elif relationship1 > 30 or relationship2 > 30:
            # 友好的：友情イベント
            if random.random() < self.friendship_probability * 2:
                return self._simulate_friendship(pokemon1, pokemon2)
        else:
            # 中立：ランダムなインタラクション
            r = random.random()
            if r < self.battle_probability:
                return self._simulate_battle(pokemon1, pokemon2)
            elif r < self.battle_probability + self.friendship_probability:
                return self._simulate_friendship(pokemon1, pokemon2)
        
        return None
    
    def _handle_awareness(self, pokemon1: PokemonALOs, pokemon2: PokemonALOs):
        """中距離での認識を処理（移動など）"""
        relationship = pokemon1.get_relationship(pokemon2.key)
        
        if relationship < -30:
            # 敵対的：近づく
            pokemon1.move_towards(pokemon2.position, speed=0.2)
        elif relationship > 50:
            # とても友好的：近づく
            pokemon1.move_towards(pokemon2.position, speed=0.15)
        elif pokemon1.mood == "tired":
            # 疲れている：離れる
            pokemon1.move_away(pokemon2.position, speed=0.1)
    
    def _handle_individual_action(self, pokemon: PokemonALOs):
        """個別のポケモンの行動を処理"""
        # エネルギーが低い場合は休憩
        if pokemon.energy < 30:
            pokemon.rest()
            if random.random() < 0.1:
                self.log_event(f"{pokemon.name}は休憩している...")
        
        # HPが低い場合
        elif pokemon.hp < 40:
            pokemon.rest()
            if random.random() < 0.15:
                self.log_event(f"{pokemon.name}は傷を癒やしている...")
        
        # 通常時：ランダムウォーク
        else:
            pokemon.random_walk(speed=0.15)
            
            # まれに技を練習
            if random.random() < self.learn_probability:
                self._practice_move(pokemon)
    
    def _simulate_battle(self, pokemon1: PokemonALOs, pokemon2: PokemonALOs) -> str:
        """バトルをシミュレート"""
        # RAGからコンテクストを取得
        query = f"{pokemon1.name}と{pokemon2.name}のバトル"
        context = self.rag_system.query_context(query, n_results=3)
        
        # ALOsシステムでバトルシミュレーション
        scenario = f"{pokemon1.name}と{pokemon2.name}が戦っている"
        
        try:
            result = self.alos_system.simulate_interaction(
                [pokemon1.to_dict(), pokemon2.to_dict()],
                scenario,
                context
            )
            
            # 結果に基づいて状態を更新
            damage1 = random.randint(10, 25)
            damage2 = random.randint(10, 25)
            
            pokemon1.take_damage(damage2)
            pokemon2.take_damage(damage1)
            
            # 関係性を悪化
            pokemon1.update_relationship(pokemon2.key, -5)
            pokemon2.update_relationship(pokemon1.key, -5)
            
            self.log_event(f"⚔️ {pokemon1.name} vs {pokemon2.name}: バトル発生！")
            self.log_event(result)
            
            return f"Battle: {pokemon1.name} vs {pokemon2.name}"
            
        except Exception as e:
            # API呼び出しに失敗した場合のフォールバック
            self.log_event(f"⚔️ {pokemon1.name}と{pokemon2.name}が戦った！")
            pokemon1.take_damage(15)
            pokemon2.take_damage(15)
            pokemon1.update_relationship(pokemon2.key, -5)
            pokemon2.update_relationship(pokemon1.key, -5)
            return f"Battle: {pokemon1.name} vs {pokemon2.name}"
    
    def _simulate_friendship(self, pokemon1: PokemonALOs, pokemon2: PokemonALOs) -> str:
        """友好的なインタラクションをシミュレート"""
        # RAGからコンテクストを取得
        query = f"{pokemon1.name}と{pokemon2.name}の友情"
        context = self.rag_system.query_context(query, n_results=3)
        
        scenario = f"{pokemon1.name}と{pokemon2.name}が友好的に交流している"
        
        try:
            result = self.alos_system.simulate_interaction(
                [pokemon1.to_dict(), pokemon2.to_dict()],
                scenario,
                context
            )
            
            # 関係性を改善
            pokemon1.update_relationship(pokemon2.key, 10)
            pokemon2.update_relationship(pokemon1.key, 10)
            
            # 気分を良くする
            pokemon1.mood = "happy"
            pokemon2.mood = "happy"
            
            # 少し回復
            pokemon1.heal(5)
            pokemon2.heal(5)
            
            self.log_event(f"💚 {pokemon1.name}と{pokemon2.name}が仲良くなった！")
            self.log_event(result)
            
            return f"Friendship: {pokemon1.name} & {pokemon2.name}"
            
        except Exception as e:
            self.log_event(f"💚 {pokemon1.name}と{pokemon2.name}が交流した")
            pokemon1.update_relationship(pokemon2.key, 10)
            pokemon2.update_relationship(pokemon1.key, 10)
            return f"Friendship: {pokemon1.name} & {pokemon2.name}"
    
    def _practice_move(self, pokemon: PokemonALOs):
        """技の練習をシミュレート"""
        if len(pokemon.current_abilities) >= 6:
            return  # すでに多くの技を覚えている
        
        # 新しい技を覚える可能性
        potential_moves = {
            "pikachu": ["ボルテッカー", "エレキボール", "なみのり"],
            "meowth": ["つじぎり", "イカサマ", "アシストパワー"],
            "sprigatito": ["エナジーボール", "ソーラービーム", "やどりぎのタネ"]
        }
        
        new_moves = [m for m in potential_moves.get(pokemon.key, []) 
                     if m not in pokemon.current_abilities]
        
        if new_moves and random.random() < 0.3:
            new_move = random.choice(new_moves)
            pokemon.learn_move(new_move)
            self.log_event(f"✨ {pokemon.name}は{new_move}を覚えた！")
    
    def _trigger_random_event(self) -> Optional[str]:
        """ランダムイベントを発生させる"""
        scenarios = self.rag_system.get_interaction_scenarios()
        
        if scenarios:
            scenario = random.choice(scenarios)
            self.log_event(f"🎲 ランダムイベント: {scenario}")
            
            # ランダムなポケモンを選択
            pokemon_list = list(self.pokemons.values())
            selected = random.sample(pokemon_list, min(2, len(pokemon_list)))
            
            # 位置を近づける
            if len(selected) == 2:
                selected[0].move_towards(selected[1].position, speed=0.5)
            
            return f"Random Event: {scenario}"
        
        return None
    
    def get_simulation_state(self) -> Dict:
        """現在のシミュレーション状態を取得"""
        return {
            "step": self.step_count,
            "pokemons": {
                key: {
                    "name": p.name,
                    "position": p.position,
                    "hp": p.hp,
                    "energy": p.energy,
                    "mood": p.mood,
                    "color": p.get_mood_color(),
                    "relationships": p.relationships,
                    "abilities": p.current_abilities,
                    "inventory": [
                        {"name": item.name, "emoji": item.get_emoji()}
                        for item in p.inventory
                    ]
                }
                for key, p in self.pokemons.items()
            },
            "items": self.item_manager.get_items_state()
        }

