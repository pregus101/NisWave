import random

shuffled_queue = []

def shuffler(queue, current_song, first=False):
    queue_copy = queue.copy()
    runA = len(queue)
    if first:
        shuffled_queue = [current_song]
    else:
        shuffled_queue = []
    print(runA)
    while runA > 1:
        runA = len(queue_copy)
        index = random.randint(0, runA-1)
        shuffled_queue.append(queue_copy[index])
        queue_copy.remove(shuffled_queue[len(shuffled_queue)-1])
    return shuffled_queue

def generated_unshuffled_queue(current_song, queue_defualt):
    if queue_defualt:
        current_index = queue_defualt.index(current_song)
        queue = queue_defualt.copy()
        for i in range(0, current_index):
            queue.remove(queue_defualt[i])
            queue.append(queue_defualt[i])
        return queue
    
def new_shuffler():
    pass