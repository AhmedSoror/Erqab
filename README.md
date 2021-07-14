# Erqab
## Optimizing ride-hailing

As summer is approaching, people are likely to travel between Cairo and Sahel a lot. Driving drains a lot of energy specially on hot days.  

The target is to create an application to connect people together where travelers are:
- willing to pay up till certain amount of money
- willing to take at least a certain amount of money in case they will be the ones to drive.

The most challenging part about this business is to match people together.
---
## Solvers Techniques
1. Greedy Algorithm:
>- Each user is either a driver(if he/she speciﬁed) or a passenger (otherwise).
>- If the number of drivers is small, convert some passengers to drivers.
>- For every driver, try to ﬁll his/her capacity with passengers satisfying the constraints.
2. Mixed-Integer Programming (MIP)
> - SCIP (Solving Constraint Integer Programs) is used to solve the problem. First, variables are defined for the solver as well as the objective function. Furthermore, constraints are defined and the solver runs to find the optimal solution.

3. Dynamic Programming
> - Brute force to find the solution while making use of repeated states.
4. Metaheuristic
> - Genatic Algorithm.
> - Population size = 80.
> - Number of generations = 100.
> - Each gene represents a driver number.
> - Each chromosone is a 1D array where index represents a travaller and value represents a gene.
> - Initial population each chromosone is heuristic solution.
> - fitness function is number of matchings.
> - parent selection through roulette wheel where weights are assigned using fitness function.
> - crossover function is splitting parent chromosones based on random index.
> - Mutation function is swapping passengers between two drivers.
> - Mutation Probability = 0.7
> - Best 2 solution are propagated into next generation in addition to new sibilings.

---
## Run on localhost:
`streamlit run Erqab.py`

---
## Deployed Link:
https://share.streamlit.io/ahmedsoror/erqab/main/Erqab.py
