# bankapp3.py
# App Streamlit – Análise Bancária / Telemarketing

import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO


# Aparência geral (Seaborn)

custom_params = {"axes.spines.right": False, "axes.spines.top": False}
sns.set_theme(style="ticks", rc=custom_params)



# Funções com cache


@st.cache_data(show_spinner=True)
def load_data(file_data):
    """Lê CSV (sep=';') ou Excel e devolve DataFrame."""
    try:
        return pd.read_csv(file_data, sep=";")
    except Exception:
        return pd.read_excel(file_data)


@st.cache_data
def multiselect_filter(df, col, selected):
    """Filtra DataFrame pela coluna col com base nas opções selecionadas."""
    if "all" in selected:
        return df
    return df[df[col].isin(selected)].reset_index(drop=True)


@st.cache_data
def convert_df(df):
    """Converte DataFrame para CSV (bytes)."""
    return df.to_csv(index=False).encode("utf-8")


@st.cache_data
def to_excel(df):
    """Converte DataFrame para Excel em memória (bytes)."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    return output.getvalue()


def carregar_imagem(caminhos):
    """Tenta carregar uma imagem a partir de uma lista de caminhos possíveis."""
    for caminho in caminhos:
        try:
            return Image.open(caminho)
        except Exception:
            continue
    return None



# Aplicação principal


def main():

    # Configuração da página (icone = telemarketing.png na mesma pasta)
    st.set_page_config(
        page_title="Análise Bancária – Telemarketing",
        page_icon="telemarketing.png",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Cabeçalho principal
    st.title("📊 Análise Bancária – Campanha de Telemarketing")

    st.info(
        """
        **Nessa atividade, você deve subir o arquivo que foi desenvolvido ao longo do módulo.  
        Será avaliado principalmente:**
        - As interações com o usuário  
        - A possibilidade de **subir arquivos**  
        - A disponibilização de resultados para **download**  
        """
    )

    st.markdown("---")

    # Imagem lateral (usa caminho relativo OU absoluto)
    sidebar_img = carregar_imagem(
        [
            "bank.png",
            r"C:\Users\aleva\OneDrive\Área de Trabalho\bankapp\bank.png",
        ]
    )
    if sidebar_img is not None:
        st.sidebar.image(sidebar_img, use_column_width=True)
    else:
        st.sidebar.warning("Imagem do banco não encontrada. Coloque 'bank.png' na mesma pasta do app.")

  
    # Upload de arquivo
   

    st.sidebar.header("📂 Suba o arquivo bancário")
    data_file = st.sidebar.file_uploader(
        "Escolha um arquivo CSV ou Excel (ex.: bank-additional-full-40.csv)",
        type=["csv", "xlsx"],
    )

    # Valores padrão para uso nas abas
    bank_raw = None
    bank_filtered = None
    graph_type = "Barras"

    # Só monta filtros se houver arquivo
    if data_file is not None:
        bank_raw = load_data(data_file)
        bank = bank_raw.copy()

      
        # Filtros na barra lateral
        
        with st.sidebar.form(key="filters_form"):

            st.subheader("⚙️ Filtros dos dados")

            graph_type = st.radio("Tipo de gráfico:", ("Barras", "Pizza"))

            # Idade
            idade_min = int(bank["age"].min())
            idade_max = int(bank["age"].max())
            idades = st.slider(
                "Faixa de idade",
                min_value=idade_min,
                max_value=idade_max,
                value=(idade_min, idade_max),
            )

            def build_list(col):
                lista = sorted(bank[col].dropna().unique().tolist())
                lista.append("all")
                return lista

            jobs_selected = st.multiselect("Profissão", build_list("job"), ["all"])
            marital_selected = st.multiselect("Estado civil", build_list("marital"), ["all"])
            default_selected = st.multiselect("Default", build_list("default"), ["all"])
            housing_selected = st.multiselect("Financiamento imóvel?", build_list("housing"), ["all"])
            loan_selected = st.multiselect("Empréstimo?", build_list("loan"), ["all"])
            contact_selected = st.multiselect("Meio de contato", build_list("contact"), ["all"])
            month_selected = st.multiselect("Mês do contato", build_list("month"), ["all"])
            dow_selected = st.multiselect("Dia da semana", build_list("day_of_week"), ["all"])

            st.form_submit_button("Aplicar filtros")

        # Aplica filtros (sempre coerentes com os valores selecionados)
        bank_filtered = (
            bank.query("age >= @idades[0] and age <= @idades[1]")
                .pipe(multiselect_filter, "job", jobs_selected)
                .pipe(multiselect_filter, "marital", marital_selected)
                .pipe(multiselect_filter, "default", default_selected)
                .pipe(multiselect_filter, "housing", housing_selected)
                .pipe(multiselect_filter, "loan", loan_selected)
                .pipe(multiselect_filter, "contact", contact_selected)
                .pipe(multiselect_filter, "month", month_selected)
                .pipe(multiselect_filter, "day_of_week", dow_selected)
        )

   
    # Abas da aplicação
    

    tab1, tab2, tab3, tab4 = st.tabs(
        ["📁 Upload & Dados", "🧹 Filtros & Tabela", "📊 Gráficos", "📥 Downloads"]
    )

    # TAB 1 
    with tab1:
        st.subheader("📁 Upload & visão inicial dos dados")

        if bank_raw is None:
            st.warning("Nenhum arquivo foi carregado ainda. Use a barra lateral para subir o dataset.")
        else:
            st.markdown("**Visualização das primeiras linhas da base original (sem filtros):**")
            st.dataframe(bank_raw.head())

            st.markdown("**Resumo das colunas:**")
            st.write(bank_raw.describe(include="all").transpose())

    #  TAB 2 
    with tab2:
        st.subheader("🧹 Dados após aplicação dos filtros")

        if bank_filtered is None:
            st.warning("Suba um arquivo na barra lateral para aplicar filtros.")
        else:
            st.markdown("**Primeiras linhas da tabela filtrada:**")
            st.dataframe(bank_filtered.head())

            st.markdown(f"**Quantidade de linhas após filtros:** {len(bank_filtered)}")

    # TAB 3
    with tab3:
        st.subheader("📊 Proporção de aceite (variável alvo `y`)")

        if bank_raw is None or bank_filtered is None:
            st.warning("Suba o arquivo e aplique filtros para visualizar os gráficos.")
        else:
            # Proporções
            bank_raw_perc = bank_raw["y"].value_counts(normalize=True).sort_index() * 100
            bank_filt_perc = bank_filtered["y"].value_counts(normalize=True).sort_index() * 100

            col_raw, col_filt = st.columns(2)

            col_raw.write("### Proporção original")
            col_raw.dataframe(bank_raw_perc.to_frame("percentual"))

            col_filt.write("### Proporção com filtros")
            col_filt.dataframe(bank_filt_perc.to_frame("percentual"))

            st.markdown("---")

            fig, ax = plt.subplots(1, 2, figsize=(10, 4))

            if graph_type == "Barras":
                # Dados brutos
                sns.barplot(
                    x=bank_raw_perc.index,
                    y=bank_raw_perc.values,
                    ax=ax[0],
                )
                ax[0].set_title("Dados brutos")
                ax[0].set_ylabel("Percentual (%)")

                # Dados filtrados
                sns.barplot(
                    x=bank_filt_perc.index,
                    y=bank_filt_perc.values,
                    ax=ax[1],
                )
                ax[1].set_title("Dados filtrados")
                ax[1].set_ylabel("Percentual (%)")

            else:  # Pizza
                bank_raw_perc.plot(kind="pie", autopct="%.2f%%", ax=ax[0])
                ax[0].set_title("Dados brutos")
                ax[0].set_ylabel("")

                bank_filt_perc.plot(kind="pie", autopct="%.2f%%", ax=ax[1])
                ax[1].set_title("Dados filtrados")
                ax[1].set_ylabel("")

            st.pyplot(fig)

    # TAB 4
    with tab4:
        st.subheader("📥 Downloads")

        if bank_filtered is None:
            st.warning("Suba um arquivo e aplique filtros para gerar downloads.")
        else:
            st.markdown("Você pode baixar a tabela filtrada em **Excel** ou **CSV**.")

            df_excel = to_excel(bank_filtered)
            df_csv = convert_df(bank_filtered)

            col1, col2 = st.columns(2)

            col1.download_button(
                label="📥 Download EXCEL (analise_bancaria_filtrada.xlsx)",
                data=df_excel,
                file_name="analise_bancaria_filtrada.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

            col2.download_button(
                label="📥 Download CSV (analise_bancaria_filtrada.csv)",
                data=df_csv,
                file_name="analise_bancaria_filtrada.csv",
                mime="text/csv",
            )

            st.markdown(
                """
                > 💡 **Dica**: esses arquivos podem ser anexados na plataforma da EBAC
                como entrega da atividade de análise bancária.
                """
            )


if __name__ == "__main__":
    main()









