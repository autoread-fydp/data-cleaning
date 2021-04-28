import pandas as pd
import librosa
import soundfile as sf

SR = 22050

def remove_leading_silence(fname, silence_ms):
    wav, sr = librosa.load(fname)
    silence_ms = max(0, silence_ms)
    sf.write("cut_"+fname, wav[int(silence_ms / 1000 * sr):], SR)

if __name__ == "__main__":
    df = pd.read_csv("silence_duration_ms.csv", index_col=0)
    df["0"] = df["0"].str.rsplit("/", n=1, expand=True)[1]
    df["0"] = "wavs/" + df["0"]

    df.apply(lambda x: remove_leading_silence(x["0"], x["1"]), axis=1) 

