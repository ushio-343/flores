# Florist API - Catálogo y Pedidos

Esta es una API Restful para un vivero, diseñada para manejar un catálogo de flores y un sistema de pedidos, utilizando **FastAPI** y **PostgreSQL**.

## Requisitos previos

Asegúrate de tener instalados los siguientes programas:
- **Python 3.8+**
- **PostgreSQL**
- **Git**

## Estructura del proyecto

```bash
florist-api/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   ├── database.py
├── README.md
├── requirements.txt
```

## Instalación

### 1. Clonar el repositorio

Clona este repositorio en tu máquina local:

```bash
git clone https://github.com/tu-usuario/florist-api.git
cd florist-api
```

### 2. Crear y activar entorno virtual

Crea un entorno virtual para aislar las dependencias del proyecto:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows
```

### 3. Instalar dependencias

Instala las dependencias necesarias para la API con el siguiente comando:

```bash
pip install -r requirements.txt
```

### 4. Configuración de la base de datos

1. Instala y configura **PostgreSQL** en tu sistema.
2. Crea una base de datos para la API:
   ```sql
   CREATE DATABASE florist_db;
   ```
3. Actualiza el archivo `app/database.py` con tus credenciales de base de datos. Busca esta línea:

   ```python
   SQLALCHEMY_DATABASE_URL = "postgresql://usuario:contraseña@localhost/nombre_base_datos"
   ```

   Y reemplaza `usuario`, `contraseña`, `localhost`, y `nombre_base_datos` por los datos correspondientes a tu configuración.

## Ejecutar la aplicación

### 1. Crear tablas en la base de datos

La aplicación utiliza SQLAlchemy para la creación automática de tablas. Cuando ejecutes el servidor, las tablas se crearán automáticamente.

### 2. Levantar el servidor

Ejecuta el siguiente comando para iniciar el servidor FastAPI:

```bash
uvicorn app.main:app --reload
```

El servidor se iniciará en `http://127.0.0.1:8000/`.

### 3. Ver la documentación de la API

La documentación interactiva generada automáticamente por Swagger estará disponible en:

- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Redoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## Endpoints de la API

### **Flores** (`/flowers/`)

1. **GET /flowers/**: Obtiene la lista de flores disponibles.

   Ejemplo de petición:
   ```bash
   curl -X 'GET' \
   'http://127.0.0.1:8000/flowers/' \
   -H 'accept: application/json'
   ```

2. **POST /flowers/**: Crea una nueva flor.

   Ejemplo de petición:
   ```bash
   curl -X 'POST' \
   'http://127.0.0.1:8000/flowers/' \
   -H 'Content-Type: application/json' \
   -d '{
     "name": "Rosa",
     "stock": 50,
     "price": 25
   }'
   ```

### **Pedidos** (`/orders/`)

1. **POST /orders/**: Crea un nuevo pedido.

   Ejemplo de petición:
   ```bash
   curl -X 'POST' \
   'http://127.0.0.1:8000/orders/' \
   -H 'Content-Type: application/json' \
   -d '{
     "flower_id": 1,
     "quantity": 10,
     "total_price": 250
   }'
   ```

## Archivos importantes

### **app/database.py**

Este archivo configura la conexión a la base de datos PostgreSQL:

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://usuario:contraseña@localhost/nombre_base_datos"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### **app/models.py**

Define los modelos de la base de datos para flores y pedidos:

```python
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Flower(Base):
    __tablename__ = "flowers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    stock = Column(Integer)
    price = Column(Integer)

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    flower_id = Column(Integer, ForeignKey("flowers.id"))
    quantity = Column(Integer)
    total_price = Column(Integer)

    flower = relationship("Flower")
```

### **app/schemas.py**

Define los esquemas para la validación y serialización de datos:

```python
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
```

### **app/crud.py**

Operaciones CRUD para manejar las flores y pedidos:

```python
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
```

### **app/main.py**

Archivo principal que define las rutas de la API:

```python
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import crud, models, schemas, database

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/flowers/", response_model=list[schemas.Flower])
def read_flowers(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    flowers = crud.get_flowers(db, skip=skip, limit=limit)
    return flowers

@app.post("/flowers/", response_model=schemas.Flower)
def create_flower(flower: schemas.FlowerCreate, db: Session = Depends(get_db)):
    return crud.create_flower(db=db, flower=flower)

@app.post("/orders/", response_model=schemas.Order)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    flower = crud.get_flower(db, flower_id=order.flower_id)
    if flower is None or flower.stock < order.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    order.total_price = order.quantity * flower.price
    return crud.create_order(db=db, order=order)
```
