#szükséges Python könyvtárak betöltése
from math import sqrt
from random import shuffle, randint
import numpy as np
from datetime import datetime

# Sudoku táblák
inputFile= 'sudoku1.txt'
#inputFile= 'sudoku2.txt'
#inputFile= 'sudoku3.txt'
#inputFile= 'sudoku4.txt'
#inputFile= 'sudoku5.txt'

#Genetikus algoritmus működéséhez szükséges változók beállítása 
POPULATION_SIZE=2000
SELECTION_RATE=0.5
MAX_GENERATIONS=500
MUTATION_RATE=0.1

# A sudoku tábla kiíratása, 0 vagy üres értékek helyén _ karakterrel a jobb olvashatóság és feladat átláthatóság érdekében
def printSudoku(sudoku, size):
    blockSize = int(sqrt(size))
    reshaped = []
    for r in range(size):
        for c in range(size):
            print(
                ( "_" if sudoku[r][c] == 0 else sudoku[r][c]),
                end = "  " if (c+1) % blockSize == 0 else " "
            )
        print()
        if (r+1) % blockSize == 0:
            print(" ")

# A kzedtei populáció generálása a megadott változó alapján, ami esetemben a POPULATION_SIZE válotzó és értéke 2000
def generatePopulation(sudoku):
    candidates = []
    for n in range(POPULATION_SIZE):
        candidate = np.zeros(sudoku.shape,np.int8)
        reshaped = np.array([])
        for i in range(0, 9, 3):
            for j in range(0, 9, 3):
                subgrid = sudoku[i:i+3, j:j+3]
                numberList = list(range(1, sudoku.shape[0]+1))
                # Bemenet másolása, és az adott egységben lévő számok ellenőrzése
                for x in range(0, 3):
                    for y in range(0, 3):
                        if sudoku[x+i,y+j]!=0:
                            candidate[x+i,y+j] = sudoku[x+i,y+j]
                            numberList.remove(sudoku[x+i,y+j])

                shuffle(numberList)
                # Véletlenszerűen generált számok hozzáadása az üres helyekre
                for x in range(0, 3):
                    for y in range(0, 3):
                        if sudoku[x+i,y+j]==0:
                            candidate[x+i,y+j] = numberList.pop()
        candidates.append(candidate)
    return candidates

# A legjobb alkalamssági értékkel rendelkező egyedek kiválasztása SELECTION_RATE változó százalékos érétke alapján
def selection(candidates, rate):
    fitnessValues = []
    
    for i in range(len(candidates)):
        fitnessValues.append(tuple([i, fitness(candidates[i])]))
        
    fitnessValues.sort(key=lambda elem: elem[1])
    selected = fitnessValues[0: int(len(fitnessValues) * rate)]                      
    indexes = [e[0] for e in selected]
    return [candidates[i] for i in indexes], selected[0][1]

# Az alkalmassági értékek kiszámítása minden eggyes sorban oszlopban és a rácsban
def fitness(candidate):
    # A duplikátumok kiszámítása minden sorban 
    rowDuplicates=0
    for row in candidate:
        for n in range(len(candidate)):
            count=np.count_nonzero(row == n+1)
            if count>1:
                rowDuplicates+=count
    # Duplikátumok megállapítása minden oszlopban 
    colDuplicates=0
    for x in range(len(candidate)-1):
        for n in range(len(candidate)):
            count=np.count_nonzero(candidate[:,x] == n+1)
            if count>1:
                colDuplicates+=count
    # A duplikátumok megállapítása egy egységen belül          
    gridDuplicates=0            
    for i in range(0, 9, 3):
        for j in range(0, 9, 3):
            for n in range(len(candidate)):
                count=np.count_nonzero(candidate[i:i+3, j:j+3] == n+1)
                if count>1:
                    gridDuplicates+=count
                
    return rowDuplicates+colDuplicates+gridDuplicates

# Egypontos keresztezés végrehajtása
def crossing(sudoku1, sudoku2):
    size=sudoku1.shape[0]
    point = randint(0, size)
    
    array1=np.reshape(sudoku1, (1, size*size))
    array2=np.reshape(sudoku2, (1, size*size))
    
    newarray1=np.concatenate([array1[0, :point*size], array2[0, point*size:]])
    newarray2=np.concatenate([array2[0, :point*size], array1[0, point*size:]])
    return np.reshape(newarray1, (size, size)), np.reshape(newarray2, (size, size))

# Egyedek mutációja, 2 szám véletlenszerű felcserélésével egy egységen belül
def mutate(sudoku, candidate):
    zeros = 0
    i=0
    # Egység keresése sudoku táblában 2 ismeretlen/ még nem megadott értékkel
    while zeros < 2:
        if i > 100:
            return candidate
        blockPlace = randint(0, sudoku.shape[0]-1)
        x = int(blockPlace/3)*3
        y = blockPlace%3*3
        block = sudoku[x:x+3, y:y+3]
        zeros = block.size - np.count_nonzero(block)
        i+=1

    # A két szám kiválasztása
    while True:
        n1 = randint(0, sudoku.shape[0]-1)
        x1 = int(n1/3)
        y1 = n1%3 
        
        n2 = randint(0, sudoku.shape[0]-1)
        x2 = int(n2/3)
        y2 = n2%3
        if (sudoku[x+x2, y+y2]==0 and sudoku[x+x1, y+y1]==0):
            break
    
    # Mutáció végrehajtása
    temp=candidate[x+x1, y+y1]
    candidate[x+x1, y+y1] = candidate[x+x2, y+y2]
    candidate[x+x2, y+y2] = temp
    return candidate

# Genetikus algoritmus futtatása, a sudoku megoldására
def solve(sudoku):
    bestFitness = -1
    lastbestFitness = 300
    # Kezdeti pupuláció generálása, a generatePopulation függvény meghívásával
    population=generatePopulation(sudoku)
    
    # amíg, nincs megoldás, vagy amíg ne mértük el a MAX_GENERATIONS értékét, ami jelenleg 500
    for i in range(MAX_GENERATIONS):
        # Alkalmassági érték alapján értékelés és szelekció
        selected, bestFitness = selection(population, SELECTION_RATE)

        # futás közbeni visszajelzés a generációk számáról és az alkalmassági érétkről
        if lastbestFitness>bestFitness:
            print("Generáció: ", i, "Alkalmassági érték: ", bestFitness)
            lastbestFitness=bestFitness

        # Ciklus feltétel ellenőrzés és érték kiiratás
        if i == MAX_GENERATIONS - 1 or fitness(selected[0]) == 0:
            print("Generáció: ", i, "Alkalmassági érték: ", fitness(selected[0]))
            break

        # Keresztezés
        shuffle(selected)
        nextPopulation=selected.copy()
        selectionSize = int(round((len(selected)/2), 0)) 
        for j in range(selectionSize):
            if len(selected)==1:
                nextPopulation.append(selected.pop())
                break
            adult1=selected.pop()
            adult2=selected.pop()
            child1, child2 = crossing(adult1, adult2)
            nextPopulation.append(child1)
            nextPopulation.append(child2)

        # A mutációs értéknek megfelelő mutáció végrehajtása
        for candidate in nextPopulation[0:int(len(nextPopulation) * MUTATION_RATE)]:
            candidate=mutate(sudoku, candidate)
            
        # Ugrás a követkző generációra
        population=nextPopulation.copy()
    return selected[0], bestFitness


if __name__=='__main__':
    # Futási idő mérése:
    startTime = datetime.now()
    # Bemeneti fájl beolvasása
    f=open(inputFile, "r")
    fileContent = f.read()
    fileLines = fileContent.split('\n')
    size = len(fileLines)
    blockSize = int(sqrt(size))

    # A megadott bemenet konvertálása numpy tömbre
    sudoku=np.zeros((size, size),np.int8)
    for i in range(size):
        line = fileLines[i].split(' ')
        for j in range(size):
            if line[j]!='-':
                sudoku[i,j] = line[j]


    # A átalakított bemenet kiíratása
    print("-------------------------------")
    print("Bemenet:")
    printSudoku(sudoku, sudoku.shape[0])
    print("-------------------------------")

    # Sudoku megoldása
    solution, bestFitness = solve(sudoku)

    # Végső eredmények kiírása
    print("-------------------------------")
    print("Megoldás:")
    printSudoku(solution, sudoku.shape[0])
    print("Alkalmassági érték: ", bestFitness)
    print("Bemeneti fájl: ", inputFile)
    endTime = datetime.now()
    print('Futási idő: {}'.format(endTime - startTime))
    print("-------------------------------")
    
