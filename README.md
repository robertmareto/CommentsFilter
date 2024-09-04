# Data Filtering Script

Este script em Python filtra dados de um arquivo CSV com base em termos fornecidos em um arquivo JSON. Ele é útil para processar dados de redes sociais, como Twitter e Instagram, e extrair linhas que contenham termos específicos, fornecendo um dataset filtrado como resultado.

Optamos por usar a Trie para otimizar o processamento do filtro para reduzir a complexidade das operações de comparação

## Funcionalidades

-   Filtra dados de um CSV com base em termos fornecidos em um JSON.
-   Oferece suporte para arquivos de dados de Twitter e Instagram, com colunas personalizadas.
-   Permite selecionar o arquivo CSV e JSON diretamente no terminal.
-   Suporta a escolha entre filtro por texto ou por nome de usuário.
-   Salva os dados filtrados em um novo arquivo CSV.

## Requisitos

-   Python 3.7 ou superior
-   Pandas
-   Unidecode

Instale as dependências utilizando o seguinte comando:

bash

Copiar código

`pip install -r requirements.txt` 

## Como usar

1.  **Clonar o repositório:**
    
    bash
    
    Copiar código
    
    `git clone https://github.com/robertmareto/CommentsFilter.git
    cd CommentsFilter` 
    
2.  **Execute o script:**
    
    bash
    
    Copiar código
    
    `python csv_filter_v2.py` 
    
    O script irá solicitar que você escolha a rede social, o tipo de filtro, e os arquivos JSON e CSV a serem utilizados. Siga as instruções no terminal para fazer as seleções.
    
3.  **Resultado:**
    
    O arquivo filtrado será salvo no diretório atual com o nome `filtered.csv`.
    

## Exemplo de Uso

### Estrutura do JSON de termos:

json

Copiar código

`[
    "termo1",
    "termo2",
    ["termo3", "termo4"]
]` 

### Estrutura do CSV:

O CSV deve conter colunas específicas dependendo da rede social selecionada:

-   **Twitter:** `Tweet Text`, `Username`, `Retweets`, `Comments`, `Favorites`, `Author Favorites`, `Author Followers`, `Author Friends`
-   **Instagram:** `Caption`, `Username`, `Likes`, `Comments`, `Video View Count`

## Desempenho

O script inclui uma funcionalidade de benchmarking que exibe o tempo total de execução e o número de linhas processadas.

## Estrutura do Código

-   **`list_files(directory:str) -> list`**: Lista todos os arquivos em um diretório.
-   **`_file_menu(filetype:str, directory:str=os.getcwd()) -> str`**: Menu para escolher um arquivo.
-   **`menu() -> tuple`**: Menu para escolher as opções de filtro.
-   **`build_set(term_file:str) -> set`**: Constrói um conjunto de termos a partir de um arquivo JSON.
-   **`build_filtered_df(raw: DataFrame, terms_set: set, row_name: str) -> DataFrame`**: Filtra o DataFrame com base nos termos fornecidos.


## Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para enviar issues ou pull requests.

## Agradecimentos

Obrigado ao @GabrielZuany pela otimização com o Trie.py e refatoração geral do codigo