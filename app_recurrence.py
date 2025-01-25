import streamlit as st
from datetime import datetime, timedelta
import pandas as pd

# --- Variáveis globais ----
days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
recurrence_options = ["Weekly", "Fortnightly", "Monthly", "Bimonthly"]
# ----- FUNÇÕES ------
def get_current_date():
    today = datetime.now()
    return today.strftime("%d/%m/%Y")

def generate_date_ordered_list(init_date, final_date):
    # Converter strings para objetos datetime
    init_date_obj = datetime.strptime(init_date, "%d/%m/%Y")
    final_date_obj = datetime.strptime(final_date, "%d/%m/%Y")
    
    # Lista para armazenar as datas e dias da semana
    data = []
    current_date = init_date_obj
    
    # Loop para preencher os dados
    while current_date <= final_date_obj:
        data.append({
            "Date": current_date.strftime("%d/%m/%Y"),
            "Day of the week": current_date.strftime("%A")
        })
        current_date += timedelta(days=1)
    
    # Criar o DataFrame
    df_ordered_list = pd.DataFrame(data)
    return df_ordered_list

def generate_single_date_ordered(single_event_date):
    # Converter a string para um objeto datetime
    init_date_obj = datetime.strptime(single_event_date, "%d/%m/%Y")
    
    # Criar o DataFrame com a data única
    data = [{
        "Date": init_date_obj.strftime("%d/%m/%Y"),
        "Day of the week": init_date_obj.strftime("%A")
    }]
    
    df_single_date = pd.DataFrame(data)
    return df_single_date

def days_of_week_filter(select_order_date, df_ordered_list):
    # Mapeamento de nomes completos para abreviações
    full_to_abbrev = {
        "Monday": "Mon",
        "Tuesday": "Tue",
        "Wednesday": "Wed",
        "Thursday": "Thu",
        "Friday": "Fri",
        "Saturday": "Sat",
        "Sunday": "Sun"
    }

    # Adicionar uma nova coluna de abreviações no DataFrame
    df_ordered_list["Day Abbrev"] = df_ordered_list["Day of the week"].map(full_to_abbrev)

    # Garantir que `select_order_date` seja uma lista (caso seja uma string, transforma em lista)
    if isinstance(select_order_date, str):
        select_order_date = [select_order_date]

    # Filtrar o DataFrame com base na lista de abreviações
    df_ordered_filtered = df_ordered_list[df_ordered_list["Day Abbrev"].isin(select_order_date)]

    # Remover a coluna de abreviações antes de retornar
    df_ordered_filtered = df_ordered_filtered.drop(columns=["Day Abbrev"])

    return df_ordered_filtered

# Função para filtrar recorrência semanal
def filter_weekly(df_ordered_list):
    return df_ordered_list  # A recorrência semanal já está coberta pela seleção dos dias da semana

# Função para filtrar recorrência quinzenal (um sim, um não)
def filter_fortnightly(df_ordered_list):
    # Filtra os dados a cada 2 linhas, começando pela primeira
    return df_ordered_list.iloc[::2]

# Função para filtrar recorrência mensal (um sim, três não)
def filter_monthly(df_ordered_list):
    # Filtra os dados com um intervalo de 4 linhas, começando pela primeira
    return df_ordered_list.iloc[::4]

# Função para filtrar recorrência bimestral (um sim, sete não)
def filter_bimonthly(df_ordered_list):
    # Filtra os dados com um intervalo de 8 linhas, começando pela primeira
    return df_ordered_list.iloc[::8]

# ----- Formulário para criação de eventos -----
@st.dialog("Event creation form")
def event_generate_forms():
    # --- Configuração da sidebar
    st.header("Create new event:")

    # Escolha por evento recorrente
    recurrent_events = st.checkbox('Want to create recurring event?')

    # Seleção para eventos recorrentes
    if recurrent_events:
        # Escolha da faixa de datas
        init_date = st.date_input("Determine the start date:", datetime.now()).strftime("%d/%m/%Y")  
        atual_date = st.checkbox("Use today's date as initial", value=False)

        if atual_date:
            init_date = datetime.now().strftime("%d/%m/%Y")
            st.write(f"Initial date: {init_date}")

        final_date = st.date_input("Determine the end date:", datetime.now() + timedelta(days=7)).strftime("%d/%m/%Y")

        recurrence = st.selectbox("Determine the desired recurrence", recurrence_options)

        if recurrence == "Weekly":
            select_order_date = st.segmented_control(
            "Determine the days of the week", days_of_week, selection_mode="multi")

        elif recurrence =="Fortnightly":
            select_order_date = st.segmented_control(
            "Determine the days of the week", days_of_week, selection_mode="single")

        elif recurrence =="Monthly":
            select_order_date = st.segmented_control(
            "Determine the days of the week", days_of_week, selection_mode="single")
        elif recurrence == "Bimonthly":
            select_order_date = st.segmented_control(
            "Determine the days of the week", days_of_week, selection_mode="single")
    # Botão para gerar eventos
        if st.button("Generate Events"):
            df_ordered_list = generate_date_ordered_list(init_date, final_date)

            df_ordered_filtered = days_of_week_filter(select_order_date, df_ordered_list)

            if recurrent_events:
                if recurrence == "Weekly":
                    df_final = filter_weekly(df_ordered_filtered)
                elif recurrence =="Fortnightly":
                    df_final = filter_fortnightly(df_ordered_filtered)
                elif recurrence =="Monthly":
                    df_final = filter_monthly(df_ordered_filtered)
                elif recurrence == "Bimonthly":
                    df_final = filter_bimonthly(df_ordered_filtered)

            # Armazenando a lista gerada no estado de sessão
            st.session_state['list_generated'] = df_final

            st.rerun()

    else:
        st.subheader('Create a single event')
        single_event_date = st.date_input("Determine the event date:", datetime.now()).strftime("%d/%m/%Y")

        if st.button("Create event"):
            df_single_date = generate_single_date_ordered(single_event_date)
            # Armazenando a lista gerada no estado de sessão
            st.session_state['list_generated'] = df_single_date

            st.rerun()
# ------ PÁGINA -----
def app():
    st.header("Welcome to the recurrences app")
    
    # Botão para chamar o formulário de eventos
    if st.button("Create new event"):
        event_generate_forms()
    # Exibindo a tabela gerada fora do dialog
    if st.button("Show events list"):
        if 'list_generated' in st.session_state:
            st.write(st.session_state['list_generated'])

# Executar o app
if __name__ == "__main__":
    app()
