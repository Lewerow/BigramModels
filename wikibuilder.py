import subprocess
import sys
import os


data_dir = "data/"
models_dir = "models/"


def extract_data(input_dir, input_file, node):
    global data_dir
    #print("Extracting data for " + input_file)
    tagged = open(data_dir + input_file + ".txt", "w")
    subprocess.call(["python", "extract.py",
                    input_dir + "/" + input_file, 
                    node], stdout=tagged)
    tagged.close()
    #print("Data extracted")


def create_symbol_table(input_file):
    global data_dir
    #print("Creating symbol table for " + input_file)
    symbols = open(data_dir + input_file + ".syms", "w")
    subprocess.call(["ngramsymbols", 
                    data_dir + input_file + ".txt"],
                    stdout=symbols)
    symbols.close()
    #print("Symbol table created")


def create_far(input_file):
    global data_dir
    #print("Converting to far archive for " + input_file)
    far = open(data_dir + input_file + ".far", "w")
    subprocess.call(["farcompilestrings", "-token_type=utf8",
                     "-symbols=" + data_dir + input_file + ".syms",
                     "-keep_symbols=1", data_dir + input_file + ".txt"], 
                     stdout=far)
    far.close()
    #print("Far archive created")


def get_counts(input_file):
    global data_dir
    #print("Counting for " + input_file)
    count = open(data_dir + input_file + ".cnts", "w")
    subprocess.call(["ngramcount", "-order=2",
                     data_dir + input_file + ".far"], stdout=count)
    #print("Counted")


def build_model(input_file, method):
    global models_dir
    #print("Building model for " + input_file)
    model = open(models_dir + input_file + ".mod", "w")
    subprocess.call(["ngrammake", "-method=" + method,
                     data_dir + input_file + ".cnts"], stdout=model)
    model.close()
    #print("Model built")


def execute():
    global data_dir
    global models_dir
    input_dir = sys.argv[1] + "/"

    subprocess.call(["mkdir", "-p", data_dir])
    subprocess.call(["mkdir", "-p", models_dir])

    # create models for each file in input directory
    for input_file in os.listdir(input_dir):
        # extract data to .txt file
        # available values: orth, lex, ctag
        extract_data(input_dir, input_file, "lex")

        # create OpenFst-style symbol table
        create_symbol_table(input_file)

        # convert symbol table to binary FAR archive
        create_far(input_file)

        # get counts
        get_counts(input_file)
        
        # Create, normalize and smooth n-gram model.
        # Smoothing methods: witten_bell(default), absolute,
        # katz, kneser_ney, presmoothed, unsmoothed
        # save models in different directory
        build_model(input_file, "katz")

if __name__ == "__main__":
    execute()
