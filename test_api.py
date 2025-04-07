"""
Anthropic API接続テスト用スクリプト
"""
import os
import sys
from dotenv import load_dotenv
from anthropic import Anthropic

def test_anthropic_api():
    """Anthropic APIへの接続をテストする"""
    # .envファイルから環境変数を読み込む
    load_dotenv()
    
    # APIキーを取得
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key or api_key == "your_api_key_here":
        print("エラー: ANTHROPIC_API_KEYが設定されていないか、デフォルト値のままです。")
        print("有効なAPIキーを.envファイルに設定するか、環境変数として設定してください。")
        return False
    
    try:
        # Anthropicクライアントの初期化
        client = Anthropic(api_key=api_key)
        
        # 簡単なメッセージを送信して接続テスト
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=10,
            messages=[{"role": "user", "content": "こんにちは"}]
        )
        
        # レスポンスを確認
        if response and response.content:
            print("APIテスト成功！Claudeからのレスポンス:")
            print(response.content[0].text)
            return True
        else:
            print("エラー: APIからレスポンスが得られませんでした。")
            return False
            
    except Exception as e:
        print(f"エラー: API接続中に例外が発生しました: {e}")
        return False

if __name__ == "__main__":
    success = test_anthropic_api()
    if success:
        print("\nAnthropicのAPIに正常に接続できました。")
        print("アプリケーションを実行できます。")
        sys.exit(0)
    else:
        print("\nAnthropicのAPIに接続できませんでした。")
        print("APIキーの設定を確認してください。")
        sys.exit(1)
