import re
import pandas as pd
from pandas import DataFrame
import json
from unidecode import unidecode
import time
import os

from Trie import Trie

def list_files(directory:str) -> list:
    """List all files in the current directory.
    - Complexity: O(n)
    - Input: 
        - directory (str) -> path to the directory.
    - Output: 
        - files (list) -> list of files in the directory.
    """
    files = []
    for file in os.listdir(directory):
        if os.path.isfile(file):
            files.append(file)
    return files

def _file_menu(filetype:str, directory:str=os.getcwd()) -> str:
    """Menu to choose a file.
    - Complexity: O(1)
    - Input: 
        - filetype (str) -> type of file to be selected.
        - directory (str) -> path to the directory.
    - Output: 
        - file_name (str) -> name of the file.
    """
    print(f"Digite o nome do arquivo {filetype} ('?' para listar): ")
    file_name:str = input()
    if file_name == '?':
        files:list = list_files(directory)
        if files:
            for index, file in enumerate(files):
                print(f"{index + 1}. {file}")
            file_index:str = input("Selecione o número do arquivo desejado: ")
            try:
                selected_file:str = files[int(file_index) - 1]
                if not selected_file.endswith(f'.{filetype}'):
                    print(f"\n============= E R R O R ==============\nO arquivo selecionado não é um arquivo {filetype}.\n{selected_file}\n")
                    return None
                file_name = selected_file
            except (IndexError, ValueError):
                print("\n============= E R R O R ==============\nNúmero de arquivo inválido.\n")
                return None
    elif not file_name.endswith(f'.{filetype}'):
        print(f"============= E R R O R ==============\nO arquivo precisa ser um arquivo {filetype}.\n")
        return None
    return file_name

def menu() -> tuple:
    """Menu to choose the filtering options.
    - Complexity: O(1)
    - Output: 
        - row_name (str) -> name of the column to be filtered.
        - terms_file (str) -> path to the JSON file.
        - dataset_file (str) -> path to the CSV file.
    """
    print("Escolha a rede social a ser filtrada:")
    print("1. Twitter")
    print("2. Instagram")
    print("3. Nome de Coluna personalizado", end='\n')
    choice = -1

    while choice not in ['1', '2', '3']:
        choice = input("Digite o número da opção desejada: ")
        if choice == '1':
            row_name_social = 'Tweet Text'
            row_name_user = 'Username'
            metadata_columns = ['Retweets', 'Comments', 'Favorites', 'Author Favorites', 'Author Followers', 'Author Friends']
        elif choice == '2':
            row_name_social = 'Caption'
            row_name_user = 'Username'
            metadata_columns = ['Likes', 'Comments', 'Video View Count']

        elif choice == '3':
            row_name_social = input("Digite o nome da coluna personalizada: ")
            row_name_user = input("Digite o nome da coluna de nome de usuário: ")
            metadata_columns = []
        else:
            print("Por favor, escolha uma opção válida.")
    
    choiceType = -1
    while choiceType not in ['1', '2']:
        print("Escolha o tipo de filtro:")
        print("1. Filtro por texto")
        print("2. Filtro por nome de usuário", end='\n')
        choiceType = input("Digite o número da opção desejada: ")
        if choiceType == '1':
            row_name = row_name_social
            post_only = bool(False)
        elif choiceType == '2':
            row_name = row_name_user
            post_only = bool(True)
        else:
            print("Por favor, escolha uma opção válida.")
    
    directory = os.getcwd()
    json_file = None
    csv_file = None
    while json_file == '?' or json_file is None or not json_file.endswith('.json'):
        json_file = _file_menu('json')
        if json_file is None:
            print("Por favor, escolha um arquivo válido.")
        else: break

    while csv_file == '?' or csv_file is None or not csv_file.endswith('.csv'):
        csv_file = _file_menu('csv')
        if csv_file is None:
            print("Por favor, escolha um arquivo válido.")
        else: break

    terms_file = os.path.join(directory, json_file)
    dataset_file = os.path.join(directory, csv_file)
    return row_name, terms_file, dataset_file, metadata_columns, post_only
    
def build_set(term_file:str) -> set:
    """Build a set of terms from a JSON file.
    - Complexity: O(n)
    - Input: 
        - term_file (str) -> path to the JSON file.
    - Output: 
        - term_set (set) -> set of terms.
    """
    with open(term_file, 'r', encoding='utf-8') as json_file:
        terms = json.load(json_file)
        term_set:set = set()
        for term in terms:
            if isinstance(term, list):
                for t in term:
                    term_set.add(t.strip())
            else:
                term_set.add(term.strip())
    return term_set

def build_list(term_file:str) -> list:
    """Build a list of terms from a JSON file.
    - Complexity: O(n)
    - Input: 
        - term_file (str) -> path to the JSON file.
    - Output: 
        - term_list (list) -> list of terms.
    """
    with open(term_file, 'r', encoding='utf-8') as json_file:
        terms = json.load(json_file)
        term_list:list = list()
        for term in terms:
            term_list.append(term)
    return term_list

def build_filtered_df(raw: pd.DataFrame, terms_list: list, row_name: str, metadata_columns: list, post_only: bool) -> pd.DataFrame:
    """Find all the matching terms in a DataFrame row.
    - Complexity: O(n^2) -> O(n) for each row.
    - Input: 
        - raw (DataFrame) -> raw DataFrame.
        - terms_list (list) -> list of terms.
        - row_name (str) -> name of the column to be filtered.
    - Output: 
        - filtered_df (DataFrame) -> filtered DataFrame.
    """
    matching_terms = []
    raw['MatchTerm'] = None

    # Preencher NaN com 0 e converter para int nas colunas de metadados
    for col in metadata_columns:
        if col != 'null':
            raw[col] = raw[col].fillna(0).astype(int)

    # Convert the set of terms to lowercase
    normalized_terms = []
    for term in terms_list:
        if isinstance(term, list):
            normalized_terms.append([unidecode(t.lower()) for t in term])
        else:
            normalized_terms.append(unidecode(term.lower()))

    for index, row in raw.iterrows():
        if post_only and row['Type'] != 'Post':
            raw.at[index, 'MatchTerm'] = 'Comment dont delete'
            #print(f"Skipping row {index} as it is not a Post")
            continue  # Continue to the next row

        # Normalize and split the row text
        words = [unidecode(word.lower()) for word in row[row_name].split()]
        for i, word in enumerate(words):
            words[i] = re.sub(r'[^a-zA-Z0-9#@_]', '', word)
       
        if not words:
            continue
        first_word = words[0]

        # Build the trie with the post words
        tst = Trie(first_word)
        for word in words[1:]:
            tst.append(word)

        # Check if the terms set contains all of the words in the post
        for term in normalized_terms:
            contain_all = True
            if isinstance(term, list):
                match_words = []  # List of matched words
                for t in term:
                    if not tst.__contains__(t):
                        contain_all = False
                        break

                if contain_all:
                    same_order = True
                    # Check if all terms are in the same order
                    first_token_order = words.index(term[0])
                    second_token_order = words.index(term[1])
                    if second_token_order < first_token_order:
                        same_order = False
                    if same_order:
                        matching_terms.append(', '.join(term))

            elif tst.__contains__(term):
                matching_terms.append(term)
        if matching_terms:
            matching_terms = list(set(matching_terms))
            raw.at[index, 'MatchTerm'] = matching_terms
        del tst
        matching_terms = []

    # Filter out the rows where 'MatchTerm' is NaN
    filtered_df = raw[raw['MatchTerm'].notnull()]

    if post_only:
        # Get Tweet IDs of the filtered Posts
        tweet_ids = filtered_df.loc[filtered_df['Type'] == 'Post', 'Tweet ID (click to view url)'].tolist()
        
        # Filter out Comments with SourcePostId matching any of the Tweet IDs
        comments_to_remove = raw[(raw['Type'] == 'Comment') & (raw['SourcePostId'].isin(tweet_ids))]
        
        # Print the IDs of comments being removed
        for comment_id in comments_to_remove['SourcePostId'].unique():
            print(f"Removing Comment with SourcePostId: {comment_id}")
        
        # Remove Comments that are associated with the Tweet IDs
        filtered_df = filtered_df[~((filtered_df['Type'] == 'Comment') & (filtered_df['SourcePostId'].isin(tweet_ids)))]

    return filtered_df
   
if  __name__ == '__main__':
    row_name, terms_file, dataset_file, metadata_columns, post_only = menu()
    init = time.time() # benchmarking
    raw = pd.read_csv(dataset_file, sep=',')
    terms_list = build_list(terms_file)
    print('Filtrando...')
    filename = dataset_file.split('/')[-1].split('.')[0]
    filtered_df = build_filtered_df(raw, terms_list, row_name, metadata_columns, post_only)
    filtered_df.to_csv(f'{filename}_filtered.csv', sep=',', header=True, index=False)
    print(f'Tempo de execução: {time.time() - init :.2f} segundos.\nTotal de linhas no dataset: {len(raw)}\nTotal de linhas filtradas: {len(filtered_df)}')