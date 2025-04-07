import os
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# Anthropic API 設定
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_MODEL_NAME = os.getenv("ANTHROPIC_MODEL_NAME", "claude-3-opus-20240229")
ANTHROPIC_SONNET_MODEL_NAME = os.getenv("ANTHROPIC_SONNET_MODEL_NAME", "claude-3-sonnet-20240229")

# トークン設定
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "4096"))

# 出力設定
DEFAULT_OUTPUT_FILE = os.getenv("DEFAULT_OUTPUT_FILE", "slides.html")

# API キーの確認
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY が設定されていません。.env ファイルを確認してください。")
