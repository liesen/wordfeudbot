import counters

def get_win_count():
    return counters.get('win_count')

def increment_win_count():
    counters.incr('win_count')

def get_lose_count():
    return counters.get('lose_count')

def increment_lose_count():
    counters.incr('lose_count')

def get_tie_count():
    return counters.get('tie_count')

def increment_tie_count():
    counters.incr('tie_count')

