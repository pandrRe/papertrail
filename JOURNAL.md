## 1

A primeira versão do projeto Papertrail foi feita com duas funcionalidades em mente:

- Busca de autores por tema, com classificação por relevância em relação ao tema de seus artigos e um resumo em IA generativa de seus trabalhos na área.
- Busca de artigos por tema.

A maior falha é a dependência de dados do Google Scholar, que não fornece banco de dados aberto ou API para integração.
Assim, dependemos de uma biblioteca `scholarly` que depende de scraping para fazer a pesquisa.
Além da lentidão e impossibilidade de carregar a base de dados completa, um dos problemas foi a limitação na pesquisa por autor:
mesmo pesquisando por tema, o autor só irá constar se o assunto estiver escrito em seu perfil, mesmo que já tenha trabalhado com o tema.

A implementação técnica era:

Conteúdo da pesquisa -> buscar autores por termo -> carregar artigos dos autores -> classificar os artigos por relevância -> gerar resumo com base em top K artigos -> retornar
-> buscar artigos por termo -> retornar

## 2

A partir disso, o projeto mudou para se integrar com bases de dados alternativas. Por final, identificamos que o OpenAlex, um projeto
de acesso livre à conteúdo científico, se identificou como o ideal a ser usado neste projeto pela quantidade de dados, fontes e quantidade
de dimensões dos dados como por exemplo nacionalidade dos autores.

Primeiro, foi necessário fazer o download da base comprimida (cerca de ~350 GB). Pelo tamanho da base, foram feitas técnicas de otimização e filtragem
para reduzir o tamanho da base descomprimida. Para este estudo, trabalha-se apenas com artigos das áreas de engenharia e ciência da computação com
relevância média para alta (inclui-se também livros).

## 3

Decidi como vai ser.
Vamos manter o cache por pesquisa.
O caminho completo é:

- Sempre bater primeiro no cache completo.
- Se o cache já expirou, recolhemos o cache do Google Scholar que deve viver mais.
- Vamos transformar a pesquisa feita em embedding e encontrar os tópicos relevantes via semantic search
  no DuckDB.
- Pegamos top autores que trabalham naquele tópico e vamos ranquear. Devemos pesar em que posição o tópico
  aparece na lista de tópicos por autor.
- Com os autores em mãos, vamos pegar a lista de artigos em que trabalharam.
