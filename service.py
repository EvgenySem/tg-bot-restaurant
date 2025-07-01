from typing import List, Optional, Dict, cast
from sqlalchemy import inspect, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, joinedload
from db_models import Users, Orders, Products, ProductTypes, engine
from pydantic import BaseModel

SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

class UserResponse(BaseModel):
    id: int
    name: str
    description: str


def get_or_create_user(user_id: int, name: str, return_model: bool = False) -> Users | UserResponse | None:
    """Получает или создает пользователя.

    Args:
        user_id: Уникальный идентификатор пользователя
        name: Имя пользователя
        return_model: возвращает Pydantic-модель, если True

    Returns:
        Объект Users или None при ошибке
    """
    try:
        with SessionLocal() as db:
            # Пытаемся найти пользователя
            user = db.get(Users, user_id)

            if not user:
                # Создаем нового пользователя
                user = Users(
                    id=user_id,
                    name=name,
                    description=''
                )
                db.add(user)

            # Всегда коммитим, даже если пользователь существовал
            db.commit()

            if return_model:
                return UserResponse(
                    id=user.id,
                    name=user.name,
                    description=user.description
                )

            return user

    except SQLAlchemyError as e:
        print(f'Ошибка базы данных в get_or_create_user: {e}')
        # Откатываем изменения (контекстный менеджер закроет сессию)
        if 'db' in locals():
            db.rollback()
        return None


def get_menu_categories() -> Optional[List[str]]:
    """Возвращает список названий категорий меню.

    Returns:
        Optional[List[str]]:
        - Список названий категорий (может быть пустым)
        - None в случае ошибки базы данных
    """
    try:
        with SessionLocal() as db:
            return db.scalars(select(ProductTypes.name)).all()

    except SQLAlchemyError as e:
        print(f'Ошибка базы данных в get_menu_categories: {e}')
        return None


def get_active_menu_of_product_type(product_type: str) -> Optional[List[Dict[str, object]]]:
    """Возвращает меню активных продуктов для указанного типа продукта.

    Args:
        product_type: Название типа продукта (категории)

    Returns:
        Optional[List[Dict]]:
        - Список активных продуктов с их атрибутами
        - None при ошибке базы данных
        - Пустой список, если категория не найдена или нет активных продуктов
    """
    try:
        with SessionLocal() as db:
            # Получаем тип продукта с жадной загрузкой ТОЛЬКО активных продуктов
            product_type_obj = cast(
                Optional[ProductTypes], # Явно указываем тип
                db.scalar(
                    select(ProductTypes)
                    .where(ProductTypes.name == product_type)
                    .options(
                        joinedload(ProductTypes.products.and_(Products.is_active == True))
                    )
                )
            )

            if not product_type_obj:
                return []  # Категория не найдена

            return [
                {
                    'id': product.id,
                    'name': product.name,
                    'cost': float(product.cost),
                    'description': product.description
                }
                for product in product_type_obj.products
                # Фильтрация уже выполнена на уровне БД через and_
            ]

    except SQLAlchemyError as e:
        print(f'Ошибка базы данных в get_menu_of_product_type: {e}')
        return None


def add_to_cart(user_id: int, product_id: int):
    try:
        with SessionLocal() as db:
            cart = db.query(Orders).filter(Orders.user_id == user_id, Orders.pay_status == False).first()
            cost = db.query(Products).filter_by(id=product_id).first().cost

        with SessionLocal() as db:
            if not cart:
                cart = Orders(user_id=user_id, pay_status=False, content={'products': [product_id],
                                                                          'total': cost}) #'total': cost
                db.add(cart)
            else:
                # cart.content.setdefault('products', []).append(product_id)
                # db.merge(cart)  # Используем merge для "прикрепления" объекта

                products = cart.content.get('products', []) # Безопасное извлечение, если нет такого ключа (защита от KeyError)
                products.append(product_id)
                cart.content['products'] = products

                total = float(cart.content.get('total')) + float(cost)
                cart.content['total'] = float(total)

            # print(cart.content)
            db.commit()
            db.refresh(cart)

            cart_data = cart.content

        return cart_data

    except SQLAlchemyError as e:
        print(f'Ошибка базы данных в add_to_cart: {e}')
        return None
    finally:
        db.close()  # Гарантированное закрытие соединения





# Проверка активных соединений
def db_check():
    inspector = inspect(engine)
    print(inspector.get_foreign_keys('orders'))



# Вызов автоматического расчета стоимости заказа
'''
# В методах работы с заказом
def create_order(user_id: int, products: list, promocode=None):
    subtotal = sum(p.cost for p in products)
    order = Orders(
        subtotal=subtotal,
        promocode=promocode,
        total_amount=order.calculated_total  # Используем гидратированное значение
    )
'''
