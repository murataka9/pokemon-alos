# インストールガイド

## 依存パッケージ

以下のパッケージが必要です：

- `openai>=2.0.0` - OpenAI API クライアント
- `numpy>=1.24.0` - 数値計算
- `matplotlib>=3.7.0` - グラフ描画
- `chromadb>=0.4.0` - ベクトルデータベース（RAG用）
- `python-dotenv>=1.0.0` - 環境変数管理
- `japanize-matplotlib>=1.1.3` - Matplotlib日本語対応

## インストール方法

### 方法1: 自動セットアップ（推奨）

```bash
cd /Users/takahito/Develop/pokemon-alos
./setup.sh
```

このスクリプトは以下を行います：
1. Pythonバージョンのチェック
2. 仮想環境の作成（オプション）
3. 依存パッケージのインストール
4. `.env`ファイルの設定（オプション）

### 方法2: 手動インストール

```bash
# 1. 依存パッケージをインストール
pip install -r requirements.txt

# 2. （オプション）.envファイルを作成
echo "OPENAI_API_KEY=your_key_here" > .env
```

### 方法3: 仮想環境を使用

```bash
# 1. 仮想環境を作成
python3 -m venv venv

# 2. 仮想環境をアクティベート
# macOS/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# 3. 依存パッケージをインストール
pip install -r requirements.txt
```

## 個別パッケージの説明

### japanize-matplotlib

Matplotlibで日本語を表示するためのパッケージです。

```bash
pip install japanize-matplotlib
```

インポートするだけで自動的に日本語フォントが設定されます：
```python
import japanize_matplotlib
```

### chromadb

RAGシステムで使用するベクトルデータベースです。

```bash
pip install chromadb
```

RAGを使わない場合は、`--no-rag`フラグで無効化できます。

### openai

OpenAI APIクライアントです。

```bash
pip install openai
```

API不要の場合は、`--no-openai`フラグで無効化できます。

## 動作確認

インストール後、以下のコマンドで動作確認できます：

```bash
# OpenAI APIなしで動作確認
python main.py --no-openai --visualizer simple

# すべての機能を使用（APIキーが必要）
python main.py
```

## トラブルシューティング

### ImportError: No module named 'xxx'

パッケージがインストールされていません：
```bash
pip install -r requirements.txt
```

### chromadbのエラー

ChromaDBのバージョン問題の可能性：
```bash
pip uninstall chromadb
pip install chromadb>=0.4.0
```

または、RAGを無効化：
```bash
python main.py --no-rag
```

### 日本語が表示されない

japanize-matplotlibを再インストール：
```bash
pip install --upgrade japanize-matplotlib
```

### Matplotlibウィンドウが開かない

バックエンドの問題の可能性：
```bash
# macOS
pip install pyobjc-framework-Cocoa

# 環境変数を設定
export MPLBACKEND=TkAgg
python main.py --no-openai
```

## システム要件

- Python 3.8以上
- メモリ: 最低2GB（RAG使用時は4GB推奨）
- OS: macOS, Linux, Windows

## 開発環境

開発に参加する場合：

```bash
# 開発用パッケージをインストール
pip install -r requirements.txt
pip install pytest black flake8 mypy

# コードフォーマット
black .

# リンター
flake8 .

# 型チェック
mypy .
```

## アンインストール

```bash
# パッケージをアンインストール
pip uninstall -y openai numpy matplotlib chromadb python-dotenv japanize-matplotlib

# 仮想環境を削除（使用している場合）
rm -rf venv/
```

