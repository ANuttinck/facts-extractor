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
import os.path
import string
import re
import csv
import sys

if len(sys.argv) != 3:
    print(__doc__)
    sys.exit(-1)

goldstd_fname = './gold-standard-sample.tsv'

# definition des mots cles utilises pour l'extraction des donnees
verbs = ["is", "are", "mean", "means", "was", "were", "will be", "to be"]
dets = ["the", "a", "an", "The"]
previous_noun = ["part(s)?", "type(s)?", "one(s)?", "style(s)?", "word(s)?", "set(s)?"]
end_wds = ["from", "in", "of", "that", "for", "with", "and", "around",
           "or", "on", "who", "where", "what", "which", "at", "by", "[a-z]+ed", "made"]

end_pat = r"\b(\.|\,|(" + r"|".join(end_wds) + r")\b)"
type_pat = r"(?P<type>[ \w\_\-\&\s\"]+?)\s?"

# definition du pattern de la regex
complete_pat = r"\b(" + r"|".join(verbs) + r")\s+(((" + r"|".join(dets) + r")\s+)?(\w+\s+)*(" + \
                r"|".join(previous_noun) + r")\s+(of|for)\s+)?((" + r"|".join(dets) + r")\s+)?" + type_pat + end_pat

# compilation du pattern de la regex
relations_re = re.compile(complete_pat)

def extractType(page):

    matching = relations_re.search(page.content)
    if matching:
        typ = matching.group("type")
        return typ.split()[-1].strip()
    else:
        return ""


def eval_acc_goldstd(predicted_fact):

    with open(goldstd_fname, mode='r', encoding='utf-8') as infile:
        reader = csv.reader(infile, delimiter='\t')
        goldstd = {rows[0]:rows[1] for rows in reader}

    scores = list(map(lambda ent: goldstd[ent] == predicted_fact[ent],
                        goldstd.keys()))

    non_empty = list(map(lambda ent: predicted_fact[ent] != "",
                        goldstd.keys()))

    precision = float(sum(scores)) / sum(non_empty)
    rappel = float(sum(scores)) / len(scores)
    
    return precision, rappel

# ecriture du fichier output avec l'extraction de faits
with open(sys.argv[2], 'w', encoding="utf-8") as output:
    types = {}
    for page in Parser(sys.argv[1]):
        typ = extractType(page)
        types[page.title] = typ

        if typ:
            output.write(page.title + "\t" + typ + "\n")

if os.path.isfile(goldstd_fname):
	precision_gs, rappel_gs = eval_acc_goldstd(types)
	print("Precision sur le gold standard: {0:.2%}".format(precision_gs))
	print("Rappel sur le gold standard: {0:.2%}".format(rappel_gs))
	print("F = {0:.2%}".format(2 * (rappel_gs * precision_gs)/(rappel_gs + precision_gs)))

non_empty = sum(map(lambda val: val != "", types.values()))
print("Nombre de predictions non nulles sur l'ensemble de {0}: {1}/{2}".format(sys.argv[1], non_empty, len(types.values())))
print("Rappel maximal sur le gold standard {0}: {1:.2%}".format(sys.argv[1], non_empty / len(types.values())))
