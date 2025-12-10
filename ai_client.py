"""AI APIクライアントモジュール"""
from typing import Optional

from database import get_setting


CATEGORIZE_PROMPT = """
以下のテキストを分析して、最も適切なカテゴリを1つだけ返してください。

カテゴリ一覧:
- url: URLやリンク
- email: メールアドレス
- code: プログラムコード、スクリプト
- phone: 電話番号
- filepath: ファイルパス、ディレクトリパス
- text: 上記に該当しない一般的なテキスト

テキスト:
{text}

カテゴリ名のみを返してください（例: code）:
"""


def categorize_with_openai(text: str) -> Optional[str]:
    """OpenAI APIでカテゴリ分類"""
    api_key = get_setting("openai_api_key", "")
    if not api_key:
        return None

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": CATEGORIZE_PROMPT.format(text=text[:1000]),
                }
            ],
            max_tokens=20,
            temperature=0,
        )

        result = response.choices[0].message.content.strip().lower()

        # 有効なカテゴリか確認
        valid_categories = ["url", "email", "code", "phone", "filepath", "text"]
        if result in valid_categories:
            return result

    except Exception as e:
        print(f"OpenAI APIエラー: {e}")

    return None


def categorize_with_gemini(text: str) -> Optional[str]:
    """Google Gemini APIでカテゴリ分類"""
    api_key = get_setting("gemini_api_key", "")
    if not api_key:
        return None

    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-pro")

        response = model.generate_content(
            CATEGORIZE_PROMPT.format(text=text[:1000]),
            generation_config={
                "max_output_tokens": 20,
                "temperature": 0,
            },
        )

        result = response.text.strip().lower()

        # 有効なカテゴリか確認
        valid_categories = ["url", "email", "code", "phone", "filepath", "text"]
        if result in valid_categories:
            return result

    except Exception as e:
        print(f"Gemini APIエラー: {e}")

    return None


def categorize_with_ai(text: str) -> Optional[str]:
    """設定されたAIプロバイダーでカテゴリ分類"""
    ai_provider = get_setting("ai_provider", "none")
    if ai_provider == "openai":
        return categorize_with_openai(text)
    elif ai_provider == "gemini":
        return categorize_with_gemini(text)

    return None


def test_api_connection(provider: str, api_key: str) -> tuple[bool, str]:
    """API接続テスト"""
    if provider == "openai":
        try:
            from openai import OpenAI

            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5,
            )
            return True, "接続成功"
        except Exception as e:
            return False, f"接続エラー: {str(e)}"

    elif provider == "gemini":
        try:
            import google.generativeai as genai

            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-pro")
            response = model.generate_content("test")
            return True, "接続成功"
        except Exception as e:
            return False, f"接続エラー: {str(e)}"

    return False, "不明なプロバイダー"
