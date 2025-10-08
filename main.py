"""
メインプログラム: ポケモンALOsシミュレーション

使い方:
    python main.py [オプション]

オプション:
    --no-rag: RAGシステムを使用しない
    --visualizer: ビジュアライザーのタイプ (standard/simple) デフォルト: standard
    --interval: 更新間隔（ミリ秒） デフォルト: 500
    --no-openai: OpenAI APIを使わない（ローカルシミュレーションのみ）
"""
import os
import sys
import argparse
from dotenv import load_dotenv

from rag_system import PokemonRAG
from alos_system import ALOsSystem
from pokemon_alos import PokemonALOs
from simulation_engine import SimulationEngine
from visualization import PokemonVisualizer, SimplePokemonVisualizer


def main():
    # 引数のパース
    parser = argparse.ArgumentParser(description='ポケモンALOsシミュレーション')
    parser.add_argument('--no-rag', action='store_true', help='RAGシステムを使用しない')
    parser.add_argument('--visualizer', type=str, default='standard', 
                       choices=['standard', 'simple'], help='ビジュアライザーのタイプ')
    parser.add_argument('--interval', type=int, default=500, help='更新間隔（ミリ秒）')
    parser.add_argument('--no-openai', action='store_true', help='OpenAI APIを使わない')
    
    args = parser.parse_args()
    
    # 環境変数の読み込み
    load_dotenv()
    
    print("=" * 60)
    print("🎮 ポケモンALOsシミュレーション")
    print("   論文 'Towards Digital Nature' に基づく実装")
    print("=" * 60)
    print()
    
    # OpenAI APIキーの確認
    use_openai = not args.no_openai
    api_key = os.getenv('OPENAI_API_KEY')
    
    if use_openai and not api_key:
        print("⚠️  警告: OPENAI_API_KEYが設定されていません")
        print("   .envファイルを作成し、APIキーを設定してください")
        print("   ローカルシミュレーションのみで実行します")
        use_openai = False
    
    # RAGシステムの初期化
    print("📚 RAGシステムを初期化中...")
    use_rag = not args.no_rag
    try:
        rag_system = PokemonRAG(
            context_file="pokemon_context.json",
            use_rag=use_rag
        )
        print(f"   ✅ RAGシステム初期化完了 (モード: {'RAG有効' if use_rag else 'RAG無効'})")
    except Exception as e:
        print(f"   ⚠️  RAGシステムの初期化に失敗: {e}")
        print("   RAG無効モードで続行します")
        rag_system = PokemonRAG(context_file="pokemon_context.json", use_rag=False)
    
    # ALOsシステムの初期化
    alos_system = None
    if use_openai:
        print("🤖 ALOsシステムを初期化中...")
        try:
            alos_system = ALOsSystem(
                api_key=api_key,
                model="gpt-4-turbo-2024-04-09"  # ユーザーが指定したモデルに近いもの
            )
            print("   ✅ ALOsシステム初期化完了")
        except Exception as e:
            print(f"   ⚠️  ALOsシステムの初期化に失敗: {e}")
            print("   ローカルシミュレーションのみで続行します")
            use_openai = False
    
    if not use_openai:
        print("ℹ️  OpenAI APIを使用しないモードで実行します")
        print("   シンプルなローカルシミュレーションが動作します")
    
    # ポケモンALOsの作成
    print("\n🎯 ポケモンを作成中...")
    
    pokemons = []
    pokemon_keys = ['pikachu', 'meowth', 'sprigatito']
    
    for key in pokemon_keys:
        pokemon_data = rag_system.get_pokemon_data(key)
        
        # ALOs定義を生成（OpenAI使用時のみ）
        alos_definition = None
        if use_openai and alos_system:
            try:
                context = rag_system.query_context(f"{pokemon_data['name']}の特徴", n_results=3)
                alos_definition = alos_system.create_alos(key, pokemon_data, context)
                print(f"   ✅ {pokemon_data['name']} のALOs生成完了")
            except Exception as e:
                print(f"   ⚠️  {pokemon_data['name']} のALOs生成に失敗: {e}")
        else:
            print(f"   ✅ {pokemon_data['name']} を作成")
        
        pokemon = PokemonALOs(key, pokemon_data, alos_definition)
        pokemons.append(pokemon)
    
    # シミュレーションエンジンの初期化
    print("\n⚙️  シミュレーションエンジンを初期化中...")
    
    # OpenAI未使用時のダミーシステム
    if not use_openai:
        class DummyALOsSystem:
            def simulate_interaction(self, pokemons, scenario, context):
                return "（ローカルシミュレーション）"
        
        alos_system = DummyALOsSystem()
    
    engine = SimulationEngine(pokemons, alos_system, rag_system)
    print("   ✅ シミュレーションエンジン初期化完了")
    
    # ビジュアライザーの初期化と実行
    print(f"\n🎨 ビジュアライザーを起動中 (タイプ: {args.visualizer})...")
    print("   ウィンドウを閉じると終了します\n")
    
    print("=" * 60)
    print("シミュレーション開始！")
    print("=" * 60)
    print()
    
    try:
        if args.visualizer == 'simple':
            visualizer = SimplePokemonVisualizer(
                engine,
                grid_size=50,
                update_interval=args.interval
            )
        else:
            visualizer = PokemonVisualizer(
                engine,
                update_interval=args.interval
            )
        
        visualizer.run()
        
    except KeyboardInterrupt:
        print("\n\nシミュレーションを終了します...")
    except Exception as e:
        print(f"\n\nエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n" + "=" * 60)
        print(f"シミュレーション統計:")
        print(f"  総ステップ数: {engine.step_count}")
        print(f"  イベント数: {len(engine.event_log)}")
        print("\nポケモンの最終状態:")
        for key, pokemon in engine.pokemons.items():
            print(f"  {pokemon.name}:")
            print(f"    HP: {pokemon.hp}/100")
            print(f"    Energy: {pokemon.energy}/100")
            print(f"    気分: {pokemon.mood}")
            print(f"    覚えた技: {len(pokemon.current_abilities)}個")
            if pokemon.relationships:
                print(f"    関係性:")
                for other_key, rel in pokemon.relationships.items():
                    other_name = engine.pokemons[other_key].name
                    print(f"      {other_name}: {rel:+d}")
        print("=" * 60)
        print("ありがとうございました！")


if __name__ == "__main__":
    main()

