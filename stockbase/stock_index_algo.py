from stockbase.stock_core import cfg


def calc_ref_frameindex(stocks, stockframes, days):
    frames = []
    for s in stocks:
        f = stockframes[s]
        if f is not None:
            frames.append(f)

    frameindex = []
    for d in days:
        key = d.strftime('%Y-%m-%d')
        data = [f.loc[key][cfg.p_index] if key in f.index else None for f in frames]
        data = [d for d in data if d is not None]
        if all([d is None for d in data]):
            if len(frameindex) > 0:
                frameindex.append(frameindex[-1])
            else:
                frameindex.append(0)
            continue

        frameindex.append(sum(data) / len(data))
        pass

    return frameindex


def skip_stock_filter_by_index(*args):
    """
    过滤重新计算close后的stock dataframe
    """
    if not cfg.enable_filter:
        # do not skip stock
        return False

    frame = args[0]
    frameindex = args[1]
    price = frame.iloc[:, cfg.p_index].values
    for i in range(len(price)):
        price[i] = price[i] - frameindex[i]
    pmax = max(price)
    pmin = min(price)
    if pmax - pmin < 15:
        return True
    else:
        return False
    pass


def skip_stock_filter(*args):
    """
    过滤重新计算close后的stock dataframe
    """
    frame = args[0]
    price = frame.iloc[:, cfg.p_index]
    pmax = max(price)
    pmin = min(price)
    if pmax - pmin < 30:
        return True
    else:
        return False
    pass

