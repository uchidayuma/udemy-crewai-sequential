from sqlalchemy import Column, Integer, String, Date, Float
from app.database import Base


class Customer(Base):
    __tablename__ = "customer"

    customer_id = Column(Integer, primary_key=True)
    customer_name = Column(String(255), nullable=False)
    contact_number = Column(String(20))
    email = Column(String(255))
    address = Column(String(255))
    company_name = Column(String(255), nullable=False)
    last_purchase_date = Column(Date)
    total_purchase = Column(Float, default=0.0)
    last_contact_method = Column(String(50))
