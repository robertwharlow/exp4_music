import pandas as pd
import seaborn as sns
import numpy as np
import os
import matplotlib.pyplot as plt
import math
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--input")
parser.add_argument("--dashed", type=int, default=0)
parser.add_argument("--csv_path")
parser.add_argument("--png_path")
parser.add_argument("--title")
args = parser.parse_args()

with open(args.input) as fis:
    data = json.load(fis)

MAP = {
"bernstein": "Leonard Bernstein",
"debussy": "Claude Debussy",
"dvorak": "Antonín Dvořák",
"holst": "Gustav Holst",
"mahler": "Gustav Mahler",
"mozart": "Wolfgang Amadeus Mozart",
"prokofiev": "Sergei Prokofiev",
"rimski-korsakov": "Nikolai Rimsky-Korsakov",
"shostakovich": "Dmitri Shostakovich",
"sibelius": "Jean Sibelius",
"stravinsky": "Igor Stravinsky",
"wagner": "Richard Wagner"
}

recs = []
keys = []
ROUND = 0
for R in data["current"]["rounds"]:
    Q = R["Q"]
    M = len(Q)
    A = R["A"]
    P = R["P"]
    n = data["current"]["n"]
    k = len(P)
    learning_rate = math.sqrt( ((2 * math.log(M)) / (n * k)) )
    print(Q)
    Q2 = {MAP[x]: Q[x] for x in Q}
    if not keys:
        keys = ["round"] + list(Q2.keys())
    Q2["round"] = ROUND
    recs.append(Q2) 
    ROUND += 1

if os.path.dirname(args.csv_path) != "":
    os.makedirs(os.path.dirname(args.csv_path), exist_ok=True)

with open(args.csv_path, "w") as fos:
    writer = csv.DictWriter(fos, fieldnames=keys)
    writer.writeheader()
    writer.writerows(recs)

df = pd.read_csv(args.csv_path, index_col=0)

g = sns.lineplot(data=df, dashes=False)

if args.dashed != 0:
    ls = ["-", "--", ":", "-", "--", ":", "-", "--", ":", "-", "--", ":", "-", "--", ":", "-", "--", ":", "-", "--", ":", "-", "--", ":", "-", "--", ":", "-", "--", ":" ]
    for l in g.lines:
        l.set_linestyle(ls.pop())

box = g.get_position()
g.set_position([box.x0, box.y0, box.width * 0.7, box.height])

fig = plt.gcf()
fig.set_size_inches(9, 5, forward=True)

g.set_title(args.title)
g.set_ylabel('weight')
g.set_xlabel('round')

g.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)


OUTPUT = args.png_path

if os.path.dirname(OUTPUT) != "":
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)

plt.savefig(OUTPUT)
 
