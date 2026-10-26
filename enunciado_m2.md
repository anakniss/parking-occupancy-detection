# Projeto Aplicado Longitudinal — Etapa M2
## Enunciado para os alunos — Processamento de Imagens, 2026-02

## 1. Objetivo e evolução esperada

Na M1, o grupo delimitou um problema, reuniu imagens e investigou uma estratégia. Na M2, deverá transformar essa proposta em uma **implementação parcial executável, com resultados verificáveis e análise técnica**. Código passa a ser obrigatório.

A etapa do projeto em equipe corresponde a **55% da média M2**, conforme o planejamento consolidado. Laboratórios e autoavaliação são instrumentos separados. Os pesos da rubrica deste projeto somam 100% da nota da atividade.

## Condições comuns às etapas

- O trabalho é em equipe, dando continuidade ao mesmo projeto da M1 e ao mesmo repositório público. Mudanças de escopo, dados ou técnicas devem ser justificadas e registradas, preservando o histórico.
- A escolha de linguagem, bibliotecas e ferramentas continua livre. OpenCV e outras implementações prontas podem ser utilizadas; não é exigida implementação dos algoritmos do zero. O grupo deve compreender e explicar as operações utilizadas.
- O repositório é a fonte principal da entrega e deve permanecer público durante o desenvolvimento. Dados que não possam ser redistribuídos devem ter origem, condições de acesso e procedimento de obtenção documentados. Não publiquem credenciais nem dados pessoais sem autorização.
- Textos, código, modelos, imagens e métodos de terceiros devem ter fontes e condições de uso identificadas. Declarem o uso de IA generativa, indicando ferramenta, finalidade, materiais modificados e como foram verificados. O grupo responde pelo conteúdo entregue.
- O README deve identificar projeto e integrantes, problema, objetivos, entradas e saídas, estágio atual, tecnologias, estrutura, dados, instalação, execução, resultados e links para documentação e vídeos.
- Cada integrante deve ter contribuição identificável: implementação, experimentos, dados, documentação, análise ou revisão. Registrem contribuições com evidências; contagem de commits não mede isoladamente a participação.
- Datas, horário e local de submissão serão informados.

## 2. Revisão da proposta e do feedback

Registrem o que foi mantido, corrigido ou substituído desde a M1. Para cada orientação recebida, indiquem a ação tomada ou justifiquem tecnicamente por que adotaram outra solução. Atualizem objetivos, critérios de sucesso e escopo quando necessário. Não basta afirmar que o projeto “evoluiu”: relacionem as mudanças aos arquivos, experimentos e resultados.

## 3. Implementação parcial obrigatória

Entreguem código-fonte ou notebook executável que percorra um fluxo significativo: **entrada → processamento implementado → saída verificável**. Informem o que já funciona e o que permanece planejado. Um script que apenas abre imagens não demonstra o avanço esperado.

O foco da M2 é segmentação, análise de regiões/componentes, morfologia e representação/descrição. Selecionem operações pertinentes ao problema, explicando finalidade, entradas, saídas e parâmetros. Não é necessário usar todas as técnicas estudadas nem acrescentar etapas artificiais. Caso a abordagem escolhida substitua alguma dessas etapas, expliquem como realiza a função correspondente e demonstrem seus resultados.

Exemplos de saídas intermediárias: máscaras, contornos, componentes rotulados, regiões filtradas, imagens após morfologia e tabelas de área, perímetro, cor ou textura. Quando houver extração de características, identifiquem cada atributo, unidade e forma de cálculo. Inferência final ou classificador completo podem permanecer em desenvolvimento, desde que exista plano concreto para a M3.

## 4. Dados e protocolo experimental

Documentem origem, quantidade efetivamente usada, critérios de seleção, características, condições de aquisição e restrições. Identifiquem imagens por nomes ou IDs e incluam situações típicas e difíceis. Justifiquem o tamanho do conjunto em função do escopo; não existe quantidade universal obrigatória.

Definam como verificar os resultados: referência manual, rótulos, máscaras, contagens conhecidas ou outro procedimento adequado. Expliquem quem produziu as referências e seus limites. Quando houver treinamento, diferenciar treino, validação e teste. Para métodos sem treinamento, diferenciar dados usados para ajustar parâmetros daqueles reservados para avaliação final. Imagens muito semelhantes, recortes ou quadros da mesma origem não devem atravessar essas divisões de maneira a favorecer artificialmente os resultados.

## 5. Experimentos mínimos da M2

Apresentem **pelo menos uma comparação controlada entre duas configurações ou métodos**. Ela deve responder a uma pergunta técnica, como: a abertura remove ruído sem perder objetos? O limiar adaptativo melhora regiões com iluminação desigual? Um descritor permite distinguir os objetos de interesse?

Mantenham o conjunto de imagens e o procedimento de avaliação comparáveis; registrem o que mudou e o que permaneceu constante. Uma mudança que piora os resultados também pode produzir uma análise de qualidade.

Para cada experimento, registrem:

1. pergunta e configuração;
2. imagens/IDs utilizados e parâmetros;
3. comando ou procedimento de execução;
4. saídas intermediárias e finais;
5. comparação com a referência e interpretação;
6. pelo menos um caso de sucesso e um caso de falha ou limitação identificada.

Incluam pelo menos um indicador quantitativo pertinente: erro de contagem, proporção de objetos detectados, IoU/Dice com máscaras de referência, erro de medida ou outro indicador justificado. Medir apenas o tempo de execução não substitui avaliar a qualidade da saída. Se a referência ainda estiver incompleta, declarem a avaliação como preliminar e expliquem como será concluída.

## 6. Relatório parcial em Markdown

Atualizem a proposta e incluam um relatório, por exemplo `docs/relatorio_m2.md`, com:

- síntese do problema e objetivos atuais;
- resposta ao feedback e evolução desde a M1;
- dados e protocolo experimental;
- pipeline e organização efetivamente implementados, distinguindo etapas pendentes;
- fundamentação e justificativa das técnicas e parâmetros;
- experimentos, figuras, tabelas, indicadores e análise;
- falhas, limitações e riscos;
- plano de conclusão para a M3, com tarefas, responsáveis e evidências esperadas;
- contribuições dos integrantes, referências e declaração de uso de IA.

Figuras precisam de legendas e interpretação. Não apresentem somente capturas de tela ou listas de funções de biblioteca.

## 7. Execução e organização

Disponibilizem dependências e versões relevantes, preparação do ambiente, comandos de execução e um exemplo mínimo com entrada e saída esperada. Evitem caminhos absolutos específicos de um computador. Notebooks devem permitir execução em ordem, a partir de um ambiente reiniciado, sem depender de variáveis ocultas.

Código, dados, documentação, configurações e resultados devem estar organizados. Não incluam ambientes virtuais, caches ou arquivos temporários desnecessários. Se houver pesos de modelos ou arquivos grandes externos, documentem onde obtê-los e como usá-los. Não versione dataset de terceiros.

## 8. Vídeo da M2

Produzam **vídeo de aproximadamente 10 minutos**, no YouTube como **não listado**, com link no README e participação identificável de todos. Apresentem: evolução desde a M1, dados, pipeline implementado, execução real, saídas intermediárias, comparação experimental, limitações e plano da M3. O vídeo deve mostrar evidências e explicar decisões, além de apresentar slides ou texto.

Não há seminário presencial adicional para a M2.

## 9. Entrega e checklist

Enviem o link do repositório e identifiquem o commit ou tag que representa a entrega M2. A versão indicada deve conter:

- [ ] README atualizado e integrantes identificados;
- [ ] proposta revisada e resposta ao feedback;
- [ ] código parcial executável e dependências;
- [ ] dados ou instruções de obtenção e referência de avaliação;
- [ ] pipeline implementado e etapas pendentes identificadas;
- [ ] comparação entre duas configurações e indicador quantitativo;
- [ ] entradas, saídas intermediárias, resultados e análise de falhas;
- [ ] relatório parcial em Markdown e referências;
- [ ] comandos e exemplo reproduzível;
- [ ] vídeo não listado acessível pelo README;
- [ ] plano da M3 e registro das contribuições;
- [ ] histórico coerente de desenvolvimento.

Ao final, o grupo deverá conseguir demonstrar **o que já executa, quais evidências sustentam suas escolhas e o que precisa concluir na M3**.