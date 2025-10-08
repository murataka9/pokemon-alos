"""
RAGシステム: ポケモンのコンテクストデータを管理
"""
import json
import os
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings


class PokemonRAG:
    """ポケモンのコンテクスト情報をRAGで管理するクラス"""
    
    def __init__(self, context_file: str = "pokemon_context.json", use_rag: bool = True):
        """
        Args:
            context_file: コンテクストデータのJSONファイルパス
            use_rag: RAGを使用するかどうか
        """
        self.use_rag = use_rag
        self.context_data = self._load_context(context_file)
        
        if self.use_rag:
            # ChromaDBクライアントの初期化
            self.client = chromadb.Client(Settings(
                anonymized_telemetry=False,
                allow_reset=True
            ))
            
            # コレクションの作成
            try:
                self.client.delete_collection("pokemon_context")
            except:
                pass
            
            self.collection = self.client.create_collection(
                name="pokemon_context",
                metadata={"description": "Pokemon context data"}
            )
            
            # コンテクストデータをベクトルDBに追加
            self._index_context()
    
    def _load_context(self, context_file: str) -> Dict:
        """JSONファイルからコンテクストデータを読み込む"""
        with open(context_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _index_context(self):
        """コンテクストデータをベクトルDBにインデックス化"""
        documents = []
        metadatas = []
        ids = []
        
        idx = 0
        
        # 各ポケモンの情報をインデックス化
        for pokemon_key in ['pikachu', 'meowth', 'sprigatito']:
            pokemon = self.context_data[pokemon_key]
            
            # 基本情報
            doc = f"{pokemon['name']}は{pokemon['owner']}の{pokemon['species']}。"
            doc += f"タイプ: {pokemon['type']}。"
            doc += f"性格: {pokemon['personality']}"
            documents.append(doc)
            metadatas.append({"type": "basic_info", "pokemon": pokemon_key})
            ids.append(f"basic_{idx}")
            idx += 1
            
            # 能力
            abilities_doc = f"{pokemon['name']}の技: " + "、".join(pokemon['abilities'])
            documents.append(abilities_doc)
            metadatas.append({"type": "abilities", "pokemon": pokemon_key})
            ids.append(f"abilities_{idx}")
            idx += 1
            
            # 特徴
            documents.append(f"{pokemon['name']}の特徴: {pokemon['characteristics']}")
            metadatas.append({"type": "characteristics", "pokemon": pokemon_key})
            ids.append(f"char_{idx}")
            idx += 1
            
            # バトルスタイル
            documents.append(f"{pokemon['name']}の戦闘スタイル: {pokemon['battle_style']}")
            metadatas.append({"type": "battle_style", "pokemon": pokemon_key})
            ids.append(f"battle_{idx}")
            idx += 1
            
            # 関係性
            for entity, relationship in pokemon['relationships'].items():
                rel_doc = f"{pokemon['name']}と{entity}の関係: {relationship}"
                documents.append(rel_doc)
                metadatas.append({"type": "relationship", "pokemon": pokemon_key, "entity": entity})
                ids.append(f"rel_{idx}")
                idx += 1
        
        # ルール
        rules = self.context_data['pokemon_world_rules']
        for rule_key, rule_text in rules.items():
            documents.append(f"ポケモン世界のルール ({rule_key}): {rule_text}")
            metadatas.append({"type": "rule", "rule_key": rule_key})
            ids.append(f"rule_{idx}")
            idx += 1
        
        # シナリオ
        for i, scenario in enumerate(self.context_data['interaction_scenarios']):
            documents.append(f"インタラクションシナリオ: {scenario}")
            metadatas.append({"type": "scenario", "index": i})
            ids.append(f"scenario_{idx}")
            idx += 1
        
        # ベクトルDBに追加
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
    
    def query_context(self, query: str, n_results: int = 5) -> List[str]:
        """
        クエリに関連するコンテクスト情報を取得
        
        Args:
            query: 検索クエリ
            n_results: 取得する結果の数
            
        Returns:
            関連するコンテクスト情報のリスト
        """
        if not self.use_rag:
            # RAGを使わない場合は、全てのコンテクストを返す（簡略版）
            return self._get_all_context_summary()
        
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        return results['documents'][0] if results['documents'] else []
    
    def _get_all_context_summary(self) -> List[str]:
        """RAGを使わない場合の簡易コンテクスト情報"""
        summary = []
        
        for pokemon_key in ['pikachu', 'meowth', 'sprigatito']:
            pokemon = self.context_data[pokemon_key]
            summary.append(
                f"{pokemon['name']}({pokemon['owner']}の{pokemon['species']}、"
                f"タイプ: {pokemon['type']}、性格: {pokemon['personality']})"
            )
        
        return summary
    
    def get_pokemon_data(self, pokemon_key: str) -> Dict:
        """特定のポケモンの完全なデータを取得"""
        return self.context_data.get(pokemon_key, {})
    
    def get_interaction_scenarios(self) -> List[str]:
        """インタラクションシナリオのリストを取得"""
        return self.context_data.get('interaction_scenarios', [])

