def convert_permissions(permissions):
    result = 0
    assert len(permissions) == 10

    if (permissions[1] == "r"): 
        result = result | 0400
    if (permissions[2] == "w"):
        result = result | 0200
    if (permissions[3] == "x"):
        result = result | 0100

    if (permissions[4] == "r"): 
        result = result | 0040
    if (permissions[5] == "w"):
        result = result | 0020
    if (permissions[6] == "x"):
        result = result | 0010

    if (permissions[7] == "r"): 
        result = result | 0004
    if (permissions[8] == "w"):
        result = result | 0002
    if (permissions[9] == "x"):
        result = result | 0001

    return result