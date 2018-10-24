from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


class CrawlerStats(Base):
    __tablename__ = "crawler_stats"
    id = Column(Integer, primary_key=True)
    downloader_request_bytes = Column(Integer)
    downloader_request_count = Column(Integer)
    downloader_response_bytes = Column(Integer)
    downloader_response_count = Column(Integer)
    dupefilter_filtered = Column(Integer)
    finish_reason = Column(String(100))
    finish_time = Column(DateTime)
    item_scraped_count = Column(Integer)
    log_count_debug = Column(Integer)
    log_count_info = Column(Integer)
    memusage_max = Column(Integer)
    memusage_startup = Column(Integer)
    request_depth_max = Column(Integer)
    response_received_count = Column(Integer)
    scheduler_dequeued = Column(Integer)
    scheduler_dequeued_memory = Column(Integer)
    scheduler_enqueued = Column(Integer)
    scheduler_enqueued_memory = Column(Integer)
    start_time = Column(DateTime)


class Product(Base):
    __tablename__ = "product"
    __table_args__ = (UniqueConstraint("shop", "sku", "update_time", name="shop_sku"),)
    id = Column(Integer, primary_key=True)
    shop = Column(String(100))
    sku = Column(String(100))
    brand_name = Column(String(1000))
    name = Column(String(1000))
    uom = Column(String(100))
    url = Column(String(1000))
    update_time = Column(DateTime)
    source_filename = Column(String(100))

    prices = relationship("Price", back_populates="product")

    def __repr__(self):
        return f"<Product {self.shop} {self.sku} {self.name}>"


class Price(Base):
    __tablename__ = "price"
    __table_args__ = (UniqueConstraint("product_id", "update_time", name="product_id_update_time"),)
    id = Column(Integer, primary_key=True)
    price = Column(Float)
    currency = Column(String(100))
    update_time = Column(DateTime)
    source_filename = Column(String(100))

    product_id = Column(Integer, ForeignKey("product.id"))
    product = relationship("Product", back_populates="prices")

    def __repr__(self):
        return f"Price {self.product_id} {self.update_time} {self.price} {self.currency}>"


def get_session(uri):
    engine = create_engine(uri)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()
