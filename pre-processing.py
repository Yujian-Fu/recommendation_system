# Whole step:
# 

import csv 
import time

start = time.time()


action_list = ['view', 'cart', 'remove_from_cart', 'purchase']

FileFolderPath = "./dataset/"
FileName = FileFolderPath + "2019-Oct.csv"
user_dict_view = {}
user_dict_buy = {}
user_dict_add_chart = {}

with open(FileName) as f:
    print("Read file from: ", FileName)
    reader = list(csv.reader(f))
    print("The column name: ")
    print(reader[0])
    num_rows = len(reader)
    num_columns = len(reader[0])
    print_each = num_rows / 10
    print("The total number of columns and rows ", num_rows, " ", num_columns)
    for i in range(1, num_rows):
        if i % print_each == 0:
            print("Finished ", (i/print_each), "of the whole")
        
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

    print("The total number of view record: ", len(user_dict_view))
    sum = 0
    for key in user_dict_view:
        if len(user_dict_view[key]) > 1:
            sum += 1
    print("The total number of useful view record: ", sum)

    print("The total number of buy record: ", len(user_dict_buy))
    sum = 0
    for key in user_dict_view:
        if len(user_dict_view[key]) > 1:
            sum += 1
    print("The total number of useful buy record: ", sum)
            
    print("The total number of cart record: ", len(user_dict_add_chart))
    sum = 0
    for key in user_dict_add_chart:
        if len(user_dict_add_chart[key]) > 1:
            sum += 1
    print("The total number of useful buy record: ", sum)


end = time.time()
print ("Time for processing: ", round(end - start, 2))




