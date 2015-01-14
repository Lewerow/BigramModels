import extract
import sys
import glob
import time
from datetime import timedelta

start_time = 0
start_time_process = 0

def seed_time():
    global start_time
    global start_time_process
    start_time = time.perf_counter()
    start_time_process = time.process_time()

def time_taken():
    global start_time
    time_diff = time.perf_counter() - start_time
    proc_diff = time.process_time() - start_time_process

    delta_time = timedelta(seconds=time_diff)
    delta_proc = timedelta(seconds=proc_diff)
    return "real: " + str(delta_time) + " process: " + str(delta_proc)


def chunks(source, target):
    chunk_size = 200000
    report_spread = 400
    count = 0
    lemmas = []
    tags = []
    seed_time()
    print("Greetings and salutations! Please be patient while we gather data from your corpus")
    all_files = glob.glob(source + "/*.ccl")
    total_count = len(all_files)

    print("Fetched directory. File count: " + str(total_count))
    print("Time taken: " + time_taken())
    seed_time()

    for filename in all_files :
        content = open(filename, 'r').read()
        lemmas.append(extract.from_string(content, "lex"))
        tags.append(extract.from_string(content, "ctag"))
        count = count + 1

        if count % report_spread == 0:
            print("Already analyzed: " + str(count) + "/" + str(total_count - count) + " files.")
            print("Time taken: " + time_taken())



        if count % chunk_size == 0:
            lemma_file = open(target + "/lemmas" + str(count) + ".txt", "w")
            lemma_text = '\n'.join(lemmas)
            lemma_file.write(lemma_text)
            lemma_file.close()
            tag_file = open(target + "/tags" + str(count) + ".txt", "w")
            tag_file.write('\n'.join(tags))
            tag_file.close()
            lemmas = []
            tags = []

            print("Wrote down data from: " + str(count) + " files. Remaining: " + str(total_count - count) + " files")
            print("Time taken: " + time_taken())

if __name__ == "__main__":
    chunks(sys.argv[1], sys.argv[2])
