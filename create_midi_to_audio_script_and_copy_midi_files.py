import os
import shutil
import mido

with open("record_midi_as_mp3s.sh", "w") as fos:
    for a,b,c in os.walk("works"):
        if c:
            for x in c:
                if x.lower().strip().endswith(".mid"):
                    m = os.path.join(a,x)
                    out = "excerpts/{c}/{w}".format(c=a.split('/')[1], w=x.lower().strip()[:-4])
                    shutil.copy2(m, os.path.join(out,"midi.mid"))
                    cmd = """fluidsynth -a alsa -T raw -F - /usr/share/sounds/sf2/FluidR3_GM.sf2 \"{m}\" |
                      ffmpeg -f s32le -i - \"{a}\"""".format(m=m, a=os.path.join(out, "audio.mp3"))
                    print(cmd, file=fos)

