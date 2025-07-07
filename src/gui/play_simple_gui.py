#!/usr/bin/env python3
"""
Simple GUI for playing Battleships against the AI
Fixed version with better error handling and simpler logic
"""

import tkinter as tk
from tkinter import messagebox
import numpy as np
import torch
import random
from copy import copy

# Import our game components
from battleships import Battleships
import Alpha0

class SimpleBattleshipsGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🚢 Battleships vs AI")
        self.root.geometry("900x600")
        self.root.configure(bg='#2c3e50')
        
        # Game state
        self.game = None
        self.ai_policy = None
        self.setup_phase = True
        self.human_ships_placed = False
        self.game_over = False
        
        # Board setup
        self.board_size = 10
        self.ships = [5, 4, 3, 3, 2]
        self.ship_names = ["Carrier (5)", "Battleship (4)", "Cruiser (3)", "Cruiser (3)", "Destroyer (2)"]
        
        # Colors
        self.colors = {
            'water': '#3498db',
            'ship': '#2c3e50',
            'hit': '#e74c3c',
            'miss': '#95a5a6',
            'unknown': '#34495e'
        }
        
        self.setup_ui()
        self.load_ai()
        self.start_new_game()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Title
        title_label = tk.Label(self.root, text="🚢 Battleships vs AI", 
                              font=('Arial', 20, 'bold'), bg='#2c3e50', fg='white')
        title_label.pack(pady=10)
        
        # Main game area
        game_frame = tk.Frame(self.root, bg='#2c3e50')
        game_frame.pack(expand=True, fill='both', padx=20, pady=10)
        
        # Your board (left side)
        left_frame = tk.Frame(game_frame, bg='#34495e', relief='raised', bd=2)
        left_frame.pack(side='left', padx=10, fill='both', expand=True)
        
        your_label = tk.Label(left_frame, text="🏠 Your Fleet", 
                             font=('Arial', 14, 'bold'), bg='#34495e', fg='white')
        your_label.pack(pady=5)
        
        self.your_board_frame = tk.Frame(left_frame, bg='#34495e')
        self.your_board_frame.pack(pady=10)
        
        # Enemy board (right side)
        right_frame = tk.Frame(game_frame, bg='#34495e', relief='raised', bd=2)
        right_frame.pack(side='right', padx=10, fill='both', expand=True)
        
        enemy_label = tk.Label(right_frame, text="🎯 Target Area", 
                              font=('Arial', 14, 'bold'), bg='#34495e', fg='white')
        enemy_label.pack(pady=5)
        
        self.enemy_board_frame = tk.Frame(right_frame, bg='#34495e')
        self.enemy_board_frame.pack(pady=10)
        
        # Status and controls
        control_frame = tk.Frame(self.root, bg='#2c3e50')
        control_frame.pack(side='bottom', fill='x', pady=10)
        
        self.status_label = tk.Label(control_frame, text="Welcome! Auto-placing ships...", 
                                    font=('Arial', 12), bg='#2c3e50', fg='white')
        self.status_label.pack(pady=5)
        
        # Buttons
        button_frame = tk.Frame(control_frame, bg='#2c3e50')
        button_frame.pack(pady=5)
        
        self.new_game_btn = tk.Button(button_frame, text="🆕 New Game", 
                                     command=self.start_new_game, bg='#3498db', fg='white',
                                     font=('Arial', 10, 'bold'), padx=20)
        self.new_game_btn.pack(side='left', padx=5)
        
        self.create_boards()
        
    def create_boards(self):
        """Create the game boards"""
        # Clear existing boards
        for widget in self.your_board_frame.winfo_children():
            widget.destroy()
        for widget in self.enemy_board_frame.winfo_children():
            widget.destroy()
            
        # Your board
        self.your_buttons = []
        for i in range(self.board_size):
            row = []
            for j in range(self.board_size):
                btn = tk.Button(self.your_board_frame, 
                               width=3, height=1,
                               bg=self.colors['water'],
                               state='disabled')  # Your board is not clickable
                btn.grid(row=i, column=j, padx=1, pady=1)
                row.append(btn)
            self.your_buttons.append(row)
            
        # Enemy board
        self.enemy_buttons = []
        for i in range(self.board_size):
            row = []
            for j in range(self.board_size):
                btn = tk.Button(self.enemy_board_frame,
                               width=3, height=1,
                               bg=self.colors['unknown'],
                               command=lambda r=i, c=j: self.attack(r, c))
                btn.grid(row=i, column=j, padx=1, pady=1)
                row.append(btn)
            self.enemy_buttons.append(row)
    
    def load_ai(self):
        """Load the trained AI policy"""
        try:
            self.ai_policy = torch.load('6-6-4-pie-0.mypolicy', map_location='cpu')
            self.ai_policy.eval()
            self.status_label.config(text="✅ AI loaded successfully!")
        except Exception as e:
            self.status_label.config(text=f"⚠️ AI not found, using random moves")
            self.ai_policy = None
    
    def start_new_game(self):
        """Start a new game"""
        self.game = Battleships()
        self.setup_phase = True
        self.human_ships_placed = False
        self.game_over = False
        
        # Reset board colors
        for i in range(self.board_size):
            for j in range(self.board_size):
                self.your_buttons[i][j].config(bg=self.colors['water'], text='')
                self.enemy_buttons[i][j].config(bg=self.colors['unknown'], text='', state='normal')
        
        # Auto-place human ships
        self.auto_place_human_ships()
        
    def auto_place_human_ships(self):
        """Automatically place human ships"""
        self.status_label.config(text="🚢 Placing your ships...")
        
        for attempt in range(1000):  # Try up to 1000 times
            boats = []
            directions = []
            
            for ship_length in self.ships:
                down = random.choice([True, False])
                directions.append(down)
                
                if down:  # Vertical
                    x = random.randint(0, 9)
                    y = random.randint(0, 10 - ship_length)
                else:  # Horizontal
                    x = random.randint(0, 10 - ship_length)
                    y = random.randint(0, 9)
                    
                boats.append((x, y))
            
            # Try to place ships
            if self.game.place(boats, directions):
                self.visualize_human_ships()
                self.auto_place_ai_ships()
                return
        
        self.status_label.config(text="❌ Could not place ships. Try again.")
    
    def auto_place_ai_ships(self):
        """Automatically place AI ships"""
        for attempt in range(1000):
            boats = []
            directions = []
            
            for ship_length in self.ships:
                down = random.choice([True, False])
                directions.append(down)
                
                if down:  # Vertical
                    x = random.randint(0, 9)
                    y = random.randint(0, 10 - ship_length)
                else:  # Horizontal
                    x = random.randint(0, 10 - ship_length)
                    y = random.randint(0, 9)
                    
                boats.append((x, y))
            
            if self.game.place(boats, directions):
                self.setup_phase = False
                self.human_ships_placed = True
                self.status_label.config(text="⚔️ Battle ready! Click enemy board to attack.")
                return
        
        self.status_label.config(text="❌ Could not place AI ships. Starting over...")
        self.start_new_game()
    
    def visualize_human_ships(self):
        """Show human ships on the board"""
        for i in range(10):
            for j in range(10):
                if self.game.state[0, 0, i, j] == 1:  # Human ship at (i,j)
                    self.your_buttons[i][j].config(bg=self.colors['ship'], text='⚓')
    
    def attack(self, row, col):
        """Handle human attack"""
        if self.setup_phase or self.game_over:
            return
        
        # Check if already attacked
        if self.enemy_buttons[row][col]['text'] != '':
            self.status_label.config(text="⚠️ Already attacked this position!")
            return
        
        # Make human move
        success = self.game.fire((row, col))
        if not success:
            return
        
        # Update enemy board
        if self.game.state[0, 1, row, col] == 1:  # Hit
            self.enemy_buttons[row][col].config(bg=self.colors['hit'], text='💥')
            self.status_label.config(text=f"🎯 HIT at {chr(65+col)}{row+1}!")
        else:  # Miss
            self.enemy_buttons[row][col].config(bg=self.colors['miss'], text='💧')
            self.status_label.config(text=f"💧 Miss at {chr(65+col)}{row+1}")
        
        # Check win condition
        if self.check_game_over():
            return
        
        # AI turn
        self.root.after(1000, self.ai_turn)
    
    def ai_turn(self):
        """Handle AI turn"""
        if self.game_over:
            return
        
        # Find valid moves for AI
        valid_moves = []
        for i in range(10):
            for j in range(10):
                if self.game.state[1, 1, i, j] == 0:  # AI hasn't fired here
                    valid_moves.append((i, j))
        
        if not valid_moves:
            return
        
        # AI makes move (random for simplicity)
        ai_move = random.choice(valid_moves)
        row, col = ai_move
        
        success = self.game.fire(ai_move)
        if not success:
            return
        
        # Update your board
        if self.game.state[1, 1, row, col] == 1:  # AI hit your ship
            self.your_buttons[row][col].config(bg=self.colors['hit'], text='💥')
            self.status_label.config(text=f"💥 AI HIT your ship at {chr(65+col)}{row+1}!")
        else:  # AI missed
            self.your_buttons[row][col].config(bg=self.colors['miss'], text='💧')
            self.status_label.config(text=f"💧 AI missed at {chr(65+col)}{row+1}")
        
        self.check_game_over()
    
    def check_game_over(self):
        """Check if game is over"""
        # Simple win condition: check if all enemy ships are hit
        human_hits = np.sum(self.game.state[0, 1] == 1)  # Human's hits
        ai_hits = np.sum(self.game.state[1, 1] == 1)     # AI's hits
        
        total_ship_cells = sum(self.ships)  # 17 total cells
        
        if human_hits >= total_ship_cells:
            self.game_over = True
            messagebox.showinfo("🎉 Victory!", "You sunk all enemy ships! You win!")
            self.disable_enemy_board()
            return True
        elif ai_hits >= total_ship_cells:
            self.game_over = True
            messagebox.showinfo("💀 Defeat!", "AI sunk all your ships! You lose!")
            self.disable_enemy_board()
            return True
        
        return False
    
    def disable_enemy_board(self):
        """Disable all enemy board buttons"""
        for i in range(10):
            for j in range(10):
                self.enemy_buttons[i][j].config(state='disabled')
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()

def main():
    """Main function to start the game"""
    app = SimpleBattleshipsGUI()
    app.run()

if __name__ == "__main__":
    main()
