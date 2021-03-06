from aeneas.executetask import ExecuteTask
from aeneas.task import Task
import glob
import numpy as np
import os
import pandas as pd
import librosa
import tqdm
import nltk
nltk.download('punkt')


def reformat_text_to_mplain(text):
    text = text.split("\n\n")
    text = [paragraph.replace("\n", " ") for paragraph in text]

    text = [nltk.tokenize.sent_tokenize(paragraph) for paragraph in text]

    text = ["\n".join(paragraph) for paragraph in text]

    text = "\n\n".join(text)
    
    return text


def clean_smart_quotes(content):
    content = content.replace('\u2018\u2018', '"')
    content = content.replace('\u2019\u2019', '"')
    content = content.replace('\u2018', "'")
    content = content.replace('\u2019', "'")
    content = content.replace('\u201C', '"')
    content = content.replace('\u201D', '"')

    return content


def split_long_sentences(sentence, max_len=300, sep_char="; ", min_words=2):
    if len(sentence) < max_len:
        return [sentence]
    splitted_sentences = sentence.split(sep_char)
    splitted_sentences[:-1] = [fragment + sep_char for fragment in splitted_sentences[:-1]]
    # for ; and : separators, just separate and move on to the next potential separator
    if sep_char == "; ":
        new_splitted_sentences = []
        for fragment in splitted_sentences:
            new_splitted_sentences.extend(split_long_sentences(fragment, sep_char=': '))
        return new_splitted_sentences
    elif sep_char == ": ":
        new_splitted_sentences = []
        for fragment in splitted_sentences:
            new_splitted_sentences.extend(split_long_sentences(fragment, sep_char=', '))
        return new_splitted_sentences

    # if the separator is ", ", then there's a increased liklihood of there being
    # many fragments, each relatively short.
    elif sep_char == ", ":
        if len(splitted_sentences) == 2:
            return splitted_sentences
        elif len(splitted_sentences) > 2:
            new_splitted_sentences = [splitted_sentences[0]]
            for fragment in splitted_sentences[1:]:
                if len(fragment.split(" ")) > min_words:
                    new_splitted_sentences.append(fragment)
                else:
                    new_splitted_sentences[-1] += fragment
            if len(new_splitted_sentences) < 2:
                print(new_splitted_sentences)
            return new_splitted_sentences
        else:
            print(sentence)
            return [sentence]


def process_and_save_txt_files(load_filename, save_filename):
    with open(load_filename, "r", encoding="utf-8-sig") as f:
        text = f.read()

    text = clean_smart_quotes(text)
    # in this case, mplain is a aeneas format where each line is a separate sentence
    # and paragraphs are separated by \n\n
    mplain_txt = reformat_text_to_mplain(text).split("\n")
    num_characters = np.array([len(line) for line in mplain_txt])
    mplain_txt = pd.Series(mplain_txt)

    # filter out "sentences" that are far too short to be real (< 5 characters)
    # combine that sentence into the previous and next "sentences
    for idx in mplain_txt[np.bitwise_and(num_characters > 0, num_characters < 5)].index.values:
        mplain_txt.loc[idx - 1] += " " + mplain_txt.loc[idx] + " " + mplain_txt.loc[idx]

    mplain_txt = mplain_txt[~np.bitwise_or(
        np.bitwise_and(num_characters > 0, num_characters < 5),
        np.append([False], np.bitwise_and(num_characters > 0, num_characters < 5)[:-1])
    )]

    # split long sentences into shorter fragments
    mplain_txt_new = mplain_txt.apply(split_long_sentences).explode()

    dir_path = os.path.dirname(save_filename)
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)

    with open(save_filename, "w") as f:
        f.write("\n".join(mplain_txt_new))


def process_aeneas(txt_filename, wav_filename, csv_filename):
    # create Task object
    config_string = u"task_language=eng|is_text_type=plain|os_task_file_format=csv"
    task = Task(config_string=config_string)
    task.audio_file_path_absolute = wav_filename
    task.text_file_path_absolute = txt_filename
    task.sync_map_file_path_absolute = csv_filename

    # process Task
    ExecuteTask(task).execute()

    # output sync map to file
    task.output_sync_map_file()
  

if __name__ == "__main__":
    wav_files = sorted(glob.glob("anne*/wav/*.wav"))
    txt_files = sorted(glob.glob("anne*/txt/*.txt"))
    csv_files = ["/".join([f.split("/")[0], "csv", f.split("/")[2][:-3] + "csv"]) for f in txt_files]
    processed_txt = ["/".join([f.split("/")[0], "processed_txt", f.split("/")[2]]) for f in txt_files]

    wav_files = [u"/home/ezeng/fydp/data/karen_savage/{}".format(f) for f in wav_files]
    txt_files = [u"/home/ezeng/fydp/data/karen_savage/{}".format(f) for f in txt_files]
    csv_files = [u"/home/ezeng/fydp/data/karen_savage/{}".format(f) for f in csv_files]
    processed_txt = [u"/home/ezeng/fydp/data/karen_savage/{}".format(f) for f in processed_txt]

    for txt_f, save_f in zip(txt_files, processed_txt):
        process_and_save_txt_files(txt_f, save_f)

    for wav_f, txt_f, csv_f in tqdm.tqdm(zip(wav_files, processed_txt, csv_files)):
        csv_file = txt_f[:-3] + "csv"
        process_aeneas(txt_f, wav_f, csv_f)
