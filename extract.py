import xml.etree.ElementTree as etree
import sys
import getopt

def get_orths(tokens):
  return [tok.find('orth').text for tok in tokens]

def get_lemmas(tokens):
  return [tok.find('lex').find('base').text for tok in tokens]

def get_grammar(tokens):
  return [tok.find('lex').find('ctag').text for tok in tokens]


getters = {'orth' : get_orths, 'lex' : get_lemmas, 'ctag' : get_grammar}
def execute():
  global getters
  parser = etree.parse(sys.argv[1])
  tokens = parser.findall('.//tok')

  values = getters[sys.argv[2]](tokens)
  print(' '.join(values).encode('utf8'))

if __name__ == "__main__":
  execute()