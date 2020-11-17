import csv
from config import *

with open(FileFolderPath + FileNameList[0]) as f:
    reader = list(csv.reader(f))
    with open(FileFolderPath + FileNameList[0].split('.')[0] + "-small.csv", "w", newline="") as wf:
        writer = csv.writer(wf)
        print("Writing ", int(len(reader)/5), " lines")
        for idx in len(reader):
            writer.writerow(reader[idx])
            if idx > int(len(reader)/5):
                break



