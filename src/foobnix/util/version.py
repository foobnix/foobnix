def compare_versions(version1, version2):
    if not version1 or not version2:
        return 0
    
    if "-" in version1:    
        v1, r1 = version1.split("-")
    else:
        v1, r1 = version1, 0
    
    if "-" in version2:
        v2, r2 = version2.split("-")
    else:
        v2, r2 = version2, 0
    
    v1 = int(v1.replace(".",""))
    v2 = int(v2.replace(".",""))
    
    r1 = int(r1)
    r2 = int(r2)
    
    if v1 == v2 and r1==r2:
        return 0
    
    if v1 >= v2 and r1 > r2:
        return -1
    else:
        return 1
        
    