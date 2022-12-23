import time
from inspect import getfullargspec


class Function(object):
    """Function is a wrap over standard python function
    An instance of this Function class is also callable
    just like the python function that it wrapped.
    When the instance is "called" like a function it fetches
    the function to be invoked from the virtual namespace and then
    invokes the same.
    """

    def __init__(self, fn):
        self.fn = fn

    def __call__(self, *args, **kwargs):
        """Overriding the __call__ function which makes the
        instance callable.
        """
        # fetching the function to be invoked from the virtual namespace
        # through the arguments.
        fn = Namespace.get_instance().get(self.fn, *args)
        if not fn:
            raise Exception("no matching function found.")
        # invoking the wrapped function and returning the value.
        return fn(*args, **kwargs)

    def key(self, args=None):
        """Returns the key that will uniquely identifies
        a function (even when it is overloaded).
        """
        if args is None:
            args = getfullargspec(self.fn).args
        return tuple([
            self.fn.__module__,
            self.fn.__class__,
            self.fn.__name__,
            len(args or []),
        ])


class Namespace(object):
    """Namespace是一個單例類，負責保存所有的函式"""
    __instance = None

    def __init__(self):
        if self.__instance is None:
            self.function_map = dict()
            Namespace.__instance = self
        else:
            raise Exception("cannot instantiate a virtual Namespace again")

    @staticmethod
    def get_instance():
        if Namespace.__instance is None:
            Namespace()
        return Namespace.__instance

    def register(self, fn):
        """在虛擬的命名空間中注冊函式，并回傳Function類的可呼叫實體"""
        func = Function(fn)
        self.function_map[func.key()] = fn
        return func

    def get(self, fn, *args):
        """從虛擬命名空間中回傳匹配到的函式，如果沒找到匹配，則回傳None"""
        func = Function(fn)
        return self.function_map.get(func.key(args=args))


def overload(fn):
    """用于封裝函式，并回傳Function類的一個可呼叫物件"""
    return Namespace.get_instance().register(fn)


@overload
def area(length, breadth):
    return length * breadth

@overload
def area(radius):
  import math
  return math.pi * radius ** 2

@overload
def area(length, breadth, height):
  return 2 * (length * breadth + breadth * height + height * length)

@overload
def area(length, breadth, height):
  return length + breadth + height

@overload
def area():
  return 0


@overload
def volume(length, breadth, height):
  return length * breadth * height


print(f"area of cuboid with dimension (4, 3, 6) is: {area(4, 3, 6)}")
# print(f"area of rectangle with dimension (7, 2) is: {area(7, 2)}")
# print(f"area of circle with radius 7 is: {area(7)}")
# print(f"area of nothing is: {area()}")
# print(f"volume of cuboid with dimension (4, 3, 6) is: {volume(4, 3, 6)}")
