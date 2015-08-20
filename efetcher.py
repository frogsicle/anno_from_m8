__author__ = 'adenton'

import urllib2
import time
import re
import json
import random
import sys
import getopt


def usage():
    usagestr = """ python efetcher.py -b blast_results.m8  -o output_prefix
###############
-b | --blast=           input tabular blast file
-a | --anno=            file with fasta headers from refseq (>sequence|id any amount of annotation text)
-j | --json=            json file of pre-collected annotations
-o | --out=             output_prefix
-h | --help             prints this message
"""
    print(usagestr)
    sys.exit(1)


class BlastLine:
    def __init__(self, line):
        entries = line.split()
        self.qid = entries[0]
        self.hid = entries[1].split('|')[1]
        self.all = line.rstrip()


class BlastToQuery:
    """
    Holds blast results, and queries NCBI for annotation
    """

    def __init__(self, filein, nucl=True, maxhits=10000):
        linesin = open(filein).readlines()
        self.results = [BlastLine(x) for x in linesin]
        self.hits = [x.hid for x in self.results]
        self.hits = list(set(self.hits))  # get unique
        if len(self.hits) > maxhits:
            self.hits = random.sample(self.hits, maxhits)
        self.annotation_key = {}
        if nucl:
            self.db = "nuccore"
        else:
            self.db = "protein"

    def get_data(self, rettype='fasta', parsewith='fasta'):
        at_once = 200
        i = 0
        base = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?seq_stop=10'
#        base = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?'
        gb_out = {}
        l = len(self.hits)
        while i < len(self.hits):
            upper = min(i + at_once + 1, l)
            current_keys = self.hits[i:upper]
            current_keys = [x for x in current_keys if x not in self.annotation_key]
            res = get_from_ncbi(base, db=self.db, rettype=rettype, id_list=current_keys)
            if parsewith == "fasta":
                gb_out.update(parse_fasta(res))
            elif parsewith == "genbank":
                gb_out.update(parse_genbank(res))
            else:
                raise ValueError("parse functions only available for 'fasta' or 'genbank'")
            i += at_once
            time.sleep(0.34)

        self.annotation_key = gb_out

    def load_json(self, jsonfile):#todo test
        jsonin = open(jsonfile).read()
        anno_dict = json.loads(jsonin)
        self.annotation_key = anno_dict

    def load_data(self, datafile):
        annotation_key = {}
        datain = open(datafile).readlines()
        for line in datain:
            splitline = line.split()
            id = splitline[0].replace('>', '').split('|')[1]
            anno = ' '.join(splitline[1:])
            annotation_key[id] = anno
#            print 'id: '+id+'### anno:' + anno
        self.annotation_key = annotation_key

    def save_table(self, fileout):
        openfile = open(fileout, 'w')
        for blastline in self.results:
            try:
                newline = blastline.all + '\t' + self.annotation_key[blastline.hid] + '\n'
            except KeyError:
                newline = blastline.all + '\tmissing\n'
            openfile.write(newline)

    def save_json(self, fileout):
        openfile = open(fileout, 'w')
        openfile.write(json.dumps(self.annotation_key))


def parse_genbank(res):
    """
    functional but terribly slow method to parse  ID and annotation out of genbank file
    :param res:
    :return:
    """
    gb_out = {}
    annotation = ''
    res = res.split("\n")
    for line in res:
        if line.startswith('DEFINITION'):
            annotation = line.rstrip().replace('DEFINITION  ', '')
        elif line.startswith('VERSION'):
            gb_id = re.search('GI:([0-9]*)', line)
            gb_id = gb_id.group(1)
            print gb_id
        #    print gb_id.group(1)
            gb_out[gb_id] = annotation
    return gb_out


def parse_fasta(res):
    gb_out = {}
    res = res.split("\n")
    for line in res:
        if line.startswith('>'):
            gb_id = re.search('gi\|([0-9]*)', line)
            try:
                gb_id = gb_id.group(1)
            except AttributeError:
                print line + "NO MATCH"
            annotation = re.search(' (.*)', line)
            try:
                annotation = annotation.group(1)
            except AttributeError:
                print line + "NO ANNO MATCH"
            gb_out[gb_id] = annotation
    return gb_out


def get_from_ncbi(base, **kwargs):
    apistring = base
    if 'id_list' in kwargs:
        #format to id=&id=&id=&id=& for ncbi
        id_format = '&id='.join(kwargs['id_list'])
        del kwargs['id_list']
        kwargs['id'] = id_format

    for param in kwargs:
        val = kwargs[param].replace(' ', '+')
        apistring += '&' + param + '=' + val
    print 'searched for: ' + apistring
    try:
        response = urllib2.urlopen(apistring)
        out = response.read()
    except Exception as e:
        print e
        print 'returning empty string'
        out = ''
    return out


def main():
    # get opt
    fileout = "new_blast_anno"
    blastres = None
    fileanno = None
    filejson = None

    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "b:a:j:o:h",
                                       ["blast=", "anno=", "json=", "out=", "help"])
    except getopt.GetoptError as err:
        print (str(err))
        usage()

    for o, a in opts:
        if o in ("-b", "--blast"):
            blastres = a
        elif o in ("-o", "--out"):
            fileout = a
        elif o in ("-j", "--json"):
            filejson = a
        elif o in ("-a", "--anno"):
            fileanno = a
        elif o in ("-h", "--help"):
            usage()
        else:
            assert False, "unhandled option"

    if blastres is None:
        print("input blast results required (-b)")
        usage()

    br = BlastToQuery(filein=blastres)
    if filejson is not None:
        br.load_json(filejson)
    if fileanno is not None:
        br.load_data(fileanno)
    br.get_data(rettype="gb", parsewith="genbank")

    br.save_json(fileout=fileout + '.json')
    br.save_table(fileout=fileout + '.tsv')
 #   fasta = open('sequence.fasta')
 #   x = parse_fasta(fasta)
 #   print(x)
#    genbank = open('sequence.gb')
#    x = parse_genbank(genbank)
#    print x


if __name__ == '__main__':
    main()


