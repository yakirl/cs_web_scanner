
'''
Some basic points on Modules / Packages / Imports:
    - avoid circular depedencies
'''

G_VAR = 10

class BmodClass:
    def __init__(self):
        print('Mod init')

class SomeClass:
    def __init__(self):
        print('SomeClass init')

def modify_gvar():
    global G_VAR
    G_VAR = 5

def print_gvar():
    print(G_VAR)
