

class Symbols():
    def __init__(self) -> None:
        self._symbols = ['BTCUSDT', 'ETHUSDT']

    def __len__(self):
        return len(self._symbols)

    # def __iter__(self):
    #     return Symboliterator(self)
    
    def __getitem__(self, s):
        return self._symbols[s]


class Symboliterator():
    def __init__(self, symbol: Symbols) -> None:
        print("Symboliterator new object be created")
        self.symbol = symbol
        self._index = 0

    def __iter__(self):
        print("__iter__ 測試")
        return self

    def __next__(self):
        print("Symboliterator __next__ be called")
        if self._index >= len(self.symbol):
            raise StopIteration
        else:
            item = self.symbol._symbols[self._index]
            self._index += 1
            return item


symbols = Symbols()
# symbols_iter = iter(symbols)


for i in symbols:
    print(i)
