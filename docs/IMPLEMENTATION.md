```markdown
# プロトタイプ実装仕様書: 架電レコメンドツール

## 1. プロジェクト構成

```plaintext
project_root/
├── data_import/
│   ├── import_csv.py        # 基幹システムCSV の取込・クレンジング
│   ├── import_excel.py      # 支店Excel の取込・パース
│   └── parse_ocr.py         # 名刺OCRテキストの構造化パース
├── app/
│   ├── main.py              # FastAPI アプリケーションのエントリーポイント
│   ├── routers/
│   │   ├── customer.py      # 顧客詳細取得 API
│   │   └── scoring.py       # 架電優先リスト取得 API
│   ├── models/
│   │   ├── customer.py      # SQLAlchemy 顧客モデル
│   │   ├── call_record.py    # SQLAlchemy 通話記録モデル
│   │   └── ocr_card.py      # SQLAlchemy OCRカードモデル
│   └── services/
│       └── llm_service.py   # トークスクリプトヒント生成 API（LLM呼び出し）
└── frontend/
    ├── templates/
    │   ├── index.html        # 架電優先リスト画面
    │   └── customer_detail.html # 顧客詳細画面
    └── static/
        └── styles.css        # スタイルシート
```

## 2. データ取込スクリプト（Python）

### 2.1 基幹システムCSV の取込・クレンジング

`data_import/import_csv.py`
```python
import pandas as pd

def import_csv(file_path):
    df = pd.read_csv(file_path)
    # NULL補完
    df.fillna({
        'last_purchase_date': '1970-01-01',
        'total_purchase': 0.0
    }, inplace=True)
    
    # 重複排除
    df.drop_duplicates(subset='company_name', inplace=True)
    
    return df
```

### 2.2 支店Excel の取込・パース

`data_import/import_excel.py`
```python
import pandas as pd

def import_excel(file_path):
    df = pd.read_excel(file_path)
    # 必要なカラムのみを抽出
    necessary_columns = ['customer_name', 'company_name']
    return df[necessary_columns]
```

### 2.3 名刺OCRテキストの構造化パース

`data_import/parse_ocr.py`
```python
import json

def parse_ocr(text):
    # 単純なJSON形式で受け取ると仮定
    return json.loads(text)
```

## 3. バックエンド API（FastAPI）

### 3.1 FastAPI アプリケーションのエントリーポイント

`app/main.py`
```python
from fastapi import FastAPI
from app.routers import customer, scoring

app = FastAPI()

app.include_router(customer.router)
app.include_router(scoring.router)

# サーバー起動時のメッセージ
@app.on_event("startup")
def startup_event():
    print("FastAPI server is starting...")
```

### 3.2 架電優先リスト取得 API（スコアリングロジック込み）

`app/routers/scoring.py`
```python
from fastapi import APIRouter
from typing import List, Dict

router = APIRouter()

@router.get("/priority-list", response_model=List[Dict])
def get_priority_list():
    # スコア計算ロジック
    # 仮のデータでスコアを計算
    # 実際にはデータベースから取得することを想定
    customers = [
        {"customer_name": "田中商事", "total_purchase": 10000000, "days_since_last_call": 10},
        {"customer_name": "佐藤商事", "total_purchase": 5000000, "days_since_last_call": 5}
    ]
    
    for customer in customers:
        customer['score'] = (customer['total_purchase'] / 1000) + (1 / customer['days_since_last_call']) * 100
    
    # スコアで顧客リストをソート
    return sorted(customers, key=lambda x: x['score'], reverse=True)
```

### 3.3 顧客詳細取得 API

`app/routers/customer.py`
```python
from fastapi import APIRouter
from typing import Dict

router = APIRouter()

@router.get("/customer/{customer_id}", response_model=Dict)
def get_customer_detail(customer_id: int):
    # 通常はデータベースから実データを取得
    # 仮のデータを返す
    return {
        "customer_name": "田中商事",
        "contact_number": "03-xxxx-xxxx",
        "email": "info@tanakasyouji.com",
        "address": "東京都千代田区",
        "last_purchase_date": "2023-09-12",
        "total_purchase": 10000000
    }
```

### 3.4 トークスクリプトヒント生成 API（LLM呼び出し）

`app/services/llm_service.py`
```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/script-hint")
def generate_script_hint():
    # サンプルデータを仮に返す
    return {
        "hint": "新製品に興味がありそうなので次回の架電時に提案してみましょう。"
    }
```

## 4. フロントエンド（HTML/Jinja2 テンプレート）

### 4.1 架電優先リスト画面

`frontend/templates/index.html`
```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <link rel="stylesheet" href="/static/styles.css">
    <title>架電優先リスト</title>
</head>
<body>
    <header>
        <h1>架電優先リスト</h1>
        <input type="text" placeholder="顧客名で検索">
        <button>フィルター</button>
    </header>
    <main>
        <ul id="customer-list">
            <!-- 顧客リストがここに表示される -->
        </ul>
    </main>
    <script>
        // AJAXで顧客リストを取得し表示
    </script>
</body>
</html>
```

### 4.2 顧客詳細画面

`frontend/templates/customer_detail.html`
```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <link rel="stylesheet" href="/static/styles.css">
    <title>顧客詳細</title>
</head>
<body>
    <header>
        <h1>顧客詳細</h1>
    </header>
    <main>
        <div>
            <h2>顧客名: 田中商事</h2>
            <p>住所: 東京都千代田区</p>
            <p>電話番号: 03-xxxx-xxxx</p>
        </div>
        <div id="script-hint">
            <!-- トークスクリプトのヒントがここに表示される -->
        </div>
    </main>
</body>
</html>
```
```