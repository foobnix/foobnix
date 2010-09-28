'''
Created on Feb 26, 2010

@author: ivan
'''
def convert_ns(time_int):    
    time_int = time_int / 1000000000
    time_str = ""
    if time_int >= 3600:
        _hours = time_int / 3600
        time_int = time_int - (_hours * 3600)
        time_str = str(_hours) + ":"
    if time_int >= 600:
        _mins = time_int / 60
        time_int = time_int - (_mins * 60)
        time_str = time_str + str(_mins) + ":"
    elif time_int >= 60:
        _mins = time_int / 60
        time_int = time_int - (_mins * 60)
        time_str = time_str + "0" + str(_mins) + ":"
    else:
        time_str = time_str + "00:"
    if time_int > 9:
        time_str = time_str + str(time_int)
    else:
        time_str = time_str + "0" + str(time_int)
        
    return time_str

def convert_seconds_to_text(time_sec):    
        time_str = ""
        if time_sec >= 3600:
            _hours = time_sec / 3600
            time_sec = time_sec - (_hours * 3600)
            time_str = str(_hours) + ":"
        if time_sec >= 600:
            _mins = time_sec / 60
            time_sec = time_sec - (_mins * 60)
            time_str = time_str + str(_mins) + ":"
        elif time_sec >= 60:
            _mins = time_sec / 60
            time_sec = time_sec - (_mins * 60)
            time_str = time_str + "0" + str(_mins) + ":"
        else:
            time_str = time_str + "00:"
        if time_sec > 9:
            time_str = time_str + str(time_sec)
        else:
            time_str = time_str + "0" + str(time_sec)
            
        return time_str


def normilize_time(length):
    if length < 0:
        return 0
    
    length = int(length)
    result = ""
    hour = int(length / 60 / 60)
    if hour:
        if hour < 10:
            hour = "0" + str(hour)
        result = str(hour) + ":"     
    min = int(length / 60) - int(hour) * 60
    if min:
        if min < 10:
            min = "0" + str(min)
        result += str(min) + ":"
    else:
        result += "00:"
    
    sec = length - int(min) * 60 - int(hour) * 3600
    if sec < 10:
        sec = "0" + str(sec)   
    
    result += str(sec)
    return result
