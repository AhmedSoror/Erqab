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
import re
import pandas as pd
sys.setrecursionlimit(500000)

# --------------------------------------------------------------------------------------------------------------
# -------------------------------------------  Globals  --------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------
str_cars = "cars"
str_z = "z"
EPS =10e-8
INF = 10e18
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

# --------------------------------------------------------------------------------------------------------------
# -------------------------------------------  I/O  ------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------
# N, Distance limit
# user i    :  max  , min_fare  , min_capacity , capacity , location_x    , location_y
# ---------------------------------------------------------------------------------------
# driver    :  0 , min_fare  , min_capacity , capacity , location_x    , location_y
# Passenger :  max  ,   0     ,       0        ,  0       , location_x    , location_y

# --------------------------------------------------------------------------------------------------------------

def atoi(text):
    return int(text) if text.isdigit() else text
def natural_keys(summary):
    text = summary['test_case']
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]
def sortFile(files_arr):
    return [ atoi(c) for c in re.split(r'(\d+)', files_arr) ]

def ReadTestSet(test_set):
    testFiles = [join(test_set, f) for f in listdir(test_set) if isfile(join(test_set, f))]
    testFiles.sort(reverse=False, key=sortFile)
    return testFiles

def ReadLine(file,delimiter=" "):
    line = file.readline().replace("\n","")
    data = line.split(delimiter)
    # remove "\n"
    # data[-1] = int(data[-1][0:-1])
    # convert to int
    for i in range(len(data)):
        data[i] = int(data[i])
    return data

def Get_N_Dist(file, delimiter=" "):
    data = ReadLine(file, delimiter)
    return {str_n: data[0], str_dis: data[1]}

def ReadTextFile(testFile, delimiter=" "):
    print("Reading test file: {0}".format(testFile))
    with open(testFile) as f:
        # add n, m to data
        data = Get_N_Dist(f, delimiter)
        
        # read constraints 
        maxs=[]
        min_fare=[]
        min_pass=[]
        capacities=[]
        locations = []

        for i in range(data[str_n]):
            user=ReadLine(f,delimiter)
            maxs.append(user[0])
            min_fare.append(user[1])
            min_pass.append(user[2])
            capacities.append(user[3])
            locations.append((user[4],user[5]))
        f.close()   
            
    data[str_pay] = maxs
    data[str_fare] = min_fare
    data[str_min_cap] = min_pass
    data[str_cap] = capacities
    data[str_location] = locations
    
    return data


def MatchesToCars(matches):
    x = np.array(matches)
    x = x[~np.all(x == 0, axis=1)]
    cars = []
    for arr in x:
        c = 0
        car=[]
        for i in arr:
            c+=1
            if i==1:
                car.append(c)
        cars.append(car)
    return cars
    
    
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
    # Xs = [[0]*data[str_n]]*data[str_n]
    Xs = []
    Ds = []
    Ps = []
    Xs_objective=[]
    Caps = data[str_cap]
    distance_limit = data[str_dis]
    pays = data[str_pay]
    fares = data[str_fare]
    min_caps=data[str_min_cap]
    locations = data[str_location]    



    # create variables
    for i in range(data[str_n]):
        Xs.append([])
        for j in range(data[str_n]):
            Xs[i].append(solver.IntVar(0, 1, 'x_{0}_{1}'.format(i,j)))
            Xs_objective.append(Xs[i][j])
    
    for i in range(data[str_n]):
        Ds.append(solver.IntVar(0, 1, 'D_{0}'.format(i)))
        Ps.append(solver.IntVar(0, 1, 'P_{0}'.format(i)))
        
    # set objective
    
    # solver.Maximize(solver.Sum([row[i] for row in Xs]))
    solver.Maximize(solver.Sum(Xs_objective))
    

    
    # add constraints
    # --------
    for i in range(len(Xs)):       
        #a) Each driver is matched with himself
        # Xs[i][i] = Ds[i]
        solver.Add(Xs[i][i] - Ds[i] <= EPS)


        #b) If a user is a driver, he/she is matched with at most c_i passengers (not including himself).
        solver.Add(solver.Sum(Xs[i]) <= (Caps[i]+1)*Ds[i])
        
        #c) A user is matched with at most 1 driver
        passengers = [row[i] for row in Xs]
        solver.Add(solver.Sum(passengers) <= 1)

        #d) Every user is either a driver or a passenger
        solver.Add(Ds[i]+Ps[i] <= 1)

        #g) driver_i has at least minc i matched passengers (not includnig himself)
        solver.Add(solver.Sum(Xs[i]) >= (min_caps[i]+1)*Ds[i])
    

    for i in range (len(Xs)):
        for j in range (len(Xs[i])):
            # e) Any matched driver and passenger should be within a distance of distance limit from each other
            solver.Add(Xs[i][j] * GetDist(locations[i],locations[j]) <= distance_limit)
            
            # f) Passenger can pay the fare that is charged by the matched driver
            if(i!=j):
                solver.Add(Ps[j]*pays[j] >= Xs[i][j]*fares[i])

            
    
    solver.Solve()
    run_time=time.time() - start_time
    Xs_values = []
    Ds_values = []
    Ps_values = []
    for i in range (len(Xs)):
        Xs_values.append([])
        Ds_values.append(Ds[i].solution_value())
        Ps_values.append(Ps[i].solution_value())
        for j in range (len(Xs[i])):
            Xs_values[i].append((int)(Xs[i][j].solution_value()))
    cars_arr = MatchesToCars(Xs_values)

    return {str_z:round(solver.Objective().Value()), str_cars: cars_arr, "Xs": Xs_values,"time":run_time}
    
# --------------------------------------------------------------------------------------------------------------
# ------------------------------------------- Main -----------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------

def main_testfile(test_set):
    testFiles = iter(ReadTestSet(test_set))
    testFile=next(testFiles, None)
    summary=[]
    while testFile != None:
        # get current test file path
        testFile_parent = testFile.split("/")[0]+'_output'
        testFile_name = testFile.split("/")[-1]
        testFile_name = testFile_name.replace("in", "out")
        
        testCase = ReadTextFile(testFile)
        
        # ---------------------------------------------------------------------------
        # ------------------------------ MIP --------------------------------------
        # ---------------------------------------------------------------------------
        sol_MIP = SolverMIP(testCase)
        print(sol_MIP)
        
        # ---------------------------------------------------------------------------
        # ----------------------------- summary -------------------------------------
        # ---------------------------------------------------------------------------
        
        testFile=next(testFiles, None)

if __name__=="__main__":
    if len(sys.argv)>1:
        print(sys.argv[1])
        main_testfile(sys.argv[1])
    
        