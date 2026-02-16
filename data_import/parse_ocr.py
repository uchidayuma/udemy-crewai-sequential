import json


def parse_ocr(text):
    """名刺OCRテキスト（JSON形式）を構造化データに変換する"""
    return json.loads(text)
