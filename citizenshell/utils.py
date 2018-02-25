def convert_permissions(permissions):
    result = 0
    assert len(permissions) == 10

    if (permissions[1] == "r"): 
        result = result | 0o400
    if (permissions[2] == "w"):
        result = result | 0o200
    if (permissions[3] == "x"):
        result = result | 0o100

    if (permissions[4] == "r"): 
        result = result | 0o040
    if (permissions[5] == "w"):
        result = result | 0o020
    if (permissions[6] == "x"):
        result = result | 0o010

    if (permissions[7] == "r"): 
        result = result | 0o004
    if (permissions[8] == "w"):
        result = result | 0o002
    if (permissions[9] == "x"):
        result = result | 0o001

    return result