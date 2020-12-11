import json
import os

with open("excerpts/experts.json") as fis:
    e = json.load(fis)

e2 = {}
for x in e:
    if x != "beethoven":
        e2[x] = {
                "1-7": 0,
                "8-9": 0,
                "10-12": 0
            }
        for y in e[x]:
            if int(y) <= 7:
                e2[x]["1-7"] += e[x][y]
            if int(y) in [8,9]:
                e2[x]["8-9"] += e[x][y]
            if int(y) > 9:
                e2[x]["10-12"] += e[x][y]

snippets = {
        "1-7": [],
        "8-9": [],
        "10-12": []
    }

for a,b,c in os.walk("works"):
    if c:
        for x in c:
            if x.lower().strip().endswith(".mid"):
                c=a.split('/')[1]
                if c != "beethoven":
                    out = "excerpts/{c}/{w}".format(c=a.split('/')[1], w=x.lower().strip()[:-4])
                    out2 = os.path.join(out,"snippets")
                    with open(os.path.join(out,"stats.json")) as fis:
                        data = json.load(fis)
                    for t in data:
                        path = os.path.join(out2,str(t) + ".mp3")
                        if data[t]["cardinality"] > 0:
                            if data[t]["cardinality"] <= 7:
                                snippets["1-7"].append(path)
                            if data[t]["cardinality"] in [8,9]:
                                snippets["8-9"].append(path)
                            if data[t]["cardinality"] > 9:
                                snippets["10-12"].append(path)

data = {"snippets": snippets, "experts": e2}

os.makedirs("web_application/package", exist_ok=True)

with open("web_application/package/data.json", "w") as fos:
    json.dump(data,fos)




