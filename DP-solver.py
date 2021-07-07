from os import listdir
from os.path import isfile, join
import os
import numpy as np
import sys
import math
import re
import time
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

def dp_hash(matched,pos):
    res=""
    for i in range(len(matched)):
        res+= "x" if matched[i]==-1 or matched[i]==i else str(matched[i])
        
    return res

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
    print(sol,macthings)
    end_time=(time.time()-start_time)*1000
                
def SolverDPRec(n,max_distance,max_pay,min_passenger_fare,min_passengers,capacity,dist,matched,counts,memo,pos):
    
    
    if str(matched[:pos-1]) in memo:
        return memo[str(matched[:pos-1])]
        
    if pos==n:
        return 0,matched
        
    
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
        # ------------------------------ DP --------------------------------------
        # ---------------------------------------------------------------------------
        sol_DP=SolverDP(testCase)
        
        # print(sol_DP)
        
        # ---------------------------------------------------------------------------
        # ----------------------------- summary -------------------------------------
        # ---------------------------------------------------------------------------
        
        testFile=next(testFiles, None)

if __name__=="__main__": 
    if len(sys.argv)>1:
        print(sys.argv[1])
        main_testfile(sys.argv[1])
    
    
    
    
