import io
from datetime import date
from typing import Dict, Optional

import pandas as pd
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.call_record import CallRecord
from app.models.customer import Customer
from app.models.ocr_card import OcrCard

router = APIRouter()


@router.post("/import/manual", response_model=Dict)
def import_manual(
    customer_name: str = Form(...),
    company_name: str = Form(...),
    contact_number: str = Form(""),
    email: str = Form(""),
    address: str = Form(""),
    total_purchase: float = Form(0.0),
    last_purchase_date: str = Form(""),
    db: Session = Depends(get_db),
):
    parsed_date: Optional[date] = None
    if last_purchase_date:
        try:
            parsed_date = date.fromisoformat(last_purchase_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="最終購入日の形式が不正です（YYYY-MM-DD）")

    customer = Customer(
        customer_name=customer_name,
        company_name=company_name,
        contact_number=contact_number or None,
        email=email or None,
        address=address or None,
        total_purchase=total_purchase,
        last_purchase_date=parsed_date,
        last_contact_method="手動入力",
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return {"success": True, "customer_id": customer.customer_id}


@router.post("/call-record", response_model=Dict)
def add_call_record(
    customer_id: int = Form(...),
    call_date: str = Form(...),
    call_result: str = Form(...),
    call_duration: str = Form(""),
    db: Session = Depends(get_db),
):
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="顧客が見つかりません")

    try:
        parsed_date = date.fromisoformat(call_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="架電日の形式が不正です（YYYY-MM-DD）")

    record = CallRecord(
        customer_id=customer_id,
        call_date=parsed_date,
        call_result=call_result,
        call_duration=call_duration or None,
    )
    db.add(record)
    db.commit()
    return {"success": True}


@router.post("/import/csv", response_model=Dict)
async def import_csv_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="CSVファイルをアップロードしてください")

    content = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(content), encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(io.BytesIO(content), encoding="shift_jis")

    required = {"customer_name", "company_name"}
    if not required.issubset(df.columns):
        raise HTTPException(status_code=400, detail=f"CSVに必須カラムがありません: {required}")

    df.drop_duplicates(subset="company_name", inplace=True)

    count = 0
    skipped = 0
    for _, row in df.iterrows():
        exists = db.query(Customer).filter(Customer.company_name == str(row["company_name"])).first()
        if exists:
            skipped += 1
            continue
        customer = Customer(
            customer_name=str(row["customer_name"]),
            company_name=str(row["company_name"]),
            contact_number=str(row.get("contact_number", "") or "") or None,
            email=str(row.get("email", "") or "") or None,
            address=str(row.get("address", "") or "") or None,
            total_purchase=float(row.get("total_purchase", 0) or 0),
            last_contact_method="CSV取込",
        )
        db.add(customer)
        count += 1

    db.commit()
    return {"success": True, "imported": count, "skipped": skipped}


@router.post("/import/card", response_model=Dict)
def import_card(
    company_name: str = Form(...),
    personal_name: str = Form(...),
    contact_number: str = Form(""),
    email: str = Form(""),
    address: str = Form(""),
    db: Session = Depends(get_db),
):
    customer = db.query(Customer).filter(Customer.company_name == company_name).first()
    if not customer:
        customer = Customer(
            customer_name=personal_name,
            company_name=company_name,
            contact_number=contact_number or None,
            email=email or None,
            address=address or None,
            total_purchase=0.0,
            last_contact_method="名刺",
        )
        db.add(customer)
        db.flush()

    card = OcrCard(
        customer_id=customer.customer_id,
        company_name=company_name,
        personal_name=personal_name,
        email=email or None,
        contact_number=contact_number or None,
        address=address or None,
    )
    db.add(card)
    db.commit()
    return {"success": True, "customer_id": customer.customer_id}
