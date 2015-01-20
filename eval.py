from sys import stdin
import sys
import subprocess
import extract

# params
# lex / ctag
# model

temp_dir = "temp/"

def execute():
    global temp_dir;
    subprocess.call(["mkdir", "-p", temp_dir])
    line = stdin.readline()
    while (line != "\n"):
        plain = open(temp_dir + "plain.txt", 'w+')
	plain.write(line + '\n');
        plain.close()
        subprocess.call(["wcrft-app", "nkjp_e2",
                     "-i", "txt", temp_dir + "plain.txt", 
		     "-O", temp_dir + "tagged.xml"])
	extracted = extract.execute(temp_dir + "tagged.xml", sys.argv[1])

        tagged = open(temp_dir + "extracted.txt", "w")
        tagged.write(extracted + '\n')
        tagged.close()

	symbols = open(temp_dir + "symbols.syms", "w")
        subprocess.call(["ngramsymbols", temp_dir + "extracted.txt"], stdout=symbols)
        symbols.close()

	far = open(temp_dir + "far.far", "w")
        subprocess.call(["farcompilestrings",
                     "-symbols=" + temp_dir + "symbols.syms",
                     "-keep_symbols=1", temp_dir + "extracted.txt"], stdout=far)
        far.close()

	subprocess.call(["ngramperplexity", sys.argv[2], temp_dir + "far.far"])

	line = stdin.readline()
	

if __name__ == "__main__":
    execute()
