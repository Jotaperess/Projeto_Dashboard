
import pandas as pd
import streamlit as st
from scipy import stats

st.set_page_config(
    page_title="Seoul Bike",
    page_icon="🚲",
    layout="wide"
)

CORES = {
    "Inverno": "#579BD3",
    "Primavera": "#40AA82",
    "Verão": "#EFB742",
    "Outono": "#D97B55"
}


@st.cache_data
def carregar_dados():
    dados = pd.read_csv("SeoulBikeData.csv", encoding="latin1")

    dados = dados.rename(columns={
        "Date": "Data",
        "Rented Bike Count": "Alugueis",
        "Hour": "Hora",
        dados.columns[3]: "Temperatura",
        "Rainfall(mm)": "Chuva",
        "Seasons": "Estacao",
        "Functioning Day": "Funcionamento"
    })

    dados["Data"] = pd.to_datetime(
        dados["Data"], format="%d/%m/%Y", errors="coerce"
    )

    dados["Estacao"] = dados["Estacao"].replace({
        "Winter": "Inverno",
        "Spring": "Primavera",
        "Summer": "Verão",
        "Autumn": "Outono"
    })

    dados = dados.drop_duplicates(subset=["Data", "Hora"])
    dados = dados.dropna(subset=[
        "Data", "Alugueis", "Temperatura",
        "Chuva", "Hora", "Estacao"
    ])

    dados = dados[
        (dados["Funcionamento"] == "Yes") &
        (dados["Alugueis"] >= 0)
    ].copy()

    dados["FimSemana"] = dados["Data"].dt.dayofweek >= 5

    return dados


try:
    df = carregar_dados()
except FileNotFoundError:
    st.error("Coloque SeoulBikeData.csv na pasta do projeto.")
    st.stop()

if df.empty:
    st.error("Nenhum registro válido foi encontrado.")
    st.stop()


st.markdown("""
<div style="
    background:linear-gradient(110deg,#115E59,#0D9488);
    padding:24px 28px;
    border-radius:16px;
    margin-bottom:12px;
    color:white;
">
    <div style="font-size:12px;letter-spacing:2px;color:#D1FAE5">
        MOBILIDADE URBANA • SEUL
    </div>
    <div style="font-size:34px;font-weight:750;margin:5px 0;color:white">
        🚲 Seoul Bike
    </div>
    <div style="color:#E6FFFB;font-size:15px">
        Exploração estatística da demanda por bicicletas compartilhadas
    </div>
</div>
""", unsafe_allow_html=True)


with st.container(border=True):
    st.markdown("**Personalize os dados exibidos**")

    col1, col2 = st.columns(2)

    with col1:
        estacao = st.selectbox(
            "Estação do ano",
            ["Todas", "Inverno", "Primavera", "Verão", "Outono"]
        )

    with col2:
        tipo = st.selectbox(
            "Tipo de dia",
            ["Todos", "Dias úteis", "Fim de semana"]
        )


filtro = df.copy()

if estacao != "Todas":
    filtro = filtro[filtro["Estacao"] == estacao]

if tipo == "Dias úteis":
    filtro = filtro[~filtro["FimSemana"]]
elif tipo == "Fim de semana":
    filtro = filtro[filtro["FimSemana"]]

if filtro.empty:
    st.warning("Não há registros para esses filtros.")
    st.stop()


st.subheader("Visão geral")

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.metric(
        "🚲 Total de aluguéis",
        f"{filtro['Alugueis'].sum():,.0f}".replace(",", "."),
        border=True
    )

with m2:
    st.metric(
        "📊 Média por hora",
        f"{filtro['Alugueis'].mean():.1f}",
        border=True
    )

with m3:
    st.metric(
        "🌡️ Temperatura média",
        f"{filtro['Temperatura'].mean():.1f} °C",
        border=True
    )

with m4:
    st.metric(
        "📅 Dias analisados",
        str(filtro["Data"].nunique()),
        border=True
    )


st.subheader("Perfil da demanda")

g1, g2 = st.columns(2, gap="medium")

with g1:
    with st.container(border=True):
        st.markdown("#### Aluguéis ao longo do dia")

        horario = filtro.groupby(
            "Hora", as_index=False
        )["Alugueis"].mean()

        st.bar_chart(
            horario,
            x="Hora",
            y="Alugueis",
            color="#0D9488",
            height=285,
            x_label="Hora do dia",
            y_label="Média de aluguéis"
        )

        st.caption("Média de aluguéis registrados em cada hora.")


with g2:
    with st.container(border=True):
        st.markdown("#### Comparação entre estações")

        estacoes = filtro.groupby(
            "Estacao", as_index=False
        )["Alugueis"].mean()

        ordem = ["Inverno", "Primavera", "Verão", "Outono"]

        st.vega_lite_chart(
            estacoes,
            {
                "mark": {
                    "type": "bar",
                    "cornerRadiusEnd": 5
                },
                "encoding": {
                    "x": {
                        "field": "Estacao",
                        "type": "nominal",
                        "sort": ordem,
                        "title": "Estação do ano"
                    },
                    "y": {
                        "field": "Alugueis",
                        "type": "quantitative",
                        "title": "Média de aluguéis"
                    },
                    "color": {
                        "field": "Estacao",
                        "type": "nominal",
                        "scale": {
                            "domain": ordem,
                            "range": [CORES[e] for e in ordem]
                        },
                        "legend": None
                    },
                    "tooltip": [
                        {"field": "Estacao", "type": "nominal"},
                        {
                            "field": "Alugueis",
                            "type": "quantitative",
                            "format": ".1f"
                        }
                    ]
                },
                "height": 260
            },
            use_container_width=True
        )

        st.caption(
            "🟦 Inverno · 🟩 Primavera · 🟨 Verão · 🟧 Outono"
        )


with st.container(border=True):
    st.markdown("#### Temperatura e quantidade de aluguéis")

    st.scatter_chart(
        filtro,
        x="Temperatura",
        y="Alugueis",
        color="Temperatura",
        height=310,
        x_label="Temperatura (°C)",
        y_label="Aluguéis por hora"
    )

    st.caption(
        "A escala de cores representa a temperatura registrada."
    )


with st.container(border=True):
    st.markdown("#### Evolução mensal da demanda")

    mensal = filtro.groupby(
        filtro["Data"].dt.to_period("M")
    )["Alugueis"].mean().sort_index()

    mensal.index = mensal.index.astype(str)

    st.line_chart(
        mensal,
        color="#6D78C7",
        height=255,
        x_label="Mês",
        y_label="Média de aluguéis por hora"
    )

    st.caption(
        "Os dados são agrupados por mês, utilizando a média "
        "de aluguéis por hora."
    )


with st.expander("Consultar dados e estatísticas descritivas"):
    st.markdown("#### Estatísticas descritivas")

    estatisticas = filtro["Alugueis"].describe()

    estatisticas.index = [
        "Quantidade",
        "Média",
        "Desvio-padrão",
        "Mínimo",
        "1º quartil",
        "Mediana",
        "3º quartil",
        "Máximo"
    ]

    st.dataframe(
        estatisticas.to_frame("Aluguéis").round(2),
        use_container_width=True
    )

    st.markdown("#### Dados brutos")

    st.dataframe(
        filtro.sort_values(["Data", "Hora"]),
        use_container_width=True,
        hide_index=True,
        height=350
    )


st.divider()
st.subheader("Testes de hipóteses")

st.caption(
    "Comparações de médias diárias com teste t de Welch "
    "e intervalos de confiança de 95%."
)

diario = df.groupby("Data").agg(
    Media=("Alugueis", "mean"),
    Chuva=("Chuva", "sum"),
    FimSemana=("FimSemana", "first"),
    Temperatura=("Temperatura", "mean")
).sort_index()

diario["Choveu"] = diario["Chuva"] > 0


def analisar(grupo_a, grupo_b):
    resultado = stats.ttest_ind(
        grupo_a, grupo_b, equal_var=False
    )

    ic = resultado.confidence_interval(
        confidence_level=0.95
    )

    return resultado.pvalue, ic.low, ic.high


def grafico_teste(
    titulo, grupo_a, nome_a, cor_a,
    grupo_b, nome_b, cor_b
):
    p, minimo, maximo = analisar(grupo_a, grupo_b)

    dados = pd.DataFrame({
        "Grupo": [nome_a, nome_b],
        "Média": [grupo_a.mean(), grupo_b.mean()]
    })

    with st.container(border=True):
        st.markdown(f"#### {titulo}")

        st.vega_lite_chart(
            dados,
            {
                "mark": {
                    "type": "bar",
                    "cornerRadiusEnd": 5
                },
                "encoding": {
                    "x": {
                        "field": "Grupo",
                        "type": "nominal",
                        "sort": [nome_a, nome_b],
                        "title": "Grupo"
                    },
                    "y": {
                        "field": "Média",
                        "type": "quantitative",
                        "title": "Média de aluguéis por hora"
                    },
                    "color": {
                        "field": "Grupo",
                        "type": "nominal",
                        "scale": {
                            "domain": [nome_a, nome_b],
                            "range": [cor_a, cor_b]
                        },
                        "legend": None
                    },
                    "tooltip": [
                        {"field": "Grupo", "type": "nominal"},
                        {
                            "field": "Média",
                            "type": "quantitative",
                            "format": ".1f"
                        }
                    ]
                },
                "height": 250
            },
            use_container_width=True
        )

        valor_p = (
            "< 0,0001" if p < 0.0001
            else f"{p:.4f}".replace(".", ",")
        )

        st.metric("Valor-p", valor_p)

        st.caption(
            f"IC 95% da diferença: "
            f"[{minimo:.2f}; {maximo:.2f}]"
        )

        st.caption(
            f"Amostra: {len(grupo_a)} e {len(grupo_b)} dias."
        )

    return [
        titulo,
        round(grupo_a.mean() - grupo_b.mean(), 2),
        round(p, 5),
        f"[{minimo:.2f}; {maximo:.2f}]"
    ]


chuva = diario.loc[diario["Choveu"], "Media"]
sem_chuva = diario.loc[~diario["Choveu"], "Media"]

fins = diario.loc[diario["FimSemana"], "Media"]
uteis = diario.loc[~diario["FimSemana"], "Media"]


h1, h2 = st.columns(2, gap="medium")

with h1:
    r1 = grafico_teste(
        "Chuva × Sem chuva",
        chuva, "Com chuva", "#579BD3",
        sem_chuva, "Sem chuva", "#EFB742"
    )

with h2:
    r2 = grafico_teste(
        "Fim de semana × Dias úteis",
        fins, "Fim de semana", "#D97B55",
        uteis, "Dias úteis", "#40AA82"
    )


with st.expander("Tabela dos resultados dos testes"):
    resultados = pd.DataFrame(
        [r1, r2],
        columns=[
            "Teste",
            "Diferença de médias",
            "Valor-p",
            "IC 95%"
        ]
    )

    st.dataframe(
        resultados,
        use_container_width=True,
        hide_index=True
    )

st.caption(
    "Os testes utilizam o conjunto completo de dados, "
    "sem aplicar os filtros. Diferenças não comprovam causalidade."
)


st.divider()
st.subheader("Regressão linear")

st.caption(
    "Estimativa da média diária de aluguéis por hora "
    "a partir da temperatura média diária."
)

corte = int(len(diario) * 0.8)

treino = diario.iloc[:corte]
teste = diario.iloc[corte:].copy()

modelo = stats.linregress(
    treino["Temperatura"],
    treino["Media"]
)

teste["Previsto"] = (
    modelo.intercept +
    modelo.slope * teste["Temperatura"]
).clip(lower=0)

teste["Real"] = teste["Media"]

erro = teste["Real"] - teste["Previsto"]

mae = erro.abs().mean()
rmse = (erro.pow(2).mean()) ** 0.5

total = (
    (teste["Real"] - teste["Real"].mean()) ** 2
).sum()

r_quadrado = (
    1 - erro.pow(2).sum() / total
    if total > 0 else float("nan")
)


rcol1, rcol2, rcol3 = st.columns(3)

with rcol1:
    st.metric(
        "Erro médio (MAE)",
        f"{mae:.1f}",
        border=True
    )

with rcol2:
    st.metric(
        "Erro quadrático (RMSE)",
        f"{rmse:.1f}",
        border=True
    )

with rcol3:
    st.metric(
        "R² no teste",
        f"{r_quadrado:.3f}",
        border=True
    )


with st.container(border=True):
    st.markdown("#### Valores reais × previstos")

    st.line_chart(
        teste[["Real", "Previsto"]],
        color=["#579BD3", "#0D9488"],
        height=310,
        x_label="Data",
        y_label="Média de aluguéis por hora"
    )

    st.caption(
        "Azul: valores reais. Verde: estimativas do modelo."
    )


with st.expander("Detalhes do modelo"):
    st.write(
        f"Equação: Y = {modelo.intercept:.2f} "
        f"+ ({modelo.slope:.2f} × Temperatura)"
    )

    st.write(
        "Treinamento: primeiros 80% dos dias. "
        "Teste: últimos 20% dos dias."
    )

    st.dataframe(
        teste[["Temperatura", "Real", "Previsto"]].round(2),
        use_container_width=True
    )


st.divider()

st.caption(
    "Fonte: Seoul Bike Sharing Demand — "
    "UCI Machine Learning Repository (2017–2018)."
)
