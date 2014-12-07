import subprocess
import sys
import re


def execute():
    p = subprocess.Popen(["ngramprint", "--ARPA", sys.argv[1]],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    out, err = p.communicate()

    lines = out.splitlines()
    numunigrams = int(re.findall(r"\d+", lines[2])[-1])
    numbigrams = int(re.findall(r"\d+", lines[3])[-1])

    # I assume same format for every file
    distance = 2
    startunigrams = 6
    startbigrams = startunigrams + numunigrams + distance

    unigrams = []
    for n in range(startunigrams, startunigrams + numunigrams):
        unigrams.append(lines[n])
    bigrams = []
    for n in range(startbigrams, startbigrams + numbigrams):
        bigrams.append(lines[n])

if __name__ == "__main__":
    execute()