import os
import json
import mido

with open("splice_audio_into_snippets.sh", "w") as fos:
    for a,b,c in os.walk("works"):
        if c:
            for x in c:
                if x.lower().strip().endswith(".mid"):
                    os.makedirs("excerpts/{c}/{w}".format(c=a.split('/')[1], w=x.lower().strip()[:-4]), exist_ok=True)
                    out = "excerpts/{c}/{w}".format(c=a.split('/')[1], w=x.lower().strip()[:-4])
                    out2 = os.path.join(out,"snippets")
                    os.makedirs(out2, exist_ok=True)
                    with open(os.path.join(out,"stats.json")) as fis:
                        data = json.load(fis)
                    for t in data:
                        cmd = "ffmpeg -ss {t} -t 10 -i \"{a}\" \"{s}\"".format(t=t, a=os.path.join(out, "audio.mp3"), s=os.path.join(out2,str(t) + ".mp3"))
                        print(cmd, file=fos)

