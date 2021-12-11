def filter_by(data, column, value):
    temp = data.copy()
    return temp[temp[column]==value]

def sort_by(data, column, ascending=False):
    temp = data.copy()
    return temp.sort_values(by=column, ascending=ascending)
