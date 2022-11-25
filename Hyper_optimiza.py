from itertools import product

class Hyper_optimization(object):

        
    
    @staticmethod
    def generator_parameter(variables: dict)-> list:
        """ 將資料改變（配對成每一對）

                Args:
                    variables (dict): 
                    {'sma1': array([ 20,  30,  40,  50,  60,  70,  80,  90, 100, 110, 120, 130, 140,
                150, 160, 170, 180, 190, 200, 210, 220, 230, 240, 250, 260, 270,
                280, 290, 300]), 'sma2': array([ 20,  30,  40,  50,  60,  70,  80,  90, 100, 110, 120, 130, 140,
                150, 160, 170, 180, 190, 200, 210, 220, 230, 240, 250, 260, 270,
                280, 290, 300])}

                Returns:
                    list: [...{'sma1': 300, 'sma2': 130}, {'sma1': 300, 'sma2': 140}, {'sma1': 300, 'sma2': 150}, {'sma1': 300, 'sma2': 160}, {'sma1': 300, 'sma2': 170}, {'sma1': 300, 'sma2': 180}, {'sma1': 300, 'sma2': 190}, {'sma1': 300, 'sma2': 200}, {'sma1': 300, 'sma2': 210}, {'sma1': 300, 'sma2': 220}, {'sma1': 300, 'sma2': 230}, {'sma1': 300, 'sma2': 240}, {'sma1': 300, 'sma2': 250}, {'sma1': 300, 'sma2': 260}, {'sma1': 300, 'sma2': 270}, {'sma1': 300, 'sma2': 280}, {'sma1': 300, 'sma2': 290}, {'sma1': 300, 'sma2': 300}]
        """
        if not variables:
            return []
        enumeration_name =[]
        enumeration_vars =[]
        
        for name, v in variables.items():
            enumeration_name.append(name)
            enumeration_vars.append(v)

        variable_enumerations = []
        for ps in list(product(*enumeration_vars)):
            variable_enumerations.append(dict(zip(enumeration_name, ps)))

        return variable_enumerations