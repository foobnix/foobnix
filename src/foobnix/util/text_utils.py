
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


'''divides the string into pieces according to a specified maximum length
fission occurs only at the nearest left separator
If delimiter is not found, the division on the maximum length'''        
def split_string(str, length):
    if not str:
        return str
    #take the max number of characters from a string
    i = length - 1 
    separator = None
    #go around them from right to left
    while i > -1:
        #compare each character with the values of the tuple
        for simbol in (" " , "-" , "," , "/" , "_"):
            #first matching symbol assign separator
            if str[i] == simbol:
                separator = str[i]
                break
        #if the symbol is not found in the tuple, 
        #go to the next symbol to the left
        if not separator:
            i -= 1
        else: break
    #if the symbol is not found in the sequence,
    #the separator becomes the last symbol of the first row
    if not separator:
        i = length - 1
        separator = str[i]
    #divide the string into substrings
    substr1 = str[: i + 1].strip()
    substr2 = str[(i + 1) :].strip()
    #if the second row higher than the maximum length, call recursion
    if len(substr2) > length:
        substr2 = split_string(substr2, length)
    #divide the string into substrings on the separator and return the result
    str = substr1 + "\n" + substr2
    return str