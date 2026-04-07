def max_subarray_xor(nums):
    n = len(nums)
    max_xor = 0
    for i in range(n):
        current_xor = 0
        for j in range(i, n):
            current_xor ^= nums[j]
            max_xor = max(max_xor, current_xor)
    return max_xor

# Test cases
print(max_subarray_xor([3, 8, 2, 7]))       # 11
print(max_subarray_xor([0, 7, 3, 9, 5]))    # 15
print(max_subarray_xor([0, 0, 0]))          # 0
