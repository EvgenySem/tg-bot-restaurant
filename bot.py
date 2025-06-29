from service import *

# id = 1234
# name = 'User Testing'
#
# user = get_or_create_user(id, name)
# print(user)

# menu = get_menu_of_product_type('Вторые блюда')
# for p in menu:
#     print(f'{p["name"]}, Цена: {p["cost"]}, Info: {p["description"]}')

# user_id = 11111
user_id = 123
product_id = 4
res = add_to_cart(user_id, product_id)
print(res)
# res = add_to_cart(user_id, 5)
# print(res)

# db_check()