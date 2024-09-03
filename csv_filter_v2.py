import pandas as pd
from pandas import DataFrame
import json
from unidecode import unidecode
import re
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
        elif choice == '2':
            row_name_social = 'Caption'
            row_name_user = 'Username'
        elif choice == '3':
            row_name_social = input("Digite o nome da coluna personalizada: ")
            row_name_user = input("Digite o nome da coluna de nome de usuário: ")
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
        elif choiceType == '2':
            row_name = row_name_user
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
    return row_name, terms_file, dataset_file
    
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
                    term_set.add(t)
            else:
                term_set.add(term)
    return term_set

def build_filtered_df(raw:DataFrame, terms_set:set, row_name:str) -> DataFrame:
    """Find all the matching terms in a Dataframe row.
    - Complexity: O(n^2) -> O(n) for each row.
    - Input: 
        - raw (DataFrame) -> raw DataFrame.
        - terms_set (set) -> set of terms.
        - row_name (str) -> name of the column to be filtered.
    - Output: 
        - filtered_df (DataFrame) -> filtered DataFrame.
    """
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
   
if  __name__ == '__main__':
    row_name, terms_file, dataset_file = menu()
    init = time.time() # benchmarking
    raw = pd.read_csv(dataset_file, sep=',')
    terms_set = build_set(terms_file)
    print('Building filtered DataFrame...')
    filtered_df = build_filtered_df(raw, terms_set, row_name)
    filtered_df.to_csv('filtered.csv', sep=',', header=True, index=False)
    print(f'Execution time: {time.time() - init :.2f} seconds.')