def answer(population, x, y, strength):
    max_y = len(population)
    max_x = len(population[0])
    visited = []
    to_visit = [(y, x)]

    def next_coords():
        for coords in to_visit:
            yield coords
    
    for y, x in next_coords():
        if population[y][x] <= strength:
            print population
            visited.append((y, x))
            population[y][x] = -1
            if x + 1 < max_x and (y, x+1) not in visited:
                to_visit.append((y, x+1))
            if y + 1 < max_y and (y+1, x) not in visited:
                to_visit.append((y+1, x))
            if x - 1 >= 0 and (y, x-1) not in visited:
                to_visit.append((y, x-1))
            if y - 1 >= 0 and (y-1, x) not in visited:
                to_visit.append((y-1, x))

    return population

if __name__ == '__main__':
    print answer([[1, 2, 3], [2, 3, 4], [3, 2, 1]], 0, 0, 2)
    print answer([[6, 7, 2, 7, 6], [6, 3, 1, 4, 7], [0, 2, 4, 1, 10], [8, 1, 1, 4, 9], [8, 7, 4, 9, 9]], 2, 1, 5)