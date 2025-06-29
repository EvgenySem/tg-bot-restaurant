from sqlalchemy.orm import Session
from db_models import Users, Products, ProductTypes, engine

def fill_data():
    with Session(autoflush=False, bind=engine) as db:
        first_dish = ProductTypes(name='Первые блюда')
        second_dish = ProductTypes(name='Вторые блюда')
        deserts = ProductTypes(name='Десерты')
        drinks = ProductTypes(name='Напитки')

        first_dish.products = [Products(name='Борщ', cost=250, description='Свекла, картошка, капуста, говядина, томатная паста'),
                               Products(name='Солянка', cost=300, description='Колбаса 1, колбаса 2, оливки, говядина, маринованные огурцы'),
                               Products(name='Щи', cost=225, description='Капуста, морковь, говяжий бульон')
                               ]

        second_dish.products = [Products(name='Стейк рибай', cost=1250, description='Стейк рибай прожарки медиум'),
                                Products(name='Котлета с картофельным пюре', cost=360, description='Фарш свино-говяжий, картофель, молоко, масло'),
                                Products(name='Баварские сосиски с квашеной капустой', cost=400, description='Прямиком из Германии')
                                ]

        deserts.products = [Products(name='Медовик', cost=150, description='150 грамм'),
                            Products(name='Пирожное "Картошка"', cost=130, description='Печенье, шоколад, сгущенка'),
                            Products(name='Брауни', cost=140, description='Бельгийский шоколад, мука')
                            ]

        drinks.products = [Products(name='Чай', cost=100, description='250 мл'),
                            Products(name='Кофе', cost=110, description='Американо 250 мл'),
                            Products(name='Лимонад', cost=150, description='500 мл')
                            ]

        db.add_all([first_dish, second_dish, deserts, drinks])

        test_user = Users(id=12345, name='Тестовый Пользователь')
        db.add(test_user)

        db.commit()

if __name__ == '__main__':
    fill_data()
    print("Данные внесены в таблицу")
