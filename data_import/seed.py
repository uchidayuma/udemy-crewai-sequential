import os
import random
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import Base, SessionLocal, engine
import app.models.customer  # noqa: F401
import app.models.call_record  # noqa: F401
import app.models.ocr_card  # noqa: F401
from app.models.customer import Customer
from app.models.call_record import CallRecord

SURNAMES = [
    "田中", "佐藤", "鈴木", "高橋", "伊藤", "渡辺", "山本", "中村", "小林", "加藤",
    "吉田", "山田", "佐々木", "山口", "松本", "井上", "木村", "林", "斎藤", "清水",
]
GIVEN_NAMES = [
    "太郎", "次郎", "一郎", "健一", "誠", "浩", "隆", "大輔", "翔", "雄一",
    "花子", "恵子", "由美子", "幸子", "裕子", "明美", "久美子", "真由美", "直子", "里奈",
]
COMPANY_PREFIXES = [
    "東京", "大阪", "名古屋", "横浜", "福岡", "札幌", "仙台", "広島", "京都", "神戸",
    "川崎", "さいたま", "千葉", "北海道", "九州", "関東", "関西", "中部", "東海", "近畿",
]
COMPANY_TYPES = [
    "商事", "産業", "工業", "物産", "システム", "テクノロジー", "コンサルティング",
    "ソリューションズ", "ホールディングス", "サービス", "製作所", "建設", "食品", "化学", "電機",
]
ADDRESSES = [
    "東京都千代田区丸の内1-1-1",
    "大阪府大阪市北区梅田2-3-4",
    "愛知県名古屋市中村区名駅3-5-6",
    "神奈川県横浜市西区高島1-2-3",
    "福岡県福岡市博多区博多駅前4-5-6",
    "北海道札幌市中央区大通西2-7-8",
    "宮城県仙台市青葉区一番町3-9-10",
    "広島県広島市中区基町11-12-13",
    "京都府京都市下京区四条通烏丸東入",
    "兵庫県神戸市中央区三宮町1-14-15",
    "埼玉県さいたま市大宮区桜木町1-2-3",
    "千葉県千葉市中央区中央港1-3-5",
    "静岡県静岡市葵区追手町9-6-1",
    "茨城県水戸市三の丸1-1-38",
    "長野県長野市大字長野元善町481",
]
CONTACT_METHODS = ["電話", "メール", "訪問", "オンライン"]
CALL_RESULTS = [
    "折り返し希望", "商談確定", "資料送付済み", "不在",
    "興味なし", "検討中", "契約済み", "再コール希望", "担当者不在", "見積依頼",
]


def _random_date(start_days_ago: int, end_days_ago: int) -> date:
    days_ago = random.randint(start_days_ago, end_days_ago)
    return date.today() - timedelta(days=days_ago)


def _random_phone() -> str:
    area = random.choice(["03", "06", "052", "045", "092", "011", "022", "082", "075", "078"])
    return f"{area}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existing = db.query(Customer).count()
        if existing > 0:
            print(f"既にデータが存在します（{existing}件）。シードをスキップします。")
            return

        random.seed(42)

        for i in range(100):
            surname = random.choice(SURNAMES)
            given_name = random.choice(GIVEN_NAMES)
            prefix = COMPANY_PREFIXES[i % len(COMPANY_PREFIXES)]
            ctype = COMPANY_TYPES[i % len(COMPANY_TYPES)]
            # インデックスを付けて会社名の重複を防ぐ
            company_name = f"{prefix}{ctype}{i + 1:03d}"

            customer = Customer(
                customer_name=f"{surname} {given_name}",
                contact_number=_random_phone(),
                email=f"user{i + 1}@{company_name.replace(' ', '')}.co.jp",
                address=random.choice(ADDRESSES),
                company_name=company_name,
                last_purchase_date=_random_date(30, 730),
                total_purchase=round(random.uniform(500_000, 50_000_000) / 1000) * 1000,
                last_contact_method=random.choice(CONTACT_METHODS),
            )
            db.add(customer)
            db.flush()  # customer_id を確定させる

            # 架電履歴を 1〜5 件生成
            num_calls = random.randint(1, 5)
            call_dates = sorted(
                [_random_date(1, 365) for _ in range(num_calls)],
                reverse=True,
            )
            for call_date in call_dates:
                minutes = random.randint(1, 30)
                seconds = random.randint(0, 59)
                call_record = CallRecord(
                    customer_id=customer.customer_id,
                    call_date=call_date,
                    call_duration=f"{minutes:02d}:{seconds:02d}",
                    call_result=random.choice(CALL_RESULTS),
                )
                db.add(call_record)

        db.commit()
        print("シード完了: 顧客100件 + 架電履歴を投入しました。")
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed()
