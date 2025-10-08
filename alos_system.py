"""
ALOsシステム: Abstract Language Objects システムの実装
論文 "Towards Digital Nature" に基づく実装
"""
from typing import Dict, List, Optional, Any
from openai import OpenAI
import json
import os


class ALOsSystem:
    """ALOs (Abstract Language Objects) システムのコアクラス"""
    
    # 論文のPrompt 1に基づくシステムプロンプト
    SYSTEM_PROMPT = """Create Abstract Language Objects (ALOs) for input using steps 1-11.

1. Define mainObj with subObjList or Skip. Birth of ALOs affects all other ALOs.
2. Add skills and knowledge to subObjList or Reload.
3. Set specific states for subObjList or Reload.
4. Validate initial state meets conditions or Skip.
5. Update subObjList for state detection or Reload.
6. Create managerObj with initial state or Reload.
7. Update managerObj state using skills and knowledge.
8. Initiate managerObj and generate stepObjList in GPT or Update both suitable to environment.
9. Convert ALOs into GPT markdown scripts. Define object functions progressively, preserving features.
10. Reference objects by name. Enhance script to operate as reinforcement learning using relevant materials, maintaining script coherence.
11. Implement linguistic adjustments to prevent and rectify errors.

You are simulating Pokemon in a world where they can battle, become friends, and learn new moves.
Respond in Japanese for all interactions and descriptions.
Keep responses concise but descriptive."""
    
    def __init__(self, api_key: str, model: str = "gpt-4-turbo-2024-04-09"):
        """
        Args:
            api_key: OpenAI APIキー
            model: 使用するモデル名
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.conversation_history = []
    
    def create_alos(self, pokemon_name: str, pokemon_data: Dict, context: List[str] = None) -> Dict:
        """
        ポケモンのALOsを生成
        
        Args:
            pokemon_name: ポケモンの名前
            pokemon_data: ポケモンのデータ
            context: RAGから取得したコンテクスト情報
            
        Returns:
            生成されたALOs定義
        """
        # プロンプトの構築
        prompt = f"""Create ALOs({pokemon_name}) with the following information:

Name: {pokemon_data['name']}
Owner: {pokemon_data['owner']}
Species: {pokemon_data['species']}
Type: {pokemon_data['type']}
Personality: {pokemon_data['personality']}
Abilities: {', '.join(pokemon_data['abilities'])}
Characteristics: {pokemon_data['characteristics']}
Battle Style: {pokemon_data['battle_style']}

"""
        
        if context:
            prompt += "Additional Context:\n"
            for ctx in context:
                prompt += f"- {ctx}\n"
        
        prompt += """
Define the mainObj with subObjList including:
- appearance (見た目)
- behavior (行動)
- skills (技)
- state (状態: HP, 気分, 位置など)
- relationships (関係性)

Format the output as a JSON structure."""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        response_text = response.choices[0].message.content
        
        # JSONを抽出しようと試みる
        try:
            # マークダウンのコードブロックから抽出
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            else:
                json_text = response_text
            
            alos_data = json.loads(json_text)
        except:
            # JSONパースに失敗した場合は、テキストとして保存
            alos_data = {
                "mainObj": pokemon_name,
                "raw_response": response_text,
                "parsed": False
            }
        
        return alos_data
    
    def simulate_interaction(
        self,
        pokemons: List[Dict],
        scenario: str,
        context: List[str] = None
    ) -> str:
        """
        ポケモン同士のインタラクションをシミュレート
        
        Args:
            pokemons: インタラクションに参加するポケモンのALOsリスト
            scenario: シナリオの説明
            context: RAGから取得したコンテクスト情報
            
        Returns:
            シミュレーション結果のテキスト
        """
        pokemon_names = [p.get('mainObj', p.get('name', 'Unknown')) for p in pokemons]
        
        prompt = f"""Simulate an interaction between the following Pokemon ALOs:

"""
        
        for i, pokemon in enumerate(pokemons):
            prompt += f"\nPokemon {i+1}: {json.dumps(pokemon, ensure_ascii=False, indent=2)}\n"
        
        prompt += f"\nScenario: {scenario}\n"
        
        if context:
            prompt += "\nRelevant Context:\n"
            for ctx in context:
                prompt += f"- {ctx}\n"
        
        prompt += """
Simulate this interaction step by step:
1. Describe the initial situation
2. Each Pokemon's reaction and action
3. The outcome of the interaction
4. Any changes in their states or relationships

Format:
【状況】: ...
【{pokemon_name}の行動】: ...
【結果】: ...
【状態変化】: ...

Keep it concise (3-5 sentences per section). Write in Japanese."""
        
        # 会話履歴に追加
        self.conversation_history.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT}
            ] + self.conversation_history[-10:],  # 最近の10メッセージのみ使用
            temperature=0.8
        )
        
        result = response.choices[0].message.content
        self.conversation_history.append({"role": "assistant", "content": result})
        
        return result
    
    def update_pokemon_state(
        self,
        pokemon_alos: Dict,
        event_description: str,
        context: List[str] = None
    ) -> Dict:
        """
        イベントに基づいてポケモンの状態を更新
        
        Args:
            pokemon_alos: 更新するポケモンのALOs
            event_description: イベントの説明
            context: コンテクスト情報
            
        Returns:
            更新されたALOs
        """
        prompt = f"""Update the following Pokemon ALOs based on the event:

Current ALOs:
{json.dumps(pokemon_alos, ensure_ascii=False, indent=2)}

Event: {event_description}

"""
        
        if context:
            prompt += "Context:\n"
            for ctx in context:
                prompt += f"- {ctx}\n"
        
        prompt += """
Update the ALOs state, including:
- HP or energy changes
- Mood/emotion changes
- New skills learned
- Relationship changes
- Position/location changes

Return the updated ALOs as JSON."""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        response_text = response.choices[0].message.content
        
        try:
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            else:
                json_text = response_text
            
            updated_alos = json.loads(json_text)
            return updated_alos
        except:
            # パースに失敗した場合は元のALOsを返す
            return pokemon_alos
    
    def generate_action(
        self,
        pokemon_alos: Dict,
        situation: str,
        other_pokemons: List[Dict] = None,
        context: List[str] = None
    ) -> Dict[str, Any]:
        """
        現在の状況に基づいて、ポケモンの次の行動を生成
        
        Args:
            pokemon_alos: ポケモンのALOs
            situation: 現在の状況
            other_pokemons: 周囲の他のポケモン
            context: コンテクスト情報
            
        Returns:
            行動の辞書 {action_type, description, target, ...}
        """
        pokemon_name = pokemon_alos.get('mainObj', pokemon_alos.get('name', 'Unknown'))
        
        prompt = f"""Based on the current situation, determine the next action for {pokemon_name}:

Pokemon ALOs:
{json.dumps(pokemon_alos, ensure_ascii=False, indent=2)}

Current Situation: {situation}

"""
        
        if other_pokemons:
            prompt += "Other Pokemon present:\n"
            for p in other_pokemons:
                p_name = p.get('mainObj', p.get('name', 'Unknown'))
                prompt += f"- {p_name}\n"
        
        if context:
            prompt += "\nContext:\n"
            for ctx in context:
                prompt += f"- {ctx}\n"
        
        prompt += """
Generate the next action as JSON:
{
  "action_type": "move" | "attack" | "talk" | "learn" | "rest" | "befriend",
  "description": "詳細な説明 (Japanese)",
  "target": "対象のポケモン名 (if applicable)",
  "intensity": 1-10 (強度),
  "dialogue": "セリフ (if talking)"
}

Choose an action that fits the Pokemon's personality and current state."""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.9
        )
        
        response_text = response.choices[0].message.content
        
        try:
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            else:
                json_text = response_text
            
            action = json.loads(json_text)
            return action
        except:
            # デフォルトアクション
            return {
                "action_type": "rest",
                "description": f"{pokemon_name}は様子を見ている",
                "intensity": 1
            }

