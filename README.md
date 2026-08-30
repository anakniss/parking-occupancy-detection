# Parking Occupancy PDI

### Integrantes
 * Ana Clara Kniss
 * Gustavo Cezar Marquez
 * Mariana Ferreira

# Problema Investigado

O problema tratado neste projeto foca na identificação automática de vagas livres e ocupadas em estacionamentos a partir de imagens obtidas por câmeras fixas, utilizando técnicas clássicas de Processamento Digital de Imagens.
Inicialmente, o projeto será delimitado à análise de vagas previamente identificadas nas imagens, permitindo que o foco esteja na identificação de sua ocupação.

# Contexto de aplicação

A identificação automática de vagas disponíveis pode ser aplicada em estacionamentos de locais com grande fluxo de veículos, como universidades, shopping centers, aeroportos e hospitais.

Um sistema capaz de analisar imagens de estacionamento e informar o estado de ocupação das vagas poderia auxiliar motoristas na identificação de vagas disponíveis, além de possibilitar o monitoramento da ocupação do estacionamento.

A utilização de técnicas clássicas, possivelmente mais leves que técnicas de IA, pode facilitar a implementação de sistemas semelhantes sem um custo tão elevado quanto o de sistemas que utilizam IA.

# Objetivo geral

Desenvolver uma solução baseada em técnicas de Processamento Digital de Imagens capaz de identificar se uma vaga de estacionamento está ocupada ou disponível a partir de imagens.

# Visão resumida da solução proposta

A solução proposta consiste em utilizar técnicas de Processamento Digital de Imagens para analisar imagens de estacionamentos e identificar se suas vagas estão ocupadas ou disponíveis.

Inicialmente, as vagas presentes nas imagens serão identificadas previamente, para que cada uma possa ser analisada individualmente. Serão testadas diferentes técnicas de processamento para verificar quais conseguem diferenciar uma vaga ocupada de uma vaga vazia.

Ao final, o sistema deverá informar o estado de ocupação de cada vaga analisada.

# Conjunto ou origem das imagens

O dataset utilizado é composto por 12.416 imagens de estacionamento, distribuídas entre três conjuntos provinientes de universidades diferentes:

* PUCPR: 4.474 imagens;
* UFPR04: 3.791 imagens;
* UFPR05: 4.152 imagens.

O dataset é público e foi encontrado a partir do seguinte artigo:

Almeida, P., Oliveira, L. S., Silva Jr, E., Britto Jr, A., Koerich, A., PKLot – A robust dataset for parking lot classification, Expert Systems with Applications, 42(11):4937-4949, 2015.


# Estágio atual do projeto

O projeto está na fase de concepção e validação da relevância da problemática, assim como da viabilidade das soluções propostas.

# Organização do repositório

O repositório está organizado da seguinte forma:

- `README.md`: apresentação geral do projeto e informações para navegação no repositório.
- `docs/`: documentação detalhada do projeto, incluindo a proposta técnica.
- `images/`: dataset de imagens utilizadas nos experimentos e resultados obtidos.
- `src/`: códigos-fonte desenvolvidos para o processamento das imagens.

# Tecnologias previstas ou já utilizadas

- Python
- OpenCV
- Git / Github

# Instruções para reproduzir experimentos existentes, quando houver

Não tem...

# Link para o vídeo da M1

https://youtube.com ...

# Link para documentação adicional existente no próprio repositório

[proposta](docs/proposta.md)