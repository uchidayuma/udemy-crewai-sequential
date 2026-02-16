from datetime import date
from typing import Dict, List

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.call_record import CallRecord
from app.models.customer import Customer

router = APIRouter()


@router.get("/priority-list", response_model=List[Dict])
def get_priority_list(db: Session = Depends(get_db)):
    """架電優先リストをスコア順で返す。
    スコア式: (total_purchase / 1000) + (1 / days_since_last_call) * 100
    """
    latest_call_subq = (
        db.query(
            CallRecord.customer_id,
            func.max(CallRecord.call_date).label("latest_call_date"),
        )
        .group_by(CallRecord.customer_id)
        .subquery()
    )

    rows = (
        db.query(Customer, latest_call_subq.c.latest_call_date)
        .outerjoin(latest_call_subq, Customer.customer_id == latest_call_subq.c.customer_id)
        .all()
    )

    today = date.today()
    customers = []
    for customer, latest_call_date in rows:
        if latest_call_date:
            days_since_last_call = max((today - latest_call_date).days, 1)
        else:
            days_since_last_call = 365

        score = round(
            (customer.total_purchase / 1000) + (1 / days_since_last_call) * 100,
            2,
        )
        customers.append({
            "customer_id": customer.customer_id,
            "customer_name": customer.customer_name,
            "company_name": customer.company_name,
            "total_purchase": customer.total_purchase,
            "days_since_last_call": days_since_last_call,
            "score": score,
        })

    return sorted(customers, key=lambda x: x["score"], reverse=True)
