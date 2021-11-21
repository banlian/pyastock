
import os


def convert_to_list(names):

    temp = [s for s in names]

    return '[{}]\r\n'.format(temp)
    pass


def append_list():


    pass

def seperate_list():

    s = '永兴材料 天华超净 天齐锂业 北方稀土 鹏辉能源'
    print(s.split(' '))

    pass

if __name__ == "__main__":

    print(seperate_list())


    print(append_list())

    pass