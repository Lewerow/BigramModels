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

def execute(filename, token_type):
  global getters
  parser = etree.parse(filename)
  tokens = parser.findall('.//tok')

  values = getters[token_type](tokens)
  return ' '.join(values).encode('utf8')

def from_string(string, token_type):
  global getters
  parser = etree.fromstring(string)
  tokens = parser.findall('.//tok')
  values = getters[token_type](tokens)

  return ' '.join(values)

if __name__ == "__main__":
  print(execute(sys.argv[1], sys.argv[2]))
