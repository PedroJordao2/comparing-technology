# =============================================================
# Geração de Gráficos Comparativos — Resultados dos Testes de Carga
# Execute após os testes de carga com:
#   python generate_graphs.py
# Os CSVs do Locust devem estar na pasta tests/results/
# =============================================================

import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import os, glob, csv

matplotlib.rcParams.update({"font.size": 12, "figure.dpi": 120})

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "results")
GRAPH_DIR  = os.path.join(os.path.dirname(__file__), "graphs")
os.makedirs(GRAPH_DIR, exist_ok=True)

TECNOLOGIAS = ["REST", "GraphQL", "SOAP", "gRPC"]
CARGAS      = [10, 50, 100, 500]
CORES       = ["#4CAF50", "#2196F3", "#FF9800", "#9C27B0"]


# ── Dados de exemplo (substitua pelos CSVs reais do Locust) ───

# Formato: dados[tecnologia][carga] = {"avg_ms", "rps", "error_pct", "min_ms", "max_ms"}
DADOS_EXEMPLO = {
    "REST": {
        10:  {"avg_ms": 12,  "rps": 820,  "error_pct": 0.0, "min_ms": 3,  "max_ms": 45},
        50:  {"avg_ms": 18,  "rps": 2700, "error_pct": 0.1, "min_ms": 4,  "max_ms": 120},
        100: {"avg_ms": 28,  "rps": 3500, "error_pct": 0.3, "min_ms": 5,  "max_ms": 280},
        500: {"avg_ms": 95,  "rps": 5100, "error_pct": 1.2, "min_ms": 6,  "max_ms": 950},
    },
    "GraphQL": {
        10:  {"avg_ms": 15,  "rps": 650,  "error_pct": 0.0, "min_ms": 4,  "max_ms": 60},
        50:  {"avg_ms": 25,  "rps": 1980, "error_pct": 0.2, "min_ms": 5,  "max_ms": 160},
        100: {"avg_ms": 42,  "rps": 2400, "error_pct": 0.5, "min_ms": 6,  "max_ms": 380},
        500: {"avg_ms": 148, "rps": 3300, "error_pct": 2.1, "min_ms": 7,  "max_ms": 1400},
    },
    "SOAP": {
        10:  {"avg_ms": 22,  "rps": 450,  "error_pct": 0.0, "min_ms": 6,  "max_ms": 85},
        50:  {"avg_ms": 38,  "rps": 1300, "error_pct": 0.3, "min_ms": 7,  "max_ms": 220},
        100: {"avg_ms": 65,  "rps": 1550, "error_pct": 0.8, "min_ms": 8,  "max_ms": 520},
        500: {"avg_ms": 210, "rps": 2350, "error_pct": 3.5, "min_ms": 9,  "max_ms": 2100},
    },
    "gRPC": {
        10:  {"avg_ms": 5,   "rps": 1900, "error_pct": 0.0, "min_ms": 1,  "max_ms": 18},
        50:  {"avg_ms": 8,   "rps": 6100, "error_pct": 0.0, "min_ms": 2,  "max_ms": 55},
        100: {"avg_ms": 13,  "rps": 7600, "error_pct": 0.1, "min_ms": 2,  "max_ms": 110},
        500: {"avg_ms": 42,  "rps": 11800,"error_pct": 0.4, "min_ms": 3,  "max_ms": 420},
    },
}


def carregar_dados_locust(results_dir: str) -> dict | None:
    """Tenta carregar dados reais dos CSVs gerados pelo Locust."""
    csvs = glob.glob(os.path.join(results_dir, "*_stats.csv"))
    if not csvs:
        return None
    dados = {}
    for csv_path in csvs:
        tech = os.path.basename(csv_path).split("_")[0].upper()
        dados[tech] = {}
        with open(csv_path) as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("Name") == "Aggregated":
                    # Locust usa campos em inglês
                    dados[tech][int(row.get("User count", 0))] = {
                        "avg_ms":    float(row.get("Average (ms)", 0)),
                        "rps":       float(row.get("Requests/s", 0)),
                        "error_pct": float(str(row.get("Failure %", 0)).replace("%","")),
                        "min_ms":    float(row.get("Min (ms)", 0)),
                        "max_ms":    float(row.get("Max (ms)", 0)),
                    }
    return dados if dados else None


# ── Gráfico 1: Tempo médio de resposta (barra agrupada) ────────

def plot_avg_response_time(dados: dict):
    x = np.arange(len(CARGAS))
    width = 0.2

    fig, ax = plt.subplots(figsize=(12, 6))
    for i, (tech, cor) in enumerate(zip(TECNOLOGIAS, CORES)):
        valores = [dados[tech][c]["avg_ms"] for c in CARGAS]
        bars = ax.bar(x + i * width, valores, width, label=tech, color=cor, alpha=0.85)
        ax.bar_label(bars, fmt="%.0f ms", padding=2, fontsize=9)

    ax.set_title("Tempo Médio de Resposta por Tecnologia e Carga", fontsize=14, fontweight="bold")
    ax.set_xlabel("Usuários Simultâneos")
    ax.set_ylabel("Tempo Médio (ms)")
    ax.set_xticks(x + width * 1.5)
    ax.set_xticklabels([str(c) for c in CARGAS])
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    path = os.path.join(GRAPH_DIR, "1_avg_response_time.png")
    plt.savefig(path)
    print(f"  Salvo: {path}")
    plt.close()


# ── Gráfico 2: RPS conforme aumento de carga (linhas) ─────────

def plot_rps(dados: dict):
    fig, ax = plt.subplots(figsize=(12, 6))
    for tech, cor in zip(TECNOLOGIAS, CORES):
        valores = [dados[tech][c]["rps"] for c in CARGAS]
        ax.plot(CARGAS, valores, marker="o", label=tech, color=cor, linewidth=2.5)
        for c, v in zip(CARGAS, valores):
            ax.annotate(f"{v:.0f}", (c, v), textcoords="offset points",
                        xytext=(0, 8), ha="center", fontsize=9, color=cor)

    ax.set_title("Requisições por Segundo (RPS) × Carga", fontsize=14, fontweight="bold")
    ax.set_xlabel("Usuários Simultâneos")
    ax.set_ylabel("Requisições por Segundo")
    ax.set_xticks(CARGAS)
    ax.legend()
    ax.grid(linestyle="--", alpha=0.5)
    plt.tight_layout()
    path = os.path.join(GRAPH_DIR, "2_rps_por_carga.png")
    plt.savefig(path)
    print(f"  Salvo: {path}")
    plt.close()


# ── Gráfico 3: Taxa de erros (barra agrupada) ─────────────────

def plot_error_rate(dados: dict):
    x = np.arange(len(CARGAS))
    width = 0.2

    fig, ax = plt.subplots(figsize=(12, 6))
    for i, (tech, cor) in enumerate(zip(TECNOLOGIAS, CORES)):
        valores = [dados[tech][c]["error_pct"] for c in CARGAS]
        bars = ax.bar(x + i * width, valores, width, label=tech, color=cor, alpha=0.85)
        ax.bar_label(bars, fmt="%.1f%%", padding=2, fontsize=9)

    ax.set_title("Taxa de Erros por Tecnologia e Carga", fontsize=14, fontweight="bold")
    ax.set_xlabel("Usuários Simultâneos")
    ax.set_ylabel("Taxa de Erros (%)")
    ax.set_xticks(x + width * 1.5)
    ax.set_xticklabels([str(c) for c in CARGAS])
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    path = os.path.join(GRAPH_DIR, "3_taxa_erros.png")
    plt.savefig(path)
    print(f"  Salvo: {path}")
    plt.close()


# ── Gráfico 4: Min/Max de resposta com 500 usuários (radar) ───

def plot_minmax_500(dados: dict):
    labels = ["Min (ms)", "Avg (ms)", "Max (ms)"]
    x = np.arange(len(labels))
    width = 0.2

    fig, ax = plt.subplots(figsize=(10, 6))
    for i, (tech, cor) in enumerate(zip(TECNOLOGIAS, CORES)):
        d = dados[tech][500]
        valores = [d["min_ms"], d["avg_ms"], d["max_ms"]]
        bars = ax.bar(x + i * width, valores, width, label=tech, color=cor, alpha=0.85)
        ax.bar_label(bars, fmt="%.0f", padding=2, fontsize=9)

    ax.set_title("Latência Mínima / Média / Máxima com 500 Usuários", fontsize=14, fontweight="bold")
    ax.set_ylabel("Tempo (ms)")
    ax.set_xticks(x + width * 1.5)
    ax.set_xticklabels(labels)
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    path = os.path.join(GRAPH_DIR, "4_minmax_500usuarios.png")
    plt.savefig(path)
    print(f"  Salvo: {path}")
    plt.close()


# ── Main ───────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Carregando dados...")
    dados = carregar_dados_locust(OUTPUT_DIR)

    if dados:
        print("Dados reais do Locust carregados.")
else:
    print("CSVs não encontrados. Usando dados de exemplo.")
dados = DADOS_EXEMPLO

print("\nGerando gráficos...")
plot_avg_response_time(dados)
plot_rps(dados)
plot_error_rate(dados)
plot_minmax_500(dados)

print(f"\n✔ Todos os gráficos salvos em: {GRAPH_DIR}/")
