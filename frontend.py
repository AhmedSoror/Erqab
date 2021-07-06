# -------------------------------------------------------
# -----------------
# to do
# -----------------
# validate inputs
# limit input to 10 users, more than that => read from csv
# reset button
# choose solver and run
# view results
# view output records
# View input and output on the map 


import streamlit as st
import datetime
import numpy as np
import pandas as pd
from solver_MIP import SolverMIP

max = "max"
min_fare = "min_fare"
min_capacity = "min_capacity"
capacity = "max_capacity"
location_x = "location_x"
location_y = "location_y"

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

columns_name = [max  , min_fare  , min_capacity , capacity , location_x    , location_y]
dictionary_keys = [
    str_pay,
    str_fare,
    str_min_cap,
    str_cap,
    str_location
    ]

# ---------------
# input
# N, Distance limit
# user i    :  max  , min_fare  , min_capacity , capacity , location_x    , location_y
# ---------------

#make a title for your webapp
st.title("Erqab")



with st.beta_expander("Input", expanded=True):
    col1, col2 = st.beta_columns(2)
    with col1:
        n = st.text_input('Total Number of users')
    with col2:
        distance_limit = st.text_input('Distance_Limit')

    if( n and distance_limit):
        n =int(n)
        distance_limit = int(distance_limit)

        data_width = n
        data_height = len(columns_name)
        
        data = [0]*data_height
        for i in range(data_height):
            data[i]= [0]*data_width

        # user i    :  max  , min_fare  , min_capacity , capacity , location_x    , location_y
        form = st.form(key='Input_Form')
        with form:
            cols = form.beta_columns(len(columns_name))
            for ind, col in enumerate(cols):
                    # col.write("as")
                for usr in range(int(n)):
                    data[ind][usr] = col.text_input('{0}_{1}'.format(columns_name[ind],usr+1))
                    if(data[ind][usr]):
                        data[ind][usr] = (int)(data[ind][usr])
                    # col.selectbox('{0}'.format(columns_name[ind]), [i for i in range(10)], key='{0}_{1}'.format(columns_name[ind],k+1))


        submit = form.form_submit_button('Submit')
        
        if submit:
            data_dir = {str_n: n, str_dis: distance_limit}     

            for i in range(len(dictionary_keys)):
                data_dir[dictionary_keys[i]] = data[i]
            
            
            locations_arr = np.vstack((data[-2], data[-1])).T.tolist()
            data_dir[str_location] = locations_arr 

            # df = pd.DataFrame(data,columns=(columns_name))
            # st.dataframe(df)

            print(data_dir)    
            
            print(SolverMIP(data_dir))




# -----------------
# Read CSV
# -----------------
# path = st.text_input('CSV file path')
# if path:
#     df = pd.read_csv(path)
#     df
# -------------------------------------------------------


# -----------------
# Display dataframe
# -----------------

# # Get some data.
# data = np.random.randn(10, 2)

# # Show the data as a chart.
# chart = st.line_chart(data)

# start_date = datetime.date(1990, 7, 6)
# date = st.date_input('Your birthday', start_date)

# if date != start_date:
#     field_1
#     field_2
#     date


# Randomly fill a dataframe and cache it
# @st.cache(allow_output_mutation=True)
# def get_dataframe():
#     # max  , min_fare  , min_capacity , capacity , location_x    , location_y
#     return pd.DataFrame(
#         np.random.randn(5, len(columns_name)),
#         columns=(columns_name)
#         )


# df = get_dataframe()

# # Create row, column, and value inputs
# row = st.number_input('row', max_value=df.shape[0])
# col = st.number_input('column', max_value=df.shape[1])
# value = st.number_input('value')

# # Change the entry at (row, col) to the given value
# df.values[row][col] = value

# # And display the result!
# st.dataframe(df)
