import xml.etree.ElementTree as etree
import sys
import getopt

def get_sequence_probability(w1, w2):
    return 1.0

def most_probable_variant(variants):
    max_word = variants[0][0]
    max_prob = variants[0][1]

    for word, prob in variants:
        if prob > max_prob:
            max_prob = prob
            max_word = word

    return max_word

def highest_probability_disambiguation(sequence):
    return [most_probable_variant(variants) for variants in sequence]

def grammar_form_disambiguation(sequence):
    return False

def entropy_disambiguation(sequence):
    return False

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

    for note in disambiguated:
        print("\nEXPECTED:\n")
        print(' '.join(note[0]).encode('utf8'))
        print("\nACTUAL:\n")
        print(' '.join(note[1]).encode('utf8'))

