from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, Text, Enum, BigInteger, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import enum

app = FastAPI()

# Database configuration
DATABASE_URL = "mysql+pymysql://root:Pass%40123@localhost:3306/vibeosys_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Enums for Category and Unit of Measure
class CategoryEnum(str, enum.Enum):
    finished = "finished"
    semi_finished = "semi-finished"
    raw = "raw"

class UnitEnum(str, enum.Enum):
    mtr = "mtr"
    mm = "mm"
    ltr = "ltr"
    ml = "ml"
    cm = "cm"
    mg = "mg"
    gm = "gm"
    unit = "unit"
    pack = "pack"

# SQLAlchemy model for Product
class Product(Base):
    __tablename__ = "product"

    product_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    category = Column(Enum(CategoryEnum), nullable=False)
    description = Column(String(250))
    product_image = Column(Text)
    sku = Column(String(100))
    unit_of_measure = Column(Enum(UnitEnum), nullable=False)
    lead_time = Column(Integer)
    created_date = Column(TIMESTAMP, default=datetime.utcnow)
    updated_date = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

# Pydantic schemas
class ProductBase(BaseModel):
    name: str
    category: CategoryEnum
    description: Optional[str] = None
    product_image: Optional[str] = None
    sku: str
    unit_of_measure: UnitEnum
    lead_time: int

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    pass

class ProductOut(ProductBase):
    product_id: int
    created_date: datetime
    updated_date: datetime

    class Config:
        orm_mode = True

# Create tables
Base.metadata.create_all(bind=engine)

# Routes
@app.get("/product/list", response_model=List[ProductOut])
def list_products(page: int = Query(1, ge=1)):
    db = SessionLocal()
    try:
        products = db.query(Product).offset((page - 1) * 10).limit(10).all()
        return products
    finally:
        db.close()

@app.get("/product/{pid}/info", response_model=ProductOut)
def get_product_info(pid: int):
    db = SessionLocal()
    try:
        product = db.query(Product).filter(Product.product_id == pid).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    finally:
        db.close()

@app.post("/product/add", response_model=ProductOut)
def add_product(product: ProductCreate):
    db = SessionLocal()
    try:
        db_product = Product(**product.dict())
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product
    finally:
        db.close()

@app.put("/product/{pid}/update", response_model=ProductOut)
def update_product(pid: int, product: ProductUpdate):
    db = SessionLocal()
    try:
        db_product = db.query(Product).filter(Product.product_id == pid).first()
        if not db_product:
            raise HTTPException(status_code=404, detail="Product not found")

        for field, value in product.dict().items():
            setattr(db_product, field, value)
        db.commit()
        db.refresh(db_product)
        return db_product
    finally:
        db.close()
