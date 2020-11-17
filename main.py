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
            ShowProcess = len(reader) / 10

            for i in range(1, len(reader)):
                if i % ShowProcess == 0:
                    print("Finish processing ", 10*(i/ShowProcess), " percent of the whole file")
                
                Record.add_record(reader[i][0], reader[i][1], reader[i][2], reader[i][3], reader[i][4], reader[i][5], reader[i][6], reader[i][7])
            
            Record.build_similarity_matrix()
            Record.visualize()
    end = time.time()

                







