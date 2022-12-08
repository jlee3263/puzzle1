import random

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


class Game():
 
   
    def __init__(self, grid, dice):
        self.dice = dice
        self.grid = grid
        self.move = 0
        self.score = 0
        self.row= 5 # always start from botom right position
        self.col = 0


    def print_game_state(self):
        print(f"My current score and moves:{self.score}, {self.move}")
        print(f"My current row and col:{self.row}, {self.col}")    
        print(f"My dice face up value:{self.dice.current_face_up_value}")


    def is_comply(self, future_row, future_col, future_face_up_value):
        # rule as follow
        # score_in_n_move = score_in_n-1_move + ( move * face_up_value_after_tipping)
        # if score_in_n_move == grid_score_which_dice_roll_onto ==> ok , else no

        future_grid_score_label = self.grid[future_row][future_col]
        future_score = self.score + ((self.move + 1) * future_face_up_value)
        print(f"    future grid score label:{future_grid_score_label}, future row and col:{future_row}, {future_col}")  
        if future_score == future_grid_score_label:
            print(f"    workable, {future_score}, {future_grid_score_label} ")
            return True
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
            print(f"Moved forward/up, new (row,col) is ({self.row}, {self.col})")

        if direction == BACKWARD:
            self.row += 1
            print(f"Moved backward/down, new (row,col) is ({self.row}, {self.col})")

        if direction == LEFT:
            self.col -= 1
            print(f"Moved left, new (row,col) is ({self.row}, {self.col})")

        if direction == RIGHT:
            self.col += 1
            print(f"Moved right, new (row,col) is ({self.row}, {self.col})")
   

    def update_game_state(self, direction):
        # when this function is called , it means the move is considered to be legit and I will make the move
        self.update_dice_orientation(direction)
        self.update_game_moves()
        self.update_game_score()
        self.update_dice_position(direction)

    def update_dice_orientation(self, direction):
        self.dice.tip(direction)
   
    def update_game_moves(self):
        print("----- Increasing move by 1")
        print(f"Prev num move: {self.move}")
        self.move += 1
        print(f"New num move: {self.move}")
   
    def update_game_score(self):
        print("---- Updating score")
        print(f"Prev score: {self.score}")
        num_points_added = self.move * self.dice.current_face_up_value
        self.score += num_points_added
        print(f"amt added: {num_points_added}, New score: {self.score}")

    def is_solved(self):
        if self.row == 0 and self.col == 5:
            print("Dice had reached the final final with a total score of {self.score}")
            return True

        return False

    def sim_play(self, moves=20):
       
        for m in range(moves):
            print(f"playing sim move {m}")
            self.sim_play_one_random_move()
            #input("hit enter to continue")


    def sim_play_one_random_move(self, test=False):
        # simulate game play blindly
        possible_directions = self.get_possible_next_tip_direction_wrt_current_position()
        print(f"Possible directions: {possible_directions}")
        # choose a random possible direction
        chosen_direction = random.choice(possible_directions)
        self.update_game_state(chosen_direction)
        self.print_game_state()
        print("----------------------------------")

   
    def test_one_move(self, direction):
        # now direction must be a 100% legal direction to tip
        dice_info = self.dice.get_state_after_tipping(direction)
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


        print(f"------- test direction: {direction} ------------")
        future_face_up_value = dice_info["value_facing_up"]
        future_face_up_index = dice_info["face_up_index"]      

        undo_face_change = False
        if future_face_up_value == 'NA':
            undo_face_change = True
            suitable_value = self.find_one_suitable_value(future_row, future_col)
            # now we find a suitable value we will enforce it
            if suitable_value:
                self.dice.fill_in_one_value_for_one_face(suitable_value, future_face_up_index)
                return True, undo_face_change
            else:
                return False, undo_face_change
        else:
            print(f"    trying with a pre-set face value:{future_face_up_value} of index:{future_face_up_index}")
            return self.is_comply(future_row, future_col, future_face_up_value), undo_face_change
 
   
    def revert_back_one_step(self, undo_direction):

        if self.dice.faces[self.dice.current_face_up_index] != "NA":
            score_deduction = (self.dice.faces[self.dice.current_face_up_index] * self.move)
            self.score = self.score - score_deduction
            print(f"Deducting {score_deduction} from the score to prev: {self.score}")

        self.move -= 1
        print("Decrementing the moves by 1")


        print("Tipping back the dice to the prev face up orentiation and prev position")
        self.update_dice_orientation(undo_direction)
        self.update_dice_position(undo_direction)


    def find_one_suitable_value(self, future_row, future_col, use_integer=False):
        # this is the crux , how to fill the face given the future row and col?
        # can the value on the dice be restricted to just integers (both positive and negative ?
        # or the value on the dice can be a real number ?
        future_label_score = self.grid[future_row][future_col]
        current_score = self.score
        current_move = self.move
        # the condition to meet is future_total_score = current_score + ((self.move + 1) * face_up_value)
        diff = future_label_score - current_score
        # for now i only accept integers
        suitable_value = diff / (self.move + 1)
        print(f"    diff is {diff}, divisor is {self.move + 1}, value computed is {suitable_value}")
        if use_integer and suitable_value.is_integer():
            return suitable_value
        elif not use_integer:
            num_decimal_points = len(str(suitable_value).split(".")[1])
            if num_decimal_points < 10:
                return suitable_value  
        print(f"    {suitable_value} not suitable")
        return False


    def get_tip_back_direction(self, future_direction):
        undo_direction = False
        if future_direction == FORWARD:
            undo_direction =  BACKWARD
        if future_direction == BACKWARD:
            undo_direction =  FORWARD
        if future_direction == LEFT:
            undo_direction =  RIGHT
        if future_direction == RIGHT:
            undo_direction = LEFT
        print(f"direction just made: {future_direction}, undo direction: {undo_direction}")
        return undo_direction

    def play(self):
        self.solve()    
       

    def solve(self):
        # Logic as follows:
        # 1. given the cur pos: -> get_possible_grid_movents:
        # 2. for each possible movement wrt to face up value
        #       1. make the move and test
        #           if the move is valid and future value is Null
        #                    -> fill in the face with value which fit the rule -> valid move
        #                    -  if there is no legit value to fill in -> illegal move
        #           if the move is valid but the future score does not tally with future grid label -> illegal move
        # 3 Repeat from 1 till we complete OR run out of valud moves

       
        self.dice.print_state()
        self.print_game_state()
        input(" ========================= hit enter to continue ======================================")
        if self.is_solved():
            exit("YESSSSSSSSSSS")

        possible_directions = self.get_possible_next_tip_direction_wrt_current_position()
        print(f"Possible directions: {possible_directions}")
        for pd in possible_directions:


            #  if my position is 5,0 -> change all faces to NA
            if self.row == 5 and self.col == 0:
                self.dice.faces = ["NA"] * 6
            # test move first
            can_work, can_undo_face_change = self.test_one_move(pd)
            if can_work:
                self.update_game_state(pd)
                self.solve()

                print(" --------------- reverting back one step....")
                tip_back_direction = self.get_tip_back_direction(pd)
                backup_face_up_index = self.dice.current_face_up_index
                self.revert_back_one_step(tip_back_direction)

                if can_undo_face_change:
                    print(" ------------------------ reverting back one face....")
                    self.dice.fill_in_one_value_for_one_face("NA", backup_face_up_index)
             
   
        self.dice.print_state()
        self.print_game_state()
        print("We had exhausted all possible moves with no solution")
        return
       

class Dice():

    def __init__(self, faces=None):
        if not faces:
            self.faces = [False] * 6
        else:
            self.faces = faces
        self.current_face_up_value = self.faces[0]
        self.current_face_up_index = 0


    def reset(self):
        self.current_face_up_value = self.faces[0]
        self.current_face_up_index = 0


    def print_state(self):
        print(f"My faces are: {self.faces}")
        print(f"My current face up value is {self.current_face_up_value}")
        print(f"My current face up index is {self.current_face_up_index}")

    def fill_in_one_value_for_one_face(self, new_value, index):
        # assume index = [0,6]
        print(f"changing old value on index:{index} from {self.faces[index]} to {new_value}")
        self.faces[index] = new_value


    # call this function means you really do the tip and need to update state
    def tip(self, tip_direction):
       
        state = self.get_state_after_tipping(tip_direction)
        self.current_face_up_value = state["value_facing_up"]
        self.current_face_up_index = state["face_up_index"]
        print(f"Dice had tip {tip_direction}, new face up value:{self.current_face_up_value}, new face up index:{self.current_face_up_index}")
       

    def get_state_after_tipping(self, tip_direction):
        index = self.get_next_side_up_index_after_tipping(tip_direction)
        return {
            "face_up_index": index,
            "value_facing_up": self.faces[index],
            "input_direction": tip_direction
        }

    def get_next_side_up_index_after_tipping(self, tip_direction):
        if tip_direction == FORWARD:
            if self.current_face_up_index == 0:
                next_side_up_index = 3
            if self.current_face_up_index == 1:
                next_side_up_index = 3
            if self.current_face_up_index == 2:
                next_side_up_index = 3
            if self.current_face_up_index == 3:
                next_side_up_index = 5
            if self.current_face_up_index == 4:
                next_side_up_index = 0
            if self.current_face_up_index == 5:
                next_side_up_index = 4
            return next_side_up_index

        if tip_direction == BACKWARD:
            if self.current_face_up_index == 0:
                next_side_up_index = 4
            if self.current_face_up_index == 1:
                next_side_up_index = 4
            if self.current_face_up_index == 2:
                next_side_up_index = 4
            if self.current_face_up_index == 3:
                next_side_up_index = 0
            if self.current_face_up_index == 4:
                next_side_up_index = 5
            if self.current_face_up_index == 5:
                next_side_up_index = 3
            return next_side_up_index

        if tip_direction == LEFT:
            if self.current_face_up_index == 0:
                next_side_up_index = 2
            if self.current_face_up_index == 1:
                next_side_up_index = 0
            if self.current_face_up_index == 2:
                next_side_up_index = 5
            if self.current_face_up_index == 3:
                next_side_up_index = 2
            if self.current_face_up_index == 4:
                next_side_up_index = 2
            if self.current_face_up_index == 5:
                next_side_up_index = 2
            return next_side_up_index
       
        if tip_direction == RIGHT:
            if self.current_face_up_index == 0:
                next_side_up_index = 1
            if self.current_face_up_index == 1:
                next_side_up_index = 5
            if self.current_face_up_index == 2:
                next_side_up_index = 0
            if self.current_face_up_index == 3:
                next_side_up_index = 2
            if self.current_face_up_index == 4:
                next_side_up_index = 2
            if self.current_face_up_index == 5:
                next_side_up_index = 2
            return next_side_up_index
                           

if __name__ == "__main__":

    # basic up, down, left, right rolling
    original_faces = [1,4,5,3,2,6]
    print(f"================ BASIC ROLLING TEST using {original_faces} [Top, Left, Right, Back, Front, Bottom] ===========================")        

    my_dice = Dice(original_faces)
    for d in [FORWARD, BACKWARD, LEFT, RIGHT]:
        my_dice.tip(d)

    print("--------- RESET DICE TO ORIGINAL ORENTAIION --------------")
    my_dice.reset() # reset back to original state

    print("=============== RANDOWM ROLLING TEST ====================")
    # random move test
    for d in [FORWARD, FORWARD, LEFT, LEFT, RIGHT, BACKWARD, FORWARD, RIGHT]:
        my_dice.tip(d)


    print("============== FILLING FACE TEST ========================")
    value = "XXXX"
    index = 0
    my_dice.fill_in_one_value_for_one_face(value, index)
    my_dice.print_state()


    print("============== BASIC GRID MOVEMENT TEST ==================")
    my_game = Game(GRID, Dice())
    my_game.print_game_state()
    print(f"possible movements: {my_game.get_possible_next_tip_direction_wrt_current_position()}")

    print("=============== BASIC GRID BOUNDARY TEST ================")
    row = 0
    col = 0
    print(f"setting row, col manually to {row}, {col}")
    my_game.row = row
    my_game.col = col
    print(f"possible movements: {my_game.get_possible_next_tip_direction_wrt_current_position()}")

    row = 0
    col = 5
    print(f"setting row, col manually to {row}, {col}")
    my_game.row = row
    my_game.col = col
    print(f"possible movements: {my_game.get_possible_next_tip_direction_wrt_current_position()}")

   
    row = 5
    col = 0
    print(f"setting row, col manually to {row}, {col}")
    my_game.row = row
    my_game.col = col
    print(f"possible movements: {my_game.get_possible_next_tip_direction_wrt_current_position()}")

    row = 5
    col = 3
    print(f"setting row, col manually to {row}, {col}")
    my_game.row = row
    my_game.col = col
    print(f"possible movements: {my_game.get_possible_next_tip_direction_wrt_current_position()}")

    row = 0
    col = 3
    print(f"setting row, col manually to {row}, {col}")
    my_game.row = row
    my_game.col = col
    print(f"possible movements: {my_game.get_possible_next_tip_direction_wrt_current_position()}")


    row = 3
    col = 3
    print(f"setting row, col manually to {row}, {col}")
    my_game.row = row
    my_game.col = col
    print(f"possible movements: {my_game.get_possible_next_tip_direction_wrt_current_position()}")

   
    print("======================= SIMULATING SOME MOVE TEST WITHOUT ANY RULE ============================")
    # start a new game and new dice
    print(my_game.is_solved())
    my_game = Game(GRID, Dice([1,4,5,3,2,6]))
    my_game.print_game_state()
    my_game.sim_play()

    print("======================= TRUE PLAY WITH SOME RANDOM VALUES WITH RULE ============================")
    # start a new game and new dice
    my_game = Game(GRID, Dice([1,4,5,3,2,6]))
    my_game.print_game_state()
    my_game.play()

    print("======================= TRUE PLAY WITH SOME 0 VALUES WITH RULE - GO BRUTE FORCE YOURSELF ============================")
    # start a new game and new dice
    my_game = Game(GRID, Dice(['NA'] * 6))
    my_game.print_game_state()
    my_game.play()
