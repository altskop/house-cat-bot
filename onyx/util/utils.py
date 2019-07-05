# TODO move this to a class (Embed wrapper?)
def chunks(lst, max_size):
    for i in range(0, len(lst), max_size):
        yield lst[i:i+max_size]