from os import listdir
from os.path import isfile, join
import os
import numpy as np
import itertools
import sys
from numpy.lib.function_base import average
from ortools.linear_solver import pywraplp
from ortools.sat.python import cp_model
import csv
import signal
from contextlib import contextmanager
import time
import math
import re
from random import choice

sys.setrecursionlimit(500000)

# --------------------------------------------------------------------------------------------------------------
# -------------------------------------------  Globals  --------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------

INVALID = 0

str_cars = "cars"
str_z = "z"
EPS = 10e-8
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
# driver    :  -inf , min_fare  , min_capacity , capacity , location_x    , location_y
# Passenger :  max  ,   inf     ,       0        ,  0       , location_x    , location_y

# --------------------------------------------------------------------------------------------------------------


def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(summary):
    text = summary['test_case']
    return [atoi(c) for c in re.split(r'(\d+)', text)]


def sortFile(files_arr):
    return [atoi(c) for c in re.split(r'(\d+)', files_arr)]


def ReadTestSet(test_set):
    testFiles = [join(test_set, f)
                 for f in listdir(test_set) if isfile(join(test_set, f))]
    testFiles.sort(reverse=False, key=sortFile)
    return testFiles


def ReadLine(file):
    line = file.readline()
    data = line.split(" ")
    # remove "\n"
    # data[-1] = int(data[-1][0:-1])
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
        maxs = []
        min_fare = []
        min_pass = []
        capacities = []
        locations = []

        for i in range(data[str_n]):
            user = ReadLine(f)
            maxs.append(user[0])
            min_fare.append(user[1])
            min_pass.append(user[2])
            capacities.append(user[3])
            locations.append((user[4], user[5]))
        f.close()

    data[str_pay] = maxs
    data[str_fare] = min_fare
    data[str_min_cap] = min_pass
    data[str_cap] = capacities
    data[str_location] = locations

    return data


# --------------------------------------------------------------------------------------------------------------
# ------------------------------------------- Solver Greedy ----------------------------------------------------
# --------------------------------------------------------------------------------------------------------------
def SolverGreedy(data):
    # -- extracting inputs
    n = data[str_n]
    capacities = data[str_cap]
    max_pays = data[str_pay]
    min_fares = data[str_fare]
    min_capacities = data[str_min_cap]
    locations = data[str_location]
    dl = data[str_dis]
    # -- start timer
    start_time = time.time()

    matched = [0]*n  # -- if user i is matched with any driver matched[i]=1
    drivers = []  # -- list containing driver indeces
    cars = []  # -- list that will collect the soltion
    average_cap = 0
    for i in range(0, n):  # -- every user is either a driver, a passenger or randomly choose if he/she didnt specify
        if max_pays[i] == INVALID:
            drivers.append(i)
            cars.append([])
            matched[i] = 1
            average_cap += capacities[i]

    drivers_count = sum(matched)
    drivers_count =1  if (drivers_count==0) else drivers_count
    average_cap = math.floor(average_cap/drivers_count)
    # ----------------------------------------------------
    # -- too few drivers, start again and use random to get some drivers
    if(drivers_count < math.floor(n/(average_cap+1))):
        matched = [0]*n  # -- if user i is matched with any driver matched[i]=1
        drivers = []  # -- list containing driver indeces
        drivers_count = 0
        for i in range(0, n):
            if max_pays[i] == INVALID:
                drivers.append(i)
                cars.append([])
                matched[i] = 1
                drivers_count += 1
            elif min_fares[i] == INVALID:
                matched[i] = 0
            else:
                matched[i] = choice([0, 1])
                if matched[i] == 1:
                    drivers.append(i)
                    cars.append([])
                    drivers_count += 1
            if drivers_count >= math.ceil(n/4)+1:
                break
    # -------------------------------------------------------
    for k in range(0, drivers_count):  # -- loop over drivers to fill their cars
        i = drivers[k]                  # the driver index
        cars[k].append(i)               # add the driver to the car
        capacity_so_far = 0
        for j in range(0, n):
            if(capacity_so_far < capacities[i] and matched[j] == 0 and GetDist(locations[i], locations[j]) <= dl and max_pays[j] >= min_fares[i]):
                cars[k].append(j)
                matched[j] = 1
                capacity_so_far += 1

    cars_final = []
    for i in range(0, drivers_count):  # -- to satisfy the min capacity constraint
        if(len(cars[i])-1 >= min_capacities[cars[i][0]]):
            cars_final.append(cars[i])

    # -- solution is the total number of travellers wich is the sum of the each car length
    z = sum(len(x) for x in cars)
    run_time = time.time() - start_time

    return {str_z: z, str_cars: cars_final, "time": run_time}


def GetDist(loc_A, loc_B):
    return math.sqrt(math.pow(loc_A[0]-loc_B[0], 2) + math.pow(loc_A[1]-loc_B[1], 2))

# --------------------------------------------------------------------------------------------------------------
# ------------------------------------------- Main -----------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------


def main_testfile(test_set):
    testFiles = iter(ReadTestSet(test_set))
    testFile = next(testFiles, None)
    summary = []
    while testFile != None:
        # get current test file path
        testFile_parent = testFile.split("/")[0]+'_output'
        testFile_name = testFile.split("/")[-1]
        testFile_name = testFile_name.replace("in", "out")

        testCase = ReadTextFile(testFile)

        # ---------------------------------------------------------------------------
        # ------------------------------ MIP --------------------------------------
        # ---------------------------------------------------------------------------
        sol_Greedy = SolverGreedy(testCase)
        print(sol_Greedy)

        # ---------------------------------------------------------------------------
        # ----------------------------- summary -------------------------------------
        # ---------------------------------------------------------------------------

        testFile = next(testFiles, None)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(sys.argv[1])
        main_testfile(sys.argv[1])
