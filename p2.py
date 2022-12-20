import random

class Hexagon():
    def __init__(self, num):
        h1 = None
        h2 = None
        h3 = None
        self.num = num

def random_walk(home_hexagaon):

    path = []
    current = home_hexagaon
    while True:
        random_choice = random.choice([1, 2 ,3])
        if random_choice == 1:
            path.append(current.h1.num)
            current = current.h1
        elif random_choice == 2:
            path.append(current.h2.num)
            current = current.h2
        elif random_choice == 3:
            path.append(current.h3.num)
            current = current.h3

        if current.num == 1:
            break
            #print(path)
    return path


def simulate(home_hexagaon):

    random_path = random_walk(home_hexagaon)
    return random_path


if __name__ == "__main__":

    hexagons = []
    for i in range(1, 21):
        # print(i)
        hexagons.append(Hexagon(i))

    # join the hexagons
    edges = {

        1: [2,5,11],
        2: [1,3,10],
        3: [2,4,9],
        4: [3,5,8],
        5: [1,4,6],
        6: [5,7,12],
        7: [6,8,18],
        8: [4,7,13],
        9: [3,13,14],
        10: [2,14,15],
        11: [1,12,15],
        12: [6,11,17],
        13: [8,9,19],
        14: [9,10,20],
        15: [10,11,16],
        16: [15,17,20],
        17: [12,16,18],
        18: [7,17,19],
        19: [13,18,20],
        20: [14,16,19]
}

# join the edges
for hexagon_num, neighs in edges.items():

    h0 = hexagons[hexagon_num-1]
    h0.h1 = hexagons[neighs[0]-1]
    h0.h2 = hexagons[neighs[1]-1]
    h0.h3 = hexagons[neighs[2]-1]
    #print(h0.num, h0.h1.num, h0.h2.num, h0.h3.num)

num_of_trials = 50
num_of_runs_per_trial = 100000
freq = {}
avgs = []

grand_total_steps = 0
for n_trial in range(num_of_trials):
    total_steps = 0
    for n in range(1, num_of_runs_per_trial+1):
        #print(f"============== Trial: {n} =====================")
        random_path = simulate(hexagons[0])
        #print(random_path[0])
        random_path_str = ",".join(map(str, random_path))
        #print(random_path_str)
        steps = len(random_path)
        total_steps += steps
        steps_seened = freq.get(len(random_path), set())
        if random_path_str not in steps_seened:
            steps_seened.add(random_path_str)       
            
        freq[steps] = steps_seened
    #print(f"steps for trial_{n}: {steps}")

    grand_total_steps += total_steps
    avg = total_steps / num_of_runs_per_trial
    avgs.append(avg)
    #print(f" Average steps for trial_{n_trial} trials: {avg}")

print(f"Average of all trials: {sum(avgs)/len(avgs)}" )

accum_20 = 0
for i in range(1, 21):

    s = freq.get(i)
    if s:
        print(i, len(s))
        p_i = (len(s) * (1/3**i))
        accum_20 += p_i
        print("    ",  accum_20)

answer_for_20 = 1 - accum_20
print(f"answer for 20 steps: {answer_for_20}")

