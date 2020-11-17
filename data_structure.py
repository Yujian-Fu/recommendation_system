from collections import OrderedDict
import csv 
import time
from config import *


def RaiseTypeError(S):
    print("Error: action type not defined:", S)
    exit(-1)


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

        for idx, each_record in enumerate(recorder, 1):
            
            [action_time, action_type, product_id, category_id, category_code, brand, price, customer_id] = each_record[0:-1]

            self.category_dict.add_category(category_id, category_code)

            if product_id not in self.product_dict:
                self.product_dict[product_id] = product(product_id, category_id, brand)

            if customer_id not in self.customer_dict:
                self.customer_dict[customer_id] = customer(customer_id)

            self.customer_dict[customer_id].add_record(action_time, action_type, product_id, price)
            
            print('\rLoading the records:  ',idx," / ", len(recorder), " remaining time: ", round((time.time() - StartTime) * (len(recorder) - idx) / idx, 2), " s", end='')
        
        for cus_id in self.customer_dict:
            self.customer_dict[cus_id].check_interest()
        
        print("Load the dataset with time usage: ", round(time.time() - StartTime, 2), " s")
        each_customer_list = [len(self.customer_dict[user].record_dict) for user in self.customer_dict ]
        print("\nThe total num of customer is: ", len(self.customer_dict), " The total number of product is: ", len(self.product_dict), " Each customer has record on ", 
             round(sum(each_customer_list) / len(each_customer_list), 2), "products on average")
        exit(0)


    def get_product_pair(self, cus_id):
        CustomerKeyList = self.customer_dict[cus_id].produc keys()
        CustomerPairList = []
        CustomerActionList = []
        CustomerPriceList = []
        for product1 in range(len(CustomerKeyList)):
            EachItemList = []
            CustomerActionList.append(self.customer_dict[])
            for product2 in range(i+1, len(CustomerKeyList)):





        

    def build_similarity_matrix(self):
        StartTime = time.time()

        product_pair = {}

        for idx, cus_id in enumerate(self.customer_dict, 1):



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
            print('\r Building the similarity matrix:  ',idx," / ", len(self.customer_dict), " remaining time: ", round((time.time() - StartTime) * (len(self.customer_dict) - idx) / idx, 2), " s", end='')

        print("   Build the similarity matrix with time usage: ", round(time.time() - StartTime, 2), " s")

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
                
                print(relation_product, self.product_dict[relation_product].id, self.product_dict[relation_product].brand, self.product_dict[relation_product].category)
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
        self.price = []
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
        if action_type == VIEW_S:
            self.view_num += 1
        elif action_type == ADD_S:
            self.add_num += 1
        elif action_type == PURCHASE_S:
            self.purchase_num += 1
        elif action_type == REMOVE_S:
            self.remove_num += 1
        else:
            RaiseTypeError(action_type)


class customer:
    def __init__(self, customer_id):
        self.record_num = 0
        self.id = customer_id
        self.product_dict = OrderedDict()

    def add_record(self, action_time, action_type, product_id, price):
        self.record_num += 1
        if product_id in self.record_dict:
            self.product_dict[product_id].append([action_time, action_type, price])
        else:
            self.product_dict[product_id] = [[action_time, action_type, price]]

    def check_interest(self):
        for product in self.product_dict:
            product_interest = 0
            product_interest_price = 0
            each_record_interest = 0

            for product_record in self.product_dict[product]:
                
                if product_record[1] == VIEW_S:
                    each_record_interest = VIEW_W

                elif product_record[1] == ADD_S:
                    each_record_interest = ADD_W

                elif product_record[1] == PURCHASE_S:
                    each_record_interest = PURCHASE_W
                
                elif product_record[1] == REMOVE_S:
                    each_record_interest = REMOVE_W
                
                else:
                    RaiseTypeError(product_record[1])
                
                product_interest += each_record_interest
                product_interest_price += each_record_interest * product_record[2]

            product_interest_price /= product_interest
            if product_interest > MAX_W:
                product_interest = MAX_W
            
            product_dict[product] = [product_interest, product_interest_price]


    def get_weight(self, action_type_1, action_type_2):
        if action_type_1 == "remove_from_cart" or action_type_2 == "remove_from_cart": 
            return -0.5
        else:
            return 1.0


class category_dict:
    def __init__(self):
        self.category_dict = {}
    
    def add_category(self, category_id, category_name):
        if category_id not in self.category_dict:
            self.category_dict[category_id] = category_name





