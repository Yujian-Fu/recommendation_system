# Whole step:
# 
import csv 
import time
from collections import Counter
from config import *

# The code for find all product pair in the same user purchase record
def cross_pattern(user_products):
    product_dict = {}
    for product_1 in user_products:
        for product_2 in user_products:
            if product_1 is not product_2:
                if product_1 in product_dict:
                    product_dict[product_1].append(product_2)
                else:
                    product_dict[product_1] = [product_2]
    return product_dict


start = time.time()


user_dict_view = {}
user_dict_buy = {}
user_dict_add_chart = {}
category_dict = {}

buy_weight = 5
add_weight = 3


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
            print("Finished ", 10*(i/print_each), " percent of the whole")
        
        
        product_id = reader[i][2]
        user_id = reader[i][7]
        category_id = reader[i][3]
        if product_id not in category_dict:
            category_dict[product_id] = category_id
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


final_product_dict = {}
for key in user_dict_view:
    each_user_record = cross_pattern(user_dict_view[key])
    for product_id in each_user_record:
        if product_id in final_product_dict:
            final_product_dict[product_id].append(each_user_record[product_id])
        else:
            final_product_dict[product_id] = each_user_record[product_id]

for key in user_dict_buy:
    each_user_record = cross_pattern(user_dict_buy[key])
    for product_id in each_user_record:
        if product_id in final_product_dict:
            final_product_dict[product_id].append(each_user_record[product_id])
        else:
            final_product_dict[product_id] = each_user_record[product_id]

for key in user_dict_add_chart:
    each_user_record = cross_pattern(user_dict_add_chart[key])
    for product_id in each_user_record:
        if product_id in final_product_dict:
            final_product_dict[product_id].append(each_user_record[product_id])
        else:
            final_product_dict[product_id] = each_user_record[product_id]



final_product_count_dict = {}
for key in final_product_dict:
    final_product_count_dict[key] = Counter(final_product_dict[key])

end = time.time()

print ("Time for processing: ", round(end - start, 2))




