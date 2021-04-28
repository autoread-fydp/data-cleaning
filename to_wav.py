import os
import glob
import tqdm

files = glob.glob("*/mp3/*.mp3")

for f in tqdm.tqdm(files):
    wav_f = f.replace("mp3", "wav")
    os.system("ffmpeg -i " + f + " -ar 22050 -ac 1 -c:a pcm_s16le " + wav_f)
