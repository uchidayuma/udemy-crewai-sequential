from sqlalchemy import Column, Integer, String, Date, ForeignKey
from app.database import Base


class CallRecord(Base):
    __tablename__ = "call_record"

    call_id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customer.customer_id"))
    call_date = Column(Date, nullable=False)
    call_duration = Column(String(10))
    call_result = Column(String(255))
