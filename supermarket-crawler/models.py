from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, UniqueConstraint, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine("sqlite:///temp.db", echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)


class CrawlerStats(Base):
    __tablename__ = "crawler_stats"
    id = Column(Integer, primary_key=True)
    downloader_request_bytes = Column(Integer, nullable=True)
    downloader_request_count = Column(Integer, nullable=True)
    downloader_response_bytes = Column(Integer, nullable=True)
    downloader_response_count = Column(Integer, nullable=True)
    dupefilter_filtered = Column(Integer, nullable=True)
    finish_reason = Column(Integer, nullable=False)
    finish_time = Column(DateTime, nullable=False)
    item_scraped_count = Column(Integer, nullable=True)
    log_count_debug = Column(Integer, nullable=True)
    log_count_info = Column(Integer, nullable=True)
    memusage_max = Column(Integer, nullable=True)
    memusage_startup = Column(Integer, nullable=True)
    request_depth_max = Column(Integer, nullable=True)
    response_received_count = Column(Integer, nullable=True)
    scheduler_dequeued = Column(Integer, nullable=True)
    scheduler_dequeued_memory = Column(Integer, nullable=True)
    scheduler_enqueued = Column(Integer, nullable=True)
    scheduler_enqueued_memory = Column(Integer, nullable=True)
    start_time = Column(DateTime, nullable=False)


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
