# applies the Euclidean algorithm to integers a, b to return g,u,v where g = gcd(a,b) = a*u + b*v
def euclid(a,b):
    u=1
    g=a
    x=0
    y=b
    while(y!=0):
        q=g//y
        t=g%y
        u, x = x, u-q*x
        g, y = y, t
    v=(g-a*u)//b
    return (g,u,v)

# computes the inverse of f modulo q 
def inverse(f,q):
    (g,u,v) = euclid(f,q)
    if (g==1):
        return (u%q)
    else:
        return 0
# return 0 if the inverse doesn't exist


# Defines a class for polynomials with coefficients in the set Z_p, reduced modulo X**N - 1, where p and N are prime
# polynomials are represented by arrays of coefficients poly = [a_0,a_1,a_2,...a_{N-1}]

class Polynomial:

    def __init__(self,poly,p,N):
        self.poly = poly
        self.p = p  
        self.N = N
        self.reduce()

    def __add__(self,other):
        sum_poly = []
        d1 = len(self.poly)
        d2 = len(other.poly)
        d = max(d1,d2)
        for i in range(d):
            if (i < d1 and i <d2):
                sum_poly.append(self.poly[i] + other.poly[i])
            elif (i >= d1 and i < d2):
                sum_poly.append(other.poly[i])
            elif (i < d1 and i >= d2):
                sum_poly.append(self.poly[i])
        return Polynomial(sum_poly,self.p,self.N)
    
    def __iadd__(self,other):
        return self + other
   
    def __sub__(self,other):
        diff_poly = []
        d1 = len(self.poly)
        d2 = len(other.poly)
        d = max(d1,d2)
        for i in range(d):
            if (i < d1 and i <d2):
                diff_poly.append(self.poly[i]-other.poly[i])
            elif (i >= d1 and i < d2):
                diff_poly.append(-other.poly[i])
            elif (i < d1 and i >= d2):
                diff_poly.append(self.poly[i])
        return Polynomial(diff_poly,self.p,self.N)
    
    def __isub__(self,other):
        return self - other
    
    def simple_mul(self,k):   # multiplies a polynomial by a monomial X^k by inserting k zeros in the coefficient array
        shift_poly = Polynomial([0]*k + self.poly,self.p,self.N+k)
        return shift_poly
    
    def reduce(self):
        # reduce degree by letting X^N -> 1
        while(len(self.poly) > self.N):
            self.poly[-self.N-1] += self.poly[-1]
            del self.poly[-1]
        # reduce all coefficients modulo p
        for i in range(len(self.poly)):
            self.poly[i] %= self.p
        # remove all leading zero coefficients
        while(len(self.poly) > 0 and self.poly[-1]==0):
            del self.poly[-1]
        self.degree = len(self.poly)-1
        for i in range(len(self.poly)):
            if (self.poly[i] > self.p//2):
                self.poly[i] -= self.p      # center-lift all coefficients
        
        
    def check(self,other):
        if(not (self.p == other.p and self.N == other.N)):
            print("Signatures p/N of the two polynomials do not match.")
            return 1
        else:
            return 0
        
   
    def __mul__(self,other):
        product = Polynomial([],self.p,self.N)
        for i in range(len(other.poly)):
            w = (self**(other.poly[i])).simple_mul(i)
            product += w
            product.reduce()
        return product

    def __imul__(self,other):
        return self * other
    
    def __pow__(self,a):  ## multiplication of a polynomial with a scalar a
        scalarmult_poly = []
        for i in range(len(self.poly)):
            scalarmult_poly.append(self.poly[i]*a)
        return Polynomial(scalarmult_poly,self.p,self.N)
    
    def __ipow__(self,a):
        return self.__pow__(a)
    
    def polynomial_division(self,other):
        # returns the polynomials q[x], r[x] satisfying self[x] = q[x] * other[x] + r[x] where deg(r) < deg(other)
        r = Polynomial(self.poly[:],self.p,self.N)
        k = r.degree - other.degree
        if (k < 0):
            return Polynomial([],self.p,self.N), r
        q = Polynomial([0]*k + [1],self.p,self.N)
        inv = inverse(other.poly[-1],self.p)
        while(k >= 0):
            a = (r.poly[-1] * inv)%self.p
            q.poly[k] = a
            r -= other.simple_mul(k)**a
            r.reduce()
            k = r.degree - other.degree
        return q, r
    
    def __truediv__(self,other):
        return self.polynomial_division(other)        
    
    def __floordiv__(self,other):
        q,r = self.polynomial_division(other)
        return q
            
    def __mod__(self,other):
        q,r = self.polynomial_division(other)
        return r
    
    def euclid(self,other):
        u = Polynomial([1],self.p,self.N)
        g = Polynomial(self.poly[:],self.p,self.N)
        x = Polynomial([],self.p,self.N)
        y = Polynomial(other.poly[:],other.p,other.N) # N+1
        while(y.degree > -1):
            q, r = g / y
            u, x = x, u-q*x
            g, y = y, r  # r = g
        v=(g-self*u)//other
        return (g,u,v)
    
    def gcd(self,other):
        g,u,v = euclid(self,other)
        return g
    
    def inverse(self,other):
        g,u,v = self.euclid(other)
        if(g.degree > 0):
            return Polynomial([],self.p,self.N) # return a zero polynomial if the inverse doesn't exist
        else:
            return u**inverse(g.poly[0],self.p)