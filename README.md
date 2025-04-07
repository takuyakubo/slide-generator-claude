# スライド生成アプリケーション

このプロジェクトは、画像と命令文からプレゼンテーションスライドを自動生成するアプリケーションです。LangGraphとAnthropicのClaudeモデルを使用して、画像内容を分析し、構造化されたスライドを生成します。

## 特徴

- 複数の画像を同時に分析可能
- 画像内容から主要なポイントを抽出
- ユーザーの指示に基づいたスライド構造の生成
- HTMLフォーマットでのスライド出力
- ブラウザで表示可能な完全なプレゼンテーション

## 前提条件

- Python 3.9+
- Anthropic API キー

## インストール方法

1. リポジトリをクローン

```bash
git clone https://github.com/takuyakubo/slide-generator-claude.git
cd slide-generator-claude
```

2. 仮想環境を作成してアクティベート

```bash
python -m venv venv
source venv/bin/activate  # Linuxの場合
# または
venv\Scripts\activate  # Windowsの場合
```

3. 必要なパッケージをインストール

```bash
pip install -r requirements.txt
```

4. 環境変数の設定

`.env.example` ファイルを `.env` にコピーし、Anthropic APIキーを設定します。

```bash
cp .env.example .env
# .envファイルを編集してAPI_KEYを設定
```

## 使用方法

### コマンドラインから使用

```bash
python main.py --images path/to/image1.jpg path/to/image2.jpg --instruction "これらの画像をもとに、勉強会用のスライドを作成してください。" --output slides.html
```

### Pythonコードとして使用

```python
from main import create_slide_generation_workflow

# ワークフローの作成
app = create_slide_generation_workflow()

# ワークフローの実行
result = app.invoke({
    "images": ["path/to/image1.jpg", "path/to/image2.jpg"],
    "instruction": "これらの画像をもとに、勉強会用のスライドを作成してください。"
})

# 結果の保存
with open("slides.html", "w", encoding="utf-8") as f:
    f.write(result["html_output"])
```

## ワークフローの説明

このアプリケーションは以下のステップでスライドを生成します：

1. **画像処理**: 提供された画像を分析し、主要な内容、要素、構造を抽出します。
2. **コンテンツ構造抽出**: 画像分析結果とユーザーの指示を元に、スライドの基本構造を作成します。
3. **スライドアウトライン生成**: 構造をベースにして詳細なスライドのアウトラインを生成します。
4. **詳細スライド生成**: アウトラインを元に詳細なスライド内容を作成します。
5. **HTML生成**: スライド内容をHTMLフォーマットに変換して、ブラウザで表示可能なプレゼンテーションを生成します。

## エラー処理

各ステップではエラーチェックが行われ、問題が発生した場合は処理が中断されます。エラーメッセージには、エラーの詳細が含まれます。

## カスタマイズ

- `.env` ファイルでモデルの種類やトークン数を変更できます
- HTMLテンプレートを変更することで、スライドの見た目やレイアウトをカスタマイズできます
- Utilsファイルにある関数を拡張することで、より多くの画像形式に対応できます

## トラブルシューティング

- **API認証エラー**: `.env` ファイルに正しいAPIキーが設定されているか確認してください
- **画像処理エラー**: サポートされている画像形式（JPG、PNG、GIF）を使用しているか確認してください
- **メモリエラー**: 大きなサイズの画像を処理する場合、実行環境のメモリ制限に注意してください

## 制限事項

- 画像サイズや数によって処理時間が変わります
- APIの料金体系に注意してください（Anthropic APIの使用には料金が発生します）
- HTMLスライドはブラウザで表示する必要があります

## ライセンス

MITライセンス

## 貢献

バグの報告や機能提案はIssuesに投稿してください。プルリクエストも歓迎します。

## 謝辞

- このプロジェクトは [LangGraph](https://github.com/langchain-ai/langgraph) と [Anthropic Claude](https://www.anthropic.com/claude) を使用しています
- 開発に協力してくれたすべての方々に感謝します
