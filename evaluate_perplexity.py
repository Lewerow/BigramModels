import builder
import sys
import subprocess

def print_perplexity():
    f = open("input_file.inp", "w")
    f.write(sys.argv[1])
    f.close()
    
    builder.tag_files("input_file", "input_file.inp")
    builder.extract_data("input_file", "lex")
    
    data = open("input_file.txt", "r")
    out = open("input_far.far", "w")
    subprocess.call(["farcompilestrings", "-generate_keys=1", "-symbols="+sys.argv[2], "--keep_symbols=1"], stdin=data, stdout=out)

# "|", "ngramperplexity", "--v=1", sys.argv[3] ,"-"])
    data.close()
    out.close()

    subprocess.call(["ngramperplexity", "--v=1", sys.argv[3], "input_far.far"])    


if __name__ == "__main__":
    print_perplexity()
