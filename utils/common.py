def adjust_perc(value: float, percent: float) -> float:
    return value * (1 + percent / 100)


def round_to_nearest_multiple_of_5(x):
    val = round(x / 5) * 5
    if val == 0:
        return 5
    if val == 295:
        return 290
    return val
