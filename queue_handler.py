import random
from get_files import search
from pathlib import Path

def new_shuffler(index: int, queue_defualt: list[str]) -> list[str]:
    first_half: list[str] = queue_defualt[:index+1]
    second_half: list[str] = queue_defualt[index+1:]
    random.shuffle(second_half)
    return first_half + second_half

def on_play_shuffle(unshuffled: list[str], song: str) -> list[str]:
    file: str = Path(song).name

    queue: list[str] = unshuffled.copy()
    random.shuffle(queue)
    queue.remove(file)
    queue.insert(0, file)
    
    return queue


