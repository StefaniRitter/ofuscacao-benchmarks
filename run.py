#!/usr/bin/env python3
"""
Harness de medicao

Roda cada benchmark em cada versao (original + configs ofuscadas), para cada
tamanho de entrada, repetindo N vezes. Captura o tempo que o proprio benchmark
imprime ("time: X.XXX seconds") e salva tudo num CSV para a analise (Parte 3).

Uso:
    python3 run.py                # run completo -> results/medidas.csv
    python3 run.py --calibrate    # roda 1x cada original para ajustar os tamanhos
    python3 run.py --reps 3       # muda o numero de repeticoes (padrao: 10)

A versao cujo arquivo nao existe ainda é simplesmente pulada. Assim da pra
rodar só os originais agora e, quando a tiver os codigos ofuscados
em benchmarks/config1 e benchmarks/config2, rodar o resto sem mudar nada.
"""

import argparse
import csv
import re
import subprocess
import sys
from pathlib import Path
from statistics import mean, median, pstdev

# CONFIGURACAO

# Interpretador usado para rodar os benchmarks.
PYTHON = sys.executable  # o mesmo python que esta rodando este script

# Benchmarks: nome curto -> nome do arquivo (igual nas 3 versoes).
BENCHMARKS = {
    "matrizes": "t4-multi-python.py",
    "palavras": "t4-palavras.py",
}

# Versoes: nome -> pasta onde fica o arquivo daquele benchmark.
VERSIONS = {
    "original": "benchmarks/original",
    "config1":  "benchmarks/config1",
    "config2":  "benchmarks/config2",
}

# Tamanhos de entrada POR BENCHMARK.
# REGRA: no original, a MENOR entrada precisa durar >= 20 s, e cada tamanho
# tem que ser pelo menos 50% maior que o anterior.
# ESTES VALORES SAO PROVISORIOS, ajustar com `python3 run.py --calibrate`.
SIZES = {
    "matrizes": [460, 696, 1048],  # O(n^3): 576 ja da ~27s; passos de +50%
    "palavras": [160_000_000, 240_000_000, 360_000_000],  # sonda: achar o teto de RAM
}

REPS_DEFAULT = 10
RESULTS_FILE = "results/medidas.csv"

# EXECUCAO

RE_TIME = re.compile(r"time:\s*([\d.]+)\s*seconds")
RE_OK = re.compile(r"are\s+(ok|bad)")


def run_once(script: Path, size: int):
    """Roda o benchmark uma vez. Retorna (tempo_em_segundos, correto_bool)."""
    proc = subprocess.run(
        [PYTHON, str(script), str(size)],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"falhou: {script} {size}\n{proc.stderr.strip()}"
        )
    out = proc.stdout
    m_time = RE_TIME.search(out)
    m_ok = RE_OK.search(out)
    if not m_time:
        raise RuntimeError(f"nao achei 'time:' na saida de {script} {size}:\n{out}")
    elapsed = float(m_time.group(1))
    correct = (m_ok.group(1) == "ok") if m_ok else None
    return elapsed, correct


def resolve_script(version_dir: str, filename: str) -> Path | None:
    """Caminho do arquivo do benchmark naquela versao, ou None se nao existe."""
    p = Path(version_dir) / filename
    return p if p.exists() else None


def calibrate(sizes):
    """Roda 1x cada benchmark original em cada tamanho candidato e mostra o tempo.
    Serve pra voce escolher tamanhos em que a menor entrada >= 20 s."""
    print("== CALIBRACAO (apenas originais, 1 execucao por tamanho) ==\n")
    for bench, filename in BENCHMARKS.items():
        script = resolve_script(VERSIONS["original"], filename)
        if script is None:
            print(f"[{bench}] arquivo nao encontrado, pulando\n")
            continue
        print(f"[{bench}] {script}")
        for size in sizes[bench]:
            elapsed, correct = run_once(script, size)
            flag = "" if correct in (True, None) else "  <-- RESULTADO BAD!"
            marca = "  >= 20s OK" if elapsed >= 20 else "  < 20s (aumente)"
            print(f"   size={size:>12}  {elapsed:8.3f}s{marca}{flag}")
        print()
    print("Ajuste a tabela SIZES no topo do run.py conforme os tempos acima.")


def full_run(sizes, reps, out_file):
    """Run completo: todas as versoes existentes, todos os tamanhos, N repeticoes."""
    rows = []
    for bench, filename in BENCHMARKS.items():
        for version, vdir in VERSIONS.items():
            script = resolve_script(vdir, filename)
            if script is None:
                print(f"[pulando] {bench}/{version}: {Path(vdir)/filename} nao existe")
                continue
            for size in sizes[bench]:
                print(f"[{bench}/{version}] size={size} ", end="", flush=True)
                for rep in range(1, reps + 1):
                    elapsed, correct = run_once(script, size)
                    rows.append({
                        "benchmark": bench,
                        "version": version,
                        "size": size,
                        "rep": rep,
                        "time_seconds": f"{elapsed:.6f}",
                        "correct": "" if correct is None else ("ok" if correct else "bad"),
                    })
                    print(".", end="", flush=True)
                print(" ok")

    Path(out_file).parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", newline="") as f:
        w = csv.DictWriter(
            f, fieldnames=["benchmark", "version", "size", "rep", "time_seconds", "correct"]
        )
        w.writeheader()
        w.writerows(rows)

    print(f"\nSalvo: {out_file}  ({len(rows)} medidas)")
    print_summary(rows)


def print_summary(rows):
    """Resumo rapido na tela (a analise completa fica pra Parte 3)."""
    print("\n== RESUMO (s) ==")
    groups = {}
    for r in rows:
        key = (r["benchmark"], r["version"], int(r["size"]))
        groups.setdefault(key, []).append(float(r["time_seconds"]))
    print(f"{'benchmark':10} {'version':9} {'size':>12}  {'media':>8} {'mediana':>8} {'desvio':>8} {'min':>8} {'max':>8}")
    for key in sorted(groups):
        bench, version, size = key
        ts = groups[key]
        print(f"{bench:10} {version:9} {size:>12}  "
              f"{mean(ts):8.3f} {median(ts):8.3f} {pstdev(ts):8.3f} {min(ts):8.3f} {max(ts):8.3f}")


def main():
    ap = argparse.ArgumentParser(description="Harness de medicao - Trabalho IV")
    ap.add_argument("--calibrate", action="store_true",
                    help="roda 1x cada original para ajustar os tamanhos")
    ap.add_argument("--reps", type=int, default=REPS_DEFAULT,
                    help=f"numero de repeticoes (padrao: {REPS_DEFAULT})")
    ap.add_argument("--out", default=RESULTS_FILE,
                    help=f"arquivo de saida (padrao: {RESULTS_FILE})")
    args = ap.parse_args()

    if args.calibrate:
        calibrate(SIZES)
    else:
        full_run(SIZES, args.reps, args.out)


if __name__ == "__main__":
    main()
