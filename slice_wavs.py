from aeneas.executetask import ExecuteTask
from aeneas.task import Task
import glob
import numpy as np
import os
import pandas as pd
import librosa
import soundfile as sf
import tqdm


def get_segments(csv_files):
    # pandas was having issues with the quotes and commas within each string
    segments = [
        pd.read_csv(fname, header=None, sep="^").dropna()
        for fname in csv_files
    ]

    for i, (s, fname) in enumerate(zip(segments, csv_files)):
        # separate into 4 columns based on the first 3 commas
        s = s[0].str.split(n=3, pat=",", expand=True)

        # remove quotes around string
        s[3] = s[3].str[1:-1]

        s[3].replace('', np.nan, inplace=True)
        s = s.dropna()

        # name the columns for easy viewing
        s.columns = ["line", "start_sec", "end_sec", "text"]

        book = fname.split("/")[-3]
        chapter = fname.split("/")[-1]

        s["book"] = book
        s["chapter"] = chapter
        s = s.astype({"line": str, "start_sec": float, "end_sec": float, "text": str, "book": str, "chapter": str})
        s["time_diff"] = s.end_sec - s.start_sec
        segments[i] = s[s.time_diff > 0]

    # concat all books and chapters together, then save it
    full_labels = pd.concat(segments, ignore_index=True)
    rec_num = ["f%05d" % i for i in range(27739, 27739 + len(full_labels))]
    full_labels["ind"] = rec_num
    full_labels.to_csv("processed_anne/anne_full.csv")
    full_labels[["ind", "text"]].to_csv("anne_labels.csv", header=False, index=False, sep="|")

    with open("processed_anne/anne_labels.csv", "w") as f:
        for i, row in full_labels.iterrows():
            f.write(row["ind"] + "|" + ' '.join(row["text"].split()) + "\n")

    return segments


def save_wav(out_dir, index, wav, text):
    wav_filename = 'f%05d.wav' % index
    sf.write(os.path.join(out_dir, "wavs", wav_filename), wav, 22050)


def cut_wav_files(segments, wav_files):
    ind = 27739
    for segment, wav_f in tqdm.tqdm(zip(segments, wav_files), total=len(wav_files)):
        wav, sr = librosa.load(wav_f)
        for _, line in segment.iterrows():
            start_idx = int(line.start_sec * sr)
            end_idx = int(line.end_sec * sr)
            save_wav("processed_anne/", ind, wav[start_idx:end_idx], line.text)
            ind += 1


if __name__ == "__main__":
    wav_files = sorted(glob.glob("r*/wav/*.wav"))
    txt_files = sorted(glob.glob("r*/txt/*.txt"))
    csv_files = ["/".join([f.split("/")[0], "csv", f.split("/")[2][:-3] + "csv"]) for f in txt_files]

    wav_files = [u"/home/ezeng/fydp/data/karen_savage/{}".format(f) for f in wav_files]
    csv_files = [u"/home/ezeng/fydp/data/karen_savage/{}".format(f) for f in csv_files]

    if not os.path.exists("processed_anne"):
        os.mkdir("processed_anne")

    if not os.path.exists("processed_anne/wavs"):
        os.mkdir("processed_anne/wavs")


    segments = get_segments(csv_files)

    cut_wav_files(segments, wav_files)
