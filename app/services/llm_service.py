from fastapi import APIRouter

router = APIRouter()


@router.get("/script-hint")
def generate_script_hint(customer_id: int = 0):
    """トークスクリプトのヒントを返す。プロトタイプでは固定文言を使用"""
    # 実際にはLLM APIを呼び出してcustomer_idに応じたヒントを生成する
    hints = {
        1: "最終購入から3ヶ月が経過しています。新製品ラインのご案内と、前回の商談でご興味を持たれた保守サービスについて提案してみましょう。",
        2: "資料送付後のフォローアップのタイミングです。資料の感想を確認し、具体的な導入スケジュールについて話を進めましょう。",
    }
    return {
        "hint": hints.get(customer_id, "顧客のニーズに合わせた提案を心がけましょう。前回の会話内容を確認してから架電することをおすすめします。")
    }
