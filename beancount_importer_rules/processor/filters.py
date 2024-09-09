def filter_first_non_none(*values):
    return next((value for value in values if value is not None), None)
