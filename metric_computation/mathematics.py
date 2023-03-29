from typing import List


def average(nums: List) -> float:
    avg_value = sum(nums) / float(len(nums))
    return avg_value


def math_sigma(function_item, from_value: int, to_value: int) -> float:
    sigma_result = 0
    for i in range(from_value, to_value + 1):
        sigma_result += function_item(i)
    return sigma_result


def get_normalized_value(min_value: float,
                         max_value: float,
                         current_value: float) -> float:
    if min_value == max_value:
        return 0

    normalized_score = (current_value - min_value) / (max_value - min_value)

    return normalized_score
