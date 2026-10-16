
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
        "Temperature(°C)": "Temperatura",
        "Rainfall(mm)": "Chuva",
        "Seasons": "Estacao",
        "Functioning Day": "Funcionamento"
    })

    dados["Data"] = pd.to_datetime(
        dados["Data"],
        format="%d/%m/%Y",
        errors="coerce"
    )

    dados["Estacao"] = dados["Estacao"].replace({
        "Winter": "Inverno",
        "Spring": "Primavera",
        "Summer": "Verão",
        "Autumn": "Outono"
    })

    dados = dados.drop_duplicates(subset=["Data", "Hora"])

    dados = dados.dropna(subset=[
        "Data",
        "Alugueis",
        "Temperatura",
        "Chuva",
        "Hora",
        "Estacao"
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

    f1, f2 = st.columns(2)

    with f1:
        estacao = st.selectbox(
            "Estação do ano",
            ["Todas", "Inverno", "Primavera", "Verão", "Outono"]
        )

    with f2:
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

        st.caption(
            "Média de aluguéis registrados em cada hora."
        )


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
                        "title": "Estação"
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
                        {
                            "field": "Estacao",
                            "type": "nominal"
                        },
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
        "Cada ponto representa a média de aluguéis "
        "por hora naquele mês."
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
    "Teste t de Welch comparando médias diárias de aluguéis por hora. "
    "Cada ponto representa um dia; losangos mostram as médias dos grupos."
)


diario = df.groupby("Data").agg(
    Media=("Alugueis", "mean"),
    Chuva=("Chuva", "sum"),
    FimSemana=("FimSemana", "first"),
    Temperatura=("Temperatura", "mean")
).sort_index()

diario["Choveu"] = diario["Chuva"] > 0


def grafico_teste(
    titulo,
    grupo_a,
    grupo_b,
    nome_a,
    nome_b,
    cor_a,
    cor_b
):
    if len(grupo_a) < 2 or len(grupo_b) < 2:
        st.warning(f"Dados insuficientes para {titulo}.")
        return None

    media_a = grupo_a.mean()
    media_b = grupo_b.mean()
    diferenca = media_a - media_b

    teste = stats.ttest_ind(
        grupo_a,
        grupo_b,
        equal_var=False
    )

    ic_diferenca = teste.confidence_interval(
        confidence_level=0.95
    )

    ic_a = stats.t.interval(
        0.95,
        len(grupo_a) - 1,
        loc=media_a,
        scale=stats.sem(grupo_a)
    )

    ic_b = stats.t.interval(
        0.95,
        len(grupo_b) - 1,
        loc=media_b,
        scale=stats.sem(grupo_b)
    )

    pontos = pd.concat([
        grupo_a.reset_index().assign(
            Grupo=nome_a,
            Centro=1
        ),
        grupo_b.reset_index().assign(
            Grupo=nome_b,
            Centro=2
        )
    ], ignore_index=True)

    pontos = pontos.rename(columns={
        "Media": "MediaDiaria"
    })

    pontos["Posicao"] = pontos["Centro"] + [
        ((i * 17) % 29 - 14) / 65
        for i in range(len(pontos))
    ]

    medias = pd.DataFrame({
        "Grupo": [nome_a, nome_b],
        "Centro": [1, 2],
        "MediaDiaria": [media_a, media_b],
        "IC_Inferior": [ic_a[0], ic_b[0]],
        "IC_Superior": [ic_a[1], ic_b[1]]
    })

    cores = {
        "field": "Grupo",
        "type": "nominal",
        "scale": {
            "domain": [nome_a, nome_b],
            "range": [cor_a, cor_b]
        },
        "legend": {
            "title": None,
            "orient": "top"
        }
    }

    with st.container(border=True):
        st.markdown(f"#### {titulo}")

        st.markdown(
            "**Médias diárias e intervalos de confiança de 95%**"
        )

        st.vega_lite_chart(
            pontos,
            {
                "layer": [
                    {
                        "mark": {
                            "type": "circle",
                            "size": 55,
                            "opacity": 0.4
                        },
                        "encoding": {
                            "x": {
                                "field": "MediaDiaria",
                                "type": "quantitative",
                                "title": "Média de aluguéis por hora no dia"
                            },
                            "y": {
                                "field": "Posicao",
                                "type": "quantitative",
                                "scale": {
                                    "domain": [0.55, 2.45]
                                },
                                "axis": {
                                    "title": None,
                                    "values": [1, 2],
                                    "grid": False,
                                    "labelExpr": (
                                        f"datum.value == 1 ? "
                                        f"'{nome_a}' : '{nome_b}'"
                                    )
                                }
                            },
                            "color": cores,
                            "tooltip": [
                                {
                                    "field": "Data",
                                    "type": "temporal",
                                    "format": "%d/%m/%Y"
                                },
                                {
                                    "field": "Grupo",
                                    "type": "nominal"
                                },
                                {
                                    "field": "MediaDiaria",
                                    "type": "quantitative",
                                    "format": ".1f"
                                }
                            ]
                        }
                    },
                    {
                        "data": {
                            "values": medias.to_dict(
                                orient="records"
                            )
                        },
                        "mark": {
                            "type": "rule",
                            "strokeWidth": 7
                        },
                        "encoding": {
                            "x": {
                                "field": "IC_Inferior",
                                "type": "quantitative"
                            },
                            "x2": {
                                "field": "IC_Superior"
                            },
                            "y": {
                                "field": "Centro",
                                "type": "quantitative"
                            },
                            "color": {
                                **cores,
                                "legend": None
                            },
                            "tooltip": [
                                {
                                    "field": "Grupo",
                                    "type": "nominal"
                                },
                                {
                                    "field": "IC_Inferior",
                                    "title": "IC inferior",
                                    "format": ".2f"
                                },
                                {
                                    "field": "IC_Superior",
                                    "title": "IC superior",
                                    "format": ".2f"
                                }
                            ]
                        }
                    },
                    {
                        "data": {
                            "values": medias.to_dict(
                                orient="records"
                            )
                        },
                        "mark": {
                            "type": "point",
                            "shape": "diamond",
                            "filled": True,
                            "size": 280,
                            "stroke": "white",
                            "strokeWidth": 1.5
                        },
                        "encoding": {
                            "x": {
                                "field": "MediaDiaria",
                                "type": "quantitative"
                            },
                            "y": {
                                "field": "Centro",
                                "type": "quantitative"
                            },
                            "color": {
                                **cores,
                                "legend": None
                            },
                            "tooltip": [
                                {
                                    "field": "Grupo",
                                    "type": "nominal"
                                },
                                {
                                    "field": "MediaDiaria",
                                    "title": "Média do grupo",
                                    "format": ".2f"
                                }
                            ]
                        }
                    }
                ],
                "height": 230
            },
            use_container_width=True
        )

        st.caption(
            "Pontos: médias dos dias. "
            "Losangos: médias dos grupos. "
            "Barras coloridas: IC de 95% de cada média."
        )

        c1, c2 = st.columns(2)

        with c1:
            st.metric(
                f"Média: {nome_a}",
                f"{media_a:.1f}"
            )

            st.caption(
                f"IC 95%: [{ic_a[0]:.1f}; {ic_a[1]:.1f}]"
            )

        with c2:
            st.metric(
                f"Média: {nome_b}",
                f"{media_b:.1f}"
            )

            st.caption(
                f"IC 95%: [{ic_b[0]:.1f}; {ic_b[1]:.1f}]"
            )

        st.divider()

        st.markdown(
            "**Intervalo de confiança da diferença entre médias**"
        )

        intervalo = pd.DataFrame({
            "Inferior": [float(ic_diferenca.low)],
            "Superior": [float(ic_diferenca.high)],
            "Diferenca": [float(diferenca)],
            "Linha": ["Diferença"]
        })

        st.vega_lite_chart(
            intervalo,
            {
                "layer": [
                    {
                        "mark": {
                            "type": "rule",
                            "color": "#94A3B8",
                            "strokeDash": [5, 5]
                        },
                        "encoding": {
                            "x": {
                                "datum": 0,
                                "type": "quantitative"
                            }
                        }
                    },
                    {
                        "mark": {
                            "type": "rule",
                            "color": "#0D9488",
                            "strokeWidth": 7
                        },
                        "encoding": {
                            "x": {
                                "field": "Inferior",
                                "type": "quantitative",
                                "title": f"Diferença: {nome_a} − {nome_b}"
                            },
                            "x2": {
                                "field": "Superior"
                            },
                            "y": {
                                "field": "Linha",
                                "type": "nominal",
                                "axis": None
                            }
                        }
                    },
                    {
                        "mark": {
                            "type": "point",
                            "shape": "diamond",
                            "filled": True,
                            "color": "#115E59",
                            "size": 210
                        },
                        "encoding": {
                            "x": {
                                "field": "Diferenca",
                                "type": "quantitative"
                            },
                            "y": {
                                "field": "Linha",
                                "type": "nominal",
                                "axis": None
                            },
                            "tooltip": [
                                {
                                    "field": "Diferenca",
                                    "title": "Diferença",
                                    "format": ".2f"
                                },
                                {
                                    "field": "Inferior",
                                    "title": "IC inferior",
                                    "format": ".2f"
                                },
                                {
                                    "field": "Superior",
                                    "title": "IC superior",
                                    "format": ".2f"
                                }
                            ]
                        }
                    }
                ],
                "height": 70
            },
            use_container_width=True
        )

        st.caption(
            "Linha pontilhada: diferença zero. "
            "Segmento verde: IC de 95% da diferença."
        )

        c3, c4 = st.columns(2)

        valor_p = (
            "< 0,0001"
            if teste.pvalue < 0.0001
            else f"{teste.pvalue:.4f}".replace(".", ",")
        )

        with c3:
            st.metric(
                "Valor-p",
                valor_p
            )

        with c4:
            st.metric(
                "Diferença estimada",
                f"{diferenca:.1f}"
            )

        st.caption(
            f"IC 95% da diferença: "
            f"[{ic_diferenca.low:.2f}; {ic_diferenca.high:.2f}]"
        )

        st.caption(
            f"Amostras: {len(grupo_a)} e {len(grupo_b)} dias."
        )

    return {
        "Teste": titulo,
        "Diferença de médias": round(diferenca, 2),
        "Valor-p": round(float(teste.pvalue), 5),
        "IC 95%": (
            f"[{ic_diferenca.low:.2f}; "
            f"{ic_diferenca.high:.2f}]"
        )
    }


chuva = diario.loc[diario["Choveu"], "Media"]
sem_chuva = diario.loc[~diario["Choveu"], "Media"]

fins = diario.loc[diario["FimSemana"], "Media"]
uteis = diario.loc[~diario["FimSemana"], "Media"]


h1, h2 = st.columns(2, gap="medium")

with h1:
    resultado1 = grafico_teste(
        "Chuva × Sem chuva",
        chuva,
        sem_chuva,
        "Com chuva",
        "Sem chuva",
        "#579BD3",
        "#EFB742"
    )

with h2:
    resultado2 = grafico_teste(
        "Fim de semana × Dias úteis",
        fins,
        uteis,
        "Fim de semana",
        "Dias úteis",
        "#D97B55",
        "#40AA82"
    )


with st.expander("Tabela dos resultados estatísticos"):
    resultados = pd.DataFrame([
        r for r in [resultado1, resultado2]
        if r is not None
    ])

    st.dataframe(
        resultados,
        use_container_width=True,
        hide_index=True
    )


st.caption(
    "Os testes usam todos os dias disponíveis, "
    "sem os filtros superiores. "
    "As observações são médias diárias; "
    "os testes consideram variâncias diferentes. "
    "A dependência entre dias pode afetar a inferência. "
    "Associação não comprova causalidade."
)


st.divider()
st.subheader("Regressão linear")

st.caption(
    "Relação entre a temperatura média diária "
    "e a média diária de aluguéis por hora."
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
    if total > 0
    else float("nan")
)


r1, r2, r3 = st.columns(3)

with r1:
    st.metric(
        "Erro médio (MAE)",
        f"{mae:.1f}",
        border=True
    )

with r2:
    st.metric(
        "Erro quadrático (RMSE)",
        f"{rmse:.1f}",
        border=True
    )

with r3:
    st.metric(
        "R² no teste",
        f"{r_quadrado:.3f}",
        border=True
    )


with st.container(border=True):
    st.markdown(
        "#### Temperatura × Demanda — Regressão linear"
    )

    grafico = teste[
        ["Temperatura", "Real", "Previsto"]
    ].reset_index().sort_values("Temperatura")

    st.vega_lite_chart(
        grafico,
        {
            "layer": [
                {
                    "mark": {
                        "type": "circle",
                        "size": 75,
                        "opacity": 0.7,
                        "color": "#579BD3"
                    },
                    "encoding": {
                        "x": {
                            "field": "Temperatura",
                            "type": "quantitative",
                            "title": "Temperatura média diária (°C)"
                        },
                        "y": {
                            "field": "Real",
                            "type": "quantitative",
                            "title": "Média de aluguéis por hora"
                        },
                        "tooltip": [
                            {
                                "field": "Data",
                                "type": "temporal",
                                "format": "%d/%m/%Y"
                            },
                            {
                                "field": "Temperatura",
                                "type": "quantitative",
                                "format": ".1f"
                            },
                            {
                                "field": "Real",
                                "title": "Aluguéis observados",
                                "format": ".1f"
                            }
                        ]
                    }
                },
                {
                    "mark": {
                        "type": "line",
                        "color": "#0D9488",
                        "strokeWidth": 3
                    },
                    "encoding": {
                        "x": {
                            "field": "Temperatura",
                            "type": "quantitative"
                        },
                        "y": {
                            "field": "Previsto",
                            "type": "quantitative"
                        },
                        "tooltip": [
                            {
                                "field": "Temperatura",
                                "type": "quantitative",
                                "format": ".1f"
                            },
                            {
                                "field": "Previsto",
                                "title": "Aluguéis previstos",
                                "format": ".1f"
                            }
                        ]
                    }
                }
            ],
            "height": 340
        },
        use_container_width=True
    )

    st.caption(
        "Azul: médias diárias observadas. "
        "Verde: estimativas da regressão. "
        "Gráfico dos dias do conjunto de teste."
    )


with st.expander("Detalhes do modelo"):
    st.write(
        f"Equação: Y = {modelo.intercept:.2f} "
        f"+ ({modelo.slope:.2f} × Temperatura)"
    )

    st.write("Treinamento: primeiros 80% dos dias.")
    st.write("Teste: últimos 20% dos dias.")

    st.dataframe(
        teste[["Temperatura", "Real", "Previsto"]].round(2),
        use_container_width=True
    )


st.divider()

st.caption(
    "Fonte: Seoul Bike Sharing Demand — "
    "UCI Machine Learning Repository (2017–2018)."
)
