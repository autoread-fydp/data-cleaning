from aeneas.executetask import ExecuteTask
from aeneas.task import Task
import glob
import numpy as np
import os
import pandas as pd
import librosa
import soundfile as sf
import tqdm
from slice_wavs import save_wav, cut_wav_files


def get_segments(csv_files):
    segments = [
        pd.read_csv(fname, header=None, sep="^").dropna()
        for fname in csv_files
    ]

    for i, (s, fname) in enumerate(zip(segments, csv_files)):
        # separate into 3 columns based on the first 2 tabs
        s = s[0].str.split(n=2, pat="\t", expand=True)

        s[2].replace('', np.nan, inplace=True)
        s = s.dropna()

        # name the columns for easy viewing
        s.columns = ["start_sec", "end_sec", "text"]

        book = fname.split("/")[-3]
        chapter = fname.split("/")[-1]

        s["book"] = book
        s["chapter"] = chapter
        s = s.astype({"start_sec": float, "end_sec": float, "text": str, "book": str, "chapter": str})
        s["time_diff"] = s.end_sec - s.start_sec
        segments[i] = s[s.time_diff > 0]

    # concat all books and chapters together, then save it
    full_labels = pd.concat(segments, ignore_index=True)
    rec_num = ["f%05d" % i for i in range(len(full_labels))]
    full_labels["ind"] = rec_num
    full_labels.to_csv("processed_anne/anne_full.csv")

    with open("processed_anne/anne_labels.csv", "w") as f:
        for i, row in full_labels.iterrows():
            f.write(row["ind"] + "|" + ' '.join(row["text"].split()) + "\n")

    return segments



if __name__ == "__main__":
    csv_files = sorted(glob.glob("anne*/audacity-edited/*.txt"))
    wav_files = ["/".join([f.split("/")[0], "wav", f.split("/")[2][:-3] + "wav"]) for f in csv_files]

    wav_files = [u"/home/ezeng/fydp/data/karen_savage/{}".format(f) for f in wav_files]
    csv_files = [u"/home/ezeng/fydp/data/karen_savage/{}".format(f) for f in csv_files]

    if not os.path.exists("processed_anne"):
        os.mkdir("processed_anne")

    if not os.path.exists("processed_anne/wavs"):
        os.mkdir("processed_anne/wavs")


    segments = get_segments(csv_files)

    cut_wav_files(segments, wav_files)
