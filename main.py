import numpy 
from config import *
import csv
from data_structure import *
import time
import psutil
import os
import sys

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
    print("Loading the saved structure of " + FileName.split('.')[0])
    Record = record()
    Record.read_record('./record/' + FileName.split('.')[0] + "/", ['Category.pkl', 'Product.pkl', 'Customer.pkl'])
    print("Loaded")
    Record.test_customer_accuracy()


if __name__ == "__main__":
    
    for FileName in FileNameList:
        start = time.time()
        record_file = open(FileName.split('.')[0] + "_record.txt", 'a')

        preprocessing(FileName)
        print(u'The memory usage of this procession: %.4f GB' % (psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024 / 1024) )
        record_file.write(u'The memory usage of this procession: %.4f GB' % (psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024 / 1024))
        end = time.time()
        print("The whole process consumes: ", round(end - start, 2), " s")
        record_file.write("The whole process consumes: ", round(end - start, 2), " s")

    #for FileName in FileNameList:
        #testprocessing(FileName)


