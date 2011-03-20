def compare_versions(v1, v2):
    if not v1 or not v2:
        return 0
    v1 = v1.replace("-0","").replace("-","").replace(".","")
    v2 = v2.replace("-0","").replace("-","").replace(".","")
    
    v1 = int(v1)
    v2 = int(v2)
    
    if v1 == v2:
        return 0
    elif v1 > v2:
        return -1
    else:
        return 1
        
    