from os import listdir
from os.path import isfile, join
import os
import numpy as np
import itertools
import sys
from ortools.linear_solver import pywraplp
from ortools.sat.python import cp_model
import csv
import signal
from contextlib import contextmanager
import time

sys.setrecursionlimit(500000)

# --------------------------------------------------------------------------------------------------------------
# -------------------------------------------  Globals  --------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------
EPS =10e-8
INF = 10e18
str_dis = "distance_limit"
str_n = "N"
str_cap = "Caps"
str_max = "Passengers_Max"
str_min_fare = "min_fare_per_passenger"
str_min_pass = "total_min_passenger"


# --------------------------------------------------------------------------------------------------------------
# -------------------------------------------  I/O  ------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------
# N, Distance limit
# user i:  max, min_fare, min_passengers, capacity
# --------------------------------------------------------------------------------------------------------------
def ReadLine(file):
    line = file.readline()
    data = line.split(" ")
    # remove "\n"
    data[-1] = int(data[-1][0:-1])
    # convert to int
    for i in range(len(data)):
        data[i] = int(data[i])
    return data

def Get_N_Dist(file):
    data = ReadLine(file)
    return {str_n: data[0], str_dis: data[1]}

def ReadTextFile(testFile):
    print("Reading test file: {0}".format(testFile))
    with open(testFile) as f:
        # add n, m to data
        data = Get_N_Dist(f)
        
        # read constraints 
        maxs=[]
        min_fare=[]
        min_pass=[]
        capacities=[]

        for i in range(data["N"]):
            user=ReadLine(f)
            maxs.append(user[0])
            min_fare.append(user[1])
            min_pass.append(user[2])
            capacities.append(user[3])
        f.close()
            
    data[str_max] = maxs
    data[str_min_fare] = min_fare
    data[str_min_pass] = min_pass
    data[str_cap] = capacities
    
    return data

# --------------------------------------------------------------------------------------------------------------
# ------------------------------------------- Solver -----------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------

# MIP solution
def SolverMIP(data):
    run_time=0
    start_time = time.time()


    # init MIP solver
    solver = pywraplp.Solver.CreateSolver('SCIP')
    objective = solver.Objective()

    # declare variables
    Xs=[0]*data["N"]*data["N"]
    
    objective_terms = []
    for i in range(data["N"]*2):
        # create variables
        Xs[i]=solver.IntVar(0, 1, 'x_{0}'.format(i))
        # set objective
        objective_terms.append(Xs[i])
        
    solver.Maximize(solver.Sum(objective_terms))
    
    # add constraints
    # --------
    


# --------------------------------------------------------------------------------------------------------------
# ------------------------------------------- Main -----------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------


if __name__=="__main__":
    if len(sys.argv)>1:
        print(sys.argv[1])
        # main_testfile(sys.argv[1])
    