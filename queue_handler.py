import random

def new_shuffler(index: int, queue_defualt: list[str]) -> list[str]:
    first_half: list[str] = queue_defualt[:index+1]
    second_half: list[str] = queue_defualt[index+1:]
    random.shuffle(second_half)
    return first_half + second_half