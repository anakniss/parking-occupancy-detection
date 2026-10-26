# Resultados gerados por `src/run_experiments.py`

Arquivo gerado automaticamente; não edite à mão. Classe positiva = vaga ocupada.

## Parâmetros ajustados (dia de ajuste)

| Configuração | Descrição | T | τ | F1 no ajuste | faixa de τ ótimos |
|---|---|---|---|---|---|
| A_sem_morfologia | Diferença absoluta + limiar global; sem morfologia | 20 | 0,24 | 0,992 | 0,24 – 0,24 |
| B_morfologia | A + abertura (disco 3 px) e fechamento (disco 7 px) | 25 | 0,24 | 0,999 | 0,23 – 0,26 |
| C_morfologia_ganho | B + compensação global de ganho (mediana da referência / mediana do quadro) | 25 | 0,24 | 0,999 | 0,23 – 0,25 |

## Indicadores por configuração e grupo de imagens

| Configuração | Grupo | n | VP | FP | FN | VN | Acurácia | Precisão | Revocação | Especificidade | F1 | Acur. balanceada | EMA contagem | Viés contagem | Erro máx. |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A_sem_morfologia | ajuste · 2013-04-14 (Cloudy) | 2200 | 350 | 3 | 3 | 1844 | 0,997 | 0,992 | 0,992 | 0,998 | 0,992 | 0,995 | 0,073 | 0,000 | 1,000 |
| A_sem_morfologia | teste · 2013-04-16 (Sunny) | 2079 | 1740 | 8 | 12 | 319 | 0,990 | 0,995 | 0,993 | 0,976 | 0,994 | 0,984 | 0,346 | -0,077 | 3,000 |
| A_sem_morfologia | teste · 2013-04-13 (Rainy) | 1200 | 11 | 41 | 5 | 1143 | 0,962 | 0,212 | 0,688 | 0,965 | 0,324 | 0,826 | 1,333 | 1,200 | 7,000 |
| A_sem_morfologia | teste · total | 3279 | 1751 | 49 | 17 | 1462 | 0,980 | 0,973 | 0,990 | 0,968 | 0,982 | 0,979 | 0,707 | 0,390 | 7,000 |
| B_morfologia | ajuste · 2013-04-14 (Cloudy) | 2200 | 352 | 0 | 1 | 1847 | 1,000 | 1,000 | 0,997 | 1,000 | 0,999 | 0,999 | 0,018 | -0,018 | 1,000 |
| B_morfologia | teste · 2013-04-16 (Sunny) | 2079 | 1744 | 7 | 8 | 320 | 0,993 | 0,996 | 0,995 | 0,979 | 0,996 | 0,987 | 0,250 | -0,019 | 2,000 |
| B_morfologia | teste · 2013-04-13 (Rainy) | 1200 | 13 | 9 | 3 | 1175 | 0,990 | 0,591 | 0,812 | 0,992 | 0,684 | 0,902 | 0,400 | 0,200 | 4,000 |
| B_morfologia | teste · total | 3279 | 1757 | 16 | 11 | 1495 | 0,992 | 0,991 | 0,994 | 0,989 | 0,992 | 0,992 | 0,305 | 0,061 | 4,000 |
| C_morfologia_ganho | ajuste · 2013-04-14 (Cloudy) | 2200 | 352 | 0 | 1 | 1847 | 1,000 | 1,000 | 0,997 | 1,000 | 0,999 | 0,999 | 0,018 | -0,018 | 1,000 |
| C_morfologia_ganho | teste · 2013-04-16 (Sunny) | 2079 | 1739 | 7 | 13 | 320 | 0,990 | 0,996 | 0,993 | 0,979 | 0,994 | 0,986 | 0,308 | -0,115 | 3,000 |
| C_morfologia_ganho | teste · 2013-04-13 (Rainy) | 1200 | 12 | 0 | 4 | 1184 | 0,997 | 1,000 | 0,750 | 1,000 | 0,857 | 0,875 | 0,133 | -0,133 | 1,000 |
| C_morfologia_ganho | teste · total | 3279 | 1751 | 7 | 17 | 1504 | 0,993 | 0,996 | 0,990 | 0,995 | 0,993 | 0,993 | 0,244 | -0,122 | 3,000 |

EMA contagem = erro médio absoluto do nº de vagas ocupadas por imagem; viés > 0 = superestima.

## Comparações controladas (dias de teste)

| Id | Pergunta | Base → Variante | Erros corrigidos | Erros introduzidos | Comp. por vaga livre (base → var.) | Mediana fração livre (base → var.) | Mediana fração ocupada (base → var.) |
|---|---|---|---|---|---|---|---|
| E1 | A abertura e o fechamento removem ruído da máscara sem perder veículos? | A_sem_morfologia → B_morfologia | 42 | 3 | 1,00 → 0,35 | 0,000 → 0,000 | 0,783 → 0,845 |
| E2 | A compensação global de ganho reduz os falsos positivos causados pela mudança de iluminação entre a referência e o quadro atual? | B_morfologia → C_morfologia_ganho | 13 | 10 | 0,35 → 0,28 | 0,000 → 0,000 | 0,845 → 0,839 |

## Separabilidade dos descritores (B_morfologia, AUC ROC)

| Descritor | Definição / unidade | AUC ajuste | AUC teste |
|---|---|---|---|
| largest_frac | fração da vaga no maior componente (adim.) | 1,0000 | 0,9997 |
| frac_changed | fração da vaga marcada como alterada (adim.) | 1,0000 | 0,9997 |
| mean_diff | média da diferença absoluta na vaga (níveis de cinza) | 0,9994 | 0,9995 |
| n_components | nº de componentes >= área mínima | 0,7872 | 0,8738 |
| largest_solidity | solidez do maior componente (adim.) | 0,8623 | 0,9188 |
| edge_density | densidade de bordas de Canny no quadro atual (adim.) | 0,9305 | 0,8575 |
| gray_std | desvio padrão do cinza no quadro atual (níveis de cinza) | 0,9867 | 0,9601 |

AUC = 0,5 não separa; 1,0 separa perfeitamente (valores < 0,5: o descritor é maior nas vagas livres).

## Casos ilustrados e pior quadro do teste

- **A_sem_morfologia** — pior quadro: `2013-04-13_09_15_03` (7 erros). Casos: Sucesso (VP): 2013-04-16_08_40_03 vaga 2; Sucesso (VN): 2013-04-16_07_05_01 vaga 38; Falha (FP): 2013-04-13_08_25_02 vaga 10; Falha (FN): 2013-04-16_07_15_01 vaga 39.
- **B_morfologia** — pior quadro: `2013-04-13_09_15_03` (4 erros). Casos: Sucesso (VP): 2013-04-16_08_05_02 vaga 7; Sucesso (VN): 2013-04-13_08_50_03 vaga 5; Falha (FP): 2013-04-16_10_40_05 vaga 29; Falha (FN): 2013-04-16_07_15_01 vaga 39.
- **C_morfologia_ganho** — pior quadro: `2013-04-16_07_20_01` (5 erros). Casos: Sucesso (VP): 2013-04-16_08_45_03 vaga 19; Sucesso (VN): 2013-04-13_08_40_03 vaga 29; Falha (FP): 2013-04-16_07_20_01 vaga 32; Falha (FN): 2013-04-16_07_15_01 vaga 39.
