from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, UniqueConstraint, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine("sqlite:///temp.db", echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)


class Product(Base):
    __tablename__ = "product"
    __table_args__ = (UniqueConstraint("shop", "sku", "update_time", name="shop_sku"),)
    id = Column(Integer, primary_key=True)
    shop = Column(String(100), nullable=False)
    sku = Column(String(100), nullable=False)
    brand_name = Column(String(1000), nullable=True)
    name = Column(String(1000), nullable=False)
    uom = Column(String(100), nullable=False)
    url = Column(String(1000), nullable=False)
    update_time = Column(DateTime, nullable=False)

    prices = relationship("Price")


class Price(Base):
    __tablename__ = "price"
    __table_args__ = (UniqueConstraint("product_id", "update_time", name="product_id_update_time"),)
    id = Column(Integer, primary_key=True)
    price = Column(Float, nullable=False)
    currency = Column(String(100), nullable=False)
    update_time = Column(DateTime, nullable=False)

    product_id = Column(Integer, ForeignKey("product.id"))


Base.metadata.create_all(engine)
