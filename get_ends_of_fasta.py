import sys
import getopt


def get_ends(fasta_str, out_length=84):
    start_dict = {}
    mid_dict = {}
    end_dict = {}
    last_id = None
    seq = ''
    for line in fasta_str.split('\n'):
        if line.startswith('>'):
            if last_id is not None:
                lseq = len(seq)
                if lseq > out_length * 3:
                    start_dict[last_id] = seq[0:out_length]
                    mid_dict[last_id] = seq[(lseq/2):(lseq/2 + out_length)]
                    end_dict[last_id] = seq[(lseq - out_length):]
            last_id = line.replace('>', '')
            seq = ''
        elif line != '':
            seq += line
        lseq = len(seq)
        if lseq > out_length * 3:
            start_dict[last_id] = seq[0:out_length]
            mid_dict[last_id] = seq[(lseq/2):(lseq/2 + out_length)]
            end_dict[last_id] = seq[(lseq - out_length):]
    return start_dict, mid_dict, end_dict


def save_fasta(fileout, fasta_dict):
    savehere = open(fileout, 'w')
    for key in fasta_dict:
        savehere.write('>' + key + '\n')
        savehere.write(fasta_dict[key] + '\n')

def usage():
    usagestr = """ python get_ends_of_fasta.py -f assembly.fa -o output_prefix
###############
-f | --fasta=           input fasta file (perhaps an assembly that one wants to QC)
-o | --out=             output_prefix
-h | --help             prints this message
"""
    print(usagestr)
    sys.exit(1)

def main():
    # get opt
    fileout = "split_seqs"
    fastain = None
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "f:o:h",
                                       ["fasta=", "out=", "help"])
    except getopt.GetoptError as err:
        print (str(err))
        usage()

    for o, a in opts:
        if o in ("-f", "--fasta"):
            fastain = a
        elif o in ("-o", "--out"):
            fileout = a
        elif o in ("-h", "--help"):
            usage()
        else:
            assert False, "unhandled option"

    if fastain is None:
        print("input fasta required")
        usage()

    stringin = open(fastain).read()
    startf, midf, endf = get_ends(stringin)
    #saving
    save_fasta(fileout + '_start.fa', startf)
    save_fasta(fileout + '_mid.fa', midf)
    save_fasta(fileout + '_end.fa', endf)

if __name__ == "__main__":
    main()