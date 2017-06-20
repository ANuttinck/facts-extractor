'''Extracts type facts from a wikipedia file
usage: extractor.py wikipedia.txt output.txt

Every line of output.txt contains a fact of the form
    <title> TAB <type>
where <title> is the title of the Wikipedia page, and
<type> is a simple noun (excluding abstract types like
sort, kind, part, form, type, number, ...).

If you do not know the type of an entity, skip the article.
(Public skeleton code)'''

from parser import Parser
from random import choice
import string
# import nltk
import re
import csv
import sys

if len(sys.argv) != 3:
    print(__doc__)
    sys.exit(-1)

def extractType(page):
    relations_list = ["is a", "is the", "are", "is an", "was the", "were", "was a", "was an"]
    relation_patterns = [r"(?<=\b%s\s)((\w*)(?:\s*))*" % rel for rel in relations_list]
	"(is|means)\s+((the|a|an)\s+)?((part of|type of|one of)\s+)?((a|the)\s+)?((\w+)\s+)+(from|in|of|\W|that|for)"
	"is.*(?=\s\bof\s)"
	"(is|mean)\s+((the|a|an)\s+)?(\b\w+\b\s+)*(?P<type>\b\w+\b)(\b(from|in|of|that|for)\b)"
	"\b(is|mean)\b\s+(\b(the|a|an)\b\s+)?(\w+\s+)*(?P<type>\w+)(\s+\b(from|in|of|that|for)\b)"
	"\b(is|mean)\b\s+(\b(the|a|an)\b\s+)?(\b(part|type|one)\b\s+\bof\b\s+)+(\b(a|the)\b\s+)?(\w+(\')?\w+\s+)*(?P<type>\w+)(\s+\b(from|in|of|that|for)\b)(\s+\w+)*\.$"
    relations_re = re.compile('|'.join(relation_patterns))
    be_EofS = relations_re.search(page.content)

    if be_EofS:
        before_of = re.search("\w*(?=\s\bof)", be_EofS.group())
        if before_of:
            return before_of.group()
        else:
            """
            tag_sentence = nltk.pos_tag(re.split("\s+", be_EofS.group()))
            for wd, tag in tag_sentence:
                if tag in ['NN']:
                    return wd
                else:
                    return be_EofS[0]
            """
            return re.split("\s+", be_EofS.group())[0]

    else:
        list_of_words = re.split("\s+", page.content.replace(string.punctuation, ""))
        potential_answer = [wd for wd in list_of_words if len(wd) > 2]
        if potential_answer:
            return choice(potential_answer)
        else:
            return ""


def eval_acc_goldstd(predicted_fact):

    with open('../gold-standard-sample.tsv', mode='r') as infile:
        reader = csv.reader(infile, delimiter='\t')
        goldstd = {rows[0]:rows[1] for rows in reader}

    scores = list(map(lambda ent: goldstd[ent]==predicted_fact[ent],
                        goldstd.keys()))

    return float(sum(scores)) / len(scores)


with open(sys.argv[2], 'w', encoding="utf-8") as output:
    types = {}
    for page in Parser(sys.argv[1]):
        typ = extractType(page)

        types[page.title] = typ

        if typ:
            output.write(page.title + "\t" + typ + "\n")
    print(eval_acc_goldstd(types))
