from Count.Base import Pandas_count


def get_symobl_filter_useful(all_symbols):
    """
        將過濾完的標的(can trade symobl)輸出

    """
    out_list = []
    for each_data in all_symbols:
        symbolname = each_data[0]
        data = each_data[1]
        # 不想要太新的商品
        if len(data) > 360:
            # 價格太低的商品不要
            if data.iloc[-1]['Close'] > 20:
                mom_num = Pandas_count.momentum(data['Close'], 30)
                out_list.append([symbolname.split('-')[0].upper(), mom_num.iloc[-1]])

    sort_example = sorted(out_list, key=lambda x: x[1], reverse=True)
    return sort_example
