import pandas as pd

if __name__ == "__main__":
    anne_full = pd.read_csv("anne_full.csv", index_col=0)

    silence_duration_ms = pd.read_csv("silence_duration_ms.csv", index_col=0)
    silence_duration_ms["0"] = silence_duration_ms["0"].str.rsplit("/", n=1, expand=True)[1].str[:-4]
    silence_duration_ms.columns = ["ind", "silence_ms"]
    anne_full = anne_full.merge(silence_duration_ms, on="ind")
    
    anne_full["start_sec"] = anne_full.start_sec + (anne_full.silence_ms.clip(0, None) / 1000)
    
    # anne_full = anne_full[anne_full.time_diff < 10]

    anne_full["time_diff"] = anne_full.end_sec - anne_full.start_sec

    anne_full["num_words"] = anne_full.text.str.split().apply(len)
    
    # filter for segments that aren't too long
    anne_full = anne_full[anne_full.time_diff < 10]
    
    # filter for segments that aren't too short
    anne_full = anne_full[anne_full.time_diff > 0.5]

    # filter out End of chapter...
    anne_full = anne_full[~((anne_full.time_diff > 5) & (anne_full.num_words == 4))]
    anne_full = anne_full[~((anne_full.time_diff > 8) & (anne_full.num_words == 12))]

    # save to new csv
    anne_full.to_csv("anne_full_filtered.csv")

    with open("anne_labels_filtered.csv", "w") as f:
        for i, row in anne_full[anne_full.time_diff < 10].iterrows():
            f.write(row["ind"] + "|" + ' '.join(row["text"].split()) + "\n")
