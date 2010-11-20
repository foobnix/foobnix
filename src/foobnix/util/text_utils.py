
def capitilize_query(line):
    if not line:
        return line
    
    if line.startswith("http://"):
        return line
    
    line = u"" + line.strip()
    result = ""
    for word in line.split():
        result += " " + word[0].upper() + word[1:]
    return result.strip()

def capitilize_string(src):
    if not src:
        return src
        
    line = u"" + src.strip()
    result = ""
    for word in line.split():
        result += " " + word[0].upper() + word[1:].lower()
    return result.strip()


def smart_splitter(input, max_len):
    if not input:
        return input
    
    if max_len > len(input):
        return input
        
    separators = (" " , "-" , "," , "/" , "_", "\n")    
    result = []    
    buffer = ""
    for i in xrange(len(input)):
        char = input[i]
        buffer += char
                
        if len(buffer) >= max_len:
            if char in separators:   
                result.append(buffer.strip())
                buffer = ""                
    result.append(buffer[:max_len].strip())
    return result
        
