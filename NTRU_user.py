import Polynomial as poly
import math, random
import csv

class NTRU_user:
    
    def __init__(self,name,N,p,q,d,new=True,public=False):  # N,p,q should be distinct primes, q > (6*d +1)*p
        self.name = name
        self.N = N
        self.d = d
        self.p = p
        self.q = q
        self.XN_1_p = poly.Polynomial([-1] + [0]*(self.N-1) + [1],self.p,self.N+1)
        self.XN_1_q = poly.Polynomial([-1] + [0]*(self.N-1) + [1],self.q,self.N+1)
        if new:
            degree = -1
            while(degree == -1):
                self.f_p, self.f_q = self.generate_ternary_poly(self.d+1,self.d)
                self.f_p_inv = self.f_p.inverse(self.XN_1_p)
                self.f_q_inv = self.f_q.inverse(self.XN_1_q)
                degree = min(self.f_p_inv.degree,self.f_q_inv.degree)
            self.g_p, self.g_q = self.generate_ternary_poly(self.d,self.d)
            self.h = self.f_q_inv * self.g_q              # h is the public key of an NTRU_user
    
    @classmethod
    def init_user(cls,filename,public=True):
        with open(filename, newline='') as csvfile:
            filereader = csv.reader(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_NONNUMERIC)
            row1 = next(filereader)
            name, N, p, q, d = row1
            N, p, q, d = int(N), int(p), int(q), int(d)
            user = cls(name,N,p,q,d,new=False,public=public)
            row2 = next(filereader)
            for i in range(len(row2)):
                row2[i] = int(row2[i])
            user.h = poly.Polynomial(row2,user.q,user.N)
            if not public:
                row3 = next(filereader)
                for i in range(len(row3)):
                    row3[i] = int(row3[i])
                user.f_p = poly.Polynomial(row3,user.p,user.N)
                user.f_q = poly.Polynomial(row3,user.q,user.N)
                user.f_p_inv = user.f_p.inverse(user.XN_1_p)
                user.f_q_inv = user.f_q.inverse(user.XN_1_q)
            return user

    def generate_ternary_poly(self,d1,d2):   # generate ternary polynomials of degree < self.N with d1 coefficients equal to 1,
        if (d1 + d2 < self.N):               # d2 coefficients equal to -1, the rest being 0, under the condition d1 + d2 < N.
            coefficients = [0]*self.N
            index_list = [k for k in range(self.N)]
            for i in range(d1):
                index = random.randint(0,len(index_list)-1)
                coefficients[index_list[index]] = 1
                del index_list[index]
            for i in range(d2):
                index = random.randint(0,len(index_list)-1)
                coefficients[index_list[index]] = -1
                del index_list[index]
            ternary_poly_p = poly.Polynomial(coefficients[:],self.p,self.N)
            ternary_poly_q = poly.Polynomial(coefficients[:],self.q,self.N)
            return ternary_poly_p, ternary_poly_q
        else:
            print('Parameters d_1 + d_2 too large, their sum must be less than N!')
            
        
    def output_public_key(self,filename='public_key.csv'):
        with open(filename, 'w', newline='') as csvfile:
            filewriter = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_NONNUMERIC)
            filewriter.writerow([self.name,self.N,self.p,self.q,self.d])
            filewriter.writerow(self.h.poly)
            
    def output_private_key(self,filename='private_key.csv'):
        with open(filename, 'w', newline='') as csvfile:
            filewriter = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_NONNUMERIC)
            filewriter.writerow([self.name,self.N,self.p,self.q,self.d])
            filewriter.writerow(self.h.poly)
            filewriter.writerow(self.f_p.poly)
 
    def encode(self,message): # encodes a message of type string into a Polynomial
        poly_array = []
        message_len = len(message)
        N = self.N
        p = self.p
        c = int(math.log(p,256))
        position = -1
        while(position < message_len):
            num_poly = len(poly_array)
            coefficients = []
            for i in range(N):
                coeff = 0
                for j in range(c):
                    position += 1
                    if (position < message_len):
                        char_value = ord(message[position])
                    else:
                        char_value = ord(' ')       # padding with spaces
                    coeff += char_value * 256**j   
                coefficients.append(coeff)
            mess_pol = poly.Polynomial(coefficients,p,N)
            poly_array.append(mess_pol)
        return poly_array

    def decode(self,pol_array):
        message = ''
        for i in range(len(pol_array)):
            for j in range(self.N):
                coeff = (pol_array[i].poly[j])%self.p
                while (coeff != 0):
                    message += chr(coeff%256)
                    coeff //= 256
        return message
    
    def encrypt(self,pol_array):
        encrypted_pol_array = []
        for pol in pol_array:
            r_p, r_q = self.generate_ternary_poly(self.d,self.d)
            e = ((self.h**self.p) * r_q) + pol
            encrypted_pol_array.append(e)        
        return encrypted_pol_array

    def decrypt(self,encrypted_pol_array):
        decrypted_pol_array = []
        for encrypted_pol in encrypted_pol_array:
            a = self.f_q * encrypted_pol
            b = self.f_p_inv * a
            decrypted_pol_array.append(b)
        return decrypted_pol_array
    
    def sign(self,signature):
        pass
    
    def verify(self,message,signature):
        pass
    
    def send(self,message,user,filename='encrypted.csv'):
        pol_array = user.encode(message)
        encrypted_pol_array = user.encrypt(pol_array)
        with open(filename, 'w', newline='') as csvfile:
            filewriter = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_NONNUMERIC)
            for pol in encrypted_pol_array:
                filewriter.writerow(pol.poly)
        return encrypted_pol_array
    
    def receive(self,filename):
        encrypted_pol_array = []
        with open(filename, newline='') as csvfile:
            filereader = csv.reader(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_NONNUMERIC)
            for row in filereader:
                for i in range(len(row)):
                    row[i] = int(row[i])
                pol = poly.Polynomial(row,self.q,self.N)
                encrypted_pol_array.append(pol)
        decrypted_pol_array = self.decrypt(encrypted_pol_array)
        message = self.decode(decrypted_pol_array)
        return message