def flip (n,n_bits,bit):
    """n -> decimal number
    n_bits -> number of bits in the number
    bit -> index of the bit to flip"""
    n_bin = reverse(bin(n)[2:]) 
    n_bin += "0"*(n_bits-len(n_bin))
    if n_bin[bit] == "1" :
        n_bin = n_bin[:bit] + "0" + n_bin[bit+1:]
    else :
         n_bin = n_bin[:bit] + "1" + n_bin[bit+1:]
    return to_dec(n_bin)


def to_dec (n_bin):
    n = 0
    for k in range(len(n_bin)):
        n += (2**k) * int(n_bin[k])
    return n

def reverse (string:str):
    a = ""
    for k in range(len(string)-1,-1,-1):
        a += string[k]
    return a

def L1 (n_matches):
    """n_matches -> in power of 2"""
    placement = [x for x in range(2**n_matches)]
    for i in range(2**n_matches):
        for j in range(n_matches): # flip every bit
            placement[i] = flip( placement[i] , n_matches , j )
    return placement

def L3 (n_matches):
    """n_matches -> in power of 2"""
    placement = [x for x in range(2**n_matches)]
    for i in range(2**n_matches):
        placement[i] = flip( placement[i] , n_matches , n_matches-1 )  # on flip le dernier bit
    return placement

def L2 (n_matches):
    """n_matches -> in power of 2"""
    placement = [x for x in range(2**n_matches)]
    for i in range(2**n_matches):
        for j in range(n_matches-1): # on flip les 'n_matches-1' bit
            placement[i] = flip( placement[i] , n_matches , j )
    return placement

def L4 (n_matches):
    """n_matches -> in power of 2"""
    return [x for x in range(2**n_matches)]

def L5 (n_matches):
    return L4 (n_matches)

def L6 (n_matches):
    return L4(n_matches)