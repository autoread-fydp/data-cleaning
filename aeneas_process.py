from aeneas.executetask import ExecuteTask
from aeneas.task import Task
import glob
import tqdm
import nltk
nltk.download('punkt')


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
    wav_files = sorted(glob.glob("r*/wav/*.wav"))
    txt_files = sorted(glob.glob("r*/txt/*.txt"))
    csv_files = ["/".join([f.split("/")[0], "csv", f.split("/")[2][:-3] + "csv"]) for f in txt_files]
    # csv_files = ["/".join(["/".join(f.split("/")[:-2]), "csv-filtered", f.split("/")[-1][:-3] + "csv"]) for f in wav_files]
    
    processed_txt = ["/".join([f.split("/")[0], "processed_txt", f.split("/")[2]]) for f in txt_files]

    wav_files = [u"/home/ezeng/fydp/data/karen_savage/{}".format(f) for f in wav_files]
    txt_files = [u"/home/ezeng/fydp/data/karen_savage/{}".format(f) for f in txt_files]
    csv_files = [u"/home/ezeng/fydp/data/karen_savage/{}".format(f) for f in csv_files]
    processed_txt = [u"/home/ezeng/fydp/data/karen_savage/{}".format(f) for f in processed_txt]

    for wav_f, txt_f, csv_f in tqdm.tqdm(zip(wav_files, processed_txt, csv_files), total=len(wav_files)):
        csv_file = txt_f[:-3] + "csv"
        process_aeneas(txt_f, wav_f, csv_f)
