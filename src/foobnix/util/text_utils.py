
def capitilize_query(line):
    if line.startswith("http"):
        return line
    
    line = u"" + line.strip()
    result = ""
    for word in line.split():
        result += " " + word[0].upper() + word[1:]
    return result

def capitilize_string(src):
    line = u"" + src.strip()
    result = ""
    for word in line.split():
        result += " " + word[0].upper() + word[1:].lower()
    return result
