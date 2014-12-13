import xml.etree.ElementTree as etree
import sys
import getopt

def get_sequence_probability(w1, w2):
    return 1.0

def extract_words_from_ocr(tree):
    return True 

def split_fields(variant):
    elems = variant.strip().split(' ')
    return (elems[0], float(elems[-1]))

def prepare_note(n):
    nonzero_threshold = 0.0001
    words = n.findall('.//item')
    real_text = [item.find('actual').text for item in words]
    possibilities = [[split_fields(variant.text) for variant in item.findall('.//variant')] for item in words]
    
    nonzero_possibilities = [[variant for variant in item if variant[1] > nonzero_threshold] for item in possibilities]

    return (real_text, nonzero_possibilities)

def estimate_probabilities(path):
    xml = etree.parse(path)
    notes = xml.findall('.//note')
    texts = [prepare_note(n) for n in notes]
    return texts


if __name__ == "__main__":
    print(estimate_probabilities(sys.argv[1]))
