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

Desenvolver uma abordagem computacional com técnicas clássicas de Processamento Digital de Imagens para identificar automaticamente a ocupação de vagas de estacionamento a partir de imagens obtidas por câmeras fixas.

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

## Acesso ao dataset para reprodução

O conjunto completo do PKLot não é versionado neste repositório. Para obtê-lo, use a versão pública disponibilizada no [Hugging Face](https://huggingface.co/datasets/Voxel51/PKLot). O repositório contém uma amostra em `images/input/`; ela pode ser usada para conferir a estrutura local sem baixar o conjunto completo.

Uma forma de baixar e carregar os dados e suas anotações é usar o FiftyOne:

```bash
python -m pip install -U fiftyone "huggingface-hub>=0.20.0"
```

Em seguida, execute este código Python na máquina em que os experimentos serão reproduzidos:

```python
import fiftyone as fo
from fiftyone.utils.huggingface import load_from_hub

# Load the dataset
# Note: other available arguments include 'max_samples', etc
dataset = load_from_hub("Voxel51/PKLot")

# Launch the App
session = fo.launch_app(dataset)
session.wait()
```

O comando instala o FiftyOne. O código carrega o dataset PKLot pela plataforma Hugging Face e abre o FiftyOne App, onde é possível explorar as imagens e suas anotações. O objeto `dataset` também fica disponível no Python para uso nos experimentos. Consulte a página do dataset para obter detalhes sobre os campos e as anotações.

# Estágio atual do projeto

O projeto está em evolução para a etapa M2, com foco em uma implementação parcial executável e em validação experimental de técnicas clássicas de processamento de imagens para ocupação de vagas.

# Resposta ao feedback da M1 e evolução para a M2

A proposta original foi mantida em sua ideia central: analisar vagas conhecidas em câmeras fixas por comparação entre uma imagem atual e uma imagem de referência. Os principais ajustes foram:

1. Escopo focado: a etapa de detecção automática de vagas foi retirada da prioridade da M2. Em vez disso, a análise será aplicada sobre regiões previamente conhecidas, usando coordenadas ou metadados do conjunto de dados. Essa decisão reduz ambiguidades e permite avaliar a classificação da ocupação com maior controle experimental.
2. Reprodutibilidade e controle de dados: o conjunto completo do PKLot não será versionado no repositório. A proposta passa a manter uma amostra representativa e instruções de acesso ao dataset para reprodução.
3. Avaliação comparativa: o projeto agora prevê pelo menos duas configurações controladas, com variação explícita de parâmetros ou de técnica (por exemplo, diferença absoluta com e sem morfologia, ou limiar global e limiar adaptativo), de modo a medir quantitativamente a qualidade da resposta.

Essas mudanças estão alinhadas aos pontos levantados no feedback da M1, especialmente no que diz respeito a escopo, documentação e reprodução do experimento.

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

[https://youtube.com ...](https://youtu.be/s6ykhlP6b3k)

# Link para documentação adicional existente no próprio repositório

[proposta](docs/proposta.md)