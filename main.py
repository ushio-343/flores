from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .Database .Crud .Models . import crud, models, schemas, database

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# Dependency para obtener la sesión de la base de datos
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Rutas para flores
@app.get("/flowers/", response_model=list[schemas.Flower])
def read_flowers(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    flowers = crud.get_flowers(db, skip=skip, limit=limit)
    return flowers

@app.post("/flowers/", response_model=schemas.Flower)
def create_flower(flower: schemas.FlowerCreate, db: Session = Depends(get_db)):
    return crud.create_flower(db=db, flower=flower)

# Rutas para pedidos
@app.post("/orders/", response_model=schemas.Order)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    flower = crud.get_flower(db, flower_id=order.flower_id)
    if flower is None or flower.stock < order.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    order.total_price = order.quantity * flower.price
    return crud.create_order(db=db, order=order)
