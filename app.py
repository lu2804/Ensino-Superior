#pip install streamlit plotly pandas
import streamlit as st
import pandas as pd
import plotly.express as px
import os 

# --- Configurações Iniciais do Streamlit ---
# Define o layout da página para ser amplo e o título que aparece na aba do navegador.
st.set_page_config(layout="wide", page_title="Educação Superior RIDE/DF")

# Título principal do aplicativo
st.title("🎓 Análise da Educação Superior na RIDE/DF")
# Descrição introdutória
st.markdown("Este painel interativo permite explorar dados sobre instituições e docentes de ensino superior na Região Integrada de Desenvolvimento do Distrito Federal e Entorno (RIDE/DF).")

# --- Função para Carregar e Pré-processar os Dados ---
# Usa @st.cache_data para armazenar em cache o DataFrame.
# Isso evita que os dados sejam recarregados e processados toda vez que o usuário interage com o app,
# tornando-o muito mais rápido.
@st.cache_data
def carregar_dados():
   
    try:
        # Define o nome do arquivo CSV
        csv_file_name = "table_EDUCACAO_SUPERIOR_RIDE_DF.csv"
        
        # Constrói o caminho completo para o CSV usando o diretório do script atual
        script_dir = os.path.dirname(__file__)
        csv_file_path_absolute = os.path.join(script_dir, csv_file_name)
        
        # DEBUG: Imprime o caminho completo que o script está tentando acessar (na UI do Streamlit)
        st.info(f"Tentando carregar o CSV de: `{csv_file_path_absolute}`")
        
        # Verifica se o arquivo existe antes de tentar carregar
        if not os.path.exists(csv_file_path_absolute):
            st.error(f"Erro: O arquivo '{csv_file_name}' não foi encontrado.")
            st.error(f"Por favor, coloque o arquivo CSV na mesma pasta do 'app.py'."
                     f" O caminho absoluto que o script esperava encontrar o CSV é: `{csv_file_path_absolute}`")
            return pd.DataFrame() # Retorna um DataFrame vazio para evitar erros posteriores

        # Carrega o CSV usando o separador ';' e codificação 'utf-8'
        df = pd.read_csv(csv_file_path_absolute, sep=';', encoding='utf-8')
        
        # --- Verificação de Colunas Essenciais ---
        # Lista de nomes de colunas esperados no arquivo CSV original.
        required_original_cols = [
            'NU_ANO_CENSO', 'CO_MUNICIPIO_IES', 'nome_municipio', 'IN_CAPITAL_IES',
            'TP_ORGANIZACAO_ACADEMICA', 'TP_REDE', 'TP_CATEGORIA_ADMINISTRATIVA',
            'NO_IES', 'SG_IES', 'QT_DOC_TOTAL', 'QT_TEC_TOTAL', 'NO_MANTENEDORA',
            'QT_DOC_EX_SEM_GRAD', 'QT_DOC_EX_GRAD', 'QT_DOC_EX_ESP',
            'QT_DOC_EX_MEST', 'QT_DOC_EX_DOUT',
            'QT_LIVRO_ELETRONICO', 
            'QT_DOC_EX_FEMI', 
            'QT_DOC_EX_MASC' 
        ]
        
        missing_cols = [col for col in required_original_cols if col not in df.columns]
        if missing_cols:
            st.error(f"Erro: As seguintes colunas essenciais não foram encontradas no arquivo CSV: {', '.join(missing_cols)}."
                     f" Verifique se o arquivo está correto e se os nomes das colunas correspondem (sensível a maiúsculas/minúsculas).")
            return pd.DataFrame()

        # Renomeia colunas para nomes mais amigáveis
        df.rename(columns={
            'NU_ANO_CENSO': 'Ano do Censo',
            'nome_municipio': 'Município',
            'IN_CAPITAL_IES': 'É Capital?',
            'TP_ORGANIZACAO_ACADEMICA': 'Organização Acadêmica',
            'TP_REDE': 'Tipo de Rede',
            'TP_CATEGORIA_ADMINISTRATIVA': 'Categoria Administrativa',
            'NO_MANTENEDORA': 'Mantenedora',
            'NO_IES': 'Nome da IES',
            'SG_IES': 'Sigla da IES',
            'QT_DOC_TOTAL': 'Total de Docentes',
            'QT_TEC_TOTAL': 'Total de Técnicos',
            # Renomear colunas de docentes por nível de formação
            'QT_DOC_EX_SEM_GRAD': 'Docentes Sem Graduação',
            'QT_DOC_EX_GRAD': 'Docentes com Graduação',
            'QT_DOC_EX_ESP': 'Docentes com Especialização',
            'QT_DOC_EX_MEST': 'Docentes com Mestrado',
            'QT_DOC_EX_DOUT': 'Docentes com Doutorado',
            'QT_LIVRO_ELETRONICO': 'Total de Livros Eletrônicos', 
            'QT_DOC_EX_FEMI': 'Docentes Feminino', 
            'QT_DOC_EX_MASC': 'Docentes Masculino' 
        }, inplace=True)

        # Preencher valores NaN (Not a Number) em colunas numéricas de contagem com 0.
        numeric_cols_to_fill = [
            'Total de Docentes', 'Total de Técnicos',
            'Docentes Sem Graduação', 'Docentes com Graduação', 'Docentes com Especialização',
            'Docentes com Mestrado', 'Docentes com Doutorado',
            'Total de Livros Eletrônicos', 'Docentes Feminino', 'Docentes Masculino' # Novas colunas
        ]
        for col in numeric_cols_to_fill:
            if col in df.columns: 
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0) 

        # Mapear valores numéricos para descrições textuais mais compreensíveis em colunas categóricas
        if 'É Capital?' in df.columns:
            df['É Capital?'] = df['É Capital?'].map({1: 'Sim', 0: 'Não'}).fillna('Não Definido')
        
        if 'Organização Acadêmica' in df.columns:
            organizacao_map = {
                1: 'Universidade', 2: 'Centro Universitário',
                3: 'Faculdade', 4: 'Instituto Federal de Educação, Ciência e Tecnologia (IF)',
                5: 'Centro Federal de Educação Tecnológica (CEFET)',
                99: 'Outra' 
            }
            df['Organização Acadêmica'] = df['Organização Acadêmica'].map(organizacao_map).fillna('Não Definido')

        if 'Tipo de Rede' in df.columns:
            rede_map = {1: 'Pública', 2: 'Privada'}
            df['Tipo de Rede'] = df['Tipo de Rede'].map(rede_map).fillna('Não Definido')

        if 'Categoria Administrativa' in df.columns:
            categoria_map = {
                1: 'Pública Federal', 2: 'Pública Estadual', 3: 'Pública Municipal',
                4: 'Privada Comunitária', 5: 'Privada Confessional', 6: 'Privada Filantrópica',
                7: 'Privada Sem Fins Lucrativos', 8: 'Privada Com Fins Lucrativos'
            }
            df['Categoria Administrativa'] = df['Categoria Administrativa'].map(categoria_map).fillna('Não Definido')

        return df
    
    except Exception as e:
        st.error(f"Ocorreu um erro inesperado ao carregar ou processar os dados: {e}")
        st.info("Verifique se o arquivo CSV está no formato correto (separador ';', codificação 'utf-8') e se não há problemas de dados.")
        return pd.DataFrame() 

# Carrega os dados uma vez (ou do cache)
df = carregar_dados()

# --- Bloco Principal da Aplicação Streamlit ---
if not df.empty:
    # --- Sidebar com Filtros ---
    st.sidebar.header("🔎 Filtros Interativos")
    st.sidebar.markdown("Selecione as opções abaixo para filtrar os dados em todo o painel.")

    

    if "Organização Acadêmica" in df.columns:
        organizacoes = sorted(df["Organização Acadêmica"].unique())
        organizacao_sel = st.sidebar.selectbox("Organização Acadêmica", ['Todas'] + list(organizacoes))
    else:
        st.sidebar.warning("Coluna 'Organização Acadêmica' não disponível para filtragem.")
        organizacao_sel = 'Todas' 

    if "Tipo de Rede" in df.columns:
        tipos_rede = sorted(df["Tipo de Rede"].unique())
        tipo_rede_sel = st.sidebar.selectbox("Tipo de Rede", ['Todas'] + list(tipos_rede))
    else:
        st.sidebar.warning("Coluna 'Tipo de Rede' não disponível para filtragem.")
        tipo_rede_sel = 'Todas' 

    if "Município" in df.columns:
        municipios = sorted(df["Município"].unique())
        municipio_sel = st.sidebar.selectbox("Município", ['Todos'] + list(municipios))
    else:
        st.sidebar.warning("Coluna 'Município' não disponível para filtragem.")
        municipio_sel = 'Todos' 



    # --- Aplicação dos Filtros ao DataFrame ---
    df_filtrado = df.copy() 


    if organizacao_sel != 'Todas' and "Organização Acadêmica" in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado["Organização Acadêmica"] == organizacao_sel]
        
    if tipo_rede_sel != 'Todas' and "Tipo de Rede" in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado["Tipo de Rede"] == tipo_rede_sel]
        
    if municipio_sel != 'Todos' and "Município" in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado["Município"] == municipio_sel]
        

    # --- Verificação de DataFrame Filtrado Vazio ---
    if df_filtrado.empty:
        st.info("Nenhum registro encontrado para os filtros selecionados. Por favor, ajuste os filtros na barra lateral.")
    else:
        # --- VALORES CHAVE (Key Metrics) ---
        st.subheader("💡 Métricas Chave")
        
        total_ies = df_filtrado['Nome da IES'].nunique() if 'Nome da IES' in df_filtrado.columns else 0
        total_docentes_ex = df_filtrado['Total de Docentes'].sum() if 'Total de Docentes' in df_filtrado.columns else 0
        total_municipios_c_ies = df_filtrado['Município'].nunique() if 'Município' in df_filtrado.columns else 0
        total_livros_eletronicos = df_filtrado['Total de Livros Eletrônicos'].sum() if 'Total de Livros Eletrônicos' in df_filtrado.columns else 0
        
        col1, col2, col3, col4 = st.columns(4) 
        with col1:
            st.metric(label="Total de IES", value=total_ies)
        with col2:
            st.metric(label="Total de Docentes", value=f"{total_docentes_ex:,.0f}".replace(",", "X").replace(".", ",").replace("X", "."))
        with col3:
            st.metric(label="Municípios c/ IES", value=total_municipios_c_ies)
        with col4: # Nova métrica
            st.metric(label="Total de Livros Eletrônicos", value=f"{total_livros_eletronicos:,.0f}".replace(",", "X").replace(".", ",").replace("X", "."))


        # --- PRÉVIA DOS DADOS ---
        st.subheader("📋 Prévia dos Dados Filtrados")
        st.write(f"Exibindo os primeiros **{min(10, len(df_filtrado))}** registros de **{len(df_filtrado)}** (de um total de **{len(df)}**).")
        st.dataframe(df_filtrado.head(10)) 

        # --- GRÁFICOS E VISUALIZAÇÕES ---
        st.subheader("📊 Visualizações e Gráficos")

        # 1. Modelo de Gráfico de Barras: Total de IES por Município
        if "Município" in df_filtrado.columns and "Nome da IES" in df_filtrado.columns and not df_filtrado.empty:
                st.markdown("##### Total de IES por Município")
                ies_por_municipio = df_filtrado.groupby("Município")['Nome da IES'].nunique().reset_index(name="Total de IES")
                ies_por_municipio = ies_por_municipio.sort_values("Total de IES", ascending=False)
                
                fig_ies_municipio = px.bar(
                    ies_por_municipio, 
                    x="Município", 
                    y="Total de IES", 
                    text="Total de IES", 
                    title="Número Total de Instituições de Ensino Superior por Município",
                    labels={"Total de IES": "Número de Instituições", "Município": "Município"},
                    color_discrete_sequence=['#2C5E8A'] # Cor alterada para '#2C5E8A'
                )
                fig_ies_municipio.update_traces(textposition='outside') 
                fig_ies_municipio.update_layout(xaxis_title="Município", yaxis_title="Total de IES", hovermode="x unified")
                st.plotly_chart(fig_ies_municipio, use_container_width=True)
        else:
            st.warning("Não foi possível gerar 'Total de IES por Município': Colunas necessárias ausentes ou dados filtrados vazios.")

        # 2. Novo Gráfico de Barras: Quantidade total de técnicos por Mantenedora
        if "Mantenedora" in df_filtrado.columns and "Total de Técnicos" in df_filtrado.columns and not df_filtrado.empty:
            st.markdown("##### Quantidade Total de Técnicos por Mantenedora")
            tec_por_mantenedora = df_filtrado.groupby("Mantenedora")["Total de Técnicos"].sum().reset_index()
            tec_por_mantenedora = tec_por_mantenedora.sort_values("Total de Técnicos", ascending=True)

            fig_tec_mantenedora = px.bar(
                tec_por_mantenedora,
                x="Total de Técnicos", 
                y="Mantenedora",     
                orientation='h',     
                text="Total de Técnicos", 
                title="Quantidade Total de Técnicos por Mantenedora",
                labels={"Total de Técnicos": "Quantidade Total de Técnicos", "Mantenedora": "Nome da Mantenedora"},
                  color_discrete_map={
                    'Total de Técnicos': '#2C5E8A', # Tom de azul mais escuro
                                },
            )
            fig_tec_mantenedora.update_traces(textposition='outside')
            fig_tec_mantenedora.update_layout(xaxis_title="Quantidade Total de Técnicos", yaxis_title="Mantenedora", hovermode="y unified")
            st.plotly_chart(fig_tec_mantenedora, use_container_width=True)
        else:
            st.warning("Não foi possível gerar 'Quantidade Total de Técnicos por Mantenedora': Colunas necessárias ausentes ou dados filtrados vazios.")


        # 3. NOVO GRÁFICO: Quantidade de Docentes por Sexo em Organização Acadêmica 
        if all(col in df_filtrado.columns for col in ["Organização Acadêmica", "Docentes Feminino", "Docentes Masculino"]) and not df_filtrado.empty:
            
            # Agrupa os dados por Organização Acadêmica e soma os docentes femininos e masculinos
            docentes_por_org_e_sexo = df_filtrado.groupby('Organização Acadêmica')[[
                'Docentes Feminino', 
                'Docentes Masculino'
            ]].sum().reset_index()

            # Transforma o DataFrame para o formato "long" para que o Plotly Express possa criar barras agrupadas
            docentes_long = docentes_por_org_e_sexo.melt(
                id_vars=['Organização Acadêmica'], 
                value_vars=['Docentes Feminino', 'Docentes Masculino'],
                var_name='Sexo', 
                value_name='Quantidade de Docentes'
            )

            # Calcular o total de docentes para esta visualização
            total_docentes_para_grafico = docentes_long['Quantidade de Docentes'].sum()
            
            # --- Layout para Título e Métrica ---
            st.markdown("#### Quantidade de Docentes do sexo feminino, Quantidade de docentes do sexo masculino por Organização Acadêmica")
            
            # Usando colunas para a métrica total e o título da sub-seção do gráfico
            col_total_docentes, col_sub_titulo_grafico = st.columns([0.25, 0.75])

            with col_total_docentes:
                # círculo

                st.markdown(f"""
                <div style="
                    border: 4px solid #3366CC; 
                    border-radius: 50%; 
                    width: 150px; 
                    height: 150px; 
                    display: flex; 
                    flex-direction: column; 
                    justify-content: center; 
                    align-items: center; 
                    margin: 20px auto;
                    color: {'white' if st.config.get_option('theme.base') == 'dark' else 'black'};
                    background-color: {'#0E1117' if st.config.get_option('theme.base') == 'dark' else 'white'};
                    text-align: center;
                ">
                    <span style="font-size: 14px;">Quantidade total de docentes</span>
                    <span style="font-size: 24px; font-weight: bold;">{f'{total_docentes_para_grafico / 1000:,.1f}'.replace(",", "X").replace(".", ",").replace("X", ".")} mil</span>
                </div>
                """, unsafe_allow_html=True)

            with col_sub_titulo_grafico:
                st.markdown("##### Quantidade de docentes do sexo feminino / Quantidade de docentes do sexo masculino")


            # Ordena a coluna 'Organização Acadêmica' para uma apresentação consistente no eixo X
            docentes_long['Organização Acadêmica'] = pd.Categorical(
                docentes_long['Organização Acadêmica'], 
                categories=sorted(docentes_long['Organização Acadêmica'].unique()), 
                ordered=True
            )

            # Define a ordem das categorias 'Sexo' para que as barras sejam sempre exibidas na mesma sequência
            category_orders = {
                "Sexo": ['Docentes Feminino', 'Docentes Masculino'],
                "Organização Acadêmica": sorted(docentes_long['Organização Acadêmica'].unique())
            }

            fig_docentes_org_sexo = px.bar(
                docentes_long, 
                x='Organização Acadêmica', 
                y='Quantidade de Docentes',
                color='Sexo', # Cria as barras agrupadas por sexo
                barmode='group', # Garante que as barras sejam agrupadas
                # O título principal acima, este é um subtítulo visual
                labels={
                    "Organização Acadêmica": "Organização Acadêmica", 
                    "Quantidade de Docentes": "Quantidade de Docentes",
                    "Sexo": "Sexo do Docente"
                },
                color_discrete_map={
                    'Docentes Feminino': '#2C5E8A', # Tom de azul mais escuro
                    'Docentes Masculino': '#5FAEEB'  # Tom de azul mais claro
                },
                category_orders=category_orders 
            )
            # Formatação dos números nas barras para "mil" e posicionamento externo
            fig_docentes_org_sexo.update_traces(texttemplate='%{y:,.1s}', textposition='outside')
            
            fig_docentes_org_sexo.update_layout(
                xaxis_title="Organização Acadêmica", 
                yaxis_title="", # Eixo Y sem título para replicar a imagem
                hovermode="x unified",
                # Posicionamento da legenda abaixo do gráfico
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.2, # Ajusta para ficar abaixo do gráfico
                    xanchor="center",
                    x=0.10, # Centraliza horizontalmente
                    title_text="" # Remove o título da legenda
                )
            )
            st.plotly_chart(fig_docentes_org_sexo, use_container_width=True)
        else:
            st.warning("Não foi possível gerar 'Quantidade de Docentes por Sexo e Organização Acadêmica': Colunas necessárias ausentes ou dados filtrados vazios.")


        # 4. Modelo de Gráfico de Pizza: Distribuição de Instituições por Categoria Administrativa 
        if "Categoria Administrativa" in df_filtrado.columns and not df_filtrado.empty:
            st.markdown("##### Distribuição de Instituições por Categoria Administrativa")
            cat_admin_counts = df_filtrado['Categoria Administrativa'].value_counts().reset_index()
            cat_admin_counts.columns = ['Categoria Administrativa', 'Número de IES']
            
            # Ordenar os dados em ordem decrescente pelo 'Número de IES'
            cat_admin_counts = cat_admin_counts.sort_values(by='Número de IES', ascending=False)

            fig_cat_admin = px.pie(
                cat_admin_counts, 
                values='Número de IES', 
                names='Categoria Administrativa', 
                title='Distribuição de Instituições de Ensino Superior por Categoria Administrativa',
                hole=0, 
                height=600, # Aumenta a altura do gráfico
                # Cores em tons de azul conforme solicitado (e uma cor extra para 'Outras Categorias')
                color_discrete_sequence=['#2470AD', '#33A3FF', '#7DC3FC', '#C7E3F9', '#1A4B7D'] 
            )
            fig_cat_admin.update_traces(textposition='inside', textinfo='percent') # Mostra percentual e label dentro das fatias
            st.plotly_chart(fig_cat_admin, use_container_width=True)
        else:
            st.warning("Não foi possível gerar 'Distribuição de Instituições por Categoria Administrativa': Coluna 'Categoria Administrativa' ausente ou dados filtrados vazios.")

         # 5. Gráfico de Árvore (Treemap): Estrutura das IES por Organização Acadêmica (Tamanho e Cor: Livros Eletrônicos)
        if all(col in df_filtrado.columns for col in ["Organização Acadêmica", "Total de Livros Eletrônicos"]) and not df_filtrado.empty:
            st.markdown("##### Estrutura das IES por Organização Acadêmica (Tamanho e Cor: Livros Eletrônicos)")
            
            df_treemap_data = df_filtrado.groupby('Organização Acadêmica').agg(
                Soma_Livros_Eletronicos=('Total de Livros Eletrônicos', 'sum')
            ).reset_index()
            
            fig_treemap_livros = px.treemap(
                df_treemap_data, 
                path=['Organização Acadêmica'], 
                values='Soma_Livros_Eletronicos', 
                color='Soma_Livros_Eletronicos', 
                title=None, # Título do gráfico de árvore removido
                color_continuous_scale=[(0, "#035AC4"), (1, "#69ADE4")], # Escala de cor azul do mais escuro ao mais claro
                hover_data=['Soma_Livros_Eletronicos'] 
            )
            fig_treemap_livros.update_layout(
                margin = dict(t=0, l=0, r=0, b=0), 
                uniformtext_minsize=10, 
                uniformtext_mode='hide',
                height=400,
            )
            fig_treemap_livros.update_traces(marker_line_width=0) # Removido o 0.1 para borda quase invisível
            st.plotly_chart(fig_treemap_livros, use_container_width=True) 
        else:
            st.warning("Não foi possível gerar 'Gráfico de Árvore': Colunas essenciais ausentes ou dados filtrados vazios.")


        # 6. Modelo de Gráfico de Barras: Total de Docentes por Nível de Formação
        docentes_cols_for_plot = [
                'Docentes Sem Graduação', 'Docentes com Graduação', 'Docentes com Especialização',
                'Docentes com Mestrado', 'Docentes com Doutorado'
            ]

        if all(col in df_filtrado.columns for col in docentes_cols_for_plot) and not df_filtrado.empty:
                st.markdown("##### Total de Docentes por Nível de Formação")
                
                docentes_resumo_filtrado = df_filtrado[docentes_cols_for_plot].sum().reset_index()
                docentes_resumo_filtrado.columns = ['Nível de Formação', 'Total de Docentes']
                docentes_resumo_filtrado = docentes_resumo_filtrado.sort_values(by='Total de Docentes', ascending=False)

                fig_docentes = px.bar(
                    docentes_resumo_filtrado, 
                    x='Nível de Formação', 
                    y='Total de Docentes', 
                    title='Total de Docentes por Nível de Formação (Dados Filtrados)',
                    labels={'Nível de Formação': 'Nível de Formação', 'Total de Docentes': 'Quantidade Total de Docentes'},
                    text='Total de Docentes', 
                    color_discrete_sequence=['#2C5E8A'] # Cor alterada para '#2C5E8A'
                )
                fig_docentes.update_traces(textposition='outside')
                fig_docentes.update_layout(xaxis_title="Nível de Formação", yaxis_title="Quantidade Total de Docentes", hovermode="x unified")
                st.plotly_chart(fig_docentes, use_container_width=True)
        else:
                st.warning("Não foi possível gerar 'Total de Docentes por Nível de Formação': Colunas de docentes ausentes ou dados filtrados vazios.")

        # 7. Tabela Detalhada das IES Filtradas (Mantida)
        if not df_filtrado.empty:
            st.markdown("##### Tabela Detalhada das IES Filtradas por Município, Instituição e Totais")
            
            group_cols = ['Ano do Censo', 'Município', 'Nome da IES', 'Sigla da IES', 
                          'Organização Acadêmica', 'Tipo de Rede', 'Categoria Administrativa']
            
            measures = ['Total de Docentes', 'Total de Técnicos']

            if all(col in df_filtrado.columns for col in group_cols + measures):
                ies_summary_table = df_filtrado.groupby(group_cols).agg(
                    Total_Docentes_IES=('Total de Docentes', 'sum'),
                    Total_Tecnicos_IES=('Total de Técnicos', 'sum')
                ).reset_index()

                final_cols = ['Ano do Censo', 'Município', 'Nome da IES', 'Sigla da IES', 
                              'Organização Acadêmica', 'Tipo de Rede', 'Categoria Administrativa',
                              'Total_Docentes_IES', 'Total_Tecnicos_IES']
                
                st.dataframe(ies_summary_table[final_cols])
            else:
                st.warning("Não foi possível gerar a 'Tabela Detalhada das IES': Colunas essenciais ausentes ou dados filtrados vazios para agrupamento.")

            st.markdown("""
                Esta tabela detalha as Instituições de Ensino Superior (IES) com base nos filtros aplicados,
                fornecendo uma visão granular da estrutura educacional por localização, tipo e dados de pessoal.
            """)
        else:
            st.info("Nenhum dado filtrado para exibir na tabela detalhada das IES.")
       

else:
    st.info("O aplicativo não pôde carregar os dados. Verifique a mensagem de erro acima para mais detalhes.")
