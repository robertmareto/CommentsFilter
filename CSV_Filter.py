import csv
import json
import re
from unidecode import unidecode
import os
import time

INCORRECT_FILE_FORMAT = 1
INVALID_VALUE_SELECTED = 2
FILE_NOT_FOUND = 3
PROCESSING_ERROR = 4

# Função para listar os arquivos do diretório
def list_files(directory):
    try:
        files = os.listdir(directory)
        for i, file in enumerate(files):
            print(f"{i+1}. {file}")
        return files
    except FileNotFoundError:
        print(f"O diretório '{directory}' não foi encontrado.")
        return []

# Função para criar expressões regulares a partir dos termos
def create_regex_pattern(term):
    term_normalized = unidecode(term)
    pattern = r'(?<!\w)' + re.escape(term_normalized) + r'(?!\w)'
    return re.compile(pattern, re.IGNORECASE)

# Função para extrair o shortcode da URL
def extract_shortcode(url):
    match = re.search(r'/p/([^/]+)/', url)
    return match.group(1) if match else ''

# Função para verificar se pelo menos um termo está presente no Caption e retorna os termos encontrados
def find_matching_terms(caption, terms):
    caption_normalized = unidecode(caption).lower()
    matching_terms = []
    for term in terms:
        if isinstance(term, str):
            regex = create_regex_pattern(term)
            if regex.search(caption_normalized):
                matching_terms.append(term)
        elif isinstance(term, list):
            if all(create_regex_pattern(t).search(caption_normalized) for t in term):
                matching_terms.append(' & '.join(term))
    return matching_terms

# Pergunta a rede social a ser filtrada
print("Escolha a rede social a ser filtrada:")
print("1. Twitter")
print("2. Instagram")
print("3. Nome de Coluna personalizado", end='\n')
choice = input("Digite o número da opção desejada: ")

if choice == '1':
    row_name_social = 'Tweet Text'
    row_name_user = 'Username'
elif choice == '2':
    row_name_social = 'Caption'
    row_name_user = 'Username'
    filter_instagram = True
elif choice == '3':
    row_name_social = input("Digite o nome da coluna personalizada: ")
    row_name_user = input("Digite o nome da coluna de nome de usuário: ")
else:
    print("\n============= E R R O R ==============\nEscolha inválida.\n")
    exit(INVALID_VALUE_SELECTED)

## Pergunta se quer filtrar o texto ou o nome do usuário
print("Escolha o tipo de filtro:")
print("1. Filtro por texto")
print("2. Filtro por nome de usuário", end='\n')
choiceType = input("Digite o número da opção desejada: ")

if choiceType == '1':
    row_name = row_name_social
elif choiceType == '2':
    row_name = row_name_user
else:
    print("\n============= E R R O R ==============\nEscolha inválida.")
    exit(INVALID_VALUE_SELECTED)

# Obtém o diretório atual de trabalho
directory = os.getcwd()

# Pergunta o nome do arquivo ou lista os arquivos do diretório
file_name = input("Digite o nome do arquivo JSON ('?' para listar): ")

if file_name == '?':
    files = list_files(directory)
    if files:
        file_index = input("Selecione o número do arquivo desejado: ")
        try:
            #Arquivo precisa ser um arquivo JSON
            if not files[int(file_index) - 1].endswith('.json'):
                print("\n============= E R R O R ==============\nO arquivo selecionado não é um arquivo JSON.\n")
                exit(INCORRECT_FILE_FORMAT)

            file_name = files[int(file_index) - 1]
        except (IndexError, ValueError):
            print("\n============= E R R O R ==============\nNúmero de arquivo inválido.\n")
            exit(INVALID_VALUE_SELECTED)
elif not file_name.endswith('.json'):
    print("============= E R R O R ==============\nO arquivo precisa ser um arquivo JSON.\n")
    exit(INCORRECT_FILE_FORMAT)

# Pergunta o nome do arquivo ou lista os arquivos do diretório
CSVfile_name = input("Digite o nome do arquivo CSV ('?' para listar)")
if CSVfile_name == '?':
    files = list_files(directory)
    if files:
        file_index = input("Selecione o número do arquivo desejado: ")
        try:
            # Arquivo precisa ser um arquivo CSV
            if not files[int(file_index) - 1].endswith('.csv'):
                print("\n============= E R R O R ==============\nO arquivo selecionado não é um arquivo CSV.\n")
                exit(INCORRECT_FILE_FORMAT)
            CSVfile_name = files[int(file_index) - 1]
        except (IndexError, ValueError):
            print("\n============= E R R O R ==============\nNúmero de arquivo inválido.\n")
            exit(INVALID_VALUE_SELECTED)
elif not CSVfile_name.endswith('.csv'):
    print("\n============= E R R O R ==============\nO arquivo precisa ser um arquivo CSV.")
    exit(INCORRECT_FILE_FORMAT)

# Carrega os termos de validação do arquivo JSON
term_file = os.path.join(directory, file_name)
CSVfile = os.path.join(directory, CSVfile_name)

if not os.path.isfile(term_file):
    print(f"\nO arquivo '{term_file}' não foi encontrado.\n")
    exit(FILE_NOT_FOUND)

if not os.path.isfile(CSVfile):
    print(f"\nO arquivo '{CSVfile}' não foi encontrado.\n")
    exit(FILE_NOT_FOUND)

init_time = time.time()
with open(term_file, 'r', encoding='utf-8') as json_file:
    terms = json.load(json_file)
    term_set = set()
    # Adiciona os termos ao conjunto
    for term in terms:
        if isinstance(term, list):
            for t in term:
                term_set.add(t)
        else:
            term_set.add(term)

# Lê o arquivo CSV e filtra as linhas
input_csv = CSVfile
CSVfileName = CSVfile.split('.csv')[0]
filtered_csv = f'{CSVfileName}_filtered.csv'

if not os.path.isfile(input_csv):
    print(f"\n============= E R R O R ==============\nO arquivo '{input_csv}' não foi encontrado.")
    exit(FILE_NOT_FOUND)

print("Executando leitura de CSV...\n")
with open(input_csv, 'r', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    total_rows = 0
    filtered_rows = 0
    rows = []

    for row in reader:
        total_rows += 1
        try:
            row[row_name]
        except KeyError:
            print(f"\n============= E R R O R ==============\nColuna '{row_name}' não encontrada no arquivo CSV.\n")
            exit(PROCESSING_ERROR)
        matching_terms = find_matching_terms(row[row_name], term_set)
        if matching_terms:
            if 'filter_instagram' in locals() and filter_instagram:
                row['Shortcode'] = extract_shortcode(row.get('URL', ''))
                # print(f"shortCode extraído: {row['Shortcode']} para URL: {row.get('URL', '')}")
            row['MatchTerm'] = ', '.join(matching_terms)
            # print(f"Termos encontrados: {row['MatchTerm']}")
            rows.append(row)
            filtered_rows += 1
    print(f"\nTotal de linhas processadas: {total_rows}")
    print(f"Total de linhas filtradas: {filtered_rows}", end = '\n')

# Escreve o CSV filtrado de volta para o arquivo
print("Escrevendo arquivo de saída...\n")
if rows:
    with open(filtered_csv, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = rows[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n============= F I L T R A D O ==============\nArquivo filtrado salvo como: {filtered_csv}\n")
else:
    print("Nenhuma linha corresponde aos termos fornecidos.")

end_time = time.time()
print(f"time taken: {end_time - init_time}s")