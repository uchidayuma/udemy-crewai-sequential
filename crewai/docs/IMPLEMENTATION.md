```markdown
# プロトタイプ実装コード: 架電レコメンドツール

## 1. プロジェクト構成

```plaintext
架電レコメンドツール/
├── backend/
│   ├── main.py                    # FastAPI アプリケーションのエントリポイント
│   ├── api/
│   │   ├── __init__.py
│   │   ├── customer.py             # 顧客詳細取得 API
│   │   ├── priority_list.py        # 架電優先リスト取得 API
│   │   └── script_hint.py          # トークスクリプトヒント生成 API
│   ├── models/
│   │   ├── __init__.py
│   │   └── customer.py             # Pydantic モデル
│   ├── data_import/
│   │   ├── __init__.py
│   │   └── import_scripts.py        # データ取込スクリプト
│   └── requirements.txt            # 必要なライブラリ
└── frontend/
    ├── index.html                  # 架電優先リスト画面
    └── customer_detail.html         # 顧客詳細画面
```

## 2. データ取込スクリプト（Python）

### 2.1. 基幹システムCSV の取込・クレンジング

```python
# backend/data_import/import_scripts.py

import pandas as pd

def import_customer_data(csv_file):
    # CSVの読み込み
    df = pd.read_csv(csv_file)

    # NULL補完
    df.fillna({'company': '不明', 'email': '不明'}, inplace=True)
    
    # 重複排除
    df.drop_duplicates(subset='email', keep='first', inplace=True)

    # データフレームをリストに変換して返す
    return df.to_dict(orient='records')
```

### 2.2. 支店Excel の取込・パース

```python
# backend/data_import/import_scripts.py (続き)

def import_branch_data(excel_file):
    # Excelの読み込み
    df = pd.read_excel(excel_file)

    # 必要なカラムのみ選択
    return df[['branch_id', 'branch_name']].to_dict(orient='records')
```

### 2.3. 名刺OCRテキストの構造化パース

```python
# backend/data_import/import_scripts.py (続き)

def parse_ocr_text(ocr_text):
    lines = ocr_text.split('\n')
    data = {}
    
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            data[key.strip()] = value.strip()
    
    return data
```

## 3. バックエンド API（FastAPI）

### 3.1. 主なバックエンドコード

```python
# backend/main.py

from fastapi import FastAPI
from api import customer, priority_list, script_hint

app = FastAPI()

# ルーティング設定
app.include_router(customer.router, prefix="/customers")
app.include_router(priority_list.router, prefix="/priority")
app.include_router(script_hint.router, prefix="/script-hints")
```

### 3.2. 架電優先リスト取得 API

```python
# backend/api/priority_list.py

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_priority_list():
    # スコアリングロジックに基づいた架電優先リストを取得
    priority_list = []  # データ取得・スコアリング処理をここに実装
    return priority_list
```

### 3.3. 顧客詳細取得 API

```python
# backend/api/customer.py

from fastapi import APIRouter

router = APIRouter()

@router.get("/{customer_id}")
def get_customer_details(customer_id: int):
    # IDに基づいて顧客詳細を取得する処理をここに実装
    customer_details = {}  # 顧客データを取得
    return customer_details
```

### 3.4. トークスクリプトヒント生成 API

```python
# backend/api/script_hint.py

from fastapi import APIRouter

router = APIRouter()

@router.get("/{customer_id}")
def generate_script_hint(customer_id: int):
    # LLMに基づくスクリプトヒント生成処理をここに実装
    script_hint = "自動生成されたスクリプトヒント"
    return {"hint": script_hint}
```

## 4. フロントエンド（HTML/Jinja2 テンプレート）

### 4.1. 架電優先リスト画面

```html
<!-- frontend/index.html -->

<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>架電優先リスト</title>
</head>
<body>
    <header>
        <h1>架電優先リスト</h1>
        <button onclick="logout()">ログアウト</button>
    </header>
    <div id="filter">
        <!-- フィルター機能ここに実装 -->
    </div>
    <div id="customer-list">
        <!-- 顧客カード動的に生成 -->
    </div>
    <script>
        function logout() {
            // ログアウト処理
        }
    </script>
</body>
</html>
```

### 4.2. 顧客詳細画面

```html
<!-- frontend/customer_detail.html -->

<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>顧客詳細</title>
</head>
<body>
    <header>
        <button onclick="goBack()">← 戻る</button>
        <h1>顧客詳細</h1>
    </header>
    <section id="customer-info">
        <!-- 基本情報表示 -->
    </section>
    <section id="contact-history">
        <!-- 連絡履歴表示 -->
    </section>
    <section id="purchase-history">
        <!-- 購買履歴表示 -->
    </section>
    <section id="script-hint">
        <!-- トークスクリプトヒント表示 -->
    </section>
    <script>
        function goBack() {
            // 前のページに戻る処理
        }
    </script>
</body>
</html>
```

## 5. 依存ライブラリ

```plaintext
# backend/requirements.txt

fastapi
uvicorn
pandas
openpyxl
```
```