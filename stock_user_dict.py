

def read_user_dict():
    dict = {}
    with open('ths_user_category.txt', 'r', encoding='utf8') as f:
        lines = f.readlines()
        lines = [l.strip('\r\n ') for l in lines]
        lines = [l for l in lines if len(l) > 0]
        print(lines)

        state = 'indict'
        dlist = []
        dname = lines[0][1:].strip()

        for l in lines[1:]:
            if l.find('#') >= 0:
                dict[dname] = dlist
                dname = l[1:].strip()
                dlist = []
            else:
                dlist.append(l)
            pass
    return dict
    pass
