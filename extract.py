import xml.etree.ElementTree as etree
import sys
import getopt

def print_orths(tokens):
  for tok in tokens:
    print(tok.find('orth').text)

def print_lemmas(tokens):
  for tok in tokens:
    print(tok.find('lex').find('base').text)

def print_grammar(tokens):
  for tok in tokens:
    print(tok.find('lex').find('ctag').text)


def execute():
  parser = etree.parse(sys.argv[1])
  tokens = parser.findall('//tok')

  if sys.argv[2] == 'orth':
    print_orths(tokens)
  elif sys.argv[2] == 'lex':
    print_lemmas(tokens)
  elif sys.argv[2] == 'ctag':
    print_grammar(tokens)

if __name__ == "__main__":
  execute()

