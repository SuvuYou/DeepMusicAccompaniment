import numpy as np
import re
from const import SORTED_CHORDS_LIST

def custom_sort_key(chord):
    return SORTED_CHORDS_LIST.index(chord)

def closest(lst, K):
     lst = np.asarray(lst)
     idx = (np.abs(lst - K)).argmin()
     
     return lst[idx]

def has_only_numbers(input_str):
    return bool(re.match('^\d+$', input_str))

def find_greatest_common_divisor(numbers_list, upper_bound = 50, lower_bound = 20):
    min_remainder = float('inf')
    chosen_gcd = upper_bound

    for potential_gcd in range(upper_bound, lower_bound, -1):
        remainders = [length % (100 * potential_gcd) for length in numbers_list]
        
        if max(remainders) < min_remainder:
            min_remainder = max(remainders)
            chosen_gcd = potential_gcd

    return chosen_gcd