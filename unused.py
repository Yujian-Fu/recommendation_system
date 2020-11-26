import numpy as np 

    def compute_item_similarity(self, SimilarityFunction):
        self.product_similarity_dict.clear()
        #assert(len(self.product_similarity_dict) == 0)
        print("Computing the item based similarity for ", len(self.product_dict), "items")
        
        index_list = []
        index_neighbor_list = []
        index_value_list = []

        start_time = time.time()
        for key_1 in self.product_dict:
            index_list.append(key_1)
            index_neighbor_list.append([])
            index_value_list.append([])

            for key_2 in self.product_dict[key_1].relation_dict:
                index_neighbor_list[-1].append(key_2)
                index_value_list[-1].append(self.product_dict[key_1].relation_dict[key_2])

        print("Time for building relation list: ", round(time.time() - start_time))
        for i in range(len(index_list)):
            if index_list[i] not in self.product_similarity_dict:
                self.product_similarity_dict[index_list[i]] = {}
            x1_array = np.array([0] * len(index_neighbor_list[i]))
            y1_array = np.array(index_neighbor_list[i])
            value1_array = np.array(index_value_list[i])
            for j in range(len(index_neighbor_list[i])):
                
                sec_index = index_list.index(index_neighbor_list[i][j])

                if index_neighbor_list[i][j] not in self.product_similarity_dict:
                    self.product_similarity_dict[index_neighbor_list[i][j]] = {}
                
                if index_neighbor_list[i][j] not in self.product_similarity_dict[index_list[i]]:
                    x_array = np.concatenate((x1_array, np.array([1] * len(index_neighbor_list[sec_index]))))
                    y_array = np.concatenate((y1_array, np.array(index_neighbor_list[sec_index])))
                    value_array = np.concatenate((value1_array, np.array(index_value_list[sec_index])))
                    sparseM = sparse.coo_matrix((value_array, (x_array, y_array)))
                    
                    similarities = cosine_similarity(sparseM)
                    self.product_similarity_dict[index_list[i]][index_neighbor_list[i][j]] = similarities[0][1]
                    self.product_similarity_dict[index_neighbor_list[i][j]][index_list[i]] = similarities[0][1]
                
                print("\rComputing ", i, " / ", len(index_list), " " , j, " / ", ITEM_THRESHOLD,  " for similarity", end= "")
                if j >= ITEM_THRESHOLD:
                    break

        exit(0)


        index1 = 0
        for key1 in self.product_dict:
            index1 += 1
            index2 = 0
            index_similarity = 0
            index_record = []
            x_list = []
            y_list = []
            value_list = []

            NeighborDict = self.product_dict[key1].relation_dict

            if key1 not in self.product_similarity_dict:
                self.product_similarity_dict[key1] = {}

            for key2 in NeighborDict:
                x_list.append(index_similarity)
                y_list.append(key2)
                value_list.append(NeighborDict[key2])
            index_similarity += 1
            index_record.append(key1)

            for key2 in NeighborDict:
                print("\rAdding ", index1, " / ", len(self.product_dict), " " , index2,  " for similarity", end= "")
                index2 += 1

                if key2 not in self.product_similarity_dict:
                    self.product_similarity_dict[key2] = {}

                if key2 not in self.product_similarity_dict[key1]:
                    NeighborNeighborDict = self.product_dict[key2].relation_dict
                    for key3 in NeighborNeighborDict:
                        x_list.append(index_similarity)
                        y_list.append(key3)
                        value_list.append(NeighborNeighborDict[key3])
                    index_similarity += 1
                    index_record.append(key2)
                
                x_index = np.array(x_list)
                y_index = np.array(y_list)
                value_index = np.array(value_list)


                if index2 > ITEM_THRESHOLD:
                    break
                
                '''
                if key2 not in self.product_similarity_dict[key1]:
                    Similarity = SimilarityFunction(self.product_dict[key1].relation_dict, self.product_dict[key2].relation_dict, len(self.product_dict))
                    self.product_similarity_dict[key1][key2] = Similarity
                    self.product_similarity_dict[key2][key1] = Similarity
                '''
            
            SparseM = sparse.coo_matrix((value_index, (x_index, y_index)))
            similarities = cosine_similarity(SparseM)

            for i in range(len(index_record)):
                for j in range(i+1, len(index_record)):
                    self.product_similarity_dict[index_record[i]][index_record[j]] = similarities[i][j]
                    self.product_similarity_dict[index_record[j]][index_record[i]] = similarities[i][j]

        
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
        
        time_start = time.time()

        print("Time for computing the similarity: ", round(time.time() - time_start, 2))
        #self.compute_customer_similarity(SimilarityFunction)


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
    def write_txt_record(self, Filename):
        File = open(Filename, "w")
        File.write("Record_Num: " + str(self.record_num) + "\n")
        File.write("Use_Parallel: " + str(self.use_parallel) + "\n")
        #File.write("Similarity_Type: " + self.similarity_type)
        File.close()


    def read_txt_record(self, FileName):
        with open(FileName, 'r') as file:
            r = file.readlines()
            self.record_num = int(r[0].split(" ")[-1].split("\n")[0])
            self.use_parallel = bool(r[1].split(" ")[-1].split("\n")[0])
            self.similarity_type = r[2].split(" ")[-1].split("\n")[0]
