# This is a sample Python script.

# Press Mayús+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
from math import gcd

def minimo_comun_multiplo(a, b):
    return abs(a * b) // gcd(a, b)

def maximo_comun_divisor(a, b):
    return gcd(a, b)

print (minimo_comun_multiplo(2,4))
print (maximo_comun_divisor(2,4))