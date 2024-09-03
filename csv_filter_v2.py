import pandas as pd
import json
from unidecode import unidecode
import re
import time

from Trie import Trie

def build_set(term_file) -> set:
    """Build a set of terms from a JSON file.
    - Complexity: O(n)
    - Input: term_file (str) -> path to the JSON file.
    - Output: term_set (set) -> set of terms.
    """
    with open(term_file, 'r', encoding='utf-8') as json_file:
        terms = json.load(json_file)
        term_set = set()
        # Adiciona os termos ao conjunto
        for term in terms:
            if isinstance(term, list):
                for t in term:
                    if t.startswith('@') or str(t[0]).isupper():
                        term_set.add(t)
            else:
                if term.startswith('@') or str(term[0]).isupper():
                    term_set.add(term)
    return term_set

# Função para criar expressões regulares a partir dos termos
def create_regex_pattern(term):
    term_normalized = unidecode(term)
    pattern = r'(?<!\w)' + re.escape(term_normalized) + r'(?!\w)'
    return re.compile(pattern, re.IGNORECASE)

# Função para extrair o shortcode da URL
def extract_shortcode(url):
    match = re.search(r'/p/([^/]+)/', url)
    return match.group(1) if match else ''

def build_filtered_df(raw:pd.DataFrame, terms_set:set) -> pd.DataFrame:
    """Find all the matching terms in a Dataframe row.
    - Complexity: O(n^2) -> O(n) for each row.
    """
    # mocked
    row_name = 'Tweet Text'
    matching_terms = []
    raw['MatchTerm'] = None
    for index, row in raw.iterrows():
        words = row[row_name].split()
        first_word = words[0]
        tst = Trie(first_word)
        for word in words[1:]:
            tst.append(word)
        for term in terms_set:
            if tst.__contains__(term):
                matching_terms.append(term)
        if len(matching_terms) > 0:
            raw.at[index, 'MatchTerm'] = matching_terms
        del tst
        matching_terms = []
    return raw[raw['MatchTerm'].notnull()]
   
csv_file = '/home/zuzu/labic/projects/CommentsFilter/dataX.csv'
sep = ','
header = True

term_file = '/home/zuzu/labic/projects/CommentsFilter/term.json'
init = time.time()
print('Reading CSV file...')
raw = pd.read_csv(csv_file, sep=sep)
print('Building terms set...')
terms_set = build_set(term_file)
print('Building filtered DataFrame...')
filtered_df = build_filtered_df(raw, terms_set)
print('Saving filtered DataFrame...')
filtered_df.to_csv('filtered.csv', sep=sep, header=header, index=False)
end = time.time()
print(f'Execution time: {end - init:.2f} seconds.')