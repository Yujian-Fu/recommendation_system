from collections import OrderedDict
import csv 
import time
from config import *
import concurrent.futures
import os
import pickle
import numpy as np 
import heapq

def RaiseTypeError(S):
    print("Error: Type not defined:", S)
    exit(-1)


class record:
    def __init__(self):
        self.category_dict = {}
        self.customer_dict = {}
        self.product_dict = {}

        self.record_num = 0
        self.use_parallel = 1 if USE_PARALLEL else 0
        self.similarity_type = SIMILARITY_TYPE

    def add_record(self, recorder):
        StartTime = time.time()

        for idx, each_record in enumerate(recorder):

            if idx > 0:
                if recorder[idx] == recorder[idx - 1]:
                    continue

            [action_time, action_type, product_id, category_id, category_code, brand, price, customer_id] = each_record[0:-1]
            product_id = int(product_id)
            category_id = int(category_id)
            price = float(price)
            customer_id = int(customer_id)

            if category_id not in self.category_dict:
                self.category_dict[category_id] = category_code

            if product_id not in self.product_dict:
                self.product_dict[product_id] = product(product_id, category_id, brand)

            self.product_dict[product_id].add_record_num(action_type)

            if customer_id not in self.customer_dict:
                self.customer_dict[customer_id] = customer(customer_id)

            self.customer_dict[customer_id].add_record(action_time, action_type, product_id, price)

            print('\rLoading the records:  ',idx+1," / ", len(recorder), " remaining time: ", round((time.time() - StartTime) * (len(recorder) - idx+1) / (idx+1), 2), " s", end='')
        print()

        
        for cus_id in self.customer_dict:
            self.customer_dict[cus_id].check_interest()
        
        print("Load the dataset with time usage: ", round(time.time() - StartTime, 2), " s")
        each_customer_list = [len(self.customer_dict[user].product_dict) for user in self.customer_dict ]
        print("Total num of customer: ", len(self.customer_dict), " Total number of product: ", len(self.product_dict), " Each customer has ", 
             round(sum(each_customer_list) / len(each_customer_list), 2), "products on average")


    def get_product_pair(self, cus_id):
        CustomerProductDict = self.customer_dict[cus_id].product_dict
        CustomerKeyList = list(CustomerProductDict.keys())
        CustomerPairList = []
        CustomerPriceDict = {}
        for index1 in range(len(CustomerKeyList)):
            ProductKey1 = CustomerKeyList[index1]
            CustomerPriceDict[ProductKey1] = self.customer_dict[cus_id].price_dict[ProductKey1]

            for index2 in range(index1+1, len(CustomerKeyList)):
                ProductKey2 = CustomerKeyList[index2]
                Weight1 = CustomerProductDict[ProductKey1]
                Weight2 = CustomerProductDict[ProductKey2]
                CustomerPairList.append([ProductKey1, ProductKey2, Weight1 * Weight2])

        return [CustomerPairList, CustomerPriceDict]


    def build_similarity_matrix(self):
        StartTime = time.time()

        ProductPairDict = {}
        ProductPriceDict = {}

        if USE_PARALLEL:
            with concurrent.futures.ProcessPoolExecutor() as executer:
                cus_list = list(self.customer_dict.keys())
                for cus_id, [CustomerPairList, CustomerPriceDict] in zip(cus_list, executer.map(self.get_product_pair, cus_list)):
                    ProductPairDict[cus_id], ProductPriceDict[cus_id] = CustomerPairList, CustomerPriceDict
        else:
            for idx, cus_id in enumerate(self.customer_dict):
                print("\rBuilding Product Pairs: ", idx, " / ", len(self.customer_dict), " remaining time: ", 
                      round((time.time() - StartTime) * (len(self.customer_dict) - idx+1) / (idx+1), 2), " s", end='')
                ProductPairDict[cus_id], ProductPriceDict[cus_id] = self.get_product_pair(cus_id)
            print()


        print("Adding price records")
        for UserID in ProductPriceDict:
            for ProductID in ProductPriceDict[UserID]:
                self.product_dict[ProductID].price.append(ProductPriceDict[UserID][ProductID])

        print("Adding Product Pairs")
        for ProductPairID in ProductPairDict:
            ProducPairList = ProductPairDict[ProductPairID]
            for ProductPair in ProducPairList:
                assert(len(ProductPair) == 3)
                self.product_dict[ProductPair[0]].add_product_pair(ProductPair[1], ProductPair[2])
                self.product_dict[ProductPair[1]].add_product_pair(ProductPair[0], ProductPair[2])

        print("Sorting the product matrix")
        for product in self.product_dict:
            self.product_dict[product].sort_value()
        #print('\r Building the similarity matrix:  ',idx," / ", len(self.customer_dict), " remaining time: ", round((time.time() - StartTime) * (len(self.customer_dict) - idx) / idx, 2), " s", end='')
                    
        print("Build the similarity matrix with time usage: ", round(time.time() - StartTime, 2), " s")


    def visualize(self):
        count = 0
        for product in self.product_dict:
            count += 1
            topK = 0
            print("The similar product for product ", self.product_dict[product].id, self.product_dict[product].brand, self.product_dict[product].category)
            for relation_product in self.product_dict[product].relation_dict:
                if self.product_dict[relation_product].category in self.category_dict:
                    print(self.product_dict[relation_product].id, round(self.product_dict[product].relation_dict[relation_product], 2), self.product_dict[relation_product].brand, self.category_dict[self.product_dict[relation_product].category])
                else:
                    print(self.product_dict[relation_product].id, round(self.product_dict[product].relation_dict[relation_product], 2), self.product_dict[relation_product].brand)
                topK += 1
                if topK > VIS_K:
                    break
            if count > VIS_NUM:
                break


    def write_pickle_record(self, FileName, TargetData):
        File = open(FileName, 'wb')
        Str = pickle.dumps(TargetData)
        File.write(Str)
        File.close()


    def write_record(self, folder_path, NameList):
        print("Write record to: ", folder_path)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        [CategoryName, ProductName, CustomerName] = NameList
        self.write_pickle_record(folder_path + CategoryName, self.category_dict)
        self.write_pickle_record(folder_path + ProductName, self.product_dict)
        self.write_pickle_record(folder_path + CustomerName, self.customer_dict)
        #self.write_pickle_record(folder_path + PSimName, self.product_similarity_dict)
        #self.write_pickle_record(folder_path + CSimName, self.customer_similarity_dict)


    def read_pickle_record(self, FileName):
        with open (FileName, 'rb') as File:
            return pickle.loads(File.read())

    def read_record(self, folder_path, NameList):
        [CategoryName, ProductName, CustomerName] = NameList
        self.category_dict = self.read_pickle_record(folder_path + CategoryName)
        self.product_dict = self.read_pickle_record(folder_path + ProductName)
        self.customer_dict = self.read_pickle_record(folder_path + CustomerName)

    def get_sum_norm(self, target_dict):
        sum_norm = 0
        for key in target_dict:
            sum_norm += target_dict[key]
        return sum_norm

    def get_item_prediction(self, product_list, interest_list):
        assert(len(product_list) == TRAIN_THRESHOLD and len(interest_list) == TRAIN_THRESHOLD)
        product_id_dict = OrderedDict()
        
        for i in range(TRAIN_THRESHOLD):
            product_neighbor_list = list(self.product_dict[product_list[i]].relation_dict.keys())
            neighbor_length = len(product_neighbor_list)
            sum_norm = self.get_sum_norm(self.product_dict[product_list[i]].relation_dict)
            for j in range(neighbor_length):
                product_id = product_neighbor_list[j]
                if product_id not in product_list:
                    # Should we add normalizatioin?
                    product_interest = self.product_dict[product_list[i]].relation_dict[product_id] * interest_list[i] / sum_norm

                    if product_id not in product_id_dict:
                        product_id_dict[product_id] = product_interest
                    else:
                        product_id_dict[product_id] += product_interest
                
                if j >= 2 * TEST_THRESHOLD:
                    break

        product_id_dict = OrderedDict(sorted(product_id_dict.items(), key = lambda t:t[1], reverse = True))
        return list(product_id_dict.keys())[0:TEST_THRESHOLD]

    def test_item_accuracy(self):
        # Item-based accuracy
        correct_accuracy = 0.0
        tested_customer = 0.0

        user_ids = list(self.customer_dict.keys())
        for user_id in user_ids:
            if len(self.customer_dict[user_id].product_dict) > TRAIN_THRESHOLD + TEST_THRESHOLD:
                correct_item = 0
                product_list = []
                interest_list = []

                # Use the sorted results for prediction?
                product_ids = list(self.customer_dict[user_id].product_dict.keys())
                for i in range(TRAIN_THRESHOLD):
                    product_list.append(product_ids[i])
                    interest_list.append(self.customer_dict[user_id].product_dict[product_ids[i]])
                prediction_list = self.get_item_prediction(product_list, interest_list)
                assert(len(prediction_list) <= TEST_THRESHOLD)
                for prediction in prediction_list:
                    if prediction in self.customer_dict[user_id].product_dict:
                        correct_item += 1
                if (len(prediction_list) > 0):
                    correct_accuracy += correct_item / len(prediction_list)
                    tested_customer += 1
                print("Updated test accuracy: ", round(correct_accuracy / tested_customer, 4), " Tested customers: ",  tested_customer)
            
                if tested_customer > TEST_NUM:
                    break
    

    def test_customer_accuracy(self):
        # Customer-based accuracy
        correct_accuracy = 0.0
        tested_customer = 0.0

        user_ids = list(self.customer_dict.keys())
        for user_id in user_ids:
            if len(self.customer_dict[user_id].product_dict) > TRAIN_THRESHOLD + TEST_THRESHOLD:
                correct_item = 0
                index_list = []
                similarity_list = []
                base_dict = {}
                # Use the sorted results for prediction?
                product_ids = list(self.customer_dict[user_id].product_dict.keys())
                for i in range(TRAIN_THRESHOLD):
                    base_dict[product_ids[i]] = self.customer_dict[user_id].product_dict[product_ids[i]]
                for compare_id in user_ids:
                    # We only consider the ids with enough products
                    if compare_id != user_id and len(self.customer_dict[compare_id].product_dict) > TRAIN_THRESHOLD + TEST_THRESHOLD:
                        if SIMILARITY_TYPE == "Cosine":
                            similarity = self.Cosine_similarity(base_dict, self.customer_dict[compare_id].product_dict)
                        elif SIMILARITY_TYPE == "Jaccard":
                            similarity = self.Jaccard_similarity(base_dict, self.customer_dict[compare_id].product_dict)
                        else:
                            print("Error similarity type")
                            exit(0)
                        index_list.append(compare_id)
                        similarity_list.append(similarity)
                
                top_neighbors = heapq.nlargest(TOPK_NEIGHBORS, range(len(similarity_list)), similarity_list.__getitem__)
                prediction_dict = OrderedDict()
                for neighbor_index in top_neighbors:
                    neighbor_similarity = similarity_list[neighbor_index]
                    neighbor_id = index_list[neighbor_index]
                    neighbor_product_dict = self.customer_dict[neighbor_id].product_dict
                    sum_norm = self.get_sum_norm(neighbor_product_dict)
                    for product_id in neighbor_product_dict:
                        if product_id not in base_dict:
                            weighted_similarity = neighbor_similarity * neighbor_product_dict[product_id] / sum_norm
                            if product_id in prediction_dict:
                                prediction_dict[product_id] = weighted_similarity
                            else:
                                prediction_dict[product_id] += weighted_similarity
                prediction_dict = OrderedDict(sorted(prediction_dict.items(), key = lambda t:t[1], reverse = True))
                prediction_list = list(prediction_dict.keys())[0:TEST_THRESHOLD]
                for prediction in prediction_list:
                    if prediction in self.customer_dict[user_id].product_dict:
                        correct_item += 1
                if len(prediction_list) > 0:
                    correct_accuracy += correct_item / len(prediction_list)
                    tested_customer += 1
                print("Update test accuracy: ", round(correct_accuracy / tested_customer, 4), " Tested customers: ",  tested_customer)

                if tested_customer > TEST_NUM:
                    break


    def Cosine_similarity(self, dict_1, dict_2):
        if len(dict_1) == 0 or len(dict_2) == 0:
            return 0

        ProdSum = 0
        Norm1 = 0
        Norm2 = 0
        #[dict_1, dict_2] =  [dict_1, dict_2] if len(dict_1) < len(dict_2) else [dict_2, dict_1]
        for key1 in dict_1:
            if key1 in dict_2:
                ProdSum += dict_1[key1] * dict_2[key1]

        if ProdSum == 0:
            return 0
        for key1 in dict_1:
            Norm1 += dict_1[key1] ** 2
        for key2 in dict_2:
            Norm2 += dict_2[key2] ** 2

        return ProdSum / ((Norm1 * Norm2) ** 0.5)

    def Jaccard_similarity(self, dict_1, dict_2):
        if len(dict_1) == 0 or len(dict_2) == 0:
            return 0

        UnionLength = 0
        #[dict_1, dict_2] =  [dict_1, dict_2] if len(dict_1) < len(dict_2) else [dict_2, dict_1]
        
        for key1 in dict_1:
            if key1 in dict_2:
                UnionLength += 1

        return UnionLength / (len(dict_1) * len(dict_2))


    # n is the number of dimension





class product:
    def __init__(self, product_id, category_id, brand):
        self.view_num = 0
        self.add_num = 0
        self.purchase_num = 0
        self.remove_num = 0

        self.total_num = 0

        self.id = product_id
        self.category = category_id
        self.brand = brand
        self.price = []
        # other_product_id: value
        self.relation_dict = OrderedDict()

    def add_product_pair(self, target_id, weight_value):
        self.total_num += 1
        if target_id in self.relation_dict:
            self.relation_dict[target_id] += weight_value
        else:
            self.relation_dict[target_id] = weight_value
    
    def sort_value(self):
        self.relation_dict = OrderedDict(sorted(self.relation_dict.items(), key = lambda t:t[1], reverse = True))

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
        self.price_dict = OrderedDict()

    def add_record(self, action_time, action_type, product_id, price):
        self.record_num += 1
        if product_id in self.product_dict:
            self.product_dict[product_id].append([action_time, action_type, price])
        else:
            self.product_dict[product_id] = [[action_time, action_type, price]]


    def check_interest(self):
        assert(len(self.price_dict) == 0)
        DeleteKeyList = []
        for product in self.product_dict:
            product_interest = 0
            product_interest_price = 0
            each_record_interest = 0
            
            for product_record in self.product_dict[product]:
                assert(len(product_record) == 3)
                
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


            if product_interest <= 0:
                DeleteKeyList.append(product)
                
            else:                    
                product_interest_price /= product_interest
                
                if product_interest > MAX_W:
                    product_interest = MAX_W

                self.product_dict[product] = product_interest
                self.price_dict[product] = product_interest_price

        for DeleteKey in DeleteKeyList:
            del self.product_dict[DeleteKey]

