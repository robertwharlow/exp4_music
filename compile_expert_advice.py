import os
import shutil
import json
import mido

X = {}
for a,b,c in os.walk("works"):
    if c:
        for x in c:
            if x.lower().strip().endswith(".mid"):
                c=a.split('/')[1]
                if c not in X:
                    X[c] = {}
                out = "excerpts/{c}/{w}".format(c=a.split('/')[1], w=x.lower().strip()[:-4])
                out2 = os.path.join(out,"snippets")
                with open(os.path.join(out,"stats.json")) as fis:
                    data = json.load(fis)
                for t in data:
                    if data[t]["cardinality"] > 0:
                        X[c][data[t]["cardinality"]] = X[c].get(data[t]["cardinality"],0) + 1

"""
with open("counts.json", "w") as fos:
    json.dump(X,fos,indent=4)
"""

for c in X:
    t = sum(X[c].values())
    for l in X[c]:
        X[c][l] = X[c][l] / t

with open("excerpts/experts.json", "w") as fos:
    json.dump(X,fos,indent=4)

