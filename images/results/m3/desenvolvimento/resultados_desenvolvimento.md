# Desenvolvimento da M3 (gerado por `src/run_final.py --etapa desenvolvimento`)

Arquivo gerado automaticamente; não edite à mão. Classe positiva = vaga ocupada.

Dias de desenvolvimento: 2013-04-13, 2013-04-14, 2013-04-16 (324 quadros avaliados).

## Parâmetros escolhidos (ajuste em todo o desenvolvimento)

| Variante | alpha | free_max | τ | faixa de τ ótimos | F1 (dentro da amostra) |
|---|---|---|---|---|---|
| fixa | — | — | 0,43 | 0,43 – 0,43 | 0,932 |
| adaptativa | 0,10 | 0,25 | 0,29 | 0,29 – 0,29 | 0,986 |
| dupla | 0,25 | 0,20 | 0,24 | 0,24 – 0,24 | 0,992 |

Regressão logística (dupla_LR): λ = 1,0, limiar de probabilidade = 0,54.

| Descritor | Peso (padronizado) |
|---|---|
| largest_frac_fix | 0,974 |
| largest_frac_ad | 2,843 |
| mean_diff_fix | 0,287 |
| mean_diff_ad | -0,624 |
| ncc_ad | -2,745 |
| gray_std | 1,316 |
| edge_density | -0,161 |

## Validação cruzada deixando um dia de fora (fora da amostra)

| Variante | Dia avaliado | alpha | free_max | Limiar | VP | FP | FN | VN | F1 | Especificidade |
|---|---|---|---|---|---|---|---|---|---|---|
| fixa | 2013-04-13 | — | 0,00 | 0,35 | 936 | 396 | 47 | 4052 | 0,809 | 0,911 |
| fixa | 2013-04-14 | — | 0,00 | 0,51 | 2123 | 200 | 177 | 2940 | 0,918 | 0,936 |
| fixa | 2013-04-16 | — | 0,00 | 0,43 | 1728 | 3 | 24 | 324 | 0,992 | 0,991 |
| fixa | todos (agregado) | — | — | — | 4787 | 599 | 248 | 7316 | 0,919 | 0,924 |
| adaptativa | 2013-04-13 | 0,10 | 0,20 | 0,29 | 939 | 42 | 44 | 4406 | 0,956 | 0,991 |
| adaptativa | 2013-04-14 | 0,25 | 0,20 | 0,28 | 2299 | 141 | 1 | 2999 | 0,970 | 0,955 |
| adaptativa | 2013-04-16 | 0,10 | 0,25 | 0,29 | 1740 | 7 | 12 | 320 | 0,995 | 0,979 |
| adaptativa | todos (agregado) | — | — | — | 4978 | 190 | 57 | 7725 | 0,976 | 0,976 |
| dupla | 2013-04-13 | 0,25 | 0,20 | 0,24 | 939 | 1 | 44 | 4447 | 0,977 | 1,000 |
| dupla | 2013-04-14 | 0,10 | 0,25 | 0,25 | 2296 | 63 | 4 | 3077 | 0,986 | 0,980 |
| dupla | 2013-04-16 | 0,25 | 0,20 | 0,24 | 1740 | 6 | 12 | 321 | 0,995 | 0,982 |
| dupla | todos (agregado) | — | — | — | 4975 | 70 | 60 | 7845 | 0,987 | 0,991 |
| dupla_LR | 2013-04-13 | 0,25 | 0,20 | 0,60 | 889 | 2 | 94 | 4446 | 0,949 | 1,000 |
| dupla_LR | 2013-04-14 | 0,10 | 0,25 | 0,57 | 2292 | 75 | 8 | 3065 | 0,982 | 0,976 |
| dupla_LR | 2013-04-16 | 0,25 | 0,20 | 0,56 | 1744 | 12 | 8 | 315 | 0,994 | 0,963 |
| dupla_LR | todos (agregado) | — | — | — | 4925 | 89 | 110 | 7826 | 0,980 | 0,989 |

**Sistema final escolhido:** `dupla` (maior F1 agregado na validação cruzada por dia do desenvolvimento (regra da variante dupla x regressão logística; empate favorece a regra)).

## Desempenho dentro da amostra, por grupo

| Variante | Grupo | n | FP | FN | F1 | Especificidade | EMA contagem |
|---|---|---|---|---|---|---|---|
| fixa | dev · dia 2013-04-13 | 5431 | 296 | 57 | 0,840 | 0,933 | 2,199 |
| fixa | dev · dia 2013-04-14 | 5440 | 232 | 92 | 0,932 | 0,926 | 2,294 |
| fixa | dev · dia 2013-04-16 | 2079 | 3 | 24 | 0,992 | 0,991 | 0,519 |
| fixa | dev · 2013-04-13 (Cloudy) | 4231 | 293 | 45 | 0,845 | 0,910 | 2,717 |
| fixa | dev · 2013-04-13 (Rainy) | 1200 | 3 | 12 | 0,348 | 0,997 | 0,367 |
| fixa | dev · 2013-04-14 (Cloudy) | 2200 | 0 | 27 | 0,960 | 1,000 | 0,491 |
| fixa | dev · 2013-04-14 (Sunny) | 3240 | 232 | 65 | 0,927 | 0,821 | 3,519 |
| fixa | dev · 2013-04-16 (Sunny) | 2079 | 3 | 24 | 0,992 | 0,991 | 0,519 |
| fixa | dev · condição Sunny | 5319 | 235 | 89 | 0,957 | 0,855 | 2,346 |
| fixa | dev · condição Cloudy | 6431 | 293 | 72 | 0,872 | 0,943 | 1,957 |
| fixa | dev · condição Rainy | 1200 | 3 | 12 | 0,348 | 0,997 | 0,367 |
| fixa | dev · total | 12950 | 531 | 173 | 0,932 | 0,933 | 1,969 |
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
| dupla_LR | dev · dia 2013-04-13 | 5431 | 3 | 45 | 0,975 | 0,999 | 0,338 |
| dupla_LR | dev · dia 2013-04-14 | 5440 | 27 | 1 | 0,994 | 0,991 | 0,206 |
| dupla_LR | dev · dia 2013-04-16 | 2079 | 12 | 8 | 0,994 | 0,963 | 0,269 |
| dupla_LR | dev · 2013-04-13 (Cloudy) | 4231 | 3 | 38 | 0,978 | 0,999 | 0,368 |
| dupla_LR | dev · 2013-04-13 (Rainy) | 1200 | 0 | 7 | 0,720 | 1,000 | 0,233 |
| dupla_LR | dev · 2013-04-14 (Cloudy) | 2200 | 2 | 1 | 0,996 | 0,999 | 0,055 |
| dupla_LR | dev · 2013-04-14 (Sunny) | 3240 | 25 | 0 | 0,994 | 0,981 | 0,309 |
| dupla_LR | dev · 2013-04-16 (Sunny) | 2079 | 12 | 8 | 0,994 | 0,963 | 0,269 |
| dupla_LR | dev · condição Sunny | 5319 | 37 | 8 | 0,994 | 0,977 | 0,293 |
| dupla_LR | dev · condição Cloudy | 6431 | 5 | 39 | 0,983 | 0,999 | 0,261 |
| dupla_LR | dev · condição Rainy | 1200 | 0 | 7 | 0,720 | 1,000 | 0,233 |
| dupla_LR | dev · total | 12950 | 42 | 54 | 0,990 | 0,995 | 0,272 |
