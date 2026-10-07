def compare_df(left, right):
    if set(left.columns) != set(right.columns):
        return False
    right = right.select(*left.columns)
    return (left.exceptAll(right).count() == 0
            and right.exceptAll(left).count() == 0)
