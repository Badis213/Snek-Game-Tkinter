from tkinter import *
import numpy as np
from random import choice

class Snake:
    def __init__(self, x: int, y: int, speed: int, angle: int):
        self.head = [y, x]
        self.body = [self.head.copy()]
        self.speed = speed
        self.angle = angle # 0 = Right, 1 = Up, 2 = Left, 3 = Down
        self.direction_changed = False

    def move(self):
        walls = [(y, x) for y in range(len(map)) for x in range(len(map[0])) if map[y][x] == 1]
        self.direction_changed = False # Unlock direction changing

        if self.angle == 0 and not (self.head[0], self.head[1] + 1) in walls:
            self.head[1] += 1
        elif self.angle == 1 and not (self.head[0] - 1, self.head[1]) in walls:
            self.head[0] -= 1
        elif self.angle == 2 and not (self.head[0], self.head[1] - 1) in walls:
            self.head[1] -= 1
        elif self.angle == 3 and not (self.head[0] + 1, self.head[1]) in walls:
            self.head[0] += 1
        else:
            game_over()

        self.body.insert(0, self.head.copy())
        self.body.pop()
    
    def collisions(self):
        head_position = (self.head[0], self.head[1])
        
        # Check self collision (ignore the head itself)
        # Convert body segments to tuples for comparison
        body_positions = {tuple(segment) for segment in self.body[1:]}  # Use a set for faster lookup
        if head_position in body_positions:
            return game_over()  # Game Over
        
        # Check food collision
        food_position = food.food_position
        if (self.head[0], self.head[1]) == food_position:
            food.eaten()
            self.body.append(self.body[-1])

        # Wall collision already checked in move function

class Food:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.food_position = (y, x)

    def eaten(self):
        global SCORE
        body_positions = {tuple(segment) for segment in snake.body}  # Snake's body positions
        empty_spaces = [(y, x) for y in range(len(map)) 
                        for x in range(len(map[0])) 
                        if map[y][x] == 0 and (y, x) not in body_positions]

        if empty_spaces:  # If there are empty spaces available
            self.y, self.x = choice(empty_spaces)  # Randomly select food position
            self.food_position = (self.y, self.x)
            SCORE += 1
            snake.speed -= 0.005 # add difficulty by adding speed         

# Game map
map = np.array([[1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 0, 0, 0, 0, 0, 0, 0, 1],
                [1, 0, 0, 0, 0, 0, 0, 0, 1],
                [1, 0, 0, 0, 0, 0, 0, 0, 1],
                [1, 0, 0, 1, 1, 1, 0, 0, 1],
                [1, 0, 0, 0, 0, 0, 0, 0, 1],
                [1, 0, 0, 0, 1, 0, 0, 0, 1],
                [1, 0, 0, 0, 1, 0, 0, 0, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1]])

# Parsing
CELL_SIZE = 70
HEIGHT = len(map) * CELL_SIZE
WIDTH = len(map[0]) * CELL_SIZE
SCORE = 0

# Initializing the window
window = Tk()
window.title('Badis\'s Snek')

# Create a score frame
score_frame = Frame(window, bg="black")
score_frame.pack(fill="x")  # Make the frame span the entire width of the window

# Score label inside the frame
score_label = Label(score_frame, text=f"SCORE: {SCORE}", font=("Arial", 24, "bold"), fg="white", bg="black", borderwidth=0, highlightthickness=0)
score_label.pack(pady=10)

# Canvas for the game, placed below the score label
canvas = Canvas(window, width=WIDTH, height=HEIGHT, bg='black')
canvas.pack()


# Update the score dynamically
def update_score():
    score_label.config(text=f"SCORE: {SCORE}")

# Function to draw the 2D map
def draw_map(snake, food):
    canvas.delete("all")
    for y in range(len(map)):
        for x in range(len(map[0])):
            x1 = x * CELL_SIZE
            y1 = y * CELL_SIZE
            x2 = x1 + CELL_SIZE
            y2 = y1 + CELL_SIZE
            if map[y][x] == 1:
                canvas.create_rectangle(x1, y1, x2, y2, fill='gray', outline='black')
            else:
                canvas.create_rectangle(x1, y1, x2, y2, fill='black', outline='black')
    food_x = food.x * CELL_SIZE
    food_y = food.y * CELL_SIZE
    canvas.create_oval(food_x, food_y, food_x + CELL_SIZE, food_y + CELL_SIZE, fill='red', outline='black')

    for segment in snake.body:
        seg_x = segment[1] * CELL_SIZE
        seg_y = segment[0] * CELL_SIZE
        if [segment[0], segment[1]] == snake.head:
            canvas.create_rectangle(seg_x, seg_y, seg_x + CELL_SIZE, seg_y + CELL_SIZE, fill='#00FF00', outline='black')
        else:
            canvas.create_rectangle(seg_x, seg_y, seg_x + CELL_SIZE, seg_y + CELL_SIZE, fill='#22AA22', outline='black')


# All the functions to call each turn
def next_turn():
    snake.collisions()
    snake.move()
    update_score()
    draw_map(snake, food)
    window.after(int(snake.speed*1000), next_turn)

# Function to call when game over
def game_over():
    print(f"Game Over ! Your score was {SCORE}.")
    window.quit()

# Initializing the first food and the player
food: Food = Food(5, 5)
snake: Snake = Snake(1, 1, 0.20, 3)

# Conditions to change direction
def change_direction(event):
    if not snake.direction_changed:  # Check if direction already changed in this turn
        if event.keysym == "Up" and snake.angle != 3:
            snake.angle = 1  # Up
            snake.direction_changed = True  # Lock direction changing
        elif event.keysym == "Down" and snake.angle != 1:
            snake.angle = 3  # Down
            snake.direction_changed = True
        elif event.keysym == "Left" and snake.angle != 0:
            snake.angle = 2  # Left
            snake.direction_changed = True
        elif event.keysym == "Right" and snake.angle != 2:
            snake.angle = 0  # Right
            snake.direction_changed = True

window.bind("<Key>", change_direction)

# Initializing game loop
draw_map(snake, food)
next_turn()
window.mainloop()