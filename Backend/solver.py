from numpy.lib.function_base import average
from ortools.linear_solver import pywraplp
from random import choices,randint,uniform
from ortools.sat.python import cp_model
from contextlib import contextmanager
from os.path import isfile, join
from collections import Counter
from random import choice
from numpy import dtype
from os import listdir
import pandas as pd
import numpy as np
import itertools
import signal
import time
import math
import sys
import csv
import os
import re


sys.setrecursionlimit(500000)

# --------------------------------------------------------------------------------------------------------------
# -------------------------------------------  Globals  --------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------
INVALID = 0
POPULATIION_SIZE=80
NUMBER_OF_GENERATIONS=100
MUTATION_PROBABILITY=0.7
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
        maxs=[]
        min_fare=[]
        min_pass=[]
        capacities=[]
        locations = []

        for i in range(data[str_n]):
            user=ReadLine(f)
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
    solo_drivers=0
    for arr in x:
        c = 0
        car=[]
        for i in arr:
            c+=1
            if i==1:
                car.append(c)
        if(len(car)>1):
            cars.append(car)
        else:
            solo_drivers +=1
    return cars, solo_drivers
    
def ReadDF(df):
    # df = pd.read_csv(dataPath, header=None, sep='\n')
    # df = df[0].str.split(',', expand=True)
    out=[]
    df = df.to_numpy()

    i=0
    while i<len(df):
        dic={}
        n=int(df[i][0])
        dl=int(df[i][1])
        init=i+1
        i=i+n+1
        dic[("n")] = n
        dic[("dl")] = dl
        needed=df[init:i]
        dic[("pay")]=needed[:,0].astype(np.int64)
        # print(pay)
        dic[("fare")]=needed[:,1].astype(np.int64)
        dic[("minc")]=needed[:,2].astype(np.int64)
        dic[("c")]=needed[:,3].astype(np.int64)
        dic[("loc")]=needed[:,4:6].astype(np.int64)
        out.append(dic)
    return out  


# --------------------------------------------------------------------------------------------------------------
# ------------------------------------------- Helpers -----------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------
def GetDist(loc_A, loc_B):
    return math.sqrt( math.pow(loc_A[0]-loc_B[0],2) + math.pow(loc_A[1]-loc_B[1],2))
   
def increment(x):
    return x+1

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
    travellers = round(solver.Objective().Value())
    for i in range (len(Xs)):
        Xs_values.append([])
        Ds_values.append(Ds[i].solution_value())
        Ps_values.append(Ps[i].solution_value())
        for j in range (len(Xs[i])):
            Xs_values[i].append((int)(Xs[i][j].solution_value()))
        
    cars_arr, solo_drivers = MatchesToCars(Xs_values)
    travellers -= solo_drivers
    return {str_z:travellers, str_cars: cars_arr, "Xs": Xs_values,"time":run_time}
 
#Greedy solution
def SolverGreedy(data):
    result = SolverGreedy1(data)
    cars_last=result[str_cars]
    i=0
    while(len(cars_last)==0 and i<10):
        i+=1
        result = SolverGreedy1(data)
        cars_last=result[str_cars]
    return  result

def SolverGreedy1(data):
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
        if(len(cars[i])-1 >= min_capacities[cars[i][0]] and len(cars[i])-1 > 1):
            # 1-indexed output
            # cars_final.append(cars[i])
            cars_final.append(list(map(increment, cars[i])))

    # -- solution is the total number of travellers wich is the sum of the each car length
    z = sum(len(x) for x in cars_final)
    run_time = time.time() - start_time
    # print(z)
    # print(cars_final)
    # print("#########")
    return {str_z: z, str_cars: cars_final, "time": run_time}
 
#DP solution
def DP_To_Cars(matched):
    
    dictionary={}
    
    for i in range(len(matched)):
        if matched[i]==-1 or i == matched[i]:
            continue
        if matched[i] in dictionary:
            dictionary[matched[i]].append(i)
        else:
            dictionary[matched[i]]=[i]
            
    return [[key] + val for key, val in dictionary.items()]

def SolverDP(data):
    start_time=time.time()
    n=data[str_n]
    max_distance=data[str_dis]
    max_pay=data[str_pay]
    min_passenger_fare=data[str_fare]
    min_passengers=data[str_min_cap]
    capacity=data[str_cap]
    locations=data[str_location]
    dist=np.linalg.norm(np.array(locations)[:, None] - np.array(locations)[None, :], axis=-1)

    sol,macthings=SolverDPRec(n, max_distance, max_pay, min_passenger_fare, min_passengers, capacity, dist,[-1]*n,[0]*n,{},0)
    
    end_time=(time.time()-start_time)*1000
    
    cars_final=DP_To_Cars(macthings)
    
    # 1-indexed output
    cars_final= [list(map(increment, cars)) for cars in cars_final]
    
    return {str_z: sol, str_cars: cars_final, "time": end_time}
              
def SolverDPRec(n,max_distance,max_pay,min_passenger_fare,min_passengers,capacity,dist,matched,counts,memo,pos):
    
    
    if str(matched[:pos-1]) in memo:
        return memo[str(matched[:pos-1])]
        
    if pos==n:
        for i in range(len(counts)):
            if counts[i]>0 and counts[i]<min_passengers[i]:
                return -n*2,[]
        return 0,matched
        
    if matched[pos] != -1:
        return SolverDPRec(n, max_distance, max_pay, min_passenger_fare, min_passengers, capacity, dist, matched, counts, memo, pos+1)
    
    best_sol,best_sol_matched=0,matched
    
    

    for j in range(n):
        if pos==j:continue
        if matched[j] !=-1 and matched[j] !=j : continue
        if max_pay[pos]>=min_passenger_fare[j] and counts[j]<capacity[j] and dist[pos][j]<=max_distance:
            new_matched=matched.copy()
            new_counts=counts.copy()
            new_matched[j]=j
            new_matched[pos]=j
            new_counts[j]=new_counts[j]+1
            can_sol,can_sol_matched=SolverDPRec(n, max_distance, max_pay, min_passenger_fare, min_passengers, capacity, dist, new_matched, new_counts,memo,pos+1)
            can_sol+=1 if matched[j]==j else 2
            if can_sol >best_sol:
                best_sol=can_sol
                best_sol_matched=can_sol_matched
    can_sol,can_sol_matched=SolverDPRec(n,max_distance,max_pay,min_passenger_fare,min_passengers,capacity,dist,matched,counts,memo,pos+1)     
    if can_sol >best_sol:
        best_sol=can_sol
        best_sol_matched=can_sol_matched
                        
    memo[str(matched[:pos-1])]=best_sol,best_sol_matched
                   
    return best_sol,best_sol_matched           

#Meta solution
def Greedy_To_Meta(data):
    greedy_sol=SolverGreedy(data)[str_cars]
    matched=[-1]*data[str_n]
    for pool in greedy_sol:
        driver=pool[0]-1
        for passenger in pool:
            matched[passenger-1]=driver
    return matched

def Meta_To_Cars(matched):
    
    dictionary={}
    
    for i in range(len(matched)):
        if matched[i]==-1 or i == matched[i]:
            continue
        if matched[i] in dictionary:
            dictionary[matched[i]].append(i)
        else:
            dictionary[matched[i]]=[i]
            
    return [[key] + val for key, val in dictionary.items()]

def mutation_function(matched,n,max_pay,min_passenger_fare):
    r=uniform(0, 1)
    if r>MUTATION_PROBABILITY:
        return
    
    passengers=np.where(matched!=-1)[0]
    passengers=passengers[matched[passengers]!=passengers]   ## remove drivers 
    
    for i in range(len(passengers)):
        driver_1= matched[passengers[i]]
        passanger_1=passengers[i]
        for j in range(i+1,len(passengers)):
            driver_2= matched[passengers[j]]
            passanger_2=passengers[j]
            
            if max_pay[passanger_1] >= min_passenger_fare[driver_2] and max_pay[passanger_2] >=min_passenger_fare[driver_1]:
                matched[passanger_1]=driver_2
                matched[passanger_2]=driver_1
                return

def crossover_function(parent_1,parent_2,n):
    index=randint(1, n-1)
    sibiling_1=np.append(parent_1[:index],parent_2[index:],axis=0)
    sibiling_2=np.append(parent_2[:index],parent_1[index:],axis=0)
    
    return sibiling_1,sibiling_2
       
def parent_selection(n,max_distance, max_pay, min_passenger_fare, min_passengers, capacity, dist,population):
    weights = [fitness_function(n, max_distance, matched, max_pay, min_passenger_fare, min_passengers, capacity, dist) for matched in population]
    selected = choices(population=population,weights=weights,k=2)
    return selected[0],selected[1]

def generate_population(n):
    return [generate_solution(n) for _ in range(POPULATIION_SIZE)]
    
def generate_solution(n):
    
    x=np.random.randint(low=-1 ,high=n, size=n)
    z=np.zeros((n,n))
    for i in range(n):
        if x[i]!=-1:
            z[x[i]][i]=1
    return z
    
def fitness_function(n,max_distance,matched,max_pay,min_passenger_fare,min_passengers,capacity,dist):
    
    res=1
    
    driver_dict={}
    
    for i in range(n):
        passanger=i
        driver=matched[passanger]
        
        if driver==-1: ## passenger not yet matched
            continue
        
        if matched[driver] != driver: ## driver matched with someone else
            return 1
        
        
        res+=1
        if driver not in driver_dict:
            driver_dict[driver]=[]
        driver_dict[driver].append(passanger)
        
        if driver==passanger:
            continue
        
        if max_pay[passanger] < min_passenger_fare[driver]: ## passenger doesnt have driver fare
            return 1
        
        if dist[passanger][driver]> max_distance: ##distance between passenger and driver is more than max distance
            return 1
        
       
    
    for driver in driver_dict:
        num_passangers=len(driver_dict[driver])-1
        
        if num_passangers==0:
            res-=1
        
        if num_passangers >capacity[driver]:
            return 1
        if num_passangers < min_passengers[driver]:
            return 1
    return res
        
def genatic_algorithm(data):
    start_time = time.time()
    n=data[str_n]
    max_distance=data[str_dis]
    max_pay=data[str_pay]
    min_passenger_fare=data[str_fare]
    min_passengers=data[str_min_cap]
    capacity=data[str_cap]
    locations=data[str_location]
    dist=np.linalg.norm(np.array(locations)[:, None] - np.array(locations)[None, :], axis=-1)
    
    greedy_solution=Greedy_To_Meta(data)
    
    
    population= [Greedy_To_Meta(data) for _ in range(POPULATIION_SIZE)]
    best_solution=population[0]
    best_solution_value=fitness_function(n, max_distance, best_solution, max_pay, min_passenger_fare, min_passengers, capacity, dist)
    best_solution_iteration=0
    
    
    
    for i in range(1,NUMBER_OF_GENERATIONS+1):
        
        population_best=population[0]
        population_best_value=fitness_function(n, max_distance, population_best, max_pay, min_passenger_fare, min_passengers, capacity, dist)
        
        if population_best_value>best_solution_value:
            best_solution=population_best
            best_solution_value=population_best_value
            best_solution_iteration=i
        
        
        next_generation=population[:2]
        
        for _ in range (int(POPULATIION_SIZE/2) -1):
            parent_1,parent_2=parent_selection(n, max_distance, max_pay, min_passenger_fare, min_passengers, capacity, dist, population)
            sibiling_1,sibiling_2=crossover_function(parent_1, parent_2, n)
            mutation_function(sibiling_1,n,max_pay,min_passenger_fare)
            mutation_function(sibiling_2,n,max_pay,min_passenger_fare)
            next_generation+=[sibiling_1,sibiling_2]
           
            
        next_generation=sorted(next_generation,key=lambda matched:fitness_function(n, max_distance, matched, max_pay, min_passenger_fare, min_passengers, capacity, dist),reverse=True)
        population=next_generation
        
    run_time = time.time() - start_time
    cars_final=Meta_To_Cars(best_solution)
    # 1-indexed output
    cars_final= [list(map(increment, cars)) for cars in cars_final]
    return {str_z: best_solution_value-1, str_cars: cars_final, "time": run_time}
     
def SolverMeta(data):
    return genatic_algorithm(data)
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
        # ---------------------------------- MIP ------------------------------------
        # ---------------------------------------------------------------------------
        sol_MIP = SolverMIP(testCase)
        # print(sol_MIP)
        
        
        # ---------------------------------------------------------------------------
        # ------------------------------ Greedy -------------------------------------
        # ---------------------------------------------------------------------------
        sol_Greedy = SolverGreedy(testCase)
        # print(sol_Greedy)
        
        
        # ------------------------------------------------------------------------
        # ------------------------------ DP --------------------------------------
        # ------------------------------------------------------------------------
        sol_DP=SolverDP(testCase)
        # print(sol_DP)

        
        # ---------------------------------------------------------------------------
        # ------------------------------ Meta-Heuristic -----------------------------
        # ---------------------------------------------------------------------------
        sol_Meta=genatic_algorithm(testCase)
        # print(sol_Meta)
        
        
        # ---------------------------------------------------------------------------
        # ----------------------------- summary -------------------------------------
        # ---------------------------------------------------------------------------
        
        
        
        
        testFile=next(testFiles, None)

if __name__=="__main__":
    if len(sys.argv)>1:
        # print(sys.argv[1])
        main_testfile(sys.argv[1])
    