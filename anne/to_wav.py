import os
import glob
import tqdm

files = glob.glob("*/wav/*.mp3")

for f in tqdm.tqdm(files):
    wav_f = f[:-3] + "wav"
    os.system("ffmpeg -i " + f + " -ar 22050 -ac 1 " + wav_f)
