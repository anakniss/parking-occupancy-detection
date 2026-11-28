# Teste final por condição climática (gerado por `src/summarize_conditions.py`)

Arquivo gerado automaticamente; não edite à mão. Reagrupa as decisões congeladas de `decisoes.csv` (nenhum reajuste; os totais conferem com `metricas.csv`). Classe positiva = vaga ocupada. Taxa de falsa ocupada = FP / (FP + VN); taxa de falsa livre = FN / (FN + VP); EMA = erro médio absoluto do nº de vagas ocupadas por imagem.

Condição = rótulo do PKLot para o quadro. Os 576 quadros do teste dividem-se em sol 158, nublado 356, chuva 62.

## Todas as configurações

| Configuração | Condição | Vaga-quadros | Livres | VP | FP | FN | VN | F1 | Especificidade | Taxa falsa ocupada | Taxa falsa livre | EMA contagem |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| B_M2 | sol | 6319 | 870 | 5396 | 76 | 53 | 794 | 0,988 | 0,913 | 0,087 | 0,010 | 0,66 |
| B_M2 | nublado | 14235 | 1247 | 12876 | 88 | 112 | 1159 | 0,992 | 0,929 | 0,071 | 0,009 | 0,51 |
| B_M2 | chuva | 2465 | 370 | 2001 | 5 | 94 | 365 | 0,976 | 0,986 | 0,014 | 0,045 | 1,47 |
| B_M2 | total | 23019 | 2487 | 20273 | 169 | 259 | 2318 | 0,990 | 0,932 | 0,068 | 0,013 | 0,66 |
| A_M2 | sol | 6319 | 870 | 5331 | 80 | 118 | 790 | 0,982 | 0,908 | 0,092 | 0,022 | 0,97 |
| A_M2 | nublado | 14235 | 1247 | 12772 | 121 | 216 | 1126 | 0,987 | 0,903 | 0,097 | 0,017 | 0,85 |
| A_M2 | chuva | 2465 | 370 | 1992 | 6 | 103 | 364 | 0,973 | 0,984 | 0,016 | 0,049 | 1,66 |
| A_M2 | total | 23019 | 2487 | 20095 | 207 | 437 | 2280 | 0,984 | 0,917 | 0,083 | 0,021 | 0,97 |
| C_M2 | sol | 6319 | 870 | 5393 | 86 | 56 | 784 | 0,987 | 0,901 | 0,099 | 0,010 | 0,76 |
| C_M2 | nublado | 14235 | 1247 | 12744 | 31 | 244 | 1216 | 0,989 | 0,975 | 0,025 | 0,019 | 0,69 |
| C_M2 | chuva | 2465 | 370 | 1970 | 2 | 125 | 368 | 0,969 | 0,995 | 0,005 | 0,060 | 2,02 |
| C_M2 | total | 23019 | 2487 | 20107 | 119 | 425 | 2368 | 0,987 | 0,952 | 0,048 | 0,021 | 0,85 |
| fixa | sol | 6319 | 870 | 5177 | 32 | 272 | 838 | 0,971 | 0,963 | 0,037 | 0,050 | 1,81 |
| fixa | nublado | 14235 | 1247 | 12309 | 34 | 679 | 1213 | 0,972 | 0,973 | 0,027 | 0,052 | 1,91 |
| fixa | chuva | 2465 | 370 | 1886 | 0 | 209 | 370 | 0,948 | 1,000 | 0,000 | 0,100 | 3,37 |
| fixa | total | 23019 | 2487 | 19372 | 66 | 1160 | 2421 | 0,969 | 0,973 | 0,027 | 0,056 | 2,04 |
| adaptativa | sol | 6319 | 870 | 5285 | 47 | 164 | 823 | 0,980 | 0,946 | 0,054 | 0,030 | 1,16 |
| adaptativa | nublado | 14235 | 1247 | 12419 | 32 | 569 | 1215 | 0,976 | 0,974 | 0,026 | 0,044 | 1,55 |
| adaptativa | chuva | 2465 | 370 | 1944 | 1 | 151 | 369 | 0,962 | 0,997 | 0,003 | 0,072 | 2,42 |
| adaptativa | total | 23019 | 2487 | 19648 | 80 | 884 | 2407 | 0,976 | 0,968 | 0,032 | 0,043 | 1,53 |
| dupla | sol | 6319 | 870 | 5283 | 38 | 166 | 832 | 0,981 | 0,956 | 0,044 | 0,030 | 1,23 |
| dupla | nublado | 14235 | 1247 | 12313 | 18 | 675 | 1229 | 0,973 | 0,986 | 0,014 | 0,052 | 1,87 |
| dupla | chuva | 2465 | 370 | 1950 | 2 | 145 | 368 | 0,964 | 0,995 | 0,005 | 0,069 | 2,31 |
| dupla | total | 23019 | 2487 | 19546 | 58 | 986 | 2429 | 0,974 | 0,977 | 0,023 | 0,048 | 1,74 |
| dupla_LR | sol | 6319 | 870 | 5280 | 58 | 169 | 812 | 0,979 | 0,933 | 0,067 | 0,031 | 1,16 |
| dupla_LR | nublado | 14235 | 1247 | 12311 | 47 | 677 | 1200 | 0,971 | 0,962 | 0,038 | 0,052 | 1,86 |
| dupla_LR | chuva | 2465 | 370 | 1955 | 0 | 140 | 370 | 0,965 | 1,000 | 0,000 | 0,067 | 2,26 |
| dupla_LR | total | 23019 | 2487 | 19546 | 105 | 986 | 2382 | 0,973 | 0,958 | 0,042 | 0,048 | 1,71 |

## E2 — diferença simples × compensação de ganho (`B_M2` → `C_M2`)

Corrigidos = vaga-quadros que a variante acerta e a base erra; introduzidos = o inverso.

| Condição | F1 | Especificidade | Taxa falsa ocupada | Taxa falsa livre | FP | FN | EMA | Corrigidos | Introduzidos |
|---|---|---|---|---|---|---|---|---|---|
| sol | 0,988 → 0,987 | 0,913 → 0,901 | 0,087 → 0,099 | 0,010 → 0,010 | 76 → 86 | 53 → 56 | 0,66 → 0,76 | 31 | 44 |
| nublado | 0,992 → 0,989 | 0,929 → 0,975 | 0,071 → 0,025 | 0,009 → 0,019 | 88 → 31 | 112 → 244 | 0,51 → 0,69 | 115 | 190 |
| chuva | 0,976 → 0,969 | 0,986 → 0,995 | 0,014 → 0,005 | 0,045 → 0,060 | 5 → 2 | 94 → 125 | 1,47 → 2,02 | 9 | 37 |
| total | 0,990 → 0,987 | 0,932 → 0,952 | 0,068 → 0,048 | 0,013 → 0,021 | 169 → 119 | 259 → 425 | 0,66 → 0,85 | 155 | 271 |

## Baseline × final (`B_M2` → `dupla`)

Corrigidos = vaga-quadros que a variante acerta e a base erra; introduzidos = o inverso.

| Condição | F1 | Especificidade | Taxa falsa ocupada | Taxa falsa livre | FP | FN | EMA | Corrigidos | Introduzidos |
|---|---|---|---|---|---|---|---|---|---|
| sol | 0,988 → 0,981 | 0,913 → 0,956 | 0,087 → 0,044 | 0,010 → 0,030 | 76 → 38 | 53 → 166 | 0,66 → 1,23 | 38 | 113 |
| nublado | 0,992 → 0,973 | 0,929 → 0,986 | 0,071 → 0,014 | 0,009 → 0,052 | 88 → 18 | 112 → 675 | 0,51 → 1,87 | 70 | 563 |
| chuva | 0,976 → 0,964 | 0,986 → 0,995 | 0,014 → 0,005 | 0,045 → 0,069 | 5 → 2 | 94 → 145 | 1,47 → 2,31 | 3 | 51 |
| total | 0,990 → 0,974 | 0,932 → 0,977 | 0,068 → 0,023 | 0,013 → 0,048 | 169 → 58 | 259 → 986 | 0,66 → 1,74 | 111 | 727 |
