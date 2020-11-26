import numpy 
from config import *
import csv
from data_structure import *
import time

# The prediction accuracy in using product similarity / customer similarity
# The time and memory consumption
# The similarity change in months
# Merge two datasets


def preprocessing(filename):
    with open(FileFolderPath + FileName) as f:
        Record = record()
        print("Read file from: ", FileFolderPath + FileName)
        reader = list(csv.reader(f))
        print("Columns: ", reader[0])
        print("The total number of columns and rows ", len(reader), " ", len(reader[0]))
        Record.add_record(reader[1:])
        Record.build_similarity_matrix()
        Record.visualize()
        Record.write_record('./record/' + FileName.split('.')[0] + "/", ['Category.pkl', 'Product.pkl', 'Customer.pkl'])


def testprocessing(filename):
    Record = record()
    Record.read_record('./record/' + FileName.split('.')[0] + "/", ['Category.pkl', 'Product.pkl', 'Customer.pkl'])
    print(Record.category_dict)


if __name__ == "__main__":
    start = time.time()
    #for FileName in FileNameList:
        #preprocessing(FileName)
    

    for FileName in FileNameList:
        testprocessing(FileName)


    end = time.time()
    print("The whole process consumes: ", round(end - start, 2), " s")
