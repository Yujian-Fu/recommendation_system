from collections import OrderedDict
import csv 
import time
from config import *


class record:
    def __init__(self):
        self.record_num = 0
        self.product_dict = {}
        self.customer_dict = {}
        self.category_dict = category_dict()
        self.min_time = ""
        self.max_time = ""
        self.product_similarity = {}
        self.customer_similarity = {}
    

    def add_record(self, recorder):
        StartTime = time.time()

        for idx, each_record in enumerate(recorder):

            print('\r Loading the records:  ',idx," / ", len(recorder), end='')

            [time, action_type, product_id, category_id, category_code, brand, price, customer_id] = each_record[0:-1]

            self.category_dict.add_category(category_id, category_code)

            if product_id not in self.product_dict:
                self.product_dict[product_id] = product(product_id, category_id, brand)

            if customer_id in self.customer_dict:
                self.customer_dict[customer_id].add_record(time, action_type, product_id, price)
            else:
                self.customer_dict[customer_id] = customer(customer_id)
                self.customer_dict[customer_id].add_record(time, action_type, product_id, price)
        print("  Load the dataset with time usage: ", round(time.time() - StartTime, 2))

    def build_similarity_matrix(self):

        for idx, cus_id in enumerate(self.customer_dict):
            print('\r Building the similarity matrix:  ',idx," / ", len(self.customer_dict), end='')

            record_dict = self.customer_dict[cus_id].record_dict

            for time_stamp_1 in record_dict:

                product_id_1 = record_dict[time_stamp_1][1]
                action_type_1 = record_dict[time_stamp_1][0]
                price = record_dict[time_stamp_1][2]
                assert(product_id_1 in self.product_dict)

                if price not in self.product_dict[product_id_1].price:
                    self.product_dict[product_id_1].price[price] = 1
                else:
                    self.product_dict[product_id_1].price[price] += 1

                self.product_dict[product_id_1].add_record_num(action_type_1)

                for time_stamp_2 in record_dict:
                    product_id_2 = record_dict[time_stamp_2][1]

                    if product_id_1 is not product_id_2:
                        action_type_2 = record_dict[time_stamp_2][0]
                        pair_weight = self.customer_dict[cus_id].get_weight(action_type_1, action_type_2)
                        self.product_dict[product_id_1].add_product_pair(product_id_2, pair_weight)


    def compute_similarity(self):
        return 0


    def visualize(self):
        count = 0
        topK = 0
        for product in self.product_dict:
            count += 1
            self.product_dict[product].sort_value()
            print("The similar product for product ", self.product_dict[product].id, self.product_dict[product].brand, self.product_dict[product].category)
            for relation_product in self.product_dict[product].relation_dict:
                
                print(relation_product, self.product_dict[relation_product].id, self.product_dict[relation_product].brand, self.product_dict[relation_product].category, end="")
                topK += 1
                if topK > VIS_K:
                    break
            if count > VIS_NUM:
                break

    def prediction_item_based(self):
        return 0


class product:
    def __init__(self, product_id, category_id, brand):
        self.view_num = 0
        self.add_num = 0
        self.purchase_num = 0
        self.remove_num = 0

        self.id = product_id
        self.category = category_id
        self.brand = brand
        self.price = {}
        # other_product_id: value
        self.relation_dict = OrderedDict()

    def add_product_pair(self, target_id, weight_value):
        if target_id in self.relation_dict:
            self.relation_dict[target_id] += weight_value
        else:
            self.relation_dict[target_id] = weight_value
    
    def sort_value(self):
        self.relation_dict = OrderedDict(sorted(self.relation_dict.items(), key = lambda t:t[1]))

    def add_record_num(self, action_type):
        if action_type == "view":
            self.view_num += 1
        elif action_type == "cart":
            self.add_num += 1
        elif action_type == "purchase":
            self.purchase_num += 1
        elif action_type == "remove_from_cart":
            self.remove_num += 1
        else:
            print("Error: action type not defined:", action_type)
            exit(0)


class customer:
    def __init__(self, customer_id):
        self.record_num = 0
        self.id = customer_id
        self.record_dict = OrderedDict()

    def add_record(self, time, action_type, product_id, price):
        self.record_num += 1
        self.record_dict[time] = [action_type, product_id, price]

    def get_weight(self, action_type_1, action_type_2):
        if action_type_1 == "remove from chart" or action_type_2 == "remove from chart": 
            return -0.5
        else:
            return 1.0


class category_dict:
    def __init__(self):
        self.category_dict = {}
    
    def add_category(self, category_id, category_name):
        if category_id not in self.category_dict:
            self.category_dict[category_id] = category_name





