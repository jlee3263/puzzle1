import random
import copy
from fractions import Fraction
from collections import deque

GRID = [
    [57, 33, 132, 268, 492, 732],
    [81, 123, 240, 443, 353, 508],
    [186, 42, 195, 704, 452, 228],
    [-7, 2, 357, 452, 317, 395],
    [5, 23, -4, 592, 445, 620],
    [0, 77, 32, 403, 337, 452]
]

FORWARD = "A"
BACKWARD = "V"
LEFT = "<-"
RIGHT = "->"

NA = "NA"


FACE_UP = "UP"
FACE_DOWN = "DOWN"
FACE_LEFT = "LEFT"
FACE_RIGHT = "RIGHT"
FACE_FRONT = "FRONT"
FACE_BACK = "BACK"


class Game():
 
   
    def __init__(self, grid, dice, replay=True, verbose=True):
        self.dice = dice
        self.grid = grid
        self.move = 0
        self.score = 0
        self.row = 5 # always start from botom right position
        self.col = 0
        self.replay = replay
        self.verbose = verbose


    def get_game_state(self):
        return self.move, self.score, self.row, self.col


    def print_game_state(self):
        print(f"    Game current score and moves:{self.score}, {self.move}")
        print(f"    Game current row and col:{self.row}, {self.col}")    
        print(f"    Game dice face up value:{self.dice.up}")


    def is_comply(self, future_row, future_col, future_face_up_value):
        # rule as follow
        # score_in_n_move = score_in_n-1_move + ( move * face_up_value_after_tipping)
        # if score_in_n_move == grid_score_which_dice_roll_onto ==> ok , else no

        future_grid_score_label = self.grid[future_row][future_col]
        future_score = self.score + ((self.move + 1) * future_face_up_value)
        if self.verbose:
            print(f"    future grid score label:{future_grid_score_label}, future row and col:{future_row}, {future_col}, future face up value: {future_face_up_value}")  
        if future_score == future_grid_score_label:
            if self.verbose:
                print(f"    workable, {future_score}, {future_grid_score_label} ")
            return True

        if self.verbose:
            print(f"    non workable, {future_score}, {future_grid_score_label} ")
        return False


    def get_possible_next_tip_direction_wrt_current_position(self):
        # FORWARD is moving up,  BACKWARD is moving down

        if self.row == 0 and self.col == 0: # top left corner
            return [RIGHT, BACKWARD]

        if self.row == 5 and self.col == 0: #  bottom left corner
            return [RIGHT, FORWARD]

        if self.row == 0 and self.col == 5: # top right corner
            return [LEFT, BACKWARD]

        if self.row == 5 and self.col == 5:  # bottom right corner
            return [LEFT, FORWARD]

        if self.row == 0 and self.col > 0 and self.col < 5: # top row
            return [RIGHT, LEFT, BACKWARD]

        if self.row == 5 and self.col > 0 and self.col < 5:  # bottom row
            return [RIGHT, LEFT, FORWARD]

        if self.row > 0 and self.row < 5 and self.col > 0 and self.col < 5:
            return [RIGHT, LEFT, FORWARD, BACKWARD]
       
        if self.col == 0:
            return [RIGHT, FORWARD, BACKWARD]
        if self.col == 5:
            return [LEFT, FORWARD, BACKWARD]


    def update_dice_position(self, direction):
        # update game state
        if direction == FORWARD: # going up
            self.row -= 1
            if self.verbose:
                print(f"    Dice on game board moved forward/up, new (row,col) is ({self.row}, {self.col})")

        if direction == BACKWARD:
            self.row += 1
            if self.verbose:
                print(f"    Dice on game board moved backward/down, new (row,col) is ({self.row}, {self.col})")

        if direction == LEFT:
            self.col -= 1
            if self.verbose:
                print(f"    Dice on game board moved left, new (row,col) is ({self.row}, {self.col})")

        if direction == RIGHT:
            self.col += 1
            if self.verbose:
                print(f"    Dice on game board moved right, new (row,col) is ({self.row}, {self.col})")
   

    def update_game_state(self, direction):
        # when this function is called , it means the move is considered to be legit and I will make the move
        self.update_dice_orientation(direction)
        self.update_game_moves()
        self.update_game_score()
        self.update_dice_position(direction)

    def update_dice_orientation(self, direction):
        self.dice.tip(direction)
   
    def update_game_moves(self):
        if self.verbose:
            print("    Increasing move by 1")
        self.move += 1
   
   
    def update_game_score(self):
        self.dice.print_state()
        if self.verbose:
            print("     Updating score")
            print(f"    Prev score: {self.score}")
        num_points_added = self.move * self.dice.up
        self.score += num_points_added
        if self.verbose:
            print(f"    amt added: {num_points_added}, New score: {self.score}")

    def is_solved(self):
        if self.row == 0 and self.col == 5:
            return True

        return False


    def test_one_moveb(self, direction):
        # now direction must be a 100% legal direction to tip
        
        if direction == BACKWARD:
            future_row = self.row + 1
            future_col = self.col

        elif direction == FORWARD:
            future_row = self.row - 1
            future_col = self.col

        elif direction == LEFT:
            future_row = self.row
            future_col = self.col - 1

        elif direction == RIGHT:
            future_row = self.row
            future_col = self.col + 1

        if self.verbose:
            print(f"    ------- test direction: {direction} ------------")

        dice_info = self.dice.get_state_after_tipping(direction)
        future_face_up_value = dice_info["up"]    

        if future_face_up_value == NA :
            suitable_value = self.find_one_suitable_value(future_row, future_col, use_integer=False)
            self.dice.fill_in_one_value_for_one_face(suitable_value, dice_info["prev_face_which_will_become_new_up_face"])
           
        else:
            suitable_value = future_face_up_value

        return self.is_comply(future_row, future_col, suitable_value)


    def find_one_suitable_value(self, future_row, future_col, use_integer):
        # this is the crux , how to fill the face given the future row and col?
        # can the value on the dice be restricted to just integers (both positive and negative ?
        # or the value on the dice can be a real number ?
        future_label_score = self.grid[future_row][future_col]
        current_score = self.score
        current_move = self.move
        # the condition to meet is future_total_score = current_score + ((self.move + 1) * face_up_value)
        diff = future_label_score - current_score
        
        if not use_integer:
            suitable_value = Fraction(diff / (self.move + 1))
            return suitable_value

        else:
            suitable_value = diff / (self.move + 1)
            if suitable_value.is_integer():
                return suitable_value

        return False


    def play(self):
        intial_dice_state = self.solveb()  
        return intial_dice_state  
    

    def replay_from_end_to_start_using_computed_path(self, path):

        print("=========================== REPLAYING FROM END TO START =======================")

        rpath = path[::-1]
        for t in rpath[:-1]:
            step_taken, r , c = t
            if step_taken == FORWARD:
                reverse_direction = BACKWARD
                pr = r + 1
                pc = c

            elif step_taken == BACKWARD:
                reverse_direction = FORWARD
                pr = r - 1
                pc = c

            elif step_taken == LEFT:
                reverse_direction = RIGHT
                pr = r
                pc = c + 1

            elif step_taken == RIGHT:
                reverse_direction = LEFT 
                pr = r
                pc = c - 1

            print(f"---- from: ({r}, {c})")
            self.dice.tip(reverse_direction)
            print(f"to: ({pr}, {pc}) ----")

        return self.dice.get_dice_state()



    def solveb(self):

        # Same logic as solve() but this one uses bfs using a queue

        q = deque([])
        ds = self.dice.get_dice_state()
        gs = self.get_game_state()
        possible_directions = self.get_possible_next_tip_direction_wrt_current_position()

        for p in possible_directions:
            if self.verbose:
                print(f"    inserting possible direction {p} to try using {copy.deepcopy(ds)} from {gs}")
            q.appendleft((p, copy.deepcopy(ds), gs, [(".", self.row, self.col)]))

        while q:

            if self.verbose:
                print("========================= POPPING NEXT ALTERNATIVE ==========================")
            try_ = q.pop()
            pd, ds, gs, path = try_

            # reinstate dice and gs 
            self.dice.up = ds["up"]
            self.dice.down = ds["down"]
            self.dice.left = ds["left"]
            self.dice.right = ds["right"]
            self.dice.front = ds["front"]
            self.dice.back = ds["back"]

            self.move = gs[0]
            self.score = gs[1]
            self.row = gs[2]
            self.col = gs[3]


            if self.verbose:
                print("My game state after reinstating")
                self.dice.print_state()
                self.print_game_state()


            if self.is_solved():
                print("===========  DESTINATION REACHED - 'A' is up, 'V' is down. '<-' is left, '->' is right ==================")
                game_score = 0
                for s in path:
                    direction_taken, r, c = s
                    square_value = self.grid[r][c]
                    game_score += square_value
                    print(f"    dice tipped \"{direction_taken}\" to reach ({r}, {c}) onto square value of: {square_value} with accumulated score of {game_score}")


                print("    Dice final state as follows:")
                for k, v in self.dice.get_dice_state().items():
                    print(f"    {k}: {v}")
                print(f"    Total score: {game_score}")

                if self.replay:
                    return self.replay_from_end_to_start_using_computed_path(path)

            can_work  = self.test_one_moveb(pd)
            if can_work:

                if self.verbose:
                    print(f"    {pd} CAN work from pos of {self.row}, {self.col}")

                self.update_game_state(pd) # execute the move
                path.append((pd, self.row, self.col)) # add in the step dice took 

                # backup dice and game state
                ds = self.dice.get_dice_state()
                gs = self.get_game_state()
                possible_directions = self.get_possible_next_tip_direction_wrt_current_position()
                for p in possible_directions:
                    if self.verbose:
                        print(f"    inserting possible direction {p} to try using {copy.deepcopy(ds)} from {gs}")
                    q.appendleft((p, copy.deepcopy(ds), gs, list(path)))

                if self.verbose:
                    print(f"My game state after executing {pd}")
                    self.dice.print_state()
                    self.print_game_state()
                

            elif self.verbose:
                print(f"    {pd} CANNOT work from pos of {self.row}, {self.col} with {self.dice.print_state()}")
            # input("========================  halt ===============================")
        print(f"We had exhausted all possible moves with no solution from last known pos of  {self.row}, {self.col} with {self.dice.print_state()}")
        return
       

class Dice():

    def __init__(self, verbose=True):

        self.up = NA
        self.down = NA
        self.left= NA
        self.right = NA
        self.front = NA
        self.back = NA
        self.verbose = verbose


    def get_dice_state(self):   
        return {
            'up': self.up, 
            'down': self.down,
            'left': self.left,
            'right': self.right,
            'front': self.front,
            'back': self.back
        }


    def print_state(self):
        if self.verbose:
            print(f"    dice face up:{self.up}, down:{self.down}, left:{self.left}, right:{self.right}, front:{self.front}, back:{self.back} ")


    def fill_in_one_value_for_one_face(self, new_value, face):

        if face == FACE_UP:
            self.up = new_value
        if face == FACE_DOWN:
            self.down = new_value
        if face == FACE_LEFT:
            self.left = new_value
        if face == FACE_RIGHT:
            self.right = new_value
        if face == FACE_FRONT:
            self.front = new_value
        if face == FACE_BACK:
            self.back = new_value

        print(f"    {face} face had been set to {new_value} as follows:")
        self.print_state()


    # call this function means you really do the tip and need to update state
    def tip(self, tip_direction):
       
        state = self.get_state_after_tipping(tip_direction)
        self.up = state["up"]
        self.down = state["down"]
        self.left = state["left"]
        self.right = state["right"]
        self.front = state["front"]
        self.back = state["back"]
        if self.verbose:
            print(f"    Dice had tipped {tip_direction} with new rotated faces as follows")
        self.print_state()
       

    def get_state_after_tipping(self, tip_direction):
        return self.get_new_udlrfb_after_tipping(tip_direction)


    def get_new_udlrfb_after_tipping(self, tip_direction):

        up = self.up
        down = self.down
        left = self.left
        right = self.right
        front = self.front
        back = self.back


        if tip_direction == FORWARD:
            new_up = back 
            new_down = front

            new_left = left
            new_right  = right

            new_front = up
            new_back = down

            prev_face_which_will_become_new_up_face = FACE_BACK


        if tip_direction == BACKWARD:

            new_up = front 
            new_down = back

            new_left = left
            new_right  = right

            new_front = down
            new_back = up

            prev_face_which_will_become_new_up_face = FACE_FRONT
           


        if tip_direction == LEFT:

            new_up = right 
            new_down = left

            new_left =  up
            new_right  = down

            new_front = front
            new_back = back

            prev_face_which_will_become_new_up_face = FACE_RIGHT


        if tip_direction == RIGHT:

            new_up = left 
            new_down = right

            new_left =  down
            new_right  = up

            new_front = front
            new_back = back

            prev_face_which_will_become_new_up_face = FACE_LEFT


        return {

            'up': new_up ,
            'down': new_down,
            'left':  new_left,
            'right': new_right,
            'front': new_front,
            'back': new_back,
            'prev_face_which_will_become_new_up_face': prev_face_which_will_become_new_up_face
        }


if __name__ == "__main__":
    
    print("======================= GO BRUTE FORCE YOURSELF ============================")
    # start a new game and new dice
    my_game = Game(GRID, Dice())
    my_game.print_game_state()
    intial_dice_state = my_game.play()

    if intial_dice_state:
        print("====================== TEST USING DICE FACES FROM PREVIOUS BRUTE FORCE ==========================")
        dice = Dice(verbose=False)
        dice.up = intial_dice_state["up"]
        dice.down = intial_dice_state["down"]
        dice.left = intial_dice_state["left"]
        dice.right = intial_dice_state["right"]
        dice.front = intial_dice_state["front"]
        dice.back = intial_dice_state["back"]
        my_game = Game(GRID, dice, replay=False, verbose=False)
        print("Starting dice orientation as follows")
        for k, v in intial_dice_state.items():
            print(k,":", v)
        my_game.print_game_state()
        my_game.play()


