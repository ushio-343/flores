from sqlalchemy import Column, Integer, String
from .database import Base

class Flower(Base):
    __tablename__ = "flowers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    stock = Column(Integer)
    price = Column(Integer)
