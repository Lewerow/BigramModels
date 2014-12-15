import xml.etree.ElementTree as etree
import sys
import getopt
import types
import subprocess

def most_probable_variant(variants):
    max_word = variants[0][0]
    max_prob = variants[0][1]

    for word, prob in variants:
        if prob > max_prob:
            max_prob = prob
            max_word = word

    return max_word

def highest_probability_disambiguation(sequence):
    # Lista jest posortowana
    return [variants[0][0] for variants in sequence]

def tag(word, preceeding_sequence):
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

def run_tagger(sequence):
    already_tagged = []
    for variants in sequence:
        if isinstance(variants[0], types.StringTypes):
           already_tagged.append((tag(variants[0], already_tagged), variants[1]))
        else:
            already_tagged.append([(tag(v[0], already_tagged), v[1]) for v in variants])
    
    return already_tagged
    

def disambiguate_obvious_words(sequence):
    obviousity_threshold = 0.8
    return [variants[0] if variants[0][1] > obviousity_threshold else variants for variants in sequence]

def disambiguate_words(sequence):
    # result is a list of tuples -> (dictionary, probability) and lists of tuples -> (dictionary, probability)
    # dictionary contains fields 'orth', 'base' and 'ctag'
    disambiguated_obvious = disambiguate_obvious_words(sequence)
    return run_tagger(disambiguated_obvious)

def get_sequence_probability(w1, w2, token_type):
    return 1.0

def bigram_disambiguation(variants, last_disambiguated, token_type):
    return most_probable_variant([(variant[0], get_sequence_probability(last_disambiguated, variant[0], token_type) * variant[1]) for variant in variants])

def token_disambiguation(sequence, token_type):
    global bigram_disambiguation
    available_words = disambiguate_words(sequence)
    empty_word = {'base': '', 'orth': '', 'ctag': ''}
    disambiguated = [empty_word]
    for i in range(0, len(available_words)):
        if not type(available_words[i]) is list:
            disambiguated.append(available_words[i][0])
        else:
            disambiguated.append(bigram_disambiguation(available_words[i], disambiguated[-1], token_type))

    del disambiguated[0]
    return [d['orth'] for d in disambiguated]

def grammar_form_disambiguation(sequence):
    return token_disambiguation(sequence, 'ctag')

def entropy_disambiguation(sequence):
    return token_disambiguation(sequence, 'base')

disambiguation_strategies = {
    'highest_probability' : highest_probability_disambiguation, 
    'grammar_form' : grammar_form_disambiguation,
    'entropy' : entropy_disambiguation
}

def disambiguate(sequence, strategy):
    global disambiguation_strategies
    if not strategy in disambiguation_strategies.keys():
        raise Exception("Unknown disambiguation strategy")

    return disambiguation_strategies[strategy](sequence)

def split_fields(variant):
    elems = variant.strip().split(' ')
    return (elems[0], float(elems[-1]))

def prepare_note(n):
    nonzero_threshold = 0.0001
    words = n.findall('.//item')
    real_text = [item.find('actual').text.strip() for item in words]
    possibilities = [[split_fields(variant.text) for variant in item.findall('.//variant')] for item in words]
    
    nonzero_possibilities = [[variant for variant in item if variant[1] > nonzero_threshold] for item in possibilities]

    return (real_text, nonzero_possibilities)

def disambiguate_all(path, strategy):
    xml = etree.parse(path)
    notes = xml.findall('.//note')
    texts = [prepare_note(n) for n in notes]

    disambiguated = [disambiguate(note[1], strategy) for note in texts] #tzn. wywalamy rzeczywista wiedze

    return [(texts[i][0], disambiguated[i]) for i in range(0, len(texts))]


if __name__ == "__main__":
    strategy = "highest_probability"
    if len(sys.argv) > 2:
        strategy = sys.argv[2]

    disambiguated = disambiguate_all(sys.argv[1], strategy)

    #for note in disambiguated:
    #    print("\nEXPECTED:\n")
    #    print(' '.join(note[0]).encode('utf8'))
    #    print("\nACTUAL:\n")
    #    print(' '.join(note[1]).encode('utf8'))

