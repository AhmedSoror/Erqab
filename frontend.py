# -------------------------------------------------------
# -----------------
# to do
# -----------------
# 1) extract data from CSV
# 2) solve multiple instance
# 3) display multiple outputs
# 4) 

# View input and output on the map
# view output records
# validate inputs
# limit input to 10 users, more than that => read from csv
# 
# -------------------------------------------------------
# -------------------------------------------------------
# -------------------------------------------------------
import streamlit as st
import SessionState 
import datetime
import numpy as np
import pandas as pd
from solver_MIP import SolverMIP

# ----------------
# Global variables
# ----------------
max = "max"
min_fare = "min_fare"
min_capacity = "min_capacity"
capacity = "max_capacity"
location_x = "location_x"
location_y = "location_y"
columns_name = [max, min_fare, min_capacity, capacity, location_x, location_y]
 
solver_Greedy ="Greedy"
solver_MIP ="MIP"
solver_Meta ="Meta"
solver_DP ="DP"
# ----------------
# dictionary keys
# ----------------

# total number of users
str_n = "n"
# distance limit
str_dis = "dl"
# capcity per driver
str_cap = "c"
# locations of users
str_location = "loc"
# array: the max money passenger i can pay.
str_pay = "pay"
# array: money charged by the driver i per passenger
str_fare = "fare"
# array: the min number of passengers to travel with the driver
str_min_cap = "minc"
# key in output dictionary that holds cars. note: should be changed later on
str_cars="Xs"
dictionary_keys = [str_pay, str_fare, str_min_cap, str_cap, str_location]


# -----------------------
# Solve
# -----------------------
def SolveInstance(data, solver_select):
    if solver_select == solver_MIP :
        sol = SolverMIP(data)
    # elif solver_select == solver_Greedy :
    #     sol.append(SolverGreedy(data))
    # elif solver_select == solver_DP :
    #     sol.append(SolverDP(data))
    # else:
    #     sol.append(SolverMeta(data))
    return sol

def SolveBulk(bulk_data, solver_select):
    sol = []
    for data in bulk_data:
        sol.append(SolveInstance(data, solver_select))
    return sol


# -----------------------
# Input Component
# -----------------------
def GetInputDict(data_input):
    data_dir = {str_n: data_input[str_n], str_dis: data_input[str_dis]}
    data = data_input["data"]
    for i in range(len(dictionary_keys)):
        data_dir[dictionary_keys[i]] = data[i]

    locations_arr = np.vstack((data[-2], data[-1])).T.tolist()
    data_dir[str_location] = locations_arr

    return data_dir

def InputComponent_old():
    with st.beta_expander("Input", expanded=True):
        col1, col2 = st.beta_columns(2)
        with col1:
            n = st.text_input('Total Number of users')
        with col2:
            distance_limit = st.text_input('Distance_Limit')

        if(n and distance_limit):
            n = int(n)
            distance_limit = int(distance_limit)

            data_width = n
            data_height = len(columns_name)

            data = [0]*data_height
            for i in range(data_height):
                data[i] = [0]*data_width

            # user i    :  max  , min_fare  , min_capacity , capacity , location_x    , location_y
            form = st.form(key='Input_Form')
            with form:
                cols = form.beta_columns(len(columns_name))
                for ind, col in enumerate(cols):
                    # col.write("as")
                    for usr in range(int(n)):
                        data[ind][usr] = col.text_input(
                            '{0}_{1}'.format(columns_name[ind], usr+1))
                        if(data[ind][usr]):
                            data[ind][usr] = (int)(data[ind][usr])
                        # col.selectbox('{0}'.format(columns_name[ind]), [i for i in range(10)], key='{0}_{1}'.format(columns_name[ind],k+1))

            submit = form.form_submit_button('Submit')

            if submit:
                data_dir = GetInputDict({str_n:n,str_dis:distance_limit,"data":data})
                sol = SolverMIP(data_dir)
                return sol

def InputComponent(id=0):
    col1, col2 = st.beta_columns(2)
    with col1:
        n = st.text_input('Total Number of users', key="n_{0}".format(id))
    with col2:
        distance_limit = st.text_input('Distance_Limit', key="dl_{0}".format(id))

    if(n and distance_limit):
        n = int(n)
        distance_limit = int(distance_limit)
        data_width = n
        data_height = len(columns_name)

        data = [0]*data_height
        for i in range(data_height):
            data[i] = [0]*data_width

        for usr in range(int(n)):
            with st.beta_expander("users {0}".format(usr+1), expanded=False):
                cols = st.beta_columns(len(columns_name))
                for ind, col in enumerate(cols):
                    data[ind][usr] = col.text_input(label='{0}'.format(columns_name[ind], usr+1), key='{0}_{1}_{2}'.format(columns_name[ind], usr+1, id))
                    if(data[ind][usr]):
                        data[ind][usr] = (int)(data[ind][usr])
                    # col.selectbox('{0}'.format(columns_name[ind]), [i for i in range(10)], key='{0}_{1}'.format(columns_name[ind],k+1))

        # m = st.markdown("""
        # <style>
        # div.stButton > button:first-child {
        #     background-color: rgb(70, 187, 26);
        # }
        # </style>""", unsafe_allow_html=True)

        
        solver_select = st.selectbox('Solver', [solver_Greedy,solver_MIP,solver_Meta,solver_DP], key="solver_select")

        mip_but = st.button('solve')
        if(mip_but):
            # df = pd.DataFrame(data,columns=(columns_name))
            # st.dataframe(df)
            data_dir = GetInputDict({str_n:n,str_dis:distance_limit,"data":data})
            return SolveInstance(data_dir, solver_select)

def SingleInputComponent(session):
    if st.button("Reset"):
        session.run_id += 1
    sol = InputComponent(session.run_id)
    if sol:
        OutputComponent(sol, session.run_id)

def CSVInput():
    path = st.text_input('CSV file path')
    if path:
        df = pd.read_csv(path, header=None, sep='\n')
        df = df[0].str.split(',', expand=True)
        df






# -----------------------
# Output Component
# -----------------------
def OutputComponent(data, id=0):
    st.write("Traverllers: {0}".format(data["z"]))
    # display cars
    data_1 = {"Cars":data[str_cars]}
    df = pd.DataFrame.from_dict(data_1)
    st.dataframe(df)


# -----------------------
# Main page
# -----------------------
def main(id=0):
    # style all buttons to be green by default
    m = st.markdown("""
        <style>
        div.stButton > button:first-child {
            background-color: rgb(70, 187, 26);
        }
        </style>""", unsafe_allow_html=True)
        
    # make a title for your webapp
    st.title("Erqab")
    # session id used for reset
    session = SessionState.get(run_id=0)
    
    sidebar = st.sidebar.radio("page",["Single Input", "Upload CSV"],0)
    if(sidebar == "Single Input"):
        SingleInputComponent(session)
    elif (sidebar == "Upload CSV"):
        # increment session id to reset component
        session.run_id += 1
        CSVInput()
        
# -----------------------
# -----------------------
# -----------------------
if __name__=="__main__":
    main()





