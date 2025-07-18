import pandas as pd
import streamlit as st
import plotly.express as px
import json
import os
import streamlit.components.v1 as components

# Load custom CSS
with open("style.css") as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

st.set_page_config(layout="wide")

# Constants and configurations
COSTS_FILE = "license_costs.json"
default_license_costs = {
    "DESKLESSPACK": 3.12,
    "ATP_ENTERPRISE": 1.59,
    "SPE_E3": 31.76,
    "EMS": 8.34,
    "STANDARDPACK": 7.92,
    "PROJECTPROFESSIONAL": 23.67,
    "VISIOCLIENT": 11.80,
    "POWER_BI_PRO": 7.92,
    "Win10_VDA_E3": 5.56,
    "Microsoft_Teams_Rooms_Pro": 33.62
}

# Load license costs
if os.path.exists(COSTS_FILE):
    with open(COSTS_FILE, "r") as f:
        license_costs = json.load(f)
else:
    license_costs = default_license_costs.copy()

# Company mapping
company_map = {
    "Clearlake": "Continente",
    "Tecnovia SGPS": "Continente",
    "Uganda": "Continente",
    "Tecnovia Angola": "Continente",
    "Tecnovia Bolivia": "Tecnovia Madeira",
    "Farrobo": "Tecnovia Madeira",
    "Hotel da Graciosa": "Tecnovia Acores"
}

# File upload
uploaded_file = st.file_uploader("Carregar ficheiro CSV", type=["csv"])
if not uploaded_file:
    st.warning("Por favor, carregue um ficheiro CSV para continuar.")
    st.stop()

# Data processing
df = pd.read_csv(uploaded_file, sep=";", engine="python", header=None)
df.columns = ["Email", "Empresa"] + [f"Licenca{i}" for i in range(1, len(df.columns) - 1)]
df["Empresa"] = df["Empresa"].str.replace('"', '').str.strip()
df["Empresa"] = df["Empresa"].replace(company_map)

# Melt data
df_melted = df.melt(
    id_vars=["Email", "Empresa"],
    value_vars=[col for col in df.columns if col.startswith("Licenca")],
    var_name="Posição",
    value_name="License"
).dropna(subset=["License"])

df_melted = df_melted[df_melted["License"].isin(license_costs.keys())]
df_melted["Cost (€)"] = df_melted["License"].map(license_costs)

# Initialize filtered data
df_filtrado = df_melted.copy()

# Sidebar
with st.sidebar:
    st.image("tecnovia_horizontal.png", use_container_width=True)
    
    st.header("Alterar custos das licenças")
    for lic in license_costs:
        license_costs[lic] = st.number_input(
            f"Custo {lic} (€)", 
            min_value=0.0, 
            value=float(license_costs[lic]), 
            step=0.01
        )
    
    if st.button("Guardar custos", key="guardar_custos_btn"):
        with open(COSTS_FILE, "w") as f:
            json.dump(license_costs, f, indent=2)
        st.success("Custos guardados com sucesso!")

# Unassigned licenses
with st.expander("Licenças não atribuídas", expanded=True):
    st.markdown("Preencha aqui o número de licenças compradas mas não atribuídas a utilizadores.")
    empresa_excedente = st.selectbox("Selecionar empresa para receber estas licenças:", sorted(df_melted["Empresa"].unique()))
    
    todas_licencas = {lic: 0 for lic in license_costs.keys()}
    defaults = {
        "ATP_ENTERPRISE": 3,
        "EMS": 1,
        "SPE_E3": 3,
        "STANDARDPACK": 1,
        "PROJECTPROFESSIONAL": 1,
        "POWER_BI_PRO": 1,
        "Win10_VDA_E3": 1
    }
    todas_licencas.update(defaults)
    
    st.markdown("**Editar número de licenças não atribuídas:**")
    col1, col2, col3 = st.columns(3)
    cols = [col1, col2, col3]
    licencas_excedentes = {}

    for i, (licenca, valor_default) in enumerate(todas_licencas.items()):
        with cols[i % 3]:
            qtd = st.number_input(f"{licenca}", min_value=0, value=valor_default, step=1, key=f"input_{licenca}")
            licencas_excedentes[licenca] = qtd

    atribuicoes_ficticias = []
    for licenca, qtd in licencas_excedentes.items():
        for _ in range(qtd):
            atribuicoes_ficticias.append({
                "Email": "contabilistico@tecnovia.pt",
                "Empresa": empresa_excedente,
                "License": licenca,
                "Cost (€)": license_costs[licenca]
            })

    df_ficticio = pd.DataFrame(atribuicoes_ficticias)
    df_filtrado = pd.concat([df_melted, df_ficticio], ignore_index=True)

# Main UI
st.title("Dashboard de Licenciamento Microsoft")
st.markdown("Visualize os custos com base nas licenças atribuídas.")

# Metrics cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-title">Total Empresas</div>
        <div class="metric-value">{}</div>
        <div class="metric-subtitle">com licenças</div>
    </div>
    """.format(len(df_filtrado["Empresa"].unique())), unsafe_allow_html=True)

with col2:
    total_licenses = len(df_filtrado)
    assigned_licenses = len(df_filtrado[df_filtrado["Email"] != "contabilistico@tecnovia.pt"])
    st.markdown("""
    <div class="metric-card">
        <div class="metric-title">Licenças</div>
        <div class="metric-value">{}/{}</div>
        <div class="metric-subtitle">atribuídas/totais</div>
    </div>
    """.format(assigned_licenses, total_licenses), unsafe_allow_html=True)

with col3:
    unique_employees = df_filtrado[df_filtrado["Email"] != "contabilistico@tecnovia.pt"]["Email"].nunique()
    st.markdown("""
    <div class="metric-card">
        <div class="metric-title">Colaboradores</div>
        <div class="metric-value">{}</div>
        <div class="metric-subtitle">com licenças</div>
    </div>
    """.format(unique_employees), unsafe_allow_html=True)

with col4:
    total_cost = df_filtrado["Cost (€)"].sum()
    st.markdown("""
    <div class="metric-card">
        <div class="metric-title">Custo Total</div>
        <div class="metric-value">{:,.2f} €</div>
        <div class="metric-subtitle">mensal</div>
    </div>
    """.format(total_cost), unsafe_allow_html=True)

# Summary tables
summary = df_filtrado.groupby(["Empresa", "License"]).agg(
    Quantidade=("License", "count"),
    Custo_Total=("Cost (€)", "sum")
).reset_index()

pivot_table = summary.pivot(index="Empresa", columns="License", values="Custo_Total").fillna(0)
pivot_table["Total (€)"] = pivot_table.sum(axis=1)
pivot_table.loc["Total Geral"] = pivot_table.sum()

pivot_qtd = summary.pivot(index="Empresa", columns="License", values="Quantidade").fillna(0)
pivot_qtd["Total Licenças"] = pivot_qtd.sum(axis=1)
total_licencas = pivot_qtd.sum(axis=0)
total_licencas.name = "Nº de Licenças"
pivot_qtd = pd.concat([pivot_qtd, pd.DataFrame([total_licencas], columns=pivot_qtd.columns)])

def style_total_and_header(df, total_labels=[], is_currency=False):
    total_bg = "#F0532D"  
    header_bg = "#993322"  
    text_color = "white"

    def highlight_totals(row):
        if row.name in total_labels:
            return [f'background-color: {total_bg}; color: {text_color};' for _ in row]
        else:
            return ['' for _ in row]

    styled = df.style.apply(highlight_totals, axis=1).set_table_styles([
        {
            'selector': 'th',
            'props': [
                ('background-color', header_bg),
                ('color', text_color)
            ]
        }
    ])

    if is_currency:
        styled = styled.format("{:.2f} €")

    return styled

# Tables
st.subheader("Resumo de Custos por Empresa e Tipo de Licença")
st.write(style_total_and_header(pivot_table, total_labels=["Total Geral"], is_currency=True))

st.subheader("Resumo de Quantidade de Licenças por Empresa e Tipo")
st.write(style_total_and_header(pivot_qtd.astype(int), total_labels=["Nº de Licenças"], is_currency=False))

# Charts
st.subheader("Distribuição de Custos por Tipo de Licença")
chart1 = summary.groupby("License")["Custo_Total"].sum().reset_index()
fig1 = px.bar(chart1, x="License", y="Custo_Total", text_auto=".2s", 
              labels={"Custo_Total": "Custo (€)"}, 
              color_discrete_sequence=["rgb(240, 83, 45)"])
st.plotly_chart(fig1, use_container_width=True)

st.subheader("Distribuição de Custos por Empresa")
chart2 = summary.groupby("Empresa")["Custo_Total"].sum().reset_index()
fig2 = px.bar(chart2, x="Empresa", y="Custo_Total", text_auto=".2s", 
              labels={"Custo_Total": "Custo (€)"}, 
              color_discrete_sequence=["rgb(240, 83, 45)"])
st.plotly_chart(fig2, use_container_width=True)

st.subheader("Análise por Tipo de Licença")
licenca_escolhida = st.selectbox("Escolhe um tipo de licença para ver distribuição por empresa:", 
                                sorted(df_melted["License"].unique()))
df_licenca = summary[summary["License"] == licenca_escolhida]
fig_drill = px.bar(df_licenca, x="Empresa", y="Custo_Total", text_auto=".2s", 
                  title=f"Custo por Empresa para a Licença '{licenca_escolhida}'", 
                  labels={"Custo_Total": "Custo (€)"}, 
                  color_discrete_sequence=["rgb(240, 83, 45)"])
st.plotly_chart(fig_drill, use_container_width=True)

st.subheader("Distribuição Percentual de Custos por Licença (por Empresa)")
empresa_escolhida = st.selectbox("Escolhe uma empresa:", 
                                sorted(summary["Empresa"].unique()), 
                                key="empresa_percent")

df_empresa = summary[summary["Empresa"] == empresa_escolhida].copy()
custo_total_empresa = df_empresa["Custo_Total"].sum()
df_empresa["Percentagem"] = (df_empresa["Custo_Total"] / custo_total_empresa) * 100

fig_percent = px.bar(df_empresa,
                    x="License",
                    y="Percentagem",
                    text=df_empresa["Percentagem"].map("{:.1f}%".format),
                    title=f"Percentagem do Custo por Licença — {empresa_escolhida}",
                    labels={"Percentagem": "% do custo"},
                    color_discrete_sequence=["rgb(240, 83, 45)"])

fig_percent.update_layout(yaxis_tickformat=".0f", yaxis_range=[0, 100])
st.plotly_chart(fig_percent, use_container_width=True)