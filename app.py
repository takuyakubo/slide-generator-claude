import os
import argparse
from main import create_slide_generation_workflow
from utils import get_image_paths_from_directory, save_html_to_file

def main():
    parser = argparse.ArgumentParser(description='画像からスライドを生成します')
    # 画像を直接指定するか、ディレクトリを指定する2つのオプション
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--images', nargs='+', help='画像ファイルのパス（複数指定可）')
    group.add_argument('--directory', help='画像ファイルが含まれるディレクトリのパス')
    
    parser.add_argument('--instruction', required=True, help='スライド生成の指示文')
    parser.add_argument('--output', default='slides.html', help='出力先HTMLファイル名')
    parser.add_argument('--model', choices=['opus', 'sonnet', 'haiku'], default='opus', 
                        help='使用するClaudeモデル (opus: 最高品質, sonnet: バランス, haiku: 高速)')
    
    args = parser.parse_args()
    
    # モデル選択
    os.environ["ANTHROPIC_MODEL_NAME"] = {
        'opus': 'claude-3-opus-20240229',
        'sonnet': 'claude-3-sonnet-20240229',
        'haiku': 'claude-3-haiku-20240307'
    }.get(args.model, 'claude-3-opus-20240229')
    
    # 画像パスの取得
    if args.directory:
        image_paths = get_image_paths_from_directory(args.directory)
        if not image_paths:
            print(f"エラー: 指定されたディレクトリ '{args.directory}' に画像ファイルが見つかりませんでした。")
            return
        print(f"{len(image_paths)}個の画像が見つかりました。")
    else:
        image_paths = args.images
    
    # ワークフローの作成と実行
    print("スライド生成を開始します...")
    app = create_slide_generation_workflow()
    
    result = app.invoke({
        "images": image_paths,
        "instruction": args.instruction
    })
    
    # エラーチェック
    if "error" in result:
        print(f"エラーが発生しました: {result['error']}")
        return
    
    # 結果をファイルに保存
    save_html_to_file(result["html_output"], args.output)
    print(f"スライドが生成されました: {args.output}")
    
    # HTMLを開く方法を提案
    print(f"\n生成されたスライドを開くには、ブラウザで以下のファイルを開いてください:")
    print(f"file://{os.path.abspath(args.output)}")

if __name__ == "__main__":
    main()
