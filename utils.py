import base64
from PIL import Image
import io
import os
from typing import List, Union, Dict, Any

def encode_image_to_base64(image_path: str) -> str:
    """
    画像ファイルをbase64エンコードする

    Args:
        image_path (str): 画像ファイルへのパス

    Returns:
        str: base64エンコードされた画像データ
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def encode_pil_image_to_base64(image: Image.Image) -> str:
    """
    PIL Imageオブジェクトをbase64エンコードする

    Args:
        image (Image.Image): PIL画像オブジェクト

    Returns:
        str: base64エンコードされた画像データ
    """
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def save_html_to_file(html_content: str, output_path: str) -> None:
    """
    HTML内容をファイルに保存する

    Args:
        html_content (str): HTML内容
        output_path (str): 出力先ファイルパス
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"HTMLファイルが保存されました: {output_path}")

def get_image_paths_from_directory(dir_path: str, extensions: List[str] = ['.jpg', '.jpeg', '.png', '.gif']) -> List[str]:
    """
    指定されたディレクトリから画像ファイルのパスを取得する

    Args:
        dir_path (str): 画像を検索するディレクトリのパス
        extensions (List[str], optional): 検索する画像の拡張子のリスト. デフォルトは ['.jpg', '.jpeg', '.png', '.gif']

    Returns:
        List[str]: 画像ファイルパスのリスト
    """
    image_paths = []
    
    for root, _, files in os.walk(dir_path):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in extensions:
                image_paths.append(os.path.join(root, file))
    
    return sorted(image_paths)

def format_error_message(error: Exception) -> Dict[str, Any]:
    """
    エラーメッセージを適切にフォーマットする

    Args:
        error (Exception): 発生したエラー

    Returns:
        Dict[str, Any]: エラー情報を含む辞書
    """
    return {
        "error": str(error),
        "error_type": type(error).__name__,
        "error_message": str(error)
    }
