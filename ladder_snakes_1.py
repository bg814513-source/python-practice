# 
import random
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import pygame  # Sound ke liye

# --- Pygame Mixer Initialize ---
pygame.mixer.init()

def play_ladder_sound():
    try:
        # Apni sound file ka naam yahan rakhein ('ladder.mp3' ya 'ladder.wav')
        pygame.mixer.music.load("ladder.mp3") 
        pygame.mixer.music.play()
    except Exception as e:
        print("Sound file missing ya play nahi ho pa rahi:", e)

# --- Window Setup ---
root = tk.Tk()
root.title("Snakes and Ladders")
root.geometry("700x720")
root.resizable(False, False)

# --- Dimensions ---
CANVAS_SIZE = 600
CELL_SIZE = CANVAS_SIZE // 10  # Exact 60px per box
TOKEN_SIZE = 20                # Small & neat circular token

canvas = tk.Canvas(root, width=CANVAS_SIZE, height=CANVAS_SIZE, bg="#f0f0f0")
canvas.place(x=50, y=20)

# --- Image Loading ---
try:
    image = Image.open("board.png").resize((CANVAS_SIZE, CANVAS_SIZE))
    board_img = ImageTk.PhotoImage(image)
    canvas.create_image(0, 0, image=board_img, anchor="nw")
except Exception:
    canvas.create_text(
        300, 300, 
        text="Please keep 'board.png' in the same folder.", 
        font=("Arial", 14)
    )

# --- Snakes & Ladders Map ---
snakes = {99: 77, 95: 75, 93: 69, 87: 24, 67: 30, 63: 19, 59: 17, 16: 7}
ladders = {9: 27, 18: 37, 25: 54, 28: 51, 56: 64, 68: 88, 76: 97, 79: 100}

# --- Player Config ---
players = {
    1: {
        "name": "Red",
        "color": "red",
        "pos": 0,
        "started": False,
        "token": canvas.create_oval(0, 0, 0, 0, fill="red", outline="black", width=2),
    },
    2: {
        "name": "Blue",
        "color": "blue",
        "pos": 0,
        "started": False,
        "token": canvas.create_oval(0, 0, 0, 0, fill="#1e90ff", outline="black", width=2),
    },
}

current_player = 1
is_moving = False

# --- Smart Center Coordinate Calculation ---
def get_coordinates(position, p_id):
    if position == 0:
        return 0, 0

    row = (position - 1) // 10
    col = (position - 1) % 10

    # Zig-Zag Board Check
    is_even_row = (row % 2 == 0)
    if not is_even_row:
        col = 9 - col

    # Box ke Top-Left Coordinates
    cell_x = col * CELL_SIZE
    cell_y = (9 - row) * CELL_SIZE

    # Absolute Box Center (MID)
    center_x = cell_x + (CELL_SIZE - TOKEN_SIZE) / 2
    center_y = cell_y + (CELL_SIZE - TOKEN_SIZE) / 2

    # Offset Separation (Red left-center, Blue right-center)
    # Direction aware taaki zig-zag row me bhi goti bahar na bhage
    offset = 5
    if p_id == 1:
        final_x = center_x - offset
    else:
        final_x = center_x + offset

    return final_x, center_y


def update_player_ui(p_id, pos):
    p_data = players[p_id]
    
    if pos == 0:
        # Base position outside grid
        if p_id == 1:
            canvas.coords(p_data["token"], 15, 565, 15 + TOKEN_SIZE, 565 + TOKEN_SIZE)
        else:
            canvas.coords(p_data["token"], 40, 565, 40 + TOKEN_SIZE, 565 + TOKEN_SIZE)
    else:
        # Exact Box MID Position
        x, y = get_coordinates(pos, p_id)

        canvas.coords(
            p_data["token"],
            x, 
            y, 
            x + TOKEN_SIZE, 
            y + TOKEN_SIZE
        )

# Base positions initialize
update_player_ui(1, 0)
update_player_ui(2, 0)

# --- Step Animation ---
def animate_move(p_id, current_pos, target_pos, callback):
    if current_pos < target_pos:
        current_pos += 1
        update_player_ui(p_id, current_pos)
        root.after(130, lambda: animate_move(p_id, current_pos, target_pos, callback))
    else:
        callback(current_pos)

# --- Turn Logic & Sound Trigger ---
def finalize_turn(final_pos):
    global current_player, is_moving

    p_data = players[current_player]

    # Snake Check
    if final_pos in snakes:
        final_pos = snakes[final_pos]
        update_player_ui(current_player, final_pos)
    
    # Ladder Check + Sound Play!
    elif final_pos in ladders:
        play_ladder_sound()  # Awaaz yahan se play hogi
        final_pos = ladders[final_pos]
        update_player_ui(current_player, final_pos)

    p_data["pos"] = final_pos

    # Win Check
    if p_data["pos"] == 100:
        messagebox.showinfo("Winner!", f"{p_data['name']} Player Wins!")
        root.destroy()
        return

    # Turn Switch
    current_player = 2 if current_player == 1 else 1
    next_player = players[current_player]

    turn_label.config(text=f"{next_player['name']}'s Turn", fg=next_player["color"])
    dice_button.config(state="normal")
    is_moving = False

# --- Dice Roll Logic ---
def roll_dice():
    global is_moving

    if is_moving:
        return

    is_moving = True
    dice_button.config(state="disabled")

    dice = random.randint(1, 6)
    dice_label.config(text=f"Dice : {dice}")

    p_data = players[current_player]

    if not p_data["started"]:
        if dice == 6:
            p_data["started"] = True
            p_data["pos"] = 1
            update_player_ui(current_player, 1)
            finalize_turn(1)
        else:
            finalize_turn(p_data["pos"])
    else:
        target = p_data["pos"] + dice
        if target <= 100:
            animate_move(current_player, p_data["pos"], target, callback=finalize_turn)
        else:
            finalize_turn(p_data["pos"])

# --- Controls UI ---
dice_label = tk.Label(root, text="Dice : 0", font=("Arial", 14, "bold"))
dice_label.place(x=50, y=640)

turn_label = tk.Label(root, text="Red's Turn", font=("Arial", 14, "bold"), fg="red")
turn_label.place(x=280, y=640)

dice_button = tk.Button(
    root,
    text="Roll Dice",
    width=14,
    font=("Arial", 12, "bold"),
    bg="#e1e1e1",
    command=roll_dice
)
dice_button.place(x=510, y=635)

root.mainloop()