import time

def extract_time(time_val):
    if not any(time_val.endswith(unit) for unit in ("s", "m", "h", "d")):
        return None
    unit = time_val[-1]
    time_num = time_val[:-1]
    if not time_num.isdigit():
        return None
    if unit == "s":
        rtime = int(time_num)
    elif unit == "m":
        rtime = int(time_num) * 60
    elif unit == "h":
        rtime = int(time_num) * 60 * 60
    elif unit == "d":
        rtime = int(time_num) * 24 * 60 * 60
    return rtime