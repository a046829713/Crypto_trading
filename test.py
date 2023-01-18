

def get_info(*args):
    out_str = ''
    for i in args:
        out_str += str(i)+" "
    return out_str


print(get_info([1, 2, 3], 4, 5, 7, "lewis"))


# print([1, 2, 3], 4, 5, 7, "lewis")
