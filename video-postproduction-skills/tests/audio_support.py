"""Local synthetic PCM only, not speech generation or proof of human listening."""
from array import array
import math
import sys
import wave
from support import pin


def tone(root,name="tone.wav",frequency=440,frames=24000,rate=48000,channels=2):
    values=array("h",(round(0.2*32767*math.sin(2*math.pi*frequency*i/rate)) for i in range(frames) for _ in range(channels)))
    if sys.byteorder!="little":values.byteswap()
    with wave.open(str(root/name),"wb") as out:
        out.setnchannels(channels);out.setsampwidth(2);out.setframerate(rate);out.writeframes(values.tobytes())
    return pin(root,name)


def stem(root,ident="toneA",frequency=440,channels=2,**changes):
    asset=tone(root,ident+".wav",frequency=frequency,channels=channels)
    evidence=pin(root,ident+"-provenance.txt","synthetic independently supplied PCM fixture, not extracted from a stereo mix; not legal/authenticity certification")
    return {"id":ident,"role":"MX","asset":asset.model_dump(),"sample_rate":48000,"channels":channels,
        "sample_count":24000,"origin":"provided_separate","independence_evidence":evidence.model_dump(),**changes}
