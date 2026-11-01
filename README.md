# Trabalho IV - Ofuscação de Código

## A ideia

Ofuscação é transformar o código pra deixá-lo difícil de entender, **sem mudar o que ele faz**. O custo disso é que o programa costuma ficar **mais lento**. Nosso trabalho é medir esse custo: quanto de desempenho a gente perde ao ofuscar.

Quem ofusca é uma **ferramenta pronta** (um "ofuscador"): passamos o código original por ela e recebemos a versão transformada equivalente.

## Os benchmarks

São **dois programas diferentes** (benchmark = programa feito pra medir desempenho, dá pra cronometrar e comparar). Escolhemos uma linguagem e testamos os dois nela.

## O que vamos medir

| Benchmark   | Versão                   | Medir?               |
| ----------- | ------------------------ | -------------------- |
| Benchmark A | Original (sem ofuscação) | ✅ linha de base de A |
| Benchmark A | Ofuscado - config 1      | ✅                    |
| Benchmark A | Ofuscado - config 2      | ✅                    |
| Benchmark B | Original (sem ofuscação) | ✅ linha de base de B |
| Benchmark B | Ofuscado - config 1      | ✅                    |
| Benchmark B | Ofuscado - config 2      | ✅                    |

Cada linha dessa tabela ainda se multiplica por **3 tamanhos de entrada × 10 repetições**.

Repare que **cada benchmark tem sua própria versão original como referência** - a comparação é sempre contra o original dele mesmo, **nunca um benchmark contra o outro**.

## A lógica do experimento

São dois eixos diferentes que se cruzam:

- **2 benchmarks** respondem: *o efeito muda conforme o programa?*
- **2 configurações** respondem: *quanto cada nível de ofuscação custa?*

Por isso ambos se cruzam na tabela acima.

## Regras de medição (não esquecer)

- Comparar sempre com o original **da mesma linguagem** - nunca comparar linguagens entre si.
- **3 tamanhos de entrada**, com pelo menos 50% de diferença entre eles.
- A **menor entrada no código original** não pode durar menos de **20 segundos**.
- **10 repetições** por caso; reportar **média, mediana, desvio padrão, mínimo e máximo**.
- Controlar a plataforma durante os testes: fechar outros programas, laptop na tomada, etc.
- Automatizar com script (são muitas execuções).
