

def read_quant_output_stocks(file):
    with open(file, 'r', encoding='utf-8') as fs:
        lines = fs.readlines()[1:]
        lines = [l.strip('\r\n') for l in lines if len(l.strip('\r\n'))>0]

    results = []
    for l in lines[1:]:
        vals = l.split(',')
        results.append((int(vals[0]), vals[1]))

    return results