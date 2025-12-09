# Sample python file for demonstration

def factorial(n):
    # TODO: optimize
    if n == 0:
        return 1
    result = 1
    for i in range(1, n + 1):
        result *= i
    print("computed")
    return result
