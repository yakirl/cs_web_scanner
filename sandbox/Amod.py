
# import only the Mod class:
#from Bmod import BmodClass
# import the whole namespace:
import Bmod

class TestClass:
    def __init__(self):
        print('TestClass init')

def test_func():
    print('test_func')

def test1():
    _mod = Bmod.BmodClass()
    #mod.test_global_var()

'''
Imported global var. 
'''
def test2():
    Bmod.modify_gvar()
    print(Bmod.G_VAR) 
    Bmod.G_VAR = 2
    Bmod.print_gvar()

if __name__ == "__main__":
    test1()
    test2()
