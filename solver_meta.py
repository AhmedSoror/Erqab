import os
import sys
import glob
import math
import time
import numpy as np
from random import choices,randint,uniform



POPULATIION_SIZE=50
NUMBER_OF_GENERATIONS=100

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




def GetDist(loc_A, loc_B):
    return math.sqrt( math.pow(loc_A[0]-loc_B[0],2) + math.pow(loc_A[1]-loc_B[1],2))

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

def mutation_function(matched,n):
    r=uniform(0, 1)
    if r>0.5:
        return
    indices=np.where(matched==1)
    if(len(indices[0])==0):
        index_1,index_2=np.random.randint(n-1,size=2)
        matched[index_1][index_2]=1
        return
        
    if(len(indices[0])==1):
        matched[indices[0][0]][indices[1][0]]= abs(matched[indices[0][0]][indices[1][0]]-1)
        return
        
    index_1,index_2=np.random.randint(len(indices[0]),size=2)
    x1,y1=indices[0][index_1],indices[1][index_1]
    x2,y2=indices[0][index_2],indices[1][index_2]
    matched[x2][y1]=1
    matched[x1][y2]=1
    matched[x1][y1]=0
    matched[x2][y2]=0

def crossover_function(parent_1,parent_2,n):
    index=randint(1, n-1)
    sibiling_1=np.append(parent_1[:index],parent_2[index:],axis=0)
    sibiling_2=np.append(parent_1[index:],parent_2[:index],axis=0)
    return sibiling_1,sibiling_2
       
def parent_selection(n,max_distance, max_pay, min_passenger_fare, min_passengers, capacity, dist,population):
    weights = [fitness_function(n, max_distance, matched, max_pay, min_passenger_fare, min_passengers, capacity, dist) for matched in population]
    selected = choices(population=population,weights=weights,k=2)
    return selected[0],selected[1]

def generate_population(n):
    return [generate_solution(n) for _ in range(POPULATIION_SIZE)]
    
def generate_solution(n):
    return np.random.randint(2, size=(n, n))
    
def fitness_function(n,max_distance,matched,max_pay,min_passenger_fare,min_passengers,capacity,dist):
    
    driver_sums=matched.sum(1)
    passanger_sums=matched.sum(0)
    
    total_drivers=0
    
    for i in range(n):
        if(driver_sums[i]>=1):
            total_drivers+=1
        for j in range(n):
            if matched[i][j]==0:
                continue
            if i==j:
                return 1
            if max_pay[j]<min_passenger_fare[i]:
                return 1
            if dist[i][j]>max_distance:
                return 1
            if driver_sums[i]>capacity[i] or driver_sums[i]<min_passengers[i] or passanger_sums[i]>0:
                return 1
            if passanger_sums[j]>1 or driver_sums[j]>0:
                return 1
    return matched.sum()+1+total_drivers

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
    
    
    population=generate_population(n)
    best_solution=generate_solution(n)
    best_solution_value=fitness_function(n, max_distance, best_solution, max_pay, min_passenger_fare, min_passengers, capacity, dist)
    best_solution_iteration=0
    
    for i in range(1,NUMBER_OF_GENERATIONS+1):
        
        population=sorted(population,key=lambda matched:fitness_function(n, max_distance, matched, max_pay, min_passenger_fare, min_passengers, capacity, dist),reverse=True)
        
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
            mutation_function(sibiling_1,n)
            mutation_function(sibiling_2,n)
            next_generation+=[sibiling_1,sibiling_2]
            
        population=next_generation
        
    run_time = time.time() - start_time
   
    return best_solution,best_solution_value-1,best_solution_iteration
    
def solve(dir_name):
    for file_name in sorted(glob.glob(dir_name+"/*"),key=len):
        data=ReadTextFile(file_name)
        print(genatic_algorithm(data))
        
        
        
    
        
       


if __name__ == "__main__":
    if not os.path.exists(sys.argv[1]+"_output"):
        os.mkdir("./"+sys.argv[1]+"_output/")  
    solve(sys.argv[1])
    
    
    