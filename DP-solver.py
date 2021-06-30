from os import listdir
from os.path import isfile, join
import os
import numpy as np
import sys
import math
import re
from collections import Counter



sys.setrecursionlimit(500000)

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

def SolverDP(data):
    n=data[str_n]
    max_distance=data[str_dis]
    max_pay=data[str_pay]
    min_passenger_fare=data[str_fare]
    min_passengers=data[str_min_cap]
    capacity=data[str_cap]
    locations=data[str_location]
    dist=np.linalg.norm(np.array(locations)[:, None] - np.array(locations)[None, :], axis=-1)
    return(SolverDP2(n, max_distance, max_pay, min_passenger_fare, min_passengers, capacity, dist,[-1]*n,[0]*n,{}))
    
def SolverDP2(n,max_distance,max_pay,min_passenger_fare,min_passengers,capacity,dist,matched,counts,memo):
    
    
    
    if (str(matched) in memo):
        return memo[str(matched)]
    
    best_sol_1=0
    best_sol_1_matched=matched
    
    
    for i in range(n):
        if matched[i]==-1:
            best_sol_2=0
            best_sol_2_matched=[]
            for j in range(n):
                if i==j:continue
                if matched[j] !=-1 and matched[j] !=j : continue
                if max_pay[i]>=min_passenger_fare[j] and counts[j]<capacity[j] and dist[i][j]<=max_distance:
                    new_matched=matched.copy()
                    new_counts=counts.copy()
                    new_matched[j]=j
                    new_matched[i]=j
                    new_counts[j]=new_counts[j]+1
                    can_sol,can_sol_matched=SolverDP2(n, max_distance, max_pay, min_passenger_fare, min_passengers, capacity, dist, new_matched, new_counts,memo)
                    can_sol+=1 if matched[j]==j else 2
                    if can_sol >best_sol_2:
                        best_sol_2=can_sol
                        best_sol_2_matched=can_sol_matched
                        
            if best_sol_2>best_sol_1:
                best_sol_1=best_sol_2
                best_sol_1_matched=best_sol_2_matched
            
    memo[str(matched)]=best_sol_1,best_sol_1_matched     
                   
    return best_sol_1,best_sol_1_matched          
                
                
    

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
        # sol_MIP = SolverMIP(testCase)
        # print(sol_MIP)
        
        # ---------------------------------------------------------------------------
        # ------------------------------ MIP --------------------------------------
        # ---------------------------------------------------------------------------
        sol_DP=SolverDP(testCase)
        print(sol_DP)
        
        # ---------------------------------------------------------------------------
        # ----------------------------- summary -------------------------------------
        # ---------------------------------------------------------------------------
        
        testFile=next(testFiles, None)

if __name__=="__main__": 
    if len(sys.argv)>1:
        print(sys.argv[1])
        main_testfile(sys.argv[1])