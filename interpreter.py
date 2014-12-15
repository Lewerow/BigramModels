import xml.etree.ElementTree as etree
import sys
import getopt
import types
import subprocess
import re


def tag(word):
    p = subprocess.Popen(" ".join(["echo", word, "|", "wcrft-app", "nkjp_e2", "-i", "txt", "-"]),
                         stdout=subprocess.PIPE,
                         shell=True)
    tagged = p.stdout.read()
    startbase = tagged.find("base") + 5
    endbase = tagged.find("/base", startbase) - 1
    base = tagged[startbase : endbase]
    startctag = tagged.find("ctag", endbase) + 5
    endctag = tagged.find("/ctag", startctag) - 1
    ctag = tagged[startctag : endctag]
    return {'orth': word, 'base': base, 'ctag': ctag}


def prepare_note(n):
    words = n.findall('.//item')
    real_text = [item.find('actual').text.strip() for item in words]

    return real_text


def disambiguate_all(path):
    xml = etree.parse(path)
    notes = xml.findall('.//note')
    texts = [prepare_note(n) for n in notes]
    tagged = [[tag(word) for word in actual] for actual in texts]
    bases = [[item.get("base") for item in actual] for actual in tagged]
    ctags = [[item.get("ctag") for item in actual] for actual in tagged]

    return [texts, bases]


def get_models(unigrams, bigrams):
    p = subprocess.Popen(["ngramprint", "--ARPA", sys.argv[2]],
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

    for n in range(startunigrams, startunigrams + numunigrams):
        unigrams.append(lines[n])
    for n in range(startbigrams, startbigrams + numbigrams):
        bigrams.append(lines[n])


def find_most_probable(bigrams, previous_word):
    word = 'OOV'
    max_probability = 0.0
    for bigram in bigrams:
        elements = bigram.split()
        if elements[1] == previous_word and -float(elements[0] > max_probability):
            word = elements[2]
            max_probability = -float(elements[0])

    return word


def predict(disambiguated, bigrams):
    predicted = []
    for n in range(0, len(disambiguated)):
        text = disambiguated[n]
        predictedText = []
        for m in range(1, len(text)):
            word = find_most_probable(bigrams, text[m-1])
            predictedText.append(word)
        predicted.append(predictedText)

    return predicted


if __name__ == "__main__":
    unigrams = []
    bigrams = []
    get_models(unigrams, bigrams)

    disambiguated = disambiguate_all(sys.argv[1])
    actual = disambiguated[0]
    bases = disambiguated[1]
    predicted = predict(bases, bigrams)

    for n in range(0, len(actual)):
        print("\nACTUAL:\n")
        print(' '.join(actual[n]).encode('utf8'))
        print("\nPREDICTED:\n")
        print(' '.join(predicted[n]).encode('utf8'))