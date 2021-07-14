# -------------------------------------------------------
# -----------------
# to do
# -----------------
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
import numpy as np
import pandas as pd
import SessionState 
import streamlit as st
from solver import ReadDF
from solver import SolverDP
from solver import SolverMIP
from solver import SolverMeta
from solver import SolverGreedy
from altair.vegalite.v4.schema.channels import Key

# ----------------
# Global variables
# ----------------
EPS =10e-8
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
str_cars = "cars"
dictionary_keys = [str_pay, str_fare, str_min_cap, str_cap, str_location]


# -----------------------
# Solve
# -----------------------
def SolveInstance(data, solver_select):
    # my_bar = st.progress(0)
    # for percent_complete in range(100):
    #     time.sleep(0.1)
    #     my_bar.progress(percent_complete + 1)
    
    spinner_msg = 'Solving...'
    if solver_select == solver_MIP :
        with st.spinner(spinner_msg):
            sol = SolverMIP(data)
            
    elif solver_select == solver_Greedy :
        with st.spinner(spinner_msg):
            sol = SolverGreedy(data)
    elif solver_select == solver_DP :
        with st.spinner(spinner_msg):
            sol = SolverDP(data)
    else:
        with st.spinner(spinner_msg):
            sol = SolverMeta(data)
    return sol

def SolveBulk(bulk_data, solver_select):
    sol = []
    for data in bulk_data:
        sol.append(SolveInstance(data, solver_select))
    return sol


# -----------------------
# Input Component
# -----------------------
# get input dictionary from input areas
def GetInputDict(data_input):
    data_dir = {str_n: data_input[str_n], str_dis: data_input[str_dis]}
    data = data_input["data"]
    for i in range(len(dictionary_keys)):
        data_dir[dictionary_keys[i]] = data[i]

    locations_arr = np.vstack((data[-2], data[-1])).T.tolist()
    data_dir[str_location] = locations_arr

    return data_dir

# input component with input fields
def InputComponent(id=0):
    # place buttons on two columns
    col1, col2 = st.beta_columns(2)
    with col1:
        n = st.text_input('Total Number of users', key="n_{0}".format(id))
    with col2:
        distance_limit = st.text_input('Distance_Limit', key="dl_{0}".format(id))
    # get data of n users after entering n and distance
    if(n and distance_limit):
        n = int(n)
        distance_limit = int(distance_limit)
        data_width = n
        data_height = len(columns_name)

        # initialize array to hold users data
        data = [0]*data_height
        for i in range(data_height):
            data[i] = [0]*data_width
        # data for each user
        for usr in range(int(n)):
            # each user in an expander
            with st.beta_expander("users {0}".format(usr+1), expanded=False):
                # display input areas in columns next to each other
                cols = st.beta_columns(len(columns_name))
                for ind, col in enumerate(cols):
                    # store input to input array
                    data[ind][usr] = col.text_input(label='{0}'.format(columns_name[ind], usr+1), key='{0}_{1}_{2}'.format(columns_name[ind], usr+1, id))
                    if(data[ind][usr]):
                        data[ind][usr] = (int)(data[ind][usr])

        # solve 
        solver_select = st.selectbox('Solver', [solver_Greedy,solver_MIP,solver_Meta,solver_DP], key="solver_select")
        solve_but = st.button('solve')
        if(solve_but):
            # convert input array to input dictionary accepted by the solver
            data_dir = GetInputDict({str_n:n,str_dis:distance_limit,"data":data})
            # solve instance by the selected solver
            return SolveInstance(data_dir, solver_select)

# singe input component
def SingleInputComponent(session):
    # reset by incrementing session id
    if st.button("Reset"):
        session.run_id += 1
    sol = InputComponent(session.run_id)
    if sol:
        OutputComponent(sol, session.run_id)

# csv input
def CSVInput(id=0):
    # # path = st.text_input('CSV file path')
    path = st.file_uploader("Choose a file",type=['csv'])
    if path:
        df = pd.read_csv(path, header=None, sep='\n')
        path.seek(0)
        df = df[0].str.split(',', expand=True)
        bulk_data = ReadDF(df)
        if bulk_data:
            solver_select = st.selectbox('Solver', [solver_Greedy,solver_MIP,solver_Meta,solver_DP], key="solver_select")
            solve_but = st.button('solve')
            if(solve_but):
                solutions = SolveBulk(bulk_data, solver_select)
                if solutions:
                    OutputBulk(solutions, id)
            return bulk_data





# -----------------------
# Output Component
# -----------------------
def OutputComponent(data, id=0):
    # dispaly total number of travellers
    st.write("Traverllers: {0}".format(data["z"]))
    # display cars
    data_1 = {"Cars":data[str_cars]}
    df = pd.DataFrame.from_dict(data_1)
     
    # drop rows with only 0s
    # a_series = (df != 0).any(axis=1)
    # df_noZeros = df.loc[a_series]
    
    # display matchings
    st.write('Matchings: ',df, Key="asd{0}".format(id))

# output multiple solutions
def OutputBulk(solutions, id=0):
    for sol in solutions:
        OutputComponent(sol, id)    


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
    # create a side bar to switch between single input and bulk input
    sidebar = st.sidebar.radio("page",["Single Input", "Upload CSV"],0)
    if(sidebar == "Single Input"):
        SingleInputComponent(session)
    elif (sidebar == "Upload CSV"):
        # increment session id to reset single input component
        session.run_id += 1
        bulk_data = CSVInput()
                

        
# -----------------------
# -----------------------
# -----------------------
if __name__=="__main__":
    main()





