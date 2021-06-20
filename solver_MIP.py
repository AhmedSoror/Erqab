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
import math

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
str_location = "locations"

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
        locations = []

        for i in range(data["N"]):
            user=ReadLine(f)
            maxs.append(user[0])
            min_fare.append(user[1])
            min_pass.append(user[2])
            capacities.append(user[3])
            locations.append((user[4],user[5]))
        f.close()
            
    data[str_max] = maxs
    data[str_min_fare] = min_fare
    data[str_min_pass] = min_pass
    data[str_cap] = capacities
    
    return data

# --------------------------------------------------------------------------------------------------------------
# ------------------------------------------- Solver -----------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------

def GetDist(loc_A, loc_B):
    return math.sqrt( math.pow(loc_A[0]-loc_B[0],2) + math.pow(loc_A[1]-loc_B[1],2))
    


# MIP solution
def SolverMIP(data):
    run_time=0
    start_time = time.time()

    # init MIP solver
    solver = pywraplp.Solver.CreateSolver('SCIP')
    objective = solver.Objective()

    # declare variables
    Xs = [[0]*data[str_n]]*data[str_n]
    Ds = [0]*data[str_n]
    Ps = [0]*data[str_n]
    Caps = data[str_cap]
    distance_limit = data[str_dis]
    passengers_max = data[str_max]
    min_fares = data[str_min_fare]
    min_passengers=data[str_min_pass]
    locations = data[str_location]    



    # create variables
    for i in range(data[str_n]):
        for j in range(str_n):
            Xs[i][j]=solver.IntVar(0, 1, 'x_{0}_{1}'.format(i,j))
    
    for i in range(len(Ds)):
        Ds[i]=solver.IntVar(0, 1, 'D_{0}'.format(i))
        Ps[i]=solver.IntVar(0, 1, 'P_{0}'.format(i))
        
    # set objective
    solver.Maximize(solver.Sum(Xs))
    
    # add constraints
    # --------
    for i in range(len(Xs)):       
        #a) If a user is a driver, he/she is matched with at most \emph{$C_{i}$} passengers. 
        solver.Add(solver.Sum(Xs[i]) <= Caps[i]*Ds[i])
        
        #b) If a user is a passenger, he/she is matched with at most 1 driver
        passengers = [row[i] for row in Xs]
        solver.Add(solver.Sum(passengers) <= 1)

        #c) Every user is either a driver or a passenger
        solver.Add(Ds[i]+Ps[i] <= 1)

        #f) driver_i$ has at least $D\_min\_pass_{i}$ matched passengers
        solver.Add(solver.Sum(Xs[i]) >= min_passengers[i]*Ds[i])
    

    for i in range (len(Xs)):
        for j in range (len(Xs[i])):
            # d) Any matched driver and passenger should be within a distance of distance\_limit from each other
            solver.Add(Xs[i][j] * GetDist(locations[i],locations[j])  <= distance_limit)
            
            # e) Passenger can pay the fare that is charged by the matched driver
            solver.Add(Xs[i][j] * passengers_max[j] <= min_fares[i])
   
    
    solver.Solve()
    run_time=time.time() - start_time
    Xs_values = [[0]*data[str_n]]*data[str_n]
    for i in range (len(Xs)):
        for j in range (len(Xs[i])):
            Xs_values[i][j]=Xs[i][j].solution_value()
    
    
    # dic = getFacWH(Xs_values)
    return {"z":round(solver.Objective().Value()), "Xs": Xs_values,"time":run_time}
    


# --------------------------------------------------------------------------------------------------------------
# ------------------------------------------- Main -----------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------


if __name__=="__main__":
    if len(sys.argv)>1:
        print(sys.argv[1])
        # main_testfile(sys.argv[1])
    