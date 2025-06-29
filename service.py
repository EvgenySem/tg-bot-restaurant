from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from db_models import Users, Orders, Products, ProductTypes, engine

SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

def get_or_create_user(user_id: int, name: str):
    try:
        with SessionLocal() as db:
            user = db.query(Users).filter_by(id=user_id).first()
            if not user:
                user = Users(id=user_id, name=name, description='')
                db.add(user)
                db.commit()
                db.refresh(user)

            user_data = {'id': user.id,
                         'name': user.name,
                         'description': user.description
                         }

        return user_data

    except SQLAlchemyError as e:
        print(f'Ошибка базы данных в get_or_create_user: {e}')
        db.rollback()
        db.close()
        return None


def get_menu_of_product_type(product_type: str):
    try:
        with SessionLocal() as db:
            menu = db.query(ProductTypes).filter_by(name=product_type).first()
            menu_data = []
            for product in menu.products:
                menu_data.append({'id': product.id,
                                  'name': product.name,
                                  'cost': product.cost,
                                  'description': product.description
                                  }
                                 )

        return menu_data

    except SQLAlchemyError as e:
        print(f'Ошибка базы данных в get_menu_of_product_type: {e}')
        db.rollback()
        db.close()
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
                cart.content['total'] = total

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




from sqlalchemy import inspect

# Проверка активных соединений
def db_check():
    inspector = inspect(engine)
    print(inspector.get_foreign_keys('orders'))


