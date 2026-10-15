# Projeto Dashboard — versão simplificada

## O que mudou

- Notebook reduzido a análises centrais: preparação, tabelas, três gráficos, dois testes t de Welch, intervalo de confiança, regressão linear simples e aplicação dos horários prioritários.
- Dashboard em **uma página**, com visual claro (verde e branco), **dois filtros**, três gráficos principais, testes e previsão.
- Apenas **quatro bibliotecas**: pandas, matplotlib, scipy e streamlit.
- Sem comentários nas células Python do notebook; explicações ficam nas células Markdown.

## Como usar

1. Mantenha `SeoulBikeData.csv` na mesma pasta destes arquivos.
2. No terminal, rode `py -m pip install -r requirements.txt`.
3. Abra `tratamento.ipynb` no VS Code/Jupyter e execute tudo.
4. Para o painel: `py -m streamlit run dashboard.py`.

## O que observar na defesa

- A análise considera apenas horas com o serviço funcionando; zeros em dias sem funcionamento não significam baixa procura.
- Nos testes, usamos uma média por dia em vez de tratar todas as horas do dia como independentes. Ainda pode existir dependência temporal entre dias.
- A regressão prevê a **média de aluguéis por hora em um dia**, usando temperatura média do mesmo dia. A previsão exige conhecer ou estimar previamente essa temperatura.
- A qualidade da regressão é apresentada com MAE, RMSE e R² no período de teste; o desempenho pode ser fraco. Isso também é um resultado relevante.
- Os horários prioritários são escolhidos com a amostra de treinamento e avaliados no teste. **Não representam quantidade de bicicletas a realocar**.
- O dashboard evita frases que entreguem interpretações: o público explora gráficos e resultados numéricos.

## Importante

Os resultados estatísticos definitivos dependem de executar o código com o **CSV original**. Não use números de arquivos sintéticos como conclusões reais. As bibliotecas `matplotlib` e `streamlit` cuidam dos gráficos; `pandas`, das tabelas; `scipy`, dos testes e da regressão.
