import random
from get_files import search

def new_shuffler(index: int, queue_defualt: list[str]) -> list[str]:
    first_half: list[str] = queue_defualt[:index+1]
    second_half: list[str] = queue_defualt[index+1:]
    random.shuffle(second_half)
    return first_half + second_half

def on_play_shuffle(unshuffled: list[str], song: str) -> list[str]:
    file: str = search(unshuffled, Path(song).name)[0]

    queue: list[str] = unshuffled.copy()
    random.shuffle(queue)
    queue.remove(file)
    queue.insert(0, file)
    
    return queue


