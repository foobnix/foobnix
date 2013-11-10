def compare_versions(v1, v2):
    
    if not v1 or not v2:
        return 0
    v1 = v1.replace("-","").replace(".","")
    v2 = v2.replace("-","").replace(".","")
    
    v1 = int(v1)
    v2 = int(v2)
    
    if v1 == v2:
        return 0
    elif v1 > v2:
        return -1
    else:
        return 1
    
    
if __name__ == '__main__':
    print compare_versions("2.6.0","2.5.3")
    
