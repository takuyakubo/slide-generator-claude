import langgraph.graph as lg
from langgraph.graph import StateGraph, END
from PIL import Image
from typing import Dict, Any, List, TypedDict, Annotated
import base64
import io
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

# 状態の型定義
class SlideGenerationState(TypedDict):
    images: List[Any]  # 画像のリスト
    instruction: str  # ユーザーからの指示
    image_content: List[Dict[str, Any]]  # 画像分析結果
    content_structure: str  # 構造化されたコンテンツ
    slide_outline: str  # スライドのアウトライン
    slide_presentation: str  # 詳細なスライドプレゼンテーション
    html_output: str  # 最終的なHTML出力
    error: str  # エラーメッセージ（存在する場合）

def create_slide_generation_workflow():
    # 画像を処理するノード
    def process_images(state: SlideGenerationState) -> SlideGenerationState:
        """複数の画像を処理して内容を抽出"""
        if "images" not in state:
            return {"error": "画像が提供されていません", **state}
        
        try:
            # 画像の読み込みと処理
            images = state["images"]
            
            # Anthropicモデルの設定
            llm = ChatAnthropic(model="claude-3-opus-20240229")
            
            all_image_content = []
            
            # 複数画像の処理
            for idx, image in enumerate(images):
                # 画像をbase64エンコード
                if isinstance(image, str):  # 画像がパスとして提供された場合
                    with open(image, "rb") as img_file:
                        img_data = base64.b64encode(img_file.read()).decode('utf-8')
                elif isinstance(image, Image.Image):  # PILイメージの場合
                    buffered = io.BytesIO()
                    image.save(buffered, format="PNG")
                    img_data = base64.b64encode(buffered.getvalue()).decode('utf-8')
                else:
                    return {"error": f"サポートされていない画像形式です (画像 {idx+1})", **state}
                
                # 画像分析リクエスト - 修正した形式
                image_message = HumanMessage(
                    content=[
                        {"type": "text", "text": f"画像 {idx+1}の内容を詳細に分析してください。主要な要素、テキスト、構造を抽出してください。"},
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": img_data
                            }
                        }
                    ]
                )
                
                image_analysis = llm.invoke([image_message])
                all_image_content.append({
                    "image_idx": idx+1, 
                    "analysis": image_analysis.content
                })
            
            return {"image_content": all_image_content, **state}
        except Exception as e:
            return {"error": f"画像処理中にエラーが発生しました: {str(e)}", **state}
    
    # 構造を抽出するノード
    def extract_content_structure(state: SlideGenerationState) -> SlideGenerationState:
        """命令と画像分析結果から構造を抽出"""
        if "error" in state:
            return state
        
        if "instruction" not in state:
            return {"error": "命令が提供されていません", **state}
        
        try:
            instruction = state["instruction"]
            image_content = state.get("image_content", [])
            
            # Anthropicモデルの設定
            llm = ChatAnthropic(model="claude-3-opus-20240229")
            
            # 複数画像の分析結果をフォーマット
            image_analyses = "\n\n".join([
                f"画像 {item['image_idx']}の分析結果:\n{item['analysis']}" 
                for item in image_content
            ])
            
            # 修正: 直接メッセージを構築
            system_message = SystemMessage(content="あなたは与えられた画像分析と命令から、スライド作成に必要な構造を抽出するアシスタントです。")
            
            human_message = HumanMessage(content=f"""
            画像分析結果：
            {image_analyses}
            
            命令：
            {instruction}
            
            上記の情報から、スライド作成に適した構造を抽出し、以下のフォーマットで出力してください：
            - タイトル
            - サブタイトル
            - 主要なポイント（箇条書き）
            - 結論
            """)
            
            # 直接メッセージのリストを渡す
            response = llm.invoke([system_message, human_message])
            
            return {"content_structure": response.content, **state}
        except Exception as e:
            return {"error": f"コンテンツ構造抽出中にエラーが発生しました: {str(e)}", **state}
    
    # スライドアウトラインを生成するノード
    def generate_slide_outline(state: SlideGenerationState) -> SlideGenerationState:
        """抽出された構造からスライドアウトラインを生成"""
        if "error" in state:
            return state
        
        try:
            content_structure = state["content_structure"]
            
            # Anthropicモデルの設定
            llm = ChatAnthropic(model="claude-3-sonnet-20240229")
            
            # 修正: 直接メッセージを構築
            system_message = SystemMessage(content="あなたはスライドアウトラインを作成するアシスタントです。")
            
            human_message = HumanMessage(content=f"""
            以下の構造からスライドのアウトラインを作成してください：
            
            {content_structure}
            
            各スライドには以下の情報を含めてください：
            1. スライド番号
            2. タイトル
            3. 主要な内容
            4. 追加すべき視覚的要素の提案
            """)
            
            # 直接メッセージのリストを渡す
            response = llm.invoke([system_message, human_message])
            
            return {"slide_outline": response.content, **state}
        except Exception as e:
            return {"error": f"スライドアウトライン生成中にエラーが発生しました: {str(e)}", **state}
    
    # 詳細なスライドを生成するノード
    def generate_detailed_slides(state: SlideGenerationState) -> SlideGenerationState:
        """アウトラインから詳細なスライド内容を生成"""
        if "error" in state:
            return state
        
        try:
            slide_outline = state["slide_outline"]
            
            # Anthropicモデルの設定
            llm = ChatAnthropic(model="claude-3-sonnet-20240229")
            
            # 修正: 直接メッセージを構築
            system_message = SystemMessage(content="あなたは詳細なスライド内容を生成するアシスタントです。")
            
            human_message = HumanMessage(content=f"""
            以下のアウトラインから詳細なスライド内容を生成してください：
            
            {slide_outline}
            
            各スライドには以下の情報を含めてください：
            1. スライド番号
            2. タイトル
            3. 内容（完全な文章）
            4. 視覚的要素（図表、画像の説明）
            5. デザインの提案
            
            JSON形式で出力してください。
            """)
            
            # 直接メッセージのリストを渡す
            response = llm.invoke([system_message, human_message])
            
            return {"slide_presentation": response.content, **state}
        except Exception as e:
            return {"error": f"詳細スライド生成中にエラーが発生しました: {str(e)}", **state}
    
    # HTMLスライドを生成するノード
    def generate_html_slides(state: SlideGenerationState) -> SlideGenerationState:
        """構造化されたスライドデータからHTMLを生成"""
        if "error" in state:
            return state
        
        try:
            slide_presentation = state["slide_presentation"]
            
            # Anthropicモデルの設定
            llm = ChatAnthropic(model="claude-3-sonnet-20240229")
            
            # HTMLテンプレート
            html_template = """
            <!DOCTYPE html>
            <html lang="ja">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>{{TITLE}}</title>
                <style>
                    body {
                        font-family: 'Arial', sans-serif;
                        margin: 0;
                        padding: 0;
                    }
                    .slide {
                        width: 100%;
                        height: 100vh;
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                        align-items: center;
                        text-align: center;
                        padding: 2rem;
                        box-sizing: border-box;
                    }
                    .slide-title {
                        font-size: 2.5rem;
                        margin-bottom: 1rem;
                    }
                    .slide-content {
                        font-size: 1.5rem;
                        max-width: 80%;
                    }
                    .controls {
                        position: fixed;
                        bottom: 1rem;
                        right: 1rem;
                        display: flex;
                        gap: 0.5rem;
                    }
                    .controls button {
                        padding: 0.5rem 1rem;
                        cursor: pointer;
                    }
                </style>
            </head>
            <body>
                <div id="presentation">
                    {{SLIDES}}
                </div>
                
                <div class="controls">
                    <button id="prev">前へ</button>
                    <button id="next">次へ</button>
                </div>
                
                <script>
                    const slides = document.querySelectorAll('.slide');
                    let currentSlide = 0;
                    
                    function showSlide(index) {
                        slides.forEach((slide, i) => {
                            slide.style.display = i === index ? 'flex' : 'none';
                        });
                    }
                    
                    document.getElementById('prev').addEventListener('click', () => {
                        currentSlide = Math.max(0, currentSlide - 1);
                        showSlide(currentSlide);
                    });
                    
                    document.getElementById('next').addEventListener('click', () => {
                        currentSlide = Math.min(slides.length - 1, currentSlide + 1);
                        showSlide(currentSlide);
                    });
                    
                    // 初期表示
                    showSlide(currentSlide);
                </script>
            </body>
            </html>
            """
            
            # 修正: 直接メッセージを構築
            system_message = SystemMessage(content="あなたはスライドデータからHTMLを生成するアシスタントです。")
            
            human_message = HumanMessage(content=f"""
            以下のスライドデータからHTMLを生成してください：
            
            {slide_presentation}
            
            以下のHTMLテンプレートを使用し、{{TITLE}}をプレゼンテーションのタイトルに、{{SLIDES}}を個々のスライドのHTMLに置き換えてください：
            
            {html_template}
            
            各スライドは<div class="slide">要素として生成し、タイトルは<h1 class="slide-title">、内容は<div class="slide-content">の中に配置してください。
            """)
            
            # 直接メッセージのリストを渡す
            response = llm.invoke([system_message, human_message])
            
            return {"html_output": response.content, **state}
        except Exception as e:
            return {"error": f"HTML生成中にエラーが発生しました: {str(e)}", **state}
    
    # エラーチェック関数
    def check_error(state: SlideGenerationState) -> str:
        """エラーがあるかどうかをチェックし、次のステップを決定する"""
        if "error" in state:
            return "error"
        return "continue"

    # ワークフローのグラフ定義
    workflow = StateGraph(SlideGenerationState)
    
    # ノードの追加
    workflow.add_node("process_images", process_images)
    workflow.add_node("extract_content_structure", extract_content_structure)
    workflow.add_node("generate_slide_outline", generate_slide_outline)
    workflow.add_node("generate_detailed_slides", generate_detailed_slides)
    workflow.add_node("generate_html_slides", generate_html_slides)
    
    # エントリーポイントの設定
    workflow.set_entry_point("process_images")
    
    # エッジとコンディショナルエッジの追加
    workflow.add_conditional_edges(
        "process_images",
        check_error,
        {
            "error": END,
            "continue": "extract_content_structure"
        }
    )
    
    workflow.add_conditional_edges(
        "extract_content_structure",
        check_error,
        {
            "error": END,
            "continue": "generate_slide_outline"
        }
    )
    
    workflow.add_conditional_edges(
        "generate_slide_outline",
        check_error,
        {
            "error": END,
            "continue": "generate_detailed_slides"
        }
    )
    
    workflow.add_conditional_edges(
        "generate_detailed_slides",
        check_error,
        {
            "error": END,
            "continue": "generate_html_slides"
        }
    )
    
    # 最後のエッジ
    workflow.add_edge("generate_html_slides", END)
    
    # コンパイル
    app = workflow.compile()
    
    return app

if __name__ == "__main__":
    # ワークフローの作成
    app = create_slide_generation_workflow()
    
    # コマンドライン引数でパスと指示を受け取る場合の例
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='画像からスライドを生成します')
    parser.add_argument('--images', nargs='+', required=True, help='画像ファイルのパス（複数指定可）')
    parser.add_argument('--instruction', required=True, help='スライド生成の指示文')
    parser.add_argument('--output', default='slides.html', help='出力先HTMLファイル名')
    
    args = parser.parse_args()
    
    # ワークフローの実行
    result = app.invoke({
        "images": args.images,
        "instruction": args.instruction
    })
    
    # エラーチェック
    if "error" in result:
        print(f"エラーが発生しました: {result['error']}")
        sys.exit(1)
    
    # 結果をファイルに保存
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(result["html_output"])
    
    print(f"スライドが生成されました: {args.output}")
