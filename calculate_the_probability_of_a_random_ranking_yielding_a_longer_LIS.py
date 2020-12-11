import os
import math
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--input")
args = parser.parse_args()

with open(args.input) as fis:
    data = json.load(fis)

#My ranking of the composers independent of Exp4
r = [
"prokofiev",
"shostakovich",
"sibelius",
"stravinsky",
"bernstein",
"rimski-korsakov",
"wagner",
"debussy",
"mahler",
"holst",
"dvorak",
"mozart",
][::-1]

r2 = {x: i+1 for x,i in zip(r, range(len(r)))}

s = [r2[x[0]] for x in sorted(data["current"]["rounds"][-1]["Q"].items(), key=lambda kv: kv[1])]

# A LIS implementation adapted from code presented on Wikipedia here https://en.wikipedia.org/wiki/Longest_increasing_subsequence
def LIS(X):
    N = len(X)
    P = [-1 for n in range(N)]
    M = [-1 for n in range(N+1)]

    L = 0
    for i in range( 0, N ):
        # Binary search for the largest positive j ≤ L
        # such that X[M[j]] <= X[i]
        lo = 1
        hi = L
        while lo <= hi:
            mid = math.ceil((lo+hi)/2)
            if X[M[mid]] <= X[i]:
                lo = mid+1
            else:
                hi = mid-1

        # After searching, lo is 1 greater than the
        # length of the longest prefix of X[i]
        newL = lo

        # The predecessor of X[i] is the last index of 
        # the subsequence of length newL-1
        P[i] = M[newL-1]
        M[newL] = i
        
        if newL > L:
            # If we found a subsequence longer than any we've
            # found yet, update L
            L = newL

    # Reconstruct the longest increasing subsequence
    S = [-1 for n in range(N)]
    k = M[L]
    for i in reversed(range( 0, L)):
        S[i] = X[k]
        k = P[k]

    return S, L

lis = LIS(s)[1]

count = 0
for i in range(10000):
    s2 = copy.deepcopy(s)
    random.shuffle(s2)
    if LIS(s2)[1] >= lis:
        count += 1

print("Input:", args.input)
print("Lis:", lis)
print("Number of random rankings out of 10,000 yielding a longest increasing subsequence as long or longer than that observed.", count)
print("Empirical Probability that a random ranking yields a longest increasing subsequence as long or longer than that observed.", count/10000)


    
