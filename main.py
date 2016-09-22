#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Universidade Federal de Minas Gerais
Departamento de Ciência da Computação
Programa de Pós-Graduação em Ciência da Computação

Redes sem Fio
Trabalho Prático 1

Feito por Gabriel de Biasi, 2016672212.
"""

import sys, math, random, copy
from timeit import default_timer as timer

#------------------------------------------------------------------#
#---------------------------- CONSTANTS ---------------------------#
#------------------------------------------------------------------#
RANGE_DBM = (-30, 10)     # Power range in dBm
ALPHA = 3.0               # Path-loss constant
BETA = 3.0                # Minimum signal-to-interference ratio
NOISE = 10.e-9 # 10nW     # Ambient noise

SEED = timer()            # timer() -> random | int -> determinist
GENERATIONS = 1000        # Maximum number of generations

POPULATION_SIZE = 1000    # Size of population
TOURNAMENT_SIZE = 2       # Size of tournament selection
MUTATION_RATE = 0.5       # Rate of mutation on power values in dBm

P_CROSSOVER = 0.5         # Probability of crossover
P_MUTATION = 0.5          # Probability of mutation
#------------------------------------------------------------------#


def dbm_to_watt(value):
    '''
    dBm to Watt converter
    '''
    return float((10 ** (value/10.0))/1000.0)


def distance(n1, n2):
    '''
    Euclidean distance
    '''
    return ((n2[0]-n1[0])**2 + (n2[1]-n1[1])**2)**(0.5)


def get_position():
    '''
    Valid position generator
    '''
    return [random.randint(-GRID, GRID),random.randint(-GRID, GRID)]


def get_power():
    '''
    Valid power value generator
    '''
    return random.randint(RANGE_DBM[0], RANGE_DBM[1])

def exit_to_file(ind):
    '''
    Put all information about positions and power
    values on the file 'graph.txt'.
    '''
    file = open('graph.txt', 'w')
    file.write('-999 %d\n' % (GRID))
    for i in range(AMOUNT):
        file.write('%d,%d\t%d,%d\t%d\n' % (ind.positions[i][0][0], ind.positions[i][0][1], ind.positions[i][1][0], ind.positions[i][1][1], ind.powers[i]))
    file.close()
    exit()

class Individual(object):
    '''
    Represents an individual in the evolution process.
    Stores the position of the sender and receiver nodes
    and their power values.
    '''
    __slots__ = ('positions', 'powers', 'fitness') # Python optimization for multiple instances

    def __init__(self, positions=[], powers=[]):
        self.positions = positions
        self.powers = powers
        self.fitness = -1


    def __repr__(self):
        return self.__str__()


    def __str__(self):
        return 'Senders & Receivers: {}\nPower in dBm: {}, Alpha: {}, Beta: {}, Noise: {}, Fitness: {}'.format(self.positions, self.powers, ALPHA, BETA, NOISE, self.get_fitness())


    def get_sinr(self, i):
        '''
        The Signal-to-interference-plus-noise ratio formula
        *-*-* Whenever the nodes are in the same place,
        the formula tends to zero *-*-*
        '''
        try:
            v1 = float(dbm_to_watt(self.powers[i])/(distance(self.positions[i][0], self.positions[i][1])**ALPHA))
        except: # Division by zero
            v1 = 0.0

        v2 = 0.0
        for j in range(AMOUNT):
            if i != j:
                try:
                    v2 += float(dbm_to_watt(self.powers[j])/(distance(self.positions[j][0], self.positions[i][1])**ALPHA))
                except: # Division by zero
                    v2 = 99999

        return float (v1 / (NOISE + v2))


    def get_fitness(self):
        '''
        Fitness Calculation
        Whenever a connection between two nodes do not
        reach the BETA value, the difference is appended
        to the fitness value.
        '''
        if self.fitness == -1:
            diff = 0.0
            for i in range(AMOUNT):
                v = self.get_sinr(i)
                if v < BETA:
                    diff += BETA - v

            self.fitness = diff

        return self.fitness


def tournament(population):
    '''
    Tournament Selection
    Gets (k) individuals at random from the
    population, choose the best one.
    '''
    candidates = random.sample(population, TOURNAMENT_SIZE)
    candidates.sort(key=lambda x: x.get_fitness())
    return candidates[0]


def crossover(ind1, ind2):
    '''
    Crossover Operation
    Creates a copy of the parents, then choose one set of sender-receiver and your power value
    from the first individual and swap with another one.
    '''
    child1 = copy.deepcopy(ind1)
    child2 = copy.deepcopy(ind2)

    child1.fitness = -1
    child2.fitness = -1

    pos = random.randint(0, AMOUNT-1)
    child1.positions[pos], child2.positions[pos] = child2.positions[pos], child1.positions[pos]
    child1.powers[pos], child2.powers[pos] = child2.powers[pos], child1.powers[pos]
    return child1, child2


def mutation(ind):
    '''
    Mutation Operation
    Choose one set of sender-receiver from the individual,
    then choose between the sender and receiver and mutates
    your position.
    For each power value, 50% chance to increase ou decrease
    your value.
    '''
    new = copy.deepcopy(ind)
    new.fitness = -1

    # Mutates the position of nodes
    for pos in new.positions:
        x = 0 if random.random() < 0.5 else 1
        y = 0 if random.random() < 0.5 else 1
        z = 1 if random.random() < 0.5 else -1

        if pos[x][y] + z > GRID or pos[x][y] + z < -GRID:
            pos[x][y] -= z
        else:
            pos[x][y] += z

    # Mutates the power values
    for i in range(AMOUNT):
        if random.random() < 0.5:
            z = MUTATION_RATE if random.random() < 0.5 else -MUTATION_RATE
            new.powers[i] += z

    return new

def evolution():
    '''
    Evolution Process
    '''
    random.seed(SEED)
    population = list()

    # Creating the population
    for i in range(POPULATION_SIZE):
        powers = list()
        positions = list()

        for j in range(AMOUNT):
            powers.append(get_power())
            positions.append([get_position(), get_position()])

        ind = Individual(positions, powers)
        population.append(ind)

    # Begining of generations
    try:
        g = 1
        while g <= GENERATIONS:

            # Calculating all the fitness values and the average
            m = 0.0
            for ind in population:
                m += ind.get_fitness()
            population.sort(key=lambda x: x.get_fitness())

            # Prints some informations about the last generation
            average = m / float(POPULATION_SIZE)
            sys.stdout.write('\rG: %d\tBest: %.1f\tAvg: %.1f' % (g, population[0].get_fitness(), average))
            sys.stdout.flush()

            # Break condition
            if population[0].get_fitness() == 0.0:
                print '\nFOUND!'
                exit_to_file(population[0])

            new_population = list()
            new_population.append(population[0]) # Elitism
            size = 1

            # Creating the new population
            while size < POPULATION_SIZE:

                # Chance for crossover
                if random.random() < P_CROSSOVER:
                    ind1 = tournament(population) # Tournament selection
                    ind2 = tournament(population)
                    c1, c2 = crossover(ind1, ind2)
                    new_population.append(c1)
                    new_population.append(c2)
                    size += 2

                # Chance for mutation
                if random.random() < P_MUTATION:
                    ind = tournament(population)
                    new_population.append(mutation(ind))
                    size += 1

            # End of generation
            population = new_population
            g += 1

    except KeyboardInterrupt:
        # If hit Control-C to stop the process
        print '\nSTOPPED'
        exit_to_file(population[0])

    if g > GENERATIONS:
        # If number of generations run out without achieving the result
        print '\nTOTAL GENERATIONS REACHED'    
        exit_to_file(population[0])


if __name__ == '__main__':

    GRID = int(sys.argv[1]) # Grid size
    AMOUNT = int(sys.argv[2]) # Amount of senders-receivers

    # Start!
    evolution()
# End :)
