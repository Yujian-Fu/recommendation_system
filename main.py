import numpy 
from config import *
import csv
from data_structure import *
import time



start = time.time()
if __name__ == "__main__":

    Record = record()
    for FileName in FileNameList:
        with open(FileFolderPath + FileName) as f:
            print("Read file from: ", FileFolderPath + FileName)
            reader = list(csv.reader(f))
            print("Columns: ", reader[0])
            print("The total number of columns and rows ", len(reader), " ", len(reader[0]))

            Record.add_record(reader)

            Record.build_similarity_matrix()
            Record.visualize()
    end = time.time()








