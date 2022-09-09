@@ -0,0 +1,91 @@
#!/usr/bin/env python3

import argparse
import os
import queue
import sounddevice as sd
import vosk
import sys
from vosk import SetLogLevel
import json
from email.mime import audio
from msilib.schema import Directory
from gtts import gTTS
import os
from colorama import Back, Fore, Style, deinit, init
from playsound import playsound

q = queue.Queue()
SetLogLevel(-1)

def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text

def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    q.put(bytes(indata))

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument(
    '-l', '--list-devices', action='store_true',
    help='show list of audio devices and exit')
args, remaining = parser.parse_known_args()
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[parser])
parser.add_argument(
    '-f', '--filename', type=str, metavar='FILENAME',
    help='audio file to store recording to')
parser.add_argument(
    '-d', '--device', type=int_or_str,
    help='input device (numeric ID or substring)')
parser.add_argument(
    '-r', '--samplerate', type=int, help='sampling rate')
args = parser.parse_args(remaining)

try:
    if args.samplerate is None:
        device_info = sd.query_devices(args.device, 'input')
        # soundfile expects an int, sounddevice provides a float:
        args.samplerate = int(device_info['default_samplerate'])

    model = vosk.Model(lang="fr")

    if args.filename:
        dump_fn = open(args.filename, "wb")
    else:
        dump_fn = None

    with sd.RawInputStream(samplerate=args.samplerate, blocksize = 8000, device=args.device, dtype='int16',
                            channels=1, callback=callback):

            rec = vosk.KaldiRecognizer(model, args.samplerate)
            while True:
                data = q.get()
                if rec.AcceptWaveform(data):
                    understand = (False)
                    parler = json.loads(rec.FinalResult())
                    if (parler['text']) == ("bonjour"):
                        reponse = ("salut")
                        print(reponse)
                        mytext = (reponse)
                        language = 'fr'
                        voice = (mytext+".mp3")
                        textSpeech = gTTS(text=mytext, lang=language, slow=False)
                        textSpeech.save(voice)
                        playsound(voice)
                        os.remove(voice)
                        understand = (True)
                    if (parler['text']) == (""):
                        understand = (True)
                    if understand == (False):
                        print("vous avez dit "+"'"+Fore.RED+(parler['text'])+Style.RESET_ALL+"'"+" mais ca ne peut pas etre encore interpreter")
except KeyboardInterrupt:
    parser.exit(0)
except Exception as e:
    parser.exit(type(e).__name__ + ': ' + str(e))
