__author__ = 'adenton'
import json
import operator
import re
import sys
import getopt


def usage():
    usagestr = """ python not-a-wordcloud.py -j values_for_counting.json > fileout.tsv
###############
-a | --annotated-blast= input tabular blast file with extra annotation column
-h | --help             prints this message
"""
    print(usagestr)
    sys.exit(1)


def count_words_in_values(anno_dict):
    word_counts = {}
    words = []
    for item in anno_dict.values():
#        if re.match('Vitis', item):
#            print item
        words += clean_words(item)

    for word in words:
        try:
            word_counts[word] += 1
        except KeyError:
            word_counts[word] = 1

    boring = ['sequence', 'genome', 'predicted', 'complete', 'partial', 'gene', 'chromosome', 'assembly', 'protein',
              'dna', 'scaffold', 'contig', 'whole', 'shotgun', 'bac', 'genomic', 'from', 'and', 'in', 'for', 'sp',
              'mrna', 'cds', 'clone', 'missing', 'strain', 'x', 'isolate']
    for boreword in boring:
        if boreword in word_counts:
            del word_counts[boreword]

    sorted_words = sorted(word_counts.items(), key=operator.itemgetter(1))
    sorted_words = list(reversed(sorted_words))
    return sorted_words


def clean_words(prose):
    pre_words = prose.split()
    words = []
    # strip all non-alphanumeric characters from end and start of string
    for pre_word in pre_words:
        try:
            pre_chars = list(pre_word)
            while not pre_chars[-1].isalnum():
                pre_chars.pop()
            while not pre_chars[0].isalnum():
                pre_chars.pop(0)
            chars_done = ''.join(pre_chars).lower()
        except IndexError:
            chars_done = ''
        words.append(chars_done)
    return words


def main():
    filein = None
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "a:h",
                                       ["annotated-blast=", "help"])
    except getopt.GetoptError as err:
        print (str(err))
        usage()

    for o, a in opts:
        if o in ("-a", "--annotated-blast"):
            filein = a
        elif o in ("-h", "--help"):
            usage()
        else:
            assert False, "unhandled option"

    if filein is None:
        print("input annotated blast required (-a)")
        usage()

#    stringin = open(filein).read()
#    anno_dict = json.loads(stringin)
    anno_dict = {}
    for line in open(filein).readlines():
        splitline = line.rstrip().split('\t')
        anno_dict[splitline[0]] = splitline[12]

    out = count_words_in_values(anno_dict)
    for row in out:
        print row[0] + '\t' + str(row[1])

if __name__ == "__main__":
    main()