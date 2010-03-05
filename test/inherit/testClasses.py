from inherit.A import A
class B(A):
    def __init__(self):
        A.__init__(self)
        print "B init"
        
    def do(self):
        A.do(self)
        
b = B()  
b.do()      

         
         
                     