from sqlalchemy.orm import Session
from . import models, schemas

def get_flower(db: Session, flower_id: int):
    return db.query(models.Flower).filter(models.Flower.id == flower_id).first()

def get_flowers(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Flower).offset(skip).limit(limit).all()

def create_flower(db: Session, flower: schemas.FlowerCreate):
    db_flower = models.Flower(**flower.dict())
    db.add(db_flower)
    db.commit()
    db.refresh(db_flower)
    return db_flower

def create_order(db: Session, order: schemas.OrderCreate):
    db_order = models.Order(**order.dict())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order
