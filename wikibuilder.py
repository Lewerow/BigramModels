import subprocess
import sys
import os
import time

import extract
from xml.etree.ElementTree import ParseError

data_dir = "data/"
counts_dir = "counts/"
models_dir = "models/"
result_dir = "result_model/"

class EmptyTagData(Exception):
    pass

def extract_data(input_dir, input_file, node):
    global data_dir
    #print("Extracting data for " + input_file)
    extracted = extract.execute(input_dir + input_file, node)

    if extracted == "":
        raise EmptyTagData

    tagged = open(data_dir + input_file + ".txt", "w")
    tagged.write(extracted)
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
    global counts_dir
    global data_dir
    #print("Counting for " + input_file)
    count = open(counts_dir + input_file + ".cnts", "w")
    subprocess.call(["ngramcount", "-order=2",
                     data_dir + input_file + ".far"], stdout=count)
    count.close()
    #print("Counted")


def build_model(output_file, input_file, method):
    #print("Building model for " + input_file)
    model = open(output_file, "w")
    subprocess.call(["ngrammake", "-method=" + method,
                     input_file], stdout=model)
    model.close()
    #print("Model built")

def merge_model(main_model, merged, out):
    global counts_dir
    #print("Building model for " + input_file)
    out_model = open(out, "w")
    subprocess.call(["ngrammerge", main_model, counts_dir + merged], stdout=out_model)
    out_model.close()
    #print("Model built")


def format_time(seconds):
    if seconds < 300:
        return str(seconds) + " s"
    if seconds < 30000:
        return str(seconds / 60) + " m"
    else:
        return str(seconds / 3600) + " h"

def execute():
    global data_dir
    global models_dir
    input_dir = sys.argv[1] + "/"

    subprocess.call(["mkdir", "-p", data_dir])
    subprocess.call(["mkdir", "-p", counts_dir])
    subprocess.call(["mkdir", "-p", models_dir])

    how_many_done = 0
    empty = 0
    invalid = 0
    
    start_time = time.time()
    # create models for each file in input directory
    for input_file in os.listdir(input_dir)[:1000]:
        if how_many_done % 100 == 0:
            print("Already analyzed: " + str(how_many_done) + ". Currently analyzing file: " + input_file)
            print("Time taken: " + format_time(time.time() - start_time))
            print("Done properly ratio: " + str((how_many_done - empty - invalid) / float(how_many_done + 0.00000001)))
            print("Empty files ratio: " + str(empty / float(how_many_done + 0.00000001)))
            print("Invalid files ratio: " + str(invalid / float(how_many_done + 0.00000001)))

        how_many_done = how_many_done + 1
        try:
            # extract data to .txt file
            # available values: orth, lex, ctag
            extract_data(input_dir, input_file, "lex")
        except ParseError:
            #print("Invalid data in: " + input_dir + input_file )
            # means that data is unparsable. Shit happens
            # but no point in continuing da loop
            invalid = invalid + 1
            continue
        except EmptyTagData:
            #print("No tagged data in file: " + input_dir + input_file)
            empty = empty + 1
            # means that wasn't tagged "properly" and is in fact and empty file
            # so no sense in continuing
            continue
        
        # create OpenFst-style symbol table
        create_symbol_table(input_file)

        # convert symbol table to binary FAR archive
        create_far(input_file)

        # get counts
        get_counts(input_file) 

def merge_models():
    global counts_dir
    global result_dir
    subprocess.call(["mkdir", "-p", result_dir])
    
    files = os.listdir (counts_dir)
    starter = files.pop()

    main_model_names = ["main_model_1.cnts", "main_model_2.cnts"]
    subprocess.call(["mv", counts_dir + starter, result_dir + main_model_names[0]])
    i = 0
    j = 1

    start_time = time.time()
    count = 0
    for input_file in files:
        if count % 100 == 0:
            print("Already merged: " + str(count) + ". Currently merging file: " + input_file)
            print("Time taken: " + format_time(time.time() - start_time))
        # incorporate various models into main one
        # but since there is no guarantee that main won't be overridden before it is totally read, we use two files
        merge_model(result_dir + main_model_names[i], input_file, result_dir + main_model_names[j])
        if i == 0:
            j = 0
            i = 1
        else:
            i = 1
            j = 0

        count = count + 1
    
      

    subprocess.call(["mv", result_dir + main_model_names[i], result_dir + "final_model.cnts"])

    # Create, normalize and smooth n-gram model.
    # Smoothing methods: witten_bell(default), absolute,
    # katz, kneser_ney, presmoothed, unsmoothed
    # save models in different directory
    build_model(result_dir + "final_model.mod", result_dir + "final_model.cnts", "katz")
 

if __name__ == "__main__":

    starter = time.time()
    execute()
    executing = time.time()
    merge_models()
    merging = time.time()

    print("Done everything. Building counts took: " + format_time(executing - starter) + ", merging and building model took: " + format_time(merging - executing) + ".\nIn total spent: " + format_time(merging - starter))
