from os import listdir
from os.path import isfile, join
import os
import numpy as np
import sys
import math
import re
import time
from collections import Counter
from random import choices,randint,uniform
from random import choice


INVALID = 0

str_cars = "cars"
str_z = "z"

POPULATIION_SIZE=80
NUMBER_OF_GENERATIONS=100
MUTATION_PROBABILITY=0.7


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

def Greedy_To_Meta(data):
    greedy_sol=SolverGreedy(data)[str_cars]
    matched=[-1]*data[str_n]
    for pool in greedy_sol:
        driver=pool[0]
        for passenger in pool:
            matched[passenger]=driver
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
    return {str_z: best_solution_value-1, str_cars: cars_final, "time": run_time}


    
def GetDist(loc_A, loc_B):
    return math.sqrt(math.pow(loc_A[0]-loc_B[0], 2) + math.pow(loc_A[1]-loc_B[1], 2))
    
def main_testfile(test_set):
    testFiles = iter(ReadTestSet(test_set))
    testFile=next(testFiles, None)
    summary=[]
    
    while testFile != None:
        print(testFile)
        # get current test file path
        testFile_parent = testFile.split("/")[0]+'_output'
        testFile_name = testFile.split("/")[-1]
        testFile_name = testFile_name.replace("in", "out")
        
        testCase = ReadTextFile(testFile)
        
        # ---------------------------------------------------------------------------
        # ----------    -------------------- MIP --------------------------------------
        # ---------------------------------------------------------------------------
        # sol_MIP = SolverMIP(testCase)
        # print(sol_MIP)
        
        # ---------------------------------------------------------------------------
        # ------------------------------ Greedy --------------------------------------
        # ---------------------------------------------------------------------------
        # sol_Greedy = SolverGreedy(testCase)
        # print(sol_Greedy)
        
        
        # ---------------------------------------------------------------------------
        # ------------------------------ DP --------------------------------------
        # ---------------------------------------------------------------------------
        # sol_DP=SolverDP(testCase)
        # print(sol_DP)
        
        # ---------------------------------------------------------------------------
        # ------------------------------ Meta-Heuristic --------------------------------------
        # ---------------------------------------------------------------------------
        sol_Meta=genatic_algorithm(testCase)
        print(sol_Meta)
        
        
        # ---------------------------------------------------------------------------
        # ----------------------------- summary -------------------------------------
        # ---------------------------------------------------------------------------
        
        testFile=next(testFiles, None)

if __name__=="__main__": 
    if len(sys.argv)>1:
        print(sys.argv[1])
        main_testfile(sys.argv[1])
   

    
    
    
    