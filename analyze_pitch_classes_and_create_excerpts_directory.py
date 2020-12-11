import os
import json
import mido

for a,b,c in os.walk("works"):
    if c:
        for x in c:
            if x.lower().strip().endswith(".mid"):
                print(a,x)
                os.makedirs("excerpts/{c}/{w}".format(c=a.split('/')[1], w=x.lower().strip()[:-4]), exist_ok=True)
                out = "excerpts/{c}/{w}".format(c=a.split('/')[1], w=x.lower().strip()[:-4])
                mid = mido.MidiFile(os.path.join(a,x))
                d = {}
                t = 0
                time = 0
                S = []
                X = {}
                for msg in mid:
                    if time > t + 10:
                        X[t] = {"cardinality": len(list(sorted(list(set(S))))), "pitches": list(sorted(list(set(S))))}
                        t = t + 10
                        S = []
                    if msg.type == "track_name":
                        print(msg.name)
                    if msg.type == "program_change":
                        c, p = msg.channel, msg.program
                        d[c] = p
                        
                    time += msg.time
                    if msg.type == "note_on":
                        if d.get(msg.channel, 0) < 96 or (104 <= d.get(msg.channel, 0) <= 111):
                            S.append(msg.note % 12)
                with open(os.path.join(out,"stats.json"), "w") as fos:
                    json.dump(X,fos)

