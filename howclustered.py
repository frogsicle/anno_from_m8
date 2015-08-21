import sys


class BlastLine:
    def __init__(self, line):
        entries = line.split()
        self.qid = entries[0]
        self.hid = entries[1]
        startend = [int(x) for x in entries[8:10]]
        self.start = min(startend)
        self.end = max(startend)

    def __str__(self):
        return str(self.__dict__)

    def overlaps(self, other):
        out = False
        if self.start <= other.start and self.end >= other.start:
            out = True
        elif self.start <= other.end and self.end >= other.end:
            out = True
        elif self.start >= other.start and self.end <= other.end:
            out = True
        return out

unique = 0
clustered = 0

filein = open(sys.argv[1]).readlines()
scaffolds = {}
for line in filein:
    bl = BlastLine(line)
    if bl.hid in scaffolds:
        scaffolds[bl.hid] += [bl]
    else:
        scaffolds[bl.hid] = [bl]

for scaffold in scaffolds:
    bls = scaffolds[scaffold]
    for i in range(len(bls)):
        bl = bls[i]
        if i == 0:
            unique += 1
        elif not any([bl.overlaps(bls[x]) for x in range(i + 1)]):  # if there's no overlap with previous hits
            print [str(bls[x]) for x in range(i + 1)]
            clustered += 1
            unique += 1

print 'clustered:\t' + str(clustered)
print 'unique:\t' + str(unique)

