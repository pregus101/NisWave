import random
from get_files import get_files

def new_shuffler(index, queue_defualt):
    first_half = queue_defualt[:index+1]
    second_half = queue_defualt[index+1:]
    random.shuffle(second_half)
    return first_half + second_half