VIEW_S = 'view'
ADD_S = 'cart'
REMOVE_S = 'remove_from_cart'
PURCHASE_S = 'purchase'

VIS_NUM = 5
VIS_K = 5

VIEW_W = 0.2
ADD_W = 0.3
PURCHASE_W = 0.5
REMOVE_W = -0.1

MAX_W = 1.0
UPDATE_W = 0.5

#Item accuracy parameters:
TRAIN_THRESHOLD = 20
TEST_THRESHOLD = 10
TEST_NUM = 1000

# Customer accuracy parameters:

SIMILARITY_TYPE = "Cosine" # Choose from "Cosine", "Jaccard", "Pearson"
TOPK_NEIGHBORS = 10


USE_PARALLEL = False
FileFolderPath = "./dataset/"
FileNameList = ["2019-Jan.csv"]