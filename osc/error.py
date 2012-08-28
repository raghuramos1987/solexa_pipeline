class MyError(Exception):
    pass

    #def __init__(self, err_str, line_int):
        #print "Error in "+err_str+"\nLine number:"+line_int

class FnfError(MyError):

    def __init__(self, file, message = ""):
        print "File not found: "+file
        print message

class ConfError(MyError):
    
    def __init__(self, err_str, line_int, err_line = ""):
        print "Error in "+err_str+"\nLine:"+err_line+\
        "Line number:"+str(line_int)

class UsageError(MyError):

    def __init__(self, message = ""):
        print message

class TransferError(MyError):

    def __init__(self, message = ""):
        print message

