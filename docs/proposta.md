# Proposta do Projeto

## Problema
Esse  projeto investiga a identificação automática de vagas livres e ocupadas em estacionamentos a partir de imagens obtidas por câmeras fixas, utilizando técnicas clássicas de Processamento Digital de Imagens.

A situação inicial considerada é a existência de imagens de um mesmo estacionamento capturadas ao longo do temo, com enquadramento fixo e com as regiões correxspondentes às vagas previamente conhecidas. A partir dessas imagens, pretende-se analisar individualmente cada vaga e determinar se ela se encontra livre ou ocupada.

O problema envolve diretamente processamento e análise de imagens, pois a decisão sobre o estado da vaga será obtida a partir da comparação visual entre uma imagem atual e uma imagem de referência da mesma região em estado livre.

Entre os fatores que podem dificultar essa comparação estão:
* variações de iluminação;
* presença de sombras;
* mudanças nas condições climáticas;
* reflexos;
* diferenças de intensidade de pixels;
* veículos com cores similares às do ambientes;
* pequenas alterações visuais entre diferentes momentos de captura.

A proposta inicial consiste em investigar se técnicas como pré-processamento, diferenteça absoluta entre imagens, limiarização e operações morfológicas são suficientes para identificar alterações significativas nas regiões correspondentes às vagas.

A principal questão investiga pelo projeto é:

Como identificar vagas livres e ocupadas em imagens de estacionamentos utilizandos técnicas clássicas de Processamento Digital de Imagens baseadas na comparação entre imagens, considerando variações de iluminação, sombras e condições ambientais?

A partir das classificações individuais, também deverá ser possível obter informações gerais sobre o eestacionamento, como:
* quantidade total de vagas analisadas;
* quantidade de vagas livres;
* quantidade de vagas ocupadas;
* percentual de ocupação do estacionamento.