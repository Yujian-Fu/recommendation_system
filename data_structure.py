from collections import OrderedDict
import csv 
import time
from config import *
import concurrent.futures
import os
import pickle


def RaiseTypeError(S):
    print("Error: Type not defined:", S)
    exit(-1)


class record:
    def __init__(self):
        self.category_dict = {}
        self.customer_dict = {}
        self.product_dict = {}
        
        self._product_dict = {}
        self._customer_dict = {}

        self.product_similarity_dict = {}
        #self.customer_similarity_dict = {}
        self.customer_union_dict = {}

        self.record_num = 0
        self.use_parallel = 1 if USE_PARALLEL else 0
        self.similarity_type = SIMILARITY_TYPE
        self.item_threshold = ITEM_THRESHOLD


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
        
        '''
        for cus_id in self.customer_dict:
            for product_id in self.customer_dict[cus_id].product_dict:
                if product_id not in self._product_dict:
                    self._product_dict[product_id] = {}
                if cus_id not in self._product_dict[product_id]:
                    self._product_dict[product_id][cus_id] = 0
                self._product_dict[product_id][cus_id] += self.customer_dict[cus_id].product_dict[product_id]
        
        
        for product_id in self._product_dict:
            ProductCustomerDict = self._product_dict[product_id]
            cust_id_list = list(ProductCustomerDict.keys())
            for index1 in range(len(cust_id_list)):
                UserID1 = cust_id_list[index1]
                if UserID1 not in self._customer_dict:
                    self._customer_dict[UserID1] = {}

                for index2 in range(index1 + 1, len(cust_id_list)):
                    UserID2 = cust_id_list[index2]

                    if UserID2 not in self._customer_dict:
                        self._customer_dict[UserID2] = {}

                    weight = self._product_dict[product_id][UserID1] * self._product_dict[product_id][UserID2]

                    if UserID2 not in self._customer_dict[UserID1]:
                        self._customer_dict[UserID1][UserID2] = weight
                    else:
                        self._customer_dict[UserID1][UserID2] += weight
                    
                    if UserID1 not in self._customer_dict[UserID2]:
                        self._customer_dict[UserID2][UserID1] = weight
                    else:
                        self._customer_dict[UserID2][UserID1] += weight
        '''
                    
        print("Build the similarity matrix with time usage: ", round(time.time() - StartTime, 2), " s")


    def Cosine_similarity(self, dict_1, dict_2, n = 0):
        if len(dict_1) == 0 or len(dict_2) == 0:
            return 0

        ProdSum = 0
        Norm1 = 0
        Norm2 = 0
        [dict_1, dict_2] =  [dict_1, dict_2] if len(dict_1) < len(dict_2) else [dict_2, dict_1]
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

    def Jaccard_similarity(self, dict_1, dict_2, n = 0):
        if len(dict_1) == 0 or len(dict_2) == 0:
            return 0

        UnionLength = 0
        [dict_1, dict_2] =  [dict_1, dict_2] if len(dict_1) < len(dict_2) else [dict_2, dict_1]
        
        for key1 in dict_1:
            if key1 in dict_2:
                UnionLength += 1

        return UnionLength / (len(dict_1) * len(dict_2))


    # n is the number of dimension
    def Pearson_similarity(self, dict_1, dict_2, n):
        if len(dict_1) == 0 or len(dict_2) == 0:
            return 0

        Norm1 = 0
        Sum1 = 0
        Norm2 = 0
        Sum2 = 0
        Prod = 0

        [dict_1, dict_2] =  [dict_1, dict_2] if len(dict_1) < len(dict_2) else [dict_2, dict_1]

        for key1 in dict_1:
            if key1 in dict_2:
                Prod += dict_1[key1] * dict_2[key1]
        
        for key1 in dict_1:
            Norm1 += dict_1[key1] ** 2
            Sum1 += dict_1[key1]
        
        for key2 in dict_2:
            Norm2 += dict_2[key2] ** 2
            Sum2 += dict_2[key2]
        
        return (n * Prod - Sum1 * Sum2) / ((n * Norm1 - Sum1 **2) * (n * Norm2 - Sum2 **2)) ** 0.5


    def compute_similarity(self):
        if SIMILARITY_TYPE == "Cosine":
            SimilarityFunction = self.Cosine_similarity
        elif SIMILARITY_TYPE == "Jaccard":
            SimilarityFunction == self.Jaccard_similarity
        elif SIMILARITY_TYPE == "Pearson":
            SimilarityFunction = self.Pearson_similarity
        else:
            RaiseTypeError(SIMILARITY_TYPE)
        
        self.compute_item_similarity(SimilarityFunction)
        #self.compute_customer_similarity(SimilarityFunction)


    def compute_item_similarity(self, SimilarityFunction):
        assert(len(self.product_similarity_dict) == 0)
        print("Computing the item based similarity for ", len(self.product_dict), "items")
        index1 = 0

        for key1 in self.product_dict:
            index1 += 1
            index2 = 0
            

            NeighborDict = self.product_dict[key1].relation_dict

            if key1 not in self.product_similarity_dict:
                self.product_similarity_dict[key1] = {}


            for key2 in NeighborDict:
                print("\rComputing ", index1, " / ", len(self.product_dict), " " , index2,  " for similarity", end= "")
                index2 += 1
                
                if key2 not in self.product_similarity_dict:
                    self.product_similarity_dict[key2] = {}
                
                if key2 not in self.product_similarity_dict[key1]:
                    Similarity = SimilarityFunction(self.product_dict[key1].relation_dict, self.product_dict[key2].relation_dict, len(self.product_dict))
                    self.product_similarity_dict[key1][key2] = Similarity
                    self.product_similarity_dict[key2][key1] = Similarity
                
                if index2 > ITEM_THRESHOLD:
                    break
        print()
    
    '''
    def compute_customer_similarity(self, SimilarityFunction):
        assert(len(self.customer_similarity_dict) == 0)
        print("Computing the customer based similarity")

        CustomerKeyList = list(self.customer_dict.keys())
        for key1 in range(len(CustomerKeyList)):
            if key1 not in self.customer_union_dict:
                self.customer_union_dict[key1] = {}
            


        for key1 in range(len(CustomerKeyList)):
            if key1 not in self.customer_similarity_dict:
                self.customer_similarity_dict[key1] = {}

            for key2 in range(key1+1, len(CustomerKeyList)):
                if key2 not in self.customer_similarity_dict:
                    self.customer_similarity_dict[key2] = {}
                assert(key1 not in self.customer_similarity_dict[key2])
                Similarity = SimilarityFunction(self.customer_dict[key1].product_dict, self.customer_dict[key2].product_dict, len(self.product_dict))
                self.customer_similarity_dict[key1][key2] = Similarity
                self.customer_similarity_dict[key2][key1] = Similarity
    '''

    def visualize(self):
        count = 0
        for product in self.product_dict:
            count += 1
            topK = 0
            print("The similar product for product ", self.product_dict[product].id, self.product_dict[product].brand, self.product_dict[product].category)
            for relation_product in self.product_dict[product].relation_dict:
                print(self.product_dict[relation_product].id, self.product_dict[product].relation_dict[relation_product], self.product_dict[relation_product].brand, self.product_dict[relation_product].category)
                topK += 1
                if topK > VIS_K:
                    break
            if count > VIS_NUM:
                break

    def prediction_item_based(self):
        return 0


    def write_pickle_record(self, FileName, TargetData):
        File = open(FileName, 'wb')
        Str = pickle.dumps(TargetData)
        File.write(Str)
        File.close()

    def write_txt_record(self, Filename):
        File = open(Filename, "w")
        File.write("Record_Num: " + str(self.record_num) + "\n")
        File.write("Use_Parallel: " + str(self.use_parallel) + "\n")
        File.write("Similarity_Type: " + self.similarity_type)
        File.close()

    def write_record(self, folder_path, NameList):
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        [CategoryName, ProductName, CustomerName, PSimName, CSimName, TxtName] = NameList
        self.write_txt_record(TxtName)
        self.write_pickle_record(folder_path + CategoryName, self.category_dict)
        self.write_pickle_record(folder_path + ProductName, self.product_dict)
        self.write_pickle_record(folder_path + CustomerName, self.customer_dict)
        self.write_pickle_record(folder_path + PSimName, self.product_similarity_dict)
        #self.write_pickle_record(folder_path + CSimName, self.customer_similarity_dict)


    def read_pickle_record(self, FileName):
        with open (FileName, 'rb') as File:
            return pickle.loads(File.read())

    def read_txt_record(self, FileName):
        with open(FileName, 'r') as file:
            r = file.readlines()
            self.record_num = int(r[0].split(" ")[-1].split("\n")[0])
            self.use_parallel = bool(r[1].split(" ")[-1].split("\n")[0])
            self.similarity_type = r[2].split(" ")[-1].split("\n")[0]

    def read_record(self, folder_path, NameList):
        [CategoryName, ProductName, CustomerName, PSimName, CSimName, TxtName] = NameList
        self.category_dict = self.read_pickle_record(folder_path + CategoryName)
        self.product_dict = self.read_pickle_record(folder_path + ProductName)
        self.customer_dict = self.read_pickle_record(folder_path + CustomerName)
        self.product_similarity_dict = self.read_pickle_record(folder_path + PSimName)
        #self.customer_similarity_dict = self.read_pickle_record(folder_path + CSimName)
        self.read_txt_record(TxtName)

    '''
    def update_record(self, folder_path, NameList):
        [CategoryName, ProductName, CustomerName, PSimName, CSimName, TxtName] = NameList
        PD = self.read_pickle_record(folder_path + ProductName)
    '''

        


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






