import numpy 
from config import *
import csv
from data_structure import *
import time


start = time.time()
if __name__ == "__main__":

    for FileName in FileNameList:
        with open(FileFolderPath + FileName) as f:
            Record = record()
            print("Read file from: ", FileFolderPath + FileName)
            reader = list(csv.reader(f))
            print("Columns: ", reader[0])
            print("The total number of columns and rows ", len(reader), " ", len(reader[0]))

            Record.add_record(reader[1:])
            Record.build_similarity_matrix()
            Record.visualize()
            Record.write_record('./record/' + FileName.split('.')[0] + "/", ['Category.pkl', 'Product.pkl', 'Customer.pkl', 'Record.txt'])

    
    end = time.time()
    print("The whole process consumes: ", round(end - start, 2), " s")
