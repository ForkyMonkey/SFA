def find_n_gramm(n, data, indexes):
    ins = dict()
    for i in indexes:
        ngram = data[i: i + n]
        if ngram in ins.keys():
            continue
        ngrams = list()
        res = data.find(ngram, i)
        if res != -1:
            while res != -1:
                ngrams.append(res)
                res = data.find(ngram, res + 1)
        if len(ngrams) > 1:
            ins[ngram] = ngrams
    indxs = []
    for key in ins.keys():
        indxs.append(ins[key][0])
    return ins, indxs


def find_n_gramm_total(min, max, f_name, bin_mode=False):
    with open(f_name, 'rb') as f:
        data = f.read()
    if bin_mode:
        bin_data = ''
        for byte in data:
            bin_data += bin(byte)[2:]
        data = bin_data
    total_ins = []
    for k in range(min, max + 1):
        ins, indxs = find_n_gramm(k, data, range(len(data) - 1))
        if ins:
            total_ins.append(ins)
        else:
            break
    return total_ins