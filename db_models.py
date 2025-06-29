from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean, Numeric, JSON, Text, DateTime, Date, CheckConstraint
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime, UTC

engine = create_engine(
    'sqlite:///database.db',
    connect_args={"check_same_thread": False},  # Для многопоточности
    echo=True
)

class Base(DeclarativeBase):
    pass

class TimestampMixin:
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False
    )

class Users(Base, TimestampMixin):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    birth_date = Column(Date)  # birth_date=date(1990, 5, 15)  # Год, месяц, день
    description = Column(Text)
    orders = relationship('Orders', back_populates='users', cascade="all, delete-orphan")

class ProductTypes(Base, TimestampMixin):
    __tablename__ = 'product_types'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True, unique=True, nullable=False)
    description = Column(Text)
    products = relationship('Products', back_populates='product_types')

class Products(Base, TimestampMixin):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    cost = Column(Numeric(10, 2), nullable=False)
    product_type_id = Column(Integer, ForeignKey('product_types.id'), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    product_types = relationship('ProductTypes', back_populates='products')

    __table_args__ = (
        CheckConstraint('cost >= 0 AND cost <= 1000000', name='valid_cost_range'),
        CheckConstraint('is_active IN (0, 1)', name='valid_boolean'),
    )

class Orders(Base, TimestampMixin):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, index=True)
    content = Column(JSON, nullable=False)
    review = Column(Text)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    pay_status = Column(Boolean, default=False)
    description = Column(Text)
    users = relationship('Users', back_populates='orders')

