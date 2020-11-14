# Whole step:
# 

import csv 


action_list = ['view', 'cart', 'remove_from_cart', 'purchase']

FileFolderPath = "./dataset/"
FileName = FileFolderPath + "2019-Dec.csv"
user_dict_view = {}
user_dict_buy = {}
user_dict_add_chart = {}

with open(FileName) as f:
    reader = list(csv.reader(f))
    print("The column name: ")
    print(reader[0])
    num_rows = len(reader)
    num_columns = len(reader[0])
    print("The total number of columns and rows ", num_rows, " ", num_columns)
    for i in range(1, num_rows):
        
        product_id = reader[i][2]
        user_id = reader[i][7]
        if reader[i][1] == "view":
            if user_id in user_dict_view:
                user_dict_view[user_id].append(product_id)
            else:
                user_dict_view[user_id] = [product_id]
        elif reader[i][1] == "cart":
            if user_id in user_dict_add_chart:
                user_dict_add_chart[user_id].append(product_id)
            else:
                user_dict_add_chart[user_id] = [product_id]
        elif reader[i][1] == "purchase":
            if user_id in user_dict_buy:
                user_dict_buy[user_id].append(product_id)
            else:
                user_dict_buy[user_id] = [product_id]

    for key in user_dict_view:
        print(key, user_dict_view[key])


            
            






