# M3-A — Instrução do projeto longitudinal final
## Processamento de Imagens — 2026-02

**Modalidade:** em equipe, mantendo a formação do projeto longitudinal, salvo ajuste autorizado pelo professor.  
**Valor:** nota de 0 a 10; peso de **65% da média M3**.  
**Rubrica:** `02_rubrica_M3-A_projeto_longitudinal.md`.  
**Prazo, horário e local de submissão:** a informar pelo professor.

## 1. Objetivo

Consolidar uma solução de processamento de imagens executável, com avaliação experimental, documentação e análise crítica dos resultados, dando continuidade às etapas M1 e M2.

## Condições de realização

- O trabalho é em equipe, dando continuidade ao mesmo projeto da M1 e ao mesmo repositório público. Mudanças de escopo, dados ou técnicas devem ser justificadas e registradas, preservando o histórico.
- A escolha de linguagem, bibliotecas e ferramentas continua livre. OpenCV e outras implementações prontas podem ser utilizadas; não é exigida implementação dos algoritmos do zero. O grupo deve compreender e explicar as operações utilizadas.
- O repositório é a fonte principal da entrega e deve permanecer público durante o desenvolvimento. Dados que não possam ser redistribuídos devem ter origem, condições de acesso e procedimento de obtenção documentados. Não publiquem credenciais nem dados pessoais sem autorização.
- Textos, código, modelos, imagens e métodos de terceiros devem ter fontes e condições de uso identificadas. Declarem o uso de inteligência artificial (IA) generativa, indicando ferramenta, finalidade, materiais modificados, link da conversa quando disponível e como foram verificados. Se não houve uso, registrem essa informação. O grupo responde pelo conteúdo entregue.
- O README deve identificar projeto e integrantes, problema, objetivos, entradas e saídas, estágio atual, tecnologias, estrutura, dados, instalação, execução, resultados e links para documentação e vídeos.
- Cada integrante deve ter contribuição identificável: implementação, experimentos, dados, documentação, análise ou revisão. Registrem contribuições com evidências; contagem de commits não mede isoladamente a participação.
- Datas, horário e local de submissão serão informados pelo professor. Não há penalização adicional por atraso definida nestes documentos; eventual regra deverá ser comunicada previamente.

## 2. Escopo final e integração

Declarem o escopo efetivamente concluído, as mudanças em relação à proposta e o atendimento aos objetivos. A solução deve receber a entrada definida e produzir a informação final prevista: contagem, medida, categoria, máscara, detecção, reconhecimento ou outra saída verificável.

Expliquem o papel do pré-processamento, da segmentação/localização, da representação/descrição e da inferência ou decisão no pipeline adotado. Quando uma etapa não for necessária ou estiver integrada a um modelo, justifiquem essa opção. Não se exige classificador treinado para tarefas em que regras, contagem ou medidas resolvam o problema; tampouco uma interface gráfica ou aplicação comercial.

O resultado pode ter limitações e erros. O requisito é entregar a solução do escopo assumido e analisar honestamente seu desempenho; não é obter uma taxa universal de acerto.

## 3. Dados e avaliação final

Consolidem a documentação dos dados e das referências de avaliação. Identifiquem exatamente as imagens avaliadas, condições e quantidade; expliquem exclusões e limitações de representatividade.

Quando houver aprendizado, documentem treino, validação e teste, incluindo pré-processamentos ajustados aos dados. Ajustem modelos e parâmetros sem utilizar o teste final para selecionar a melhor configuração. Para métodos sem treino, reservem dados de avaliação que não tenham orientado os ajustes sempre que viável. Caso o conjunto reduzido impeça uma separação independente, declarem a avaliação exploratória e limitem as conclusões; não apresentem desempenho de ajuste como generalização comprovada.

## 4. Comparação e contribuição das escolhas

Apresentem **um baseline explícito e pelo menos uma comparação controlada ou ablação**. Baseline é uma solução de referência, como um método simples ou a configuração inicial da M2. Ablação investiga o efeito de remover ou substituir um componente.

Uma comparação entre o baseline e a solução final pode atender aos dois requisitos se isolar uma decisão e responder a uma pergunta técnica. Se vários componentes mudarem simultaneamente, ela compara sistemas, mas não demonstra a contribuição isolada de cada componente.

Usem os mesmos dados de avaliação, referências e critérios. Registrem configurações, parâmetros e resultados. Reavaliem experimentos da M2 quando necessário para assegurar comparabilidade. Não é obrigatório que o método mais complexo ou a versão final supere o baseline; qualidade experimental e interpretação são avaliadas.

## 5. Métricas e análise de erros

Escolham métricas adequadas ao objetivo e expliquem como foram calculadas.

| Tarefa | Evidência quantitativa possível | Evidência visual ou análise complementar |
|---|---|---|
| Segmentação | Interseção sobre união (IoU) ou coeficiente Dice contra máscaras de referência | Sobreposição, objetos perdidos, regiões excedentes |
| Classificação | Matriz de confusão e precisão, revocação ou F1 pertinentes | Erros por classe e efeito do desbalanceamento |
| Contagem | Erro absoluto médio e erros por imagem | Objetos unidos, duplicados ou não detectados |
| Medição/estimativa | Erro em relação à referência, com unidade | Calibração, faixa de valores e fontes de erro |
| Detecção | Precisão e revocação com regra de correspondência explícita | Falsos positivos, perdas e localização |
| Restauração | Erro ou métrica de qualidade com referência adequada | Detalhes preservados e artefatos |

A tabela oferece opções, não exige todas as métricas. Valores sem referência ou sem protocolo não sustentam conclusões. Tempo de execução pode complementar a avaliação, com hardware e condições identificados.

Apresentem tabela consolidada de resultados, exemplos de sucesso e falha, e discutam iluminação, ruído, escala, oclusão ou outras condições relevantes. Se não encontrarem falhas no conjunto avaliado, investiguem situações difíceis e explicitem o alcance limitado dos testes. Relacionem conclusões aos critérios de sucesso e evitem generalizar além dos dados.

## 6. Código e reprodução

Entreguem código-fonte completo do escopo final, configurações, dependências e instruções para reproduzir ao menos um exemplo e a avaliação relatada. Informem sementes aleatórias quando aplicáveis e limitações de hardware ou serviços externos. Modelos necessários devem estar disponíveis ou ter procedimento documentado de obtenção; instruções de treinamento não substituem um modelo necessário à demonstração quando seu treinamento exigir recursos inviáveis ao avaliador.

Incluam os testes ou verificações relevantes ao projeto: leitura das entradas, saídas esperadas, situações de falha e casos de referência. Não se exige framework de testes específico. Imagens e tabelas apresentadas devem ser rastreáveis à versão e configuração utilizadas.

## 7. Relatório final em Markdown

Disponibilizem, por exemplo, `docs/relatorio_final.md`, com:

1. problema, contexto, objetivos e escopo final;
2. fundamentação e fontes;
3. dados, referências e protocolo de avaliação;
4. pipeline final e organização da implementação;
5. justificativa das decisões e parâmetros;
6. baseline, comparação/ablação e procedimento experimental;
7. resultados quantitativos e qualitativos;
8. análise de erros, limitações e ameaças à validade;
9. atendimento aos objetivos, conclusão e melhorias futuras;
10. evolução M1 → M2 → M3 e tratamento do feedback;
11. contribuições dos integrantes e uso de IA generativa;
12. referências e instruções de reprodução, diretamente ou por links internos.

Preservem as versões anteriores ou sua rastreabilidade no Git. O README deve refletir o estado final e permitir navegar pelos materiais sem depender da apresentação.

## 8. Submissão e evidências obrigatórias

Submetam o link do repositório, os nomes dos integrantes e o identificador do commit ou da tag da versão final. Informem o caminho do relatório e das instruções de execução. Confiram os links em uma janela sem autenticação.

| Evidência | O que deve permitir verificar |
|---|---|
| Código, configurações e recursos necessários | Execução do fluxo completo e geração da saída final |
| README atualizado | Identificação, instalação, execução e navegação pelos materiais |
| Relatório final em Markdown | Problema, método, experimento, resultados, análise e conclusão |
| Registro dos dados e referências de avaliação | Origem, acesso, amostras, divisões e referência usada para medir o resultado |
| Baseline e comparação controlada ou ablação | Pergunta técnica, configurações comparáveis e resultados rastreáveis |
| Resultados e exemplos | Métricas adequadas, tabela consolidada, sucessos e falhas |
| Histórico e contribuições | Evolução M1 → M2 → M3, tratamento do feedback e participação dos integrantes |
| Fontes e declaração de IA | Materiais de terceiros identificados e uso ou não uso de IA declarado |

Os slides, o vídeo e a demonstração pertencem à atividade M3-B, com peso de 20%. Eles podem estar no mesmo repositório, mas não compõem uma segunda pontuação de comunicação nesta atividade.

## 9. Checklist final

- [ ] O escopo final e as alterações desde M1/M2 estão explícitos.
- [ ] O fluxo recebe a entrada prevista e gera uma saída verificável.
- [ ] Código, dados ou instruções de obtenção, dependências e modelos estão disponíveis.
- [ ] As instruções permitem executar um exemplo e reproduzir a avaliação.
- [ ] O protocolo diferencia ajuste e avaliação, ou assume claramente seu caráter exploratório.
- [ ] Há baseline e comparação controlada ou ablação, sem exigência de superar o baseline.
- [ ] As métricas têm referência e procedimento de cálculo identificados.
- [ ] Resultados, limitações e conclusões são coerentes com as evidências.
- [ ] Relatório, README, fontes, contribuições e declaração de IA estão atualizados.
- [ ] A versão final está identificada e os links estão acessíveis.

## Composição da média M3

| Atividade | Nota própria | Peso na M3 | Contribuição máxima na M3 |
|---|---:|---:|---:|
| A — Projeto longitudinal final | 0 a 10 | 65% | 6,50 pontos |
| B — Apresentação de resultados | 0 a 10 | 20% | 2,00 pontos |
| C — Autoavaliação individual | 0 a 10 | 15% | 1,50 ponto |
| **Total** | | **100%** | **10,00 pontos** |

**M3 = 0,65 × A + 0,20 × B + 0,15 × C.**

Exemplo: A = 8,00; B = 9,00; C = 10,00 → M3 = 5,20 + 1,80 + 1,50 = **8,50**. As notas A e B são calculadas separadamente, sem nova normalização. A autoavaliação é uma atividade independente; estes documentos não estabelecem suas instruções ou rubrica.