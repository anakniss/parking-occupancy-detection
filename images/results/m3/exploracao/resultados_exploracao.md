# Explorações no desenvolvimento (gerado por `src/explore_dev.py`)

Arquivo gerado automaticamente; não edite à mão. Só dias de desenvolvimento; parâmetros de `models/sistema_final_m3.json`. Classe positiva = vaga ocupada.

## X1 — Ganho estimado nas vagas livres

| Variante | Grupo | n | FP | FN | F1 | Especificidade | EMA contagem |
|---|---|---|---|---|---|---|---|
| adaptativa | dev · dia 2013-04-13 | 5431 | 8 | 45 | 0,973 | 0,998 | 0,390 |
| adaptativa | dev · dia 2013-04-14 | 5440 | 65 | 4 | 0,985 | 0,979 | 0,493 |
| adaptativa | dev · dia 2013-04-16 | 2079 | 7 | 12 | 0,995 | 0,979 | 0,327 |
| adaptativa | dev · 2013-04-13 (Cloudy) | 4231 | 8 | 36 | 0,977 | 0,998 | 0,415 |
| adaptativa | dev · 2013-04-13 (Rainy) | 1200 | 0 | 9 | 0,609 | 1,000 | 0,300 |
| adaptativa | dev · 2013-04-14 (Cloudy) | 2200 | 0 | 1 | 0,999 | 1,000 | 0,018 |
| adaptativa | dev · 2013-04-14 (Sunny) | 3240 | 65 | 3 | 0,983 | 0,950 | 0,815 |
| adaptativa | dev · 2013-04-16 (Sunny) | 2079 | 7 | 12 | 0,995 | 0,979 | 0,327 |
| adaptativa | dev · condição Sunny | 5319 | 72 | 15 | 0,988 | 0,956 | 0,624 |
| adaptativa | dev · condição Cloudy | 6431 | 8 | 37 | 0,983 | 0,998 | 0,280 |
| adaptativa | dev · condição Rainy | 1200 | 0 | 9 | 0,609 | 1,000 | 0,300 |
| adaptativa | dev · total | 12950 | 80 | 61 | 0,986 | 0,990 | 0,423 |
| adaptativa + ganho | dev · dia 2013-04-13 | 5431 | 8 | 46 | 0,972 | 0,998 | 0,397 |
| adaptativa + ganho | dev · dia 2013-04-14 | 5440 | 40 | 1 | 0,991 | 0,987 | 0,301 |
| adaptativa + ganho | dev · dia 2013-04-16 | 2079 | 13 | 593 | 0,793 | 0,960 | 11,154 |
| adaptativa + ganho | dev · 2013-04-13 (Cloudy) | 4231 | 8 | 36 | 0,977 | 0,998 | 0,415 |
| adaptativa + ganho | dev · 2013-04-13 (Rainy) | 1200 | 0 | 10 | 0,545 | 1,000 | 0,333 |
| adaptativa + ganho | dev · 2013-04-14 (Cloudy) | 2200 | 0 | 1 | 0,999 | 1,000 | 0,018 |
| adaptativa + ganho | dev · 2013-04-14 (Sunny) | 3240 | 40 | 0 | 0,990 | 0,969 | 0,494 |
| adaptativa + ganho | dev · 2013-04-16 (Sunny) | 2079 | 13 | 593 | 0,793 | 0,960 | 11,154 |
| adaptativa + ganho | dev · condição Sunny | 5319 | 53 | 593 | 0,906 | 0,967 | 4,662 |
| adaptativa + ganho | dev · condição Cloudy | 6431 | 8 | 37 | 0,983 | 0,998 | 0,280 |
| adaptativa + ganho | dev · condição Rainy | 1200 | 0 | 10 | 0,545 | 1,000 | 0,333 |
| adaptativa + ganho | dev · total | 12950 | 61 | 640 | 0,926 | 0,992 | 2,083 |
| dupla | dev · dia 2013-04-13 | 5431 | 1 | 44 | 0,977 | 1,000 | 0,316 |
| dupla | dev · dia 2013-04-14 | 5440 | 19 | 2 | 0,995 | 0,994 | 0,154 |
| dupla | dev · dia 2013-04-16 | 2079 | 6 | 12 | 0,995 | 0,982 | 0,346 |
| dupla | dev · 2013-04-13 (Cloudy) | 4231 | 1 | 36 | 0,981 | 1,000 | 0,330 |
| dupla | dev · 2013-04-13 (Rainy) | 1200 | 0 | 8 | 0,667 | 1,000 | 0,267 |
| dupla | dev · 2013-04-14 (Cloudy) | 2200 | 0 | 1 | 0,999 | 1,000 | 0,018 |
| dupla | dev · 2013-04-14 (Sunny) | 3240 | 19 | 1 | 0,995 | 0,985 | 0,247 |
| dupla | dev · 2013-04-16 (Sunny) | 2079 | 6 | 12 | 0,995 | 0,982 | 0,346 |
| dupla | dev · condição Sunny | 5319 | 25 | 13 | 0,995 | 0,985 | 0,286 |
| dupla | dev · condição Cloudy | 6431 | 1 | 37 | 0,985 | 1,000 | 0,224 |
| dupla | dev · condição Rainy | 1200 | 0 | 8 | 0,667 | 1,000 | 0,267 |
| dupla | dev · total | 12950 | 26 | 58 | 0,992 | 0,997 | 0,253 |
| dupla + ganho | dev · dia 2013-04-13 | 5431 | 0 | 45 | 0,977 | 1,000 | 0,331 |
| dupla + ganho | dev · dia 2013-04-14 | 5440 | 23 | 11 | 0,993 | 0,993 | 0,250 |
| dupla + ganho | dev · dia 2013-04-16 | 2079 | 5 | 493 | 0,835 | 0,985 | 9,385 |
| dupla + ganho | dev · 2013-04-13 (Cloudy) | 4231 | 0 | 36 | 0,981 | 1,000 | 0,340 |
| dupla + ganho | dev · 2013-04-13 (Rainy) | 1200 | 0 | 9 | 0,609 | 1,000 | 0,300 |
| dupla + ganho | dev · 2013-04-14 (Cloudy) | 2200 | 0 | 1 | 0,999 | 1,000 | 0,018 |
| dupla + ganho | dev · 2013-04-14 (Sunny) | 3240 | 23 | 10 | 0,992 | 0,982 | 0,407 |
| dupla + ganho | dev · 2013-04-16 (Sunny) | 2079 | 5 | 493 | 0,835 | 0,985 | 9,385 |
| dupla + ganho | dev · condição Sunny | 5319 | 28 | 503 | 0,923 | 0,983 | 3,917 |
| dupla + ganho | dev · condição Cloudy | 6431 | 0 | 37 | 0,986 | 1,000 | 0,230 |
| dupla + ganho | dev · condição Rainy | 1200 | 0 | 9 | 0,609 | 1,000 | 0,300 |
| dupla + ganho | dev · total | 12950 | 28 | 549 | 0,940 | 0,996 | 1,750 |

Ganho aplicado à referência adaptativa (mínimo, mediana e máximo por dia):

| Dia | Variante | Mínimo | Mediana | Máximo |
|---|---|---|---|---|
| 2013-04-13 | adaptativa + ganho | 0,874 | 0,999 | 1,141 |
| 2013-04-13 | dupla + ganho | 0,874 | 0,999 | 1,141 |
| 2013-04-14 | adaptativa + ganho | 0,670 | 1,003 | 1,199 |
| 2013-04-14 | dupla + ganho | 0,672 | 1,005 | 1,200 |
| 2013-04-16 | adaptativa + ganho | 0,600 | 0,979 | 1,547 |
| 2013-04-16 | dupla + ganho | 0,652 | 0,985 | 1,384 |

## X2 — Textura sem referência (LBP) x diferença, regressão logística

Validação cruzada deixando um dia de fora; λ = 1,0; limiar de probabilidade pelo maior F1 nos dois dias de treino. Descritores de textura: `lbp0`, `lbp1`, `lbp2`, `lbp3`, `lbp4`, `lbp5`, `lbp6`, `lbp7`, `lbp8`, `lbp9`, `gray_std`, `edge_density`, `croma_atual`.

| Descritores | Dia avaliado | Limiar | VP | FP | FN | VN | F1 | Especificidade |
|---|---|---|---|---|---|---|---|---|
| textura (sem referência) | 2013-04-13 | 0,41 | 882 | 132 | 101 | 4316 | 0,883 | 0,970 |
| textura (sem referência) | 2013-04-14 | 0,48 | 2131 | 230 | 169 | 2910 | 0,914 | 0,927 |
| textura (sem referência) | 2013-04-16 | 0,41 | 1639 | 18 | 113 | 309 | 0,962 | 0,945 |
| textura (sem referência) | todos (agregado) | — | 4652 | 380 | 383 | 7535 | 0,924 | 0,952 |
| diferença (descritores da dupla_LR) | 2013-04-13 | 0,60 | 889 | 2 | 94 | 4446 | 0,949 | 1,000 |
| diferença (descritores da dupla_LR) | 2013-04-14 | 0,65 | 2293 | 38 | 7 | 3102 | 0,990 | 0,988 |
| diferença (descritores da dupla_LR) | 2013-04-16 | 0,56 | 1744 | 12 | 8 | 315 | 0,994 | 0,963 |
| diferença (descritores da dupla_LR) | todos (agregado) | — | 4926 | 52 | 109 | 7863 | 0,984 | 0,993 |
| textura + diferença | 2013-04-13 | 0,62 | 884 | 0 | 99 | 4448 | 0,947 | 1,000 |
| textura + diferença | 2013-04-14 | 0,35 | 2292 | 177 | 8 | 2963 | 0,961 | 0,944 |
| textura + diferença | 2013-04-16 | 0,29 | 1750 | 22 | 2 | 305 | 0,993 | 0,933 |
| textura + diferença | todos (agregado) | — | 4926 | 199 | 109 | 7716 | 0,970 | 0,975 |
