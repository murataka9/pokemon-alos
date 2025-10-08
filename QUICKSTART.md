# クイックスタートガイド

## 最速で始める（OpenAI APIなし）

```bash
# 1. 依存パッケージをインストール
pip install -r requirements.txt

# 2. すぐに実行（APIキー不要）
python main.py --no-openai
```

## OpenAI APIを使う場合

```bash
# 1. セットアップスクリプトを実行
./setup.sh

# または手動で設定
pip install -r requirements.txt
echo "OPENAI_API_KEY=your_key_here" > .env

# 2. 実行
python main.py
```

## おすすめの実行方法

### 初回実行（軽量・高速）
```bash
python main.py --no-openai --visualizer simple --interval 300
```

### 本格的なシミュレーション（OpenAI API必須）
```bash
python main.py --visualizer standard --interval 500
```

### RAGなしで高速化
```bash
python main.py --no-rag --interval 200
```

## 操作方法

- シミュレーションは自動で進行します
- ウィンドウを閉じると終了します
- ログが右側にリアルタイムで表示されます
- ポケモンの色：
  - 🟡 ピカチュウ: 黄色
  - ⚪ ニャース: 灰色
  - 🟢 ニャオハ: 緑
  - HPが減ると色が暗くなります

## トラブルシューティング

### すぐに終了する場合
Matplotlibのバックエンド問題の可能性があります：
```bash
# Macの場合
pip install pyobjc-framework-Cocoa

# 環境変数を設定
export MPLBACKEND=TkAgg
python main.py --no-openai
```

### 日本語が文字化けする場合
```bash
pip install --upgrade japanize-matplotlib
```

### エラーが出る場合
完全にクリーンな環境で再インストール：
```bash
pip uninstall -y openai numpy matplotlib chromadb python-dotenv
pip install -r requirements.txt
```

## 次のステップ

詳細な情報は`README_POKEMON.md`をご覧ください！

