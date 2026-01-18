import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.subplots as sp
import streamlit as st
from datetime import datetime, timedelta
import calendar

def show_dashboard(df):
    # ----------- Preparação dos dados ----------- #
    df['Data'] = pd.to_datetime(df['Data'])
    df['Mês'] = df['Data'].dt.month
    df['Ano'] = df['Data'].dt.year
    df['Mês_Nome'] = df['Data'].dt.strftime('%b')
    df['Dia_Semana'] = df['Data'].dt.day_name()
    df['Semana'] = df['Data'].dt.isocalendar().week
    df['Trimestre'] = df['Data'].dt.quarter
    
    # Cálculos Rápidos
    df_entradas = df[df['Tipo'] == 'entrada']
    df_saidas = df[df['Tipo'] == 'saida']
    
    total_receita = df_entradas['Valor'].sum()
    total_despesa = df_saidas['Valor'].sum()
    saldo_atual = total_receita - total_despesa
    margem_lucro = (saldo_atual / total_receita * 100) if total_receita > 0 else 0
    
    # Médias
    media_mensal_entrada = df_entradas.groupby(df_entradas['Data'].dt.to_period('M'))['Valor'].sum().mean()
    media_mensal_saida = df_saidas.groupby(df_saidas['Data'].dt.to_period('M'))['Valor'].sum().mean()
    
    # ----------- Dashboard ----------- #
    st.title("💰 Dashboard Financeiro Inteligente")
    
    # 1. KPI Cards melhorados com cores condicionais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💰 Total Entradas", 
                 f"R$ {total_receita:,.2f}", 
                 f"Média: R$ {media_mensal_entrada:,.0f}/mês",
                 delta_color="normal")
    
    with col2:
        st.metric("📉 Total Saídas", 
                 f"R$ {total_despesa:,.2f}", 
                 f"Média: R$ {media_mensal_saida:,.0f}/mês",
                 delta_color="inverse")
    
    with col3:
        saldo_color = "normal" if saldo_atual >= 0 else "inverse"
        st.metric("⚖️ Saldo Líquido", 
                 f"R$ {saldo_atual:,.2f}", 
                 f"{margem_lucro:.1f}% de margem",
                 delta_color=saldo_color)
    
    with col4:
        # Taxa de poupança
        taxa_poupanca = (saldo_atual / total_receita * 100) if total_receita > 0 else 0
        st.metric("🎯 Taxa Poupança", 
                 f"{taxa_poupanca:.1f}%", 
                 "do que entra você guarda",
                 delta_color="normal" if taxa_poupanca >= 20 else "inverse")
    
    st.markdown("---")
    
    # 2. Gráfico de Evolução com área sombreada e meta
    st.subheader("📈 Evolução Patrimonial")
    
    # Calcular saldo acumulado
    df['Valor_Ajustado'] = df.apply(lambda x: x['Valor'] if x['Tipo'] == 'entrada' else -x['Valor'], axis=1)
    df_sorted = df.sort_values('Data')
    df_sorted['Saldo_Acumulado'] = df_sorted['Valor_Ajustado'].cumsum()
    
    fig_saldo = go.Figure()
    
    # Área do saldo
    fig_saldo.add_trace(go.Scatter(
        x=df_sorted['Data'],
        y=df_sorted['Saldo_Acumulado'],
        fill='tozeroy',
        mode='lines',
        name='Saldo Acumulado',
        line=dict(color='#2E86AB', width=3),
        fillcolor='rgba(46, 134, 171, 0.2)'
    ))
    
    # Linha de meta (opcional - 20% crescimento anualizado)
    meta_inicial = df_sorted['Saldo_Acumulado'].iloc[0] if len(df_sorted) > 0 else 0
    dias = (df_sorted['Data'].max() - df_sorted['Data'].min()).days
    meta_final = meta_inicial * (1.2 ** (dias/365))  # 20% ao ano
    fig_saldo.add_trace(go.Scatter(
        x=[df_sorted['Data'].min(), df_sorted['Data'].max()],
        y=[meta_inicial, meta_final],
        mode='lines',
        name='Meta (20% ao ano)',
        line=dict(color='#A63A50', width=2, dash='dash')
    ))
    
    fig_saldo.update_layout(
        title='Evolução do Patrimônio com Meta',
        xaxis_title='Data',
        yaxis_title='Saldo (R$)',
        hovermode='x unified',
        template='plotly_white',
        showlegend=True
    )
    
    st.plotly_chart(fig_saldo, use_container_width=True)
    
    # 3. Análise comparativa mensal
    st.subheader("📊 Análise Mensal Detalhada")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de Sankey para fluxo de dinheiro
        st.markdown("**🔀 Fluxo Financeiro**")
        
        # Preparar dados para Sankey
        labels = ['Entradas', 'Saídas', 'Saldo'] + list(df_saidas['Categoria'].unique())
        source = [0, 0]  # Entradas -> Saídas, Entradas -> Saldo
        target = [1, 2]
        value = [total_despesa, saldo_atual]
        
        # Adicionar categorias de despesas
        for i, (cat, val) in enumerate(df_saidas.groupby('Categoria')['Valor'].sum().items()):
            labels.append(cat)
            source.append(1)  # Saídas -> Categoria
            target.append(2 + i)  # Índice da categoria
            value.append(val)
        
        fig_sankey = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=labels,
                color=['#00CC96', '#EF553B', '#2E86AB'] + ['#FF6B6B'] * len(df_saidas['Categoria'].unique())
            ),
            link=dict(
                source=source,
                target=target,
                value=value,
                color=['rgba(0, 204, 150, 0.3)', 'rgba(46, 134, 171, 0.3)'] + 
                      ['rgba(255, 107, 107, 0.3)'] * len(df_saidas['Categoria'].unique())
            )
        )])
        
        fig_sankey.update_layout(title_text="Fluxo do Dinheiro", font_size=10)
        st.plotly_chart(fig_sankey, use_container_width=True)
    
    with col2:
        # Pizza donut para distribuição
        st.markdown("**📦 Distribuição por Categoria**")
        
        # Agrupar categorias pequenas em "Outros"
        cat_sums = df_saidas.groupby('Categoria')['Valor'].sum()
        threshold = cat_sums.sum() * 0.05  # 5% threshold
        main_cats = cat_sums[cat_sums >= threshold]
        other_sum = cat_sums[cat_sums < threshold].sum()
        
        if other_sum > 0:
            main_cats['Outros'] = other_sum
        
        fig_donut = px.pie(
            values=main_cats.values,
            names=main_cats.index,
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        fig_donut.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate="<b>%{label}</b><br>R$ %{value:,.2f}<br>%{percent}"
        )
        
        st.plotly_chart(fig_donut, use_container_width=True)
    
    # 4. Tabela interativa com transações recentes
    st.subheader("📝 Últimas Transações")
    
    # Ordenar por data decrescente
    df_recent = df.sort_values('Data', ascending=False).head(10)
    
    # Formatar valores
    df_recent['Valor_Formatado'] = df_recent.apply(
        lambda x: f"R$ {x['Valor']:,.2f}", axis=1
    )
    
    # Adicionar ícones baseados no tipo
    df_recent['Tipo_Icon'] = df_recent['Tipo'].map({
        'entrada': '💰',
        'saida': '💸'
    })
    
    # Mostrar tabela
    st.dataframe(
        df_recent[['Data', 'Tipo_Icon', 'Categoria', 'Descrição', 'Valor_Formatado']],
        column_config={
            "Data": st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
            "Tipo_Icon": "Tipo",
            "Valor_Formatado": "Valor"
        },
        hide_index=True,
        use_container_width=True
    )
    
    # 5. Análise temporal
    st.subheader("⏰ Padrões Temporais")
    
    tab1, tab2, tab3 = st.tabs(["📅 Por Dia da Semana", "📆 Por Mês", "📊 Tendência"])
    
    with tab1:
        # Gastos por dia da semana
        dias_ordem = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        df_saidas['Dia_Semana'] = pd.Categorical(df_saidas['Dia_Semana'], categories=dias_ordem, ordered=True)
        gastos_dia = df_saidas.groupby('Dia_Semana')['Valor'].sum().reindex(dias_ordem)
        
        fig_dia = px.bar(
            x=[d[:3] for d in dias_ordem],
            y=gastos_dia.values,
            title="Gastos por Dia da Semana",
            color=gastos_dia.values,
            color_continuous_scale='Reds',
            labels={'x': 'Dia', 'y': 'Valor Gasto (R$)'}
        )
        st.plotly_chart(fig_dia, use_container_width=True)
    
    with tab2:
        # Evolução mensal
        df_mensal = df.groupby(['Ano', 'Mês'])['Valor_Ajustado'].sum().reset_index()
        df_mensal['Data_Ref'] = df_mensal.apply(
            lambda x: datetime(x['Ano'], x['Mês'], 1), axis=1
        )
        df_mensal = df_mensal.sort_values('Data_Ref')
        df_mensal['Saldo_Mensal'] = df_mensal['Valor_Ajustado'].cumsum()
        
        fig_mes = px.line(
            df_mensal,
            x='Data_Ref',
            y='Saldo_Mensal',
            title="Evolução Mensal do Saldo",
            markers=True,
            line_shape='spline'
        )
        
        # Adicionar barras para entrada/saída mensal
        df_mensal_det = df.groupby(['Ano', 'Mês', 'Tipo'])['Valor'].sum().unstack().fillna(0)
        df_mensal_det['Data_Ref'] = [datetime(ano, mes, 1) for ano, mes in df_mensal_det.index]
        
        fig_mes.add_trace(go.Bar(
            x=df_mensal_det['Data_Ref'],
            y=df_mensal_det.get('entrada', 0),
            name='Entradas',
            marker_color='#00CC96',
            opacity=0.3
        ))
        
        fig_mes.add_trace(go.Bar(
            x=df_mensal_det['Data_Ref'],
            y=-df_mensal_det.get('saida', 0),
            name='Saídas',
            marker_color='#EF553B',
            opacity=0.3
        ))
        
        fig_mes.update_layout(barmode='overlay')
        st.plotly_chart(fig_mes, use_container_width=True)
    
    with tab3:
        # Heatmap de gastos
        st.markdown("**🔥 Heatmap de Gastos Diários**")
        
        # Criar heatmap
        df_saidas['Dia'] = df_saidas['Data'].dt.day
        heatmap_data = df_saidas.pivot_table(
            index='Mês_Nome',
            columns='Dia',
            values='Valor',
            aggfunc='sum',
            fill_value=0
        )
        
        # Ordenar meses
        meses_ordem = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        heatmap_data = heatmap_data.reindex([m for m in meses_ordem if m in heatmap_data.index])
        
        fig_heat = px.imshow(
            heatmap_data,
            labels=dict(x="Dia do Mês", y="Mês", color="Valor Gasto"),
            color_continuous_scale='Reds',
            aspect='auto'
        )
        
        st.plotly_chart(fig_heat, use_container_width=True)
    
    # 6. Insights automáticos
    st.subheader("🤖 Insights Inteligentes")
    
    # Calcular insights
    insights = []
    
    # Maior gasto
    if not df_saidas.empty:
        maior_gasto = df_saidas.loc[df_saidas['Valor'].idxmax()]
        insights.append(f"⚠️ **Maior gasto**: {maior_gasto['Categoria']} - R$ {maior_gasto['Valor']:,.2f} em {maior_gasto['Data'].strftime('%d/%m/%Y')}")
    
    # Categoria mais frequente
    if not df_saidas.empty:
        cat_frequente = df_saidas['Categoria'].mode()[0]
        freq = (df_saidas['Categoria'] == cat_frequente).sum()
        insights.append(f"🔁 **Categoria mais frequente**: {cat_frequente} ({freq} transações)")
    
    # Dia com mais gastos
    if not df_saidas.empty:
        dia_mais_gasto = df_saidas.groupby('Dia_Semana')['Valor'].sum().idxmax()
        valor_dia = df_saidas.groupby('Dia_Semana')['Valor'].sum().max()
        insights.append(f"📅 **Dia de maior gasto**: {dia_mais_gasto} (R$ {valor_dia:,.2f})")
    
    # Meta de poupança
    if taxa_poupanca < 20:
        insights.append(f"🎯 **Recomendação**: Aumente sua taxa de poupança (atual: {taxa_poupanca:.1f}%, meta: 20%)")
    else:
        insights.append(f"✅ **Excelente!** Sua taxa de poupança de {taxa_poupanca:.1f}% está acima da meta de 20%")
    
    # Mostrar insights
    for insight in insights:
        st.info(insight)
    
    # 7. Download de relatório
    st.markdown("---")
    st.subheader("📥 Exportar Relatório")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Gerar Relatório Resumido", use_container_width=True):
            # Criar relatório resumido
            relatorio = f"""
            📋 RELATÓRIO FINANCEIRO
            Data: {datetime.now().strftime('%d/%m/%Y')}
            Período: {df['Data'].min().strftime('%d/%m/%Y')} a {df['Data'].max().strftime('%d/%m/%Y')}
            
            📈 MÉTRICAS PRINCIPAIS:
            • Total Entradas: R$ {total_receita:,.2f}
            • Total Saídas: R$ {total_despesa:,.2f}
            • Saldo Líquido: R$ {saldo_atual:,.2f}
            • Margem de Lucro: {margem_lucro:.1f}%
            • Taxa de Poupança: {taxa_poupanca:.1f}%
            
            🏆 TOP 3 CATEGORIAS DE GASTO:
            """
            
            top_cats = df_saidas.groupby('Categoria')['Valor'].sum().nlargest(3)
            for i, (cat, valor) in enumerate(top_cats.items(), 1):
                percentual = (valor / total_despesa * 100) if total_despesa > 0 else 0
                relatorio += f"{i}. {cat}: R$ {valor:,.2f} ({percentual:.1f}%)\n"
            
            st.download_button(
                label="⬇️ Baixar Relatório (.txt)",
                data=relatorio,
                file_name=f"relatorio_financeiro_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain"
            )
    
    with col2:
        # Opção para exportar dados
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📁 Exportar Dados Completos (.csv)",
            data=csv,
            file_name=f"dados_financeiros_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )

# Código adicional para um sistema completo de controle financeiro:
def sistema_controle_financeiro_completo():
    """
    Sistema completo de controle financeiro com:
    1. Cadastro de transações
    2. Dashboard visual
    3. Metas e orçamentos
    4. Alertas automáticos
    5. Relatórios personalizados
    """
    
    st.sidebar.title("💼 Controle Financeiro")
    
    menu = st.sidebar.selectbox(
        "Menu",
        ["🏠 Dashboard", "➕ Nova Transação", "🎯 Metas", "⚙️ Configurações"]
    )
    
    # Carregar dados (simulação - na prática, use um banco de dados)
    try:
        df = pd.read_csv("financas.csv")
    except:
        # Dados de exemplo
        df = pd.DataFrame({
            'Data': pd.date_range(start='2024-01-01', periods=100, freq='D'),
            'Tipo': ['entrada' if i % 3 == 0 else 'saida' for i in range(100)],
            'Categoria': ['Salário' if i % 3 == 0 else 
                         'Alimentação' if i % 5 == 0 else 
                         'Transporte' if i % 7 == 0 else 
                         'Lazer' for i in range(100)],
            'Descrição': [f'Transação {i}' for i in range(100)],
            'Valor': [3000 if i % 3 == 0 else 
                     abs(np.random.normal(50, 20)) for i in range(100)]
        })
    
    if menu == "🏠 Dashboard":
        show_dashboard(df)
    
    elif menu == "➕ Nova Transação":
        st.header("Adicionar Nova Transação")
        
        with st.form("nova_transacao"):
            col1, col2 = st.columns(2)
            
            with col1:
                data = st.date_input("Data")
                tipo = st.selectbox("Tipo", ["entrada", "saida"])
                valor = st.number_input("Valor (R$)", min_value=0.01, step=0.01)
            
            with col2:
                categoria = st.selectbox("Categoria", 
                    ["Salário", "Investimentos", "Alimentação", "Transporte", 
                     "Moradia", "Lazer", "Saúde", "Educação", "Outros"])
                descricao = st.text_input("Descrição")
            
            submitted = st.form_submit_button("Salvar Transação")
            
            if submitted:
                nova_linha = pd.DataFrame([{
                    'Data': data,
                    'Tipo': tipo,
                    'Categoria': categoria,
                    'Descrição': descricao,
                    'Valor': valor
                }])
                
                df = pd.concat([df, nova_linha], ignore_index=True)
                df.to_csv("financas.csv", index=False)
                st.success("✅ Transação salva com sucesso!")
                st.rerun()
    
    elif menu == "🎯 Metas":
        st.header("Metas Financeiras")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🏆 Definir Meta Mensal")
            meta_mensal = st.number_input("Meta de Economia Mensal (R$)", 
                                         min_value=0.0, value=1000.0)
            
            # Calcular progresso
            mes_atual = datetime.now().month
            ano_atual = datetime.now().year
            
            df_mes = df[(df['Data'].dt.month == mes_atual) & 
                       (df['Data'].dt.year == ano_atual)]
            
            saldo_mes = df_mes[df_mes['Tipo'] == 'entrada']['Valor'].sum() - \
                       df_mes[df_mes['Tipo'] == 'saida']['Valor'].sum()
            
            progresso = min(saldo_mes / meta_mensal * 100, 100) if meta_mensal > 0 else 0
            
            st.progress(progresso / 100)
            st.caption(f"Progresso: R$ {saldo_mes:,.2f} / R$ {meta_mensal:,.2f} ({progresso:.1f}%)")
        
        with col2:
            st.subheader("📊 Metas por Categoria")
            
            categorias = df[df['Tipo'] == 'saida']['Categoria'].unique()
            
            for cat in categorias[:3]:  # Mostrar apenas 3
                gasto_cat = df[(df['Categoria'] == cat) & 
                              (df['Tipo'] == 'saida') & 
                              (df['Data'].dt.month == mes_atual)]['Valor'].sum()
                
                meta_cat = st.number_input(
                    f"Meta para {cat} (R$)",
                    min_value=0.0,
                    value=gasto_cat * 0.8,  # Sugerir 20% de redução
                    key=f"meta_{cat}"
                )
                
                if meta_cat > 0:
                    percentual = min(gasto_cat / meta_cat * 100, 100)
                    cor = "green" if gasto_cat <= meta_cat else "red"
                    st.markdown(f"<span style='color:{cor}'>Gasto: R$ {gasto_cat:,.2f} ({percentual:.1f}% da meta)</span>", 
                               unsafe_allow_html=True)

# Para usar o sistema completo:
if __name__ == "__main__":
    import numpy as np
    
    # Descomente a linha abaixo para usar o sistema completo:
    # sistema_controle_financeiro_completo()
    
    # Ou use apenas o dashboard:
    # Carregue seus dados aqui
    # df = pd.read_csv("seu_arquivo.csv")
    # show_dashboard(df)