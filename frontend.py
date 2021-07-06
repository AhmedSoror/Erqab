import streamlit as st
import datetime
import numpy as np

import pandas as pd

max = "max"
min_fare = "min_fare"
min_capacity = "min_capacity"
capacity = "capacity"
location_x = "location_x"
location_y = "location_y"

columns_name = [max  , min_fare  , min_capacity , capacity , location_x    , location_y]

# ---------------
# input
# N, Distance limit
# user i    :  max  , min_fare  , min_capacity , capacity , location_x    , location_y
# ---------------

#make a title for your webapp
st.title("Erqab")

#lets try a both a text input and area as well as a date
n = st.text_input('Total Number of users')
distance_limit = st.text_input('Distance_Limit')

if( n and distance_limit):
    # user i    :  max  , min_fare  , min_capacity , capacity , location_x    , location_y
    form = st.form(key='Input_Form')

    with form:
        cols = form.beta_columns(len(columns_name))
        for ind, col in enumerate(cols):
            # col.selectbox('{0}'.format(columns_name[ind]), ['click', 'or click'], key='{0}_{1}'.format(i, ind))
            for k in range(int(n)):
                col.text_input('{0}_{1}'.format(columns_name[ind],k+1))
    submit = form.form_submit_button('Submit')
    
    if submit:
        pass
        

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
