import csv
from config import *

with open(FileFolderPath + FileNameList[0]) as f:
    reader = list(csv.reader(f))
    with open(FileFolderPath + FileNameList[0].split('.')[0] + "-small.csv") as wf:
        writer = csv.writer(wf)
        writer.writerow(reader[: int(len(writer)/5)])



