#!/bin/bash

echo "======================================"
echo "ポケモンALOsシミュレーション セットアップ"
echo "======================================"
echo ""

# Python バージョンチェック
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python バージョン: $python_version"

# 仮想環境の作成（オプション）
read -p "仮想環境を作成しますか？ (y/n): " create_venv
if [ "$create_venv" = "y" ] || [ "$create_venv" = "Y" ]; then
    echo ""
    echo "仮想環境を作成中..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✓ 仮想環境を作成・アクティベートしました"
fi

# 依存パッケージのインストール
echo ""
echo "依存パッケージをインストール中..."
pip install -r requirements.txt

echo ""
echo "✓ インストール完了！"
echo ""

# .env ファイルのチェック
if [ ! -f .env ]; then
    echo "⚠️  .envファイルが見つかりません"
    read -p "OpenAI APIキーを設定しますか？ (y/n): " setup_env
    if [ "$setup_env" = "y" ] || [ "$setup_env" = "Y" ]; then
        read -p "APIキーを入力してください: " api_key
        echo "OPENAI_API_KEY=$api_key" > .env
        echo "✓ .envファイルを作成しました"
    else
        echo "ℹ️  後で.envファイルを作成するか、--no-openaiフラグを使用してください"
    fi
else
    echo "✓ .envファイルが存在します"
fi

echo ""
echo "======================================"
echo "セットアップ完了！"
echo "======================================"
echo ""
echo "実行方法:"
echo "  python main.py                           # 標準モード"
echo "  python main.py --no-openai               # APIなしモード"
echo "  python main.py --visualizer simple       # シンプル表示"
echo "  python main.py --help                    # ヘルプ"
echo ""
echo "詳細はREADME_POKEMON.mdをご覧ください"
echo ""

