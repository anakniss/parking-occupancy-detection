# Teste final da M3 (gerado por `src/run_final.py --etapa teste`)

Arquivo gerado automaticamente; não edite à mão. Classe positiva = vaga ocupada.

Parâmetros lidos de `models/sistema_final_m3.json` (gerado em 2026-11-23T18:07:35, commit do código 9a56cdfb9d). Sistema final: **dupla**.

Dias de teste: 2013-03-13, 2013-03-14, 2013-03-19, 2013-03-21 — 576 quadros, 23019 vaga-quadros rotulados.

## Configurações avaliadas

| Configuração | Descrição | Limiar |
|---|---|---|
| B_M2 | Baseline: configuração B da M2 congelada (referência fixa, T = 25, τ = 0,24) | 0,24 |
| A_M2 | Configuração A da M2 congelada (sem morfologia) | 0,24 |
| C_M2 | Configuração C da M2 congelada (ganho global) | 0,24 |
| fixa | Só a referência fixa do início do dia (pipeline B da M2), tau reajustado no desenvolvimento | 0,43 |
| adaptativa | Só a referência adaptativa (média móvel seletiva nas vagas livres) | 0,29 |
| dupla | Referência fixa + adaptativa; ocupada se diferir das duas (menor fração >= tau) | 0,24 |
| dupla_LR | Referências da variante dupla; decisão por regressão logística sobre 7 descritores | 0,54 |

## Indicadores (total do teste)

| Configuração | VP | FP | FN | VN | Acurácia | Precisão | Revocação | Especificidade | F1 | Acur. balanceada | EMA contagem | Viés contagem | Erro máx. |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| B_M2 | 20273 | 169 | 259 | 2318 | 0,981 | 0,992 | 0,987 | 0,932 | 0,990 | 0,960 | 0,656 | -0,156 | 7,000 |
| A_M2 | 20095 | 207 | 437 | 2280 | 0,972 | 0,990 | 0,979 | 0,917 | 0,984 | 0,948 | 0,969 | -0,399 | 7,000 |
| C_M2 | 20107 | 119 | 425 | 2368 | 0,976 | 0,994 | 0,979 | 0,952 | 0,987 | 0,966 | 0,851 | -0,531 | 6,000 |
| fixa | 19372 | 66 | 1160 | 2421 | 0,947 | 0,997 | 0,944 | 0,973 | 0,969 | 0,958 | 2,038 | -1,899 | 8,000 |
| adaptativa | 19648 | 80 | 884 | 2407 | 0,958 | 0,996 | 0,957 | 0,968 | 0,976 | 0,962 | 1,535 | -1,396 | 5,000 |
| dupla | 19546 | 58 | 986 | 2429 | 0,955 | 0,997 | 0,952 | 0,977 | 0,974 | 0,964 | 1,740 | -1,611 | 6,000 |
| dupla_LR | 19546 | 105 | 986 | 2382 | 0,953 | 0,995 | 0,952 | 0,958 | 0,973 | 0,955 | 1,710 | -1,530 | 6,000 |

EMA contagem = erro médio absoluto do nº de vagas ocupadas por imagem; viés > 0 = superestima.

## Indicadores por dia, segmento e condição

| Configuração | Grupo | n | FP | FN | F1 | Especificidade | Acur. balanceada | EMA contagem |
|---|---|---|---|---|---|---|---|---|
| B_M2 | teste · dia 2013-03-13 | 5747 | 21 | 103 | 0,988 | 0,957 | 0,969 | 0,778 |
| B_M2 | teste · dia 2013-03-14 | 5838 | 51 | 73 | 0,988 | 0,904 | 0,945 | 0,753 |
| B_M2 | teste · dia 2013-03-19 | 5635 | 26 | 31 | 0,994 | 0,957 | 0,975 | 0,404 |
| B_M2 | teste · dia 2013-03-21 | 5799 | 71 | 52 | 0,988 | 0,918 | 0,954 | 0,683 |
| B_M2 | teste · 2013-03-13 (Cloudy) | 3279 | 11 | 20 | 0,995 | 0,975 | 0,984 | 0,329 |
| B_M2 | teste · 2013-03-13 (Rainy) | 1948 | 5 | 82 | 0,977 | 0,884 | 0,920 | 1,612 |
| B_M2 | teste · 2013-03-13 (Sunny) | 520 | 5 | 1 | 0,994 | 0,286 | 0,642 | 0,462 |
| B_M2 | teste · 2013-03-14 (Cloudy) | 5838 | 51 | 73 | 0,988 | 0,904 | 0,945 | 0,753 |
| B_M2 | teste · 2013-03-19 (Cloudy) | 5118 | 26 | 19 | 0,995 | 0,906 | 0,951 | 0,352 |
| B_M2 | teste · 2013-03-19 (Rainy) | 517 | 0 | 12 | 0,967 | 1,000 | 0,968 | 0,923 |
| B_M2 | teste · 2013-03-21 (Sunny) | 5799 | 71 | 52 | 0,988 | 0,918 | 0,954 | 0,683 |
| B_M2 | teste · condição Sunny | 6319 | 76 | 53 | 0,988 | 0,913 | 0,951 | 0,665 |
| B_M2 | teste · condição Cloudy | 14235 | 88 | 112 | 0,992 | 0,929 | 0,960 | 0,511 |
| B_M2 | teste · condição Rainy | 2465 | 5 | 94 | 0,976 | 0,986 | 0,971 | 1,468 |
| A_M2 | teste · dia 2013-03-13 | 5747 | 25 | 181 | 0,980 | 0,949 | 0,957 | 1,306 |
| A_M2 | teste · dia 2013-03-14 | 5838 | 66 | 103 | 0,984 | 0,876 | 0,928 | 0,993 |
| A_M2 | teste · dia 2013-03-19 | 5635 | 41 | 41 | 0,992 | 0,932 | 0,962 | 0,582 |
| A_M2 | teste · dia 2013-03-21 | 5799 | 75 | 112 | 0,981 | 0,913 | 0,945 | 0,986 |
| A_M2 | teste · 2013-03-13 (Cloudy) | 3279 | 14 | 83 | 0,983 | 0,968 | 0,969 | 1,037 |
| A_M2 | teste · 2013-03-13 (Rainy) | 1948 | 6 | 92 | 0,974 | 0,860 | 0,906 | 1,878 |
| A_M2 | teste · 2013-03-13 (Sunny) | 520 | 5 | 6 | 0,989 | 0,286 | 0,637 | 0,846 |
| A_M2 | teste · 2013-03-14 (Cloudy) | 5838 | 66 | 103 | 0,984 | 0,876 | 0,928 | 0,993 |
| A_M2 | teste · 2013-03-19 (Cloudy) | 5118 | 41 | 30 | 0,993 | 0,851 | 0,923 | 0,555 |
| A_M2 | teste · 2013-03-19 (Rainy) | 517 | 0 | 11 | 0,970 | 1,000 | 0,971 | 0,846 |
| A_M2 | teste · 2013-03-21 (Sunny) | 5799 | 75 | 112 | 0,981 | 0,913 | 0,945 | 0,986 |
| A_M2 | teste · condição Sunny | 6319 | 80 | 118 | 0,982 | 0,908 | 0,943 | 0,975 |
| A_M2 | teste · condição Cloudy | 14235 | 121 | 216 | 0,987 | 0,903 | 0,943 | 0,846 |
| A_M2 | teste · condição Rainy | 2465 | 6 | 103 | 0,973 | 0,984 | 0,967 | 1,661 |
| C_M2 | teste · dia 2013-03-13 | 5747 | 13 | 158 | 0,984 | 0,973 | 0,972 | 1,146 |
| C_M2 | teste · dia 2013-03-14 | 5838 | 24 | 152 | 0,983 | 0,955 | 0,963 | 1,027 |
| C_M2 | teste · dia 2013-03-19 | 5635 | 0 | 60 | 0,994 | 1,000 | 0,994 | 0,426 |
| C_M2 | teste · dia 2013-03-21 | 5799 | 82 | 55 | 0,986 | 0,905 | 0,947 | 0,793 |
| C_M2 | teste · 2013-03-13 (Cloudy) | 3279 | 7 | 47 | 0,990 | 0,984 | 0,984 | 0,610 |
| C_M2 | teste · 2013-03-13 (Rainy) | 1948 | 2 | 110 | 0,970 | 0,953 | 0,948 | 2,245 |
| C_M2 | teste · 2013-03-13 (Sunny) | 520 | 4 | 1 | 0,995 | 0,429 | 0,713 | 0,385 |
| C_M2 | teste · 2013-03-14 (Cloudy) | 5838 | 24 | 152 | 0,983 | 0,955 | 0,963 | 1,027 |
| C_M2 | teste · 2013-03-19 (Cloudy) | 5118 | 0 | 45 | 0,995 | 1,000 | 0,995 | 0,352 |
| C_M2 | teste · 2013-03-19 (Rainy) | 517 | 0 | 15 | 0,959 | 1,000 | 0,961 | 1,154 |
| C_M2 | teste · 2013-03-21 (Sunny) | 5799 | 82 | 55 | 0,986 | 0,905 | 0,947 | 0,793 |
| C_M2 | teste · condição Sunny | 6319 | 86 | 56 | 0,987 | 0,901 | 0,945 | 0,759 |
| C_M2 | teste · condição Cloudy | 14235 | 31 | 244 | 0,989 | 0,975 | 0,978 | 0,688 |
| C_M2 | teste · condição Rainy | 2465 | 2 | 125 | 0,969 | 0,995 | 0,967 | 2,016 |
| fixa | teste · dia 2013-03-13 | 5747 | 11 | 372 | 0,962 | 0,978 | 0,953 | 2,562 |
| fixa | teste · dia 2013-03-14 | 5838 | 19 | 267 | 0,972 | 0,964 | 0,957 | 1,849 |
| fixa | teste · dia 2013-03-19 | 5635 | 8 | 273 | 0,971 | 0,987 | 0,966 | 1,936 |
| fixa | teste · dia 2013-03-21 | 5799 | 28 | 248 | 0,971 | 0,968 | 0,959 | 1,807 |
| fixa | teste · 2013-03-13 (Cloudy) | 3279 | 7 | 171 | 0,968 | 0,984 | 0,962 | 2,049 |
| fixa | teste · 2013-03-13 (Rainy) | 1948 | 0 | 177 | 0,951 | 1,000 | 0,954 | 3,612 |
| fixa | teste · 2013-03-13 (Sunny) | 520 | 4 | 24 | 0,972 | 0,429 | 0,691 | 1,846 |
| fixa | teste · 2013-03-14 (Cloudy) | 5838 | 19 | 267 | 0,972 | 0,964 | 0,957 | 1,849 |
| fixa | teste · 2013-03-19 (Cloudy) | 5118 | 8 | 241 | 0,974 | 0,971 | 0,961 | 1,883 |
| fixa | teste · 2013-03-19 (Rainy) | 517 | 0 | 32 | 0,908 | 1,000 | 0,916 | 2,462 |
| fixa | teste · 2013-03-21 (Sunny) | 5799 | 28 | 248 | 0,971 | 0,968 | 0,959 | 1,807 |
| fixa | teste · condição Sunny | 6319 | 32 | 272 | 0,971 | 0,963 | 0,957 | 1,810 |
| fixa | teste · condição Cloudy | 14235 | 34 | 679 | 0,972 | 0,973 | 0,960 | 1,907 |
| fixa | teste · condição Rainy | 2465 | 0 | 209 | 0,948 | 1,000 | 0,950 | 3,371 |
| adaptativa | teste · dia 2013-03-13 | 5747 | 10 | 234 | 0,976 | 0,980 | 0,968 | 1,625 |
| adaptativa | teste · dia 2013-03-14 | 5838 | 14 | 336 | 0,966 | 0,974 | 0,955 | 2,205 |
| adaptativa | teste · dia 2013-03-19 | 5635 | 13 | 154 | 0,983 | 0,978 | 0,974 | 1,071 |
| adaptativa | teste · dia 2013-03-21 | 5799 | 43 | 160 | 0,979 | 0,950 | 0,959 | 1,221 |
| adaptativa | teste · 2013-03-13 (Cloudy) | 3279 | 5 | 96 | 0,982 | 0,989 | 0,977 | 1,159 |
| adaptativa | teste · 2013-03-13 (Rainy) | 1948 | 1 | 134 | 0,963 | 0,977 | 0,953 | 2,714 |
| adaptativa | teste · 2013-03-13 (Sunny) | 520 | 4 | 4 | 0,992 | 0,429 | 0,710 | 0,462 |
| adaptativa | teste · 2013-03-14 (Cloudy) | 5838 | 14 | 336 | 0,966 | 0,974 | 0,955 | 2,205 |
| adaptativa | teste · 2013-03-19 (Cloudy) | 5118 | 13 | 137 | 0,984 | 0,953 | 0,962 | 1,047 |
| adaptativa | teste · 2013-03-19 (Rainy) | 517 | 0 | 17 | 0,953 | 1,000 | 0,955 | 1,308 |
| adaptativa | teste · 2013-03-21 (Sunny) | 5799 | 43 | 160 | 0,979 | 0,950 | 0,959 | 1,221 |
| adaptativa | teste · condição Sunny | 6319 | 47 | 164 | 0,980 | 0,946 | 0,958 | 1,158 |
| adaptativa | teste · condição Cloudy | 14235 | 32 | 569 | 0,976 | 0,974 | 0,965 | 1,548 |
| adaptativa | teste · condição Rainy | 2465 | 1 | 151 | 0,962 | 0,997 | 0,963 | 2,419 |
| dupla | teste · dia 2013-03-13 | 5747 | 12 | 191 | 0,980 | 0,975 | 0,970 | 1,340 |
| dupla | teste · dia 2013-03-14 | 5838 | 8 | 436 | 0,956 | 0,985 | 0,951 | 2,932 |
| dupla | teste · dia 2013-03-19 | 5635 | 4 | 194 | 0,980 | 0,993 | 0,977 | 1,362 |
| dupla | teste · dia 2013-03-21 | 5799 | 34 | 165 | 0,980 | 0,961 | 0,964 | 1,303 |
| dupla | teste · 2013-03-13 (Cloudy) | 3279 | 6 | 61 | 0,988 | 0,986 | 0,982 | 0,744 |
| dupla | teste · 2013-03-13 (Rainy) | 1948 | 2 | 129 | 0,964 | 0,953 | 0,943 | 2,592 |
| dupla | teste · 2013-03-13 (Sunny) | 520 | 4 | 1 | 0,995 | 0,429 | 0,713 | 0,385 |
| dupla | teste · 2013-03-14 (Cloudy) | 5838 | 8 | 436 | 0,956 | 0,985 | 0,951 | 2,932 |
| dupla | teste · 2013-03-19 (Cloudy) | 5118 | 4 | 178 | 0,981 | 0,986 | 0,974 | 1,375 |
| dupla | teste · 2013-03-19 (Rainy) | 517 | 0 | 16 | 0,956 | 1,000 | 0,958 | 1,231 |
| dupla | teste · 2013-03-21 (Sunny) | 5799 | 34 | 165 | 0,980 | 0,961 | 0,964 | 1,303 |
| dupla | teste · condição Sunny | 6319 | 38 | 166 | 0,981 | 0,956 | 0,963 | 1,228 |
| dupla | teste · condição Cloudy | 14235 | 18 | 675 | 0,973 | 0,986 | 0,967 | 1,868 |
| dupla | teste · condição Rainy | 2465 | 2 | 145 | 0,964 | 0,995 | 0,963 | 2,306 |
| dupla_LR | teste · dia 2013-03-13 | 5747 | 15 | 199 | 0,979 | 0,969 | 0,966 | 1,431 |
| dupla_LR | teste · dia 2013-03-14 | 5838 | 17 | 428 | 0,956 | 0,968 | 0,944 | 2,842 |
| dupla_LR | teste · dia 2013-03-19 | 5635 | 20 | 193 | 0,978 | 0,967 | 0,964 | 1,340 |
| dupla_LR | teste · dia 2013-03-21 | 5799 | 53 | 166 | 0,978 | 0,939 | 0,952 | 1,207 |
| dupla_LR | teste · 2013-03-13 (Cloudy) | 3279 | 10 | 71 | 0,986 | 0,977 | 0,976 | 0,890 |
| dupla_LR | teste · 2013-03-13 (Rainy) | 1948 | 0 | 125 | 0,966 | 1,000 | 0,967 | 2,551 |
| dupla_LR | teste · 2013-03-13 (Sunny) | 520 | 5 | 3 | 0,992 | 0,286 | 0,640 | 0,615 |
| dupla_LR | teste · 2013-03-14 (Cloudy) | 5838 | 17 | 428 | 0,956 | 0,968 | 0,944 | 2,842 |
| dupla_LR | teste · 2013-03-19 (Cloudy) | 5118 | 20 | 178 | 0,979 | 0,928 | 0,945 | 1,359 |
| dupla_LR | teste · 2013-03-19 (Rainy) | 517 | 0 | 15 | 0,959 | 1,000 | 0,961 | 1,154 |
| dupla_LR | teste · 2013-03-21 (Sunny) | 5799 | 53 | 166 | 0,978 | 0,939 | 0,952 | 1,207 |
| dupla_LR | teste · condição Sunny | 6319 | 58 | 169 | 0,979 | 0,933 | 0,951 | 1,158 |
| dupla_LR | teste · condição Cloudy | 14235 | 47 | 677 | 0,971 | 0,962 | 0,955 | 1,860 |
| dupla_LR | teste · condição Rainy | 2465 | 0 | 140 | 0,965 | 1,000 | 0,967 | 2,258 |

## Comparações controladas (mesmas vagas-quadro, referências e rótulos)

| Id | Pergunta | Base → variante | F1 | FP | FN | EMA | Corrigidos | Introduzidos |
|---|---|---|---|---|---|---|---|---|
| Baseline x final | O sistema final da M3 supera o baseline da M2 em dias inéditos? | B_M2 → dupla | 0,990 → 0,974 | 169 → 58 | 259 → 986 | 0,66 → 1,74 | 111 | 727 |
| E3 | A referência adaptativa reduz os erros da deriva de iluminação ao longo do dia? | fixa → adaptativa | 0,969 → 0,976 | 66 → 80 | 1160 → 884 | 2,04 → 1,53 | 546 | 284 |
| E4 | Manter a referência fixa ao lado da adaptativa evita os travamentos da adaptativa? | adaptativa → dupla | 0,976 → 0,974 | 80 → 58 | 884 → 986 | 1,53 → 1,74 | 116 | 196 |
| E5 | A regressão logística sobre vários descritores supera a regra de limiar único? | dupla → dupla_LR | 0,974 → 0,973 | 58 → 105 | 986 → 986 | 1,74 → 1,71 | 52 | 99 |
| E1 (reavaliação) | A morfologia (M2) continua útil em dias inéditos? | A_M2 → B_M2 | 0,984 → 0,990 | 207 → 169 | 437 → 259 | 0,97 → 0,66 | 284 | 68 |
| E2 (reavaliação) | A compensação global de ganho (M2) continua com efeito misto? | B_M2 → C_M2 | 0,990 → 0,987 | 169 → 119 | 259 → 425 | 0,66 → 0,85 | 155 | 271 |

## Critérios de sucesso (definidos na M2) aplicados ao sistema final (dupla)

| Critério | Grupo | Valor | Atendido |
|---|---|---|---|
| F1 ≥ 0,95 em cada dia de teste | 2013-03-13 | 0,980 | sim |
| F1 ≥ 0,95 em cada dia de teste | 2013-03-14 | 0,956 | sim |
| F1 ≥ 0,95 em cada dia de teste | 2013-03-19 | 0,980 | sim |
| F1 ≥ 0,95 em cada dia de teste | 2013-03-21 | 0,980 | sim |
| Especificidade ≥ 0,98 nos quadros de chuva | chuva | 0,995 | sim |
| EMA de contagem ≤ 1,0 vaga por imagem | 2013-03-13 | 1,340 | não |
| EMA de contagem ≤ 1,0 vaga por imagem | 2013-03-14 | 2,932 | não |
| EMA de contagem ≤ 1,0 vaga por imagem | 2013-03-19 | 1,362 | não |
| EMA de contagem ≤ 1,0 vaga por imagem | 2013-03-21 | 1,303 | não |

## Casos ilustrados

- Sucesso (VP): `2013-03-14_12_35_59`, vaga 8.
- Sucesso (VN): `2013-03-21_06_50_01`, vaga 35.
- Falha (FP): `2013-03-21_16_15_11`, vaga 39.
- Falha (FN): `2013-03-13_12_30_07`, vaga 38.
- Pior quadro do sistema final: `2013-03-14_17_26_05` (6 erros; baseline no mesmo quadro: 4).
- Pior quadro do baseline: `2013-03-21_17_30_13` (7 erros; sistema final no mesmo quadro: 4).
