from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean, Numeric, JSON, Text, DateTime, Date, CheckConstraint
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime, UTC
from decimal import Decimal, ROUND_HALF_UP

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
    orders = relationship('Orders', back_populates='user', cascade="all, delete-orphan")


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


class Promocodes(Base, TimestampMixin):
    __tablename__ = 'promocodes'
    id = Column(Integer, primary_key=True, index=True)
    code_name = Column(String(30), nullable=False, unique=True, index=True)
    discount = Column(Numeric(5, 2), default=0.00, server_default='0.00', nullable=False)
    valid_from = Column(DateTime, default=datetime.now(UTC))  # Дата активации
    valid_to = Column(DateTime)  # Дата окончания
    is_active = Column(Boolean, default=True, server_default='true')  # Ручное отключение

    # Связь с заказами
    orders = relationship('Orders', back_populates='promocode')

    __table_args__ = (
        CheckConstraint('discount >= 0 AND discount <= 100', name='valid_discount_range'),
        CheckConstraint('valid_to IS NULL OR valid_to > valid_from', name='valid_period'),
    )


class Orders(Base, TimestampMixin):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, index=True)
    content = Column(JSON, nullable=False)
    subtotal = Column(Numeric(12, 2), default=0.00, nullable=False)
    promocode_id = Column(Integer, ForeignKey('promocodes.id'), index=True)
    total_amount = Column(Numeric(12, 2), default=0.00, nullable=False)
    review = Column(Text)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    pay_status = Column(Boolean, default=False)
    description = Column(Text)

    # Связи
    user = relationship('Users', back_populates='orders')
    promocode = relationship('Promocodes', back_populates='orders')

    __table_args__ = (
        CheckConstraint('total_amount >= 0', name='positive_total'),
        CheckConstraint('subtotal >= total_amount', name='valid_amounts'),
        CheckConstraint('subtotal >= 0', name='positive_subtotal'),
    )

    @hybrid_property
    def calculated_total(self) -> Decimal:
        """Автоматически вычисляемая итоговая сумма с учетом скидки."""
        subtotal = Decimal(str(self.subtotal))
        if self.promocode:
            discount = Decimal(str(self.promocode.discount)) / 100
            return (subtotal * (1 - discount)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return subtotal


