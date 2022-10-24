# class Equus:
#     def __init__(self, is_male):
#         pass

#     def run(self):
#         print(f'I run at speed {self.speed}')
#         print(f'I\'m {self.gender}')

#     def roar(self):
#         print('Equus roars')

# class Horse(Equus):
#     def __init__(self, is_male):
#         print('Horse init')
#         self.speed = 30
#         self.gender = 'male' if is_male else 'female'
#         self.is_horse = True
#     def roar(self):
#         print('Horse: Hee haw~')
#         super().roar()

# class Donkey(Equus):
#     def __init__(self, is_female):
#         print('Donkey init')
#         self.speed = 20
#         self.gender = 'female' if is_female else 'male'
#         self.is_donkey = True
#     def roar(self):
#         print('Donkey: Hee haw hee hee haw~')
#         super().roar()

# class Mule(Horse, Donkey):
#     def __init__(self, is_male):
#         print('Mule init')
#         super().__init__(is_male)

#     def roar(self):
#         print('Mule: Muuuuleee~~~')
#         super().roar()


# new_animal = Mule(is_male = True)


# print(new_animal.roar())


class dog(object):
    def __init__(self) -> None:
        self.name = "lewis"

    @classmethod
    def get_symbol(cls):
        return "this is dog-getsymbol"


class new_dog(dog):
    @classmethod
    def get_symbol(cls):
        print(cls)
        print(type(cls))
        print(123)
        print("查看父類別：", super())
        print("查看父類別：", super(new_dog, cls))
        return dog.get_symbol()


print("取得回傳值;", new_dog.get_symbol())
