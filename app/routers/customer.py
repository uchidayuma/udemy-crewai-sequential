from typing import Dict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.call_record import CallRecord
from app.models.customer import Customer

router = APIRouter()


@router.get("/customer/{customer_id}", response_model=Dict)
def get_customer_detail(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        return {
            "customer_id": customer_id,
            "customer_name": "不明な顧客",
            "contact_number": "",
            "email": "",
            "address": "",
            "company_name": "",
            "last_purchase_date": "",
            "total_purchase": 0,
            "last_contact_method": "",
            "call_history": [],
        }

    call_records = (
        db.query(CallRecord)
        .filter(CallRecord.customer_id == customer_id)
        .order_by(CallRecord.call_date.desc())
        .all()
    )

    return {
        "customer_id": customer.customer_id,
        "customer_name": customer.customer_name,
        "contact_number": customer.contact_number or "",
        "email": customer.email or "",
        "address": customer.address or "",
        "company_name": customer.company_name,
        "last_purchase_date": str(customer.last_purchase_date) if customer.last_purchase_date else "",
        "total_purchase": customer.total_purchase or 0,
        "last_contact_method": customer.last_contact_method or "",
        "call_history": [
            {
                "call_date": str(r.call_date),
                "call_result": r.call_result or "",
                "call_duration": r.call_duration or "",
            }
            for r in call_records
        ],
    }
