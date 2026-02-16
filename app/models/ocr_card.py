from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base


class OcrCard(Base):
    __tablename__ = "ocr_card"

    card_id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customer.customer_id"))
    company_name = Column(String(255))
    personal_name = Column(String(255))
    email = Column(String(255))
    contact_number = Column(String(20))
    address = Column(String(255))
