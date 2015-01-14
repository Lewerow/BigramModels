import subprocess
import sys


def tag_files(input_base, input_file):
    print("Tagging file")
    subprocess.call(["wcrft-app", "nkjp_e2",
                     "-i", "txt", input_file, "-m", "maca_config", "-O", input_base + ".xml"])
    print("File tagged")


def extract_data(input_base, node):
    print("Extracting data")
    tagged = open(input_base + ".txt", "w")
    subprocess.call(["python", "extract.py",
                    input_base + ".xml",
                    node], stdout=tagged)
    tagged.close()
    print("Data extracted")


def create_symbol_table(input_base):
    print("Creating symbol table")
    symbols = open(input_base + ".syms", "w")
    subprocess.call(["ngramsymbols", input_base + ".txt"], stdout=symbols)
    symbols.close()
    print("Symbol table created")


def create_far(input_base):
    print("Converting to far archive")
    far = open(input_base + ".far", "w")
    subprocess.call(["farcompilestrings", "-token_type=utf8",
                     "-symbols=" + input_base + ".syms",
                     "-keep_symbols=1", input_base + ".txt"], stdout=far)
    far.close()
    print("Far archive created")


def build_model(input_base, method):
    print("Building model")
    count = open(input_base + ".cnts", "w")
    subprocess.call(["ngramcount", "-order=2",
                     input_base + ".far"], stdout=count)
    count.close()
    model = open(input_base + ".mod", "w")
    subprocess.call(["ngrammake", "-method=" + method,
                     input_base + ".cnts"], stdout=model)
    model.close()
    print("Model built")


def execute():
    input_file = sys.argv[1]
    input_base = input_file[:-4]

    # create directory of output files
    subprocess.call(["mkdir", "-p", input_base])
    input_base = input_base + "/" + input_base

    tag_files(input_base, input_file)

    # extract data to .txt file
    # available values: orth, lex, ctag
    extract_data(input_base, "lex")

    # create OpenFst-style symbol table
    create_symbol_table(input_base)

    # convert symbol table to binary FAR archive
    create_far(input_base)

    # Create, normalize and smooth n-gram model.
    # Smoothing methods: witten_bell(default), absolute,
    # katz, kneser_ney, presmoothed, unsmoothed
    build_model(input_base, "katz")

if __name__ == "__main__":
    execute()
