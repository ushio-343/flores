from pydantic import BaseModel

class FlowerBase(BaseModel):
    name: str
    stock: int
    price: int

class FlowerCreate(FlowerBase):
    pass

class Flower(FlowerBase):
    id: int

    class Config:
        orm_mode = True

class OrderBase(BaseModel):
    flower_id: int
    quantity: int
    total_price: int

class OrderCreate(OrderBase):
    pass

class Order(OrderBase):
    id: int

    class Config:
        orm_mode = True
