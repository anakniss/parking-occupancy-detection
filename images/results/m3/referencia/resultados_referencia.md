# X3 — Sensibilidade do baseline à referência vazia (gerado por `src/analyze_reference.py`)

Arquivo gerado automaticamente; não edite à mão. Só a amostra da M2 (desenvolvimento da M3); baseline `B_M2` congelado (T = 25, abertura 3, fechamento 7, τ = 0,24), sem reajuste. Classe positiva = vaga ocupada. Taxa de falsa ocupada = FP / (FP + VN); taxa de falsa livre = FN / (FN + VP). Quadros que servem de referência ficam fora da avaliação (5 quadros).

## Janela com o estacionamento vazio

| Dia | Condição | Quadros na amostra | Quadros com as 40 vagas livres | Primeiro | Último |
|---|---|---|---|---|---|
| 2013-04-13 | chuva | 31 | 21 | 06:45:01 | 08:25:02 |
| 2013-04-14 | nublado | 56 | 19 | 06:40:00 | 08:10:02 |
| 2013-04-16 | sol | 53 | 1 | 06:50:01 | 06:50:01 |

## Indicadores por dia avaliado e referência

| Dia avaliado | Referência | Tipo | Quadros | VP | FP | FN | VN | F1 | Especificidade | Taxa falsa ocupada | Taxa falsa livre | EMA contagem | Erro máx. |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2013-04-13 (chuva) | 2013-04-13 06:45 (chuva) | mesmo dia | 29 | 13 | 8 | 3 | 1136 | 0,703 | 0,993 | 0,007 | 0,188 | 0,38 | 4 |
| 2013-04-13 (chuva) | 2013-04-13 08:25 (chuva) | mesmo dia, mais tarde | 29 | 13 | 0 | 3 | 1144 | 0,897 | 1,000 | 0,000 | 0,188 | 0,10 | 1 |
| 2013-04-13 (chuva) | 2013-04-14 06:40 (nublado) | outro dia | 29 | 16 | 49 | 0 | 1095 | 0,395 | 0,957 | 0,043 | 0,000 | 1,69 | 2 |
| 2013-04-13 (chuva) | 2013-04-14 08:10 (nublado) | outro dia | 29 | 16 | 55 | 0 | 1089 | 0,368 | 0,952 | 0,048 | 0,000 | 1,90 | 10 |
| 2013-04-13 (chuva) | 2013-04-16 06:50 (sol) | outro dia | 29 | 16 | 85 | 0 | 1059 | 0,274 | 0,926 | 0,074 | 0,000 | 2,93 | 6 |
| 2013-04-14 (nublado) | 2013-04-14 06:40 (nublado) | mesmo dia | 54 | 352 | 0 | 1 | 1807 | 0,999 | 1,000 | 0,000 | 0,003 | 0,02 | 1 |
| 2013-04-14 (nublado) | 2013-04-14 08:10 (nublado) | mesmo dia, mais tarde | 54 | 352 | 2 | 1 | 1805 | 0,996 | 0,999 | 0,001 | 0,003 | 0,06 | 1 |
| 2013-04-14 (nublado) | 2013-04-13 06:45 (chuva) | outro dia | 54 | 341 | 225 | 12 | 1582 | 0,742 | 0,875 | 0,125 | 0,034 | 3,94 | 13 |
| 2013-04-14 (nublado) | 2013-04-13 08:25 (chuva) | outro dia | 54 | 341 | 153 | 12 | 1654 | 0,805 | 0,915 | 0,085 | 0,034 | 2,65 | 6 |
| 2013-04-14 (nublado) | 2013-04-16 06:50 (sol) | outro dia | 54 | 352 | 43 | 1 | 1764 | 0,941 | 0,976 | 0,024 | 0,003 | 0,78 | 4 |
| 2013-04-16 (sol) | 2013-04-16 06:50 (sol) | mesmo dia | 52 | 1744 | 7 | 8 | 320 | 0,996 | 0,979 | 0,021 | 0,005 | 0,25 | 2 |
| 2013-04-16 (sol) | 2013-04-13 06:45 (chuva) | outro dia | 52 | 1726 | 87 | 26 | 240 | 0,968 | 0,734 | 0,266 | 0,015 | 1,79 | 14 |
| 2013-04-16 (sol) | 2013-04-13 08:25 (chuva) | outro dia | 52 | 1720 | 51 | 32 | 276 | 0,976 | 0,844 | 0,156 | 0,018 | 1,25 | 6 |
| 2013-04-16 (sol) | 2013-04-14 06:40 (nublado) | outro dia | 52 | 1733 | 15 | 19 | 312 | 0,990 | 0,954 | 0,046 | 0,011 | 0,38 | 4 |
| 2013-04-16 (sol) | 2013-04-14 08:10 (nublado) | outro dia | 52 | 1733 | 25 | 19 | 302 | 0,987 | 0,924 | 0,076 | 0,011 | 0,54 | 4 |
