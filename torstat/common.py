def convert_size(B, forceFloat=False, forceUnit=False):
    B = float(B)
    KB = float(1024)
    MB = float(KB ** 2)  # 1,048,576
    GB = float(KB ** 3)  # 1,073,741,824
    TB = float(KB ** 4)  # 1,099,511,627,776

    if B < KB:
        if forceFloat:
            return B
        return '{0} {1}'.format(B, 'Bytes' if 0 == B > 1 else 'Byte')
    elif KB <= B < MB:
        if forceFloat:
            return B/KB
        if forceUnit:
            return "KB"
        return '{0:.2f} KB'.format(B / KB)
    elif MB <= B < GB:
        if forceFloat:
            return B/MB
        if forceUnit:
            return "MB"
        return '{0:.2f} MB'.format(B / MB)
    elif GB <= B < TB:
        if forceFloat:
            return B/GB
        if forceUnit:
            return "GB"
        return '{0:.2f} GB'.format(B / GB)
    elif TB <= B:
        if forceFloat:
            return B/TB
        if forceUnit:
            return "TB"
        return '{0:.2f} TB'.format(B / TB)
