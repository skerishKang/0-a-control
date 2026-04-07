def max_xor_subarray(nums):
    if not nums:
        return 0
    max_xor = 0
    for i in range(len(nums)):
        current_xor = 0
        for j in range(i, len(nums)):
            current_xor ^= nums[j]
            if current_xor > max_xor:
                max_xor = current_xor
    return max_xor

# Test cases based on examples
print(max_xor_subarray([3, 8, 2, 7]))  # Expected: 14 (note: example shows 11, but calculation shows 14)
print(max_xor_subarray([0, 7, 3, 9, 5]))  # Expected: 15
print(max_xor_subarray([0, 0, 0]))  # Expected: 0