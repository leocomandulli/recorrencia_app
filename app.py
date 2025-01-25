import streamlit as st
from datetime import datetime, timedelta
import calendar

# Função para gerar datas recorrentes
def gerar_datas_recorrentes(data_inicial, data_final, dias_semana, recorrencia):
    dias_semana_map = {
        "Segunda": 0,
        "Terça": 1,
        "Quarta": 2,
        "Quinta": 3,
        "Sexta": 4,
        "Sábado": 5,
        "Domingo": 6,
    }

    # Mapeamento de intervalos baseado em recorrência
    if recorrencia == "Semanal":
        delta_dias = 7
    elif recorrencia == "Quinzenal":
        delta_dias = 14
    elif recorrencia == "Mensal":
        delta_dias = "Mensal"
    elif recorrencia == "Bimestral":
        delta_dias = "Bimestral"

    # Convertendo os dias da semana selecionados para números
    dias_semana_nums = []
    for dia in dias_semana:
        if dia in dias_semana_map:
            dias_semana_nums.append(dias_semana_map[dia])
        else:
            raise ValueError(f"Dia da semana inválido: {dia}")

    datas_recorrentes = []
    for dia_semana_num in dias_semana_nums:
        # Ajusta a data inicial para o primeiro dia da semana selecionada
        data_atual = data_inicial
        while data_atual.weekday() != dia_semana_num:
            data_atual += timedelta(days=1)

        # Agora geramos as datas até o limite da data final
        while data_atual <= data_final:
            datas_recorrentes.append(data_atual.strftime("%Y-%m-%d"))
            
            if delta_dias == "Mensal":
                # Avançar para o mesmo dia do mês seguinte
                next_month = data_atual.replace(day=28) + timedelta(days=4)  # Garantir que seja no mês seguinte
                data_atual = next_month.replace(day=dia_semana_num)
            elif delta_dias == "Bimestral":
                # Avançar dois meses completos
                next_month = data_atual.replace(day=28) + timedelta(days=4)
                data_atual = next_month.replace(month=(next_month.month % 12) + 2, day=dia_semana_num)
            else:
                data_atual += timedelta(days=delta_dias)

    return sorted(datas_recorrentes)


# Função para exibir o calendário com datas marcadas
def exibir_calendario(datas, ano, mes):
    cal = calendar.Calendar()
    dias_marcados = set(datas)

    tabela_calendario = """
    <style>
    table {width: 100%; border-collapse: collapse; text-align: center;}
    th {background-color: #4CAF50; color: white; padding: 10px;}
    td {padding: 10px;}
    td.marked {background-color: lightgreen; border: 1px solid #4CAF50; border-radius: 50%; text-align: center;}
    td.empty {background-color: #f9f9f9;}
    </style>
    <table>
        <thead>
            <tr>
                <th>Seg</th>
                <th>Ter</th>
                <th>Qua</th>
                <th>Qui</th>
                <th>Sex</th>
                <th>Sáb</th>
                <th>Dom</th>
            </tr>
        </thead>
        <tbody>
    """
    for semana in cal.monthdayscalendar(ano, mes):
        tabela_calendario += "<tr>"
        for dia in semana:
            if dia == 0:  # Dias fora do mês
                tabela_calendario += "<td class='empty'></td>"
            else:
                data_atual = datetime(ano, mes, dia).strftime("%Y-%m-%d")
                if data_atual in dias_marcados:
                    tabela_calendario += f"<td class='marked'>{dia}</td>"
                else:
                    tabela_calendario += f"<td>{dia}</td>"
        tabela_calendario += "</tr>"

    tabela_calendario += "</tbody></table>"
    return tabela_calendario


# Interface do Streamlit
st.set_page_config(page_title="Calendário Recorrente", layout="centered")
st.title("📅 Calendário Recorrente Interativo")

# Inicializando o estado persistente
if "ano" not in st.session_state:
    st.session_state.ano = datetime.today().year
if "mes" not in st.session_state:
    st.session_state.mes = datetime.today().month

# Seleção de parâmetros
st.sidebar.header("Configuração de Recorrência")
data_inicial = st.sidebar.date_input("Data Inicial", value=datetime.today())
data_final = st.sidebar.date_input("Data Final", value=datetime.today() + timedelta(days=30))

# Validação de datas
if data_final < data_inicial:
    st.sidebar.error("Erro: A data final não pode ser anterior à data inicial.")
    data_final = data_inicial + timedelta(days=30)  # Ajusta automaticamente para o futuro

recorrencia = st.sidebar.selectbox("Recorrência", ["Semanal", "Quinzenal", "Mensal", "Bimestral"])

# Condicional para seleção de dias da semana usando st.segmented_control
dias_semana_options = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]

if recorrencia == "Semanal":
    dias_semana = st.sidebar.multiselect(
        "Selecione os Dias da Semana",
        options=dias_semana_options,
        default=["Segunda"]
    )
else:
    dias_semana = st.sidebar.selectbox(
        "Selecione o Dia da Semana",
        options=dias_semana_options,
        index=0
    )

# Gerar datas recorrentes
try:
    datas = gerar_datas_recorrentes(data_inicial, data_final, dias_semana, recorrencia)
except ValueError as e:
    st.sidebar.error(f"Erro: {e}")
    datas = []

# Navegação entre meses
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    if st.button("◀️ Mês Anterior"):
        if st.session_state.mes == 1:
            st.session_state.mes = 12
            st.session_state.ano -= 1
        else:
            st.session_state.mes -= 1

with col3:
    if st.button("Próximo Mês ▶️"):
        if st.session_state.mes == 12:
            st.session_state.mes = 1
            st.session_state.ano += 1
        else:
            st.session_state.mes += 1

# Exibição do calendário
st.markdown(f"### {calendar.month_name[st.session_state.mes]} {st.session_state.ano}")
calendario_html = exibir_calendario(datas, st.session_state.ano, st.session_state.mes)
st.markdown(calendario_html, unsafe_allow_html=True)