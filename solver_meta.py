import os
import sys
import glob
import numpy as np
from random import choices,randint,uniform


POPULATIION_SIZE=50
NUMBER_OF_GENERATIONS=100

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
    
    for i in range(n):
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
    return matched.sum()+1


def genatic_algorithm(n, max_distance, max_pay, min_passenger_fare, min_passengers, capacity, dist):
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
    
    return best_solution,best_solution_value,best_solution_iteration
    


def solve(dir_name):
    for file_name in sorted(glob.glob(dir_name+"/*"),key=len):
        test_name=file_name.split(dir_name+"\\")[1]
        f=open(file_name)
        temp=f.read().splitlines()
        
        ## Number of user,Max distance between driver & passenger
        n,max_distance=map(int,(temp[0].split(" ")))  
        
        ## The maximum a user will pay if he travels with someone else
        max_pay=np.fromiter(map(lambda x:int(x.split(" ")[0]),temp[1:n+1]),dtype=int) 
        
        ## The minimum a driver will get per passenger
        min_passenger_fare=np.fromiter(map(lambda x:int(x.split(" ")[1]),temp[1:n+1]),dtype=int) 
        
        ## The minimum number of passengers required by the user if he is a driver
        min_passengers=np.fromiter(map(lambda x:int(x.split(" ")[2]),temp[1:n+1]),dtype=int) 
        
        ## The capacity of the user if he a driver
        capacity=np.fromiter(map(lambda x:int(x.split(" ")[3]),temp[1:n+1]),dtype=int) 
        
        ## the x,y cordinatses of each user
        locations=np.array(list(map(lambda x : (x.split(" ")[4],x.split(" ")[5]),temp[1:n+1])),dtype=int) 
        
        ## The distance matrix between all users
        dist=np.linalg.norm(locations[:, None] - locations[None, :], axis=-1) 
        
        print(genatic_algorithm(n, max_distance, max_pay, min_passenger_fare, min_passengers, capacity, dist))
        
        
        
       


if __name__ == "__main__":
    if not os.path.exists(sys.argv[1]+"_output"):
        os.mkdir("./"+sys.argv[1]+"_output/")  
    solve(sys.argv[1])
    
    