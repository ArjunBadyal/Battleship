#!/usr/bin/env python3
"""
Interactive GUI for playing Battleships against the trained AlphaZero AI
Click on the board to make moves, with beautiful visual feedback.
"""

import tkinter as tk
from tkinter import ttk, messagebox, font
import numpy as np
import torch
from copy import copy
import random

# Import our game components
from battleships import Battleships
from battleships2 import Battleships2
import Alpha0
import MCTS

class BattleshipsGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🚢 Battleships vs AlphaZero AI")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2c3e50')
        
        # Game state
        self.game = None
        self.ai_policy = None
        self.ai_mcts = None
        self.setup_phase = True
        self.user_ships_placed = False
        self.current_ship_index = 0
        self.ship_placement_start = None
        self.human_is_player_0 = True  # Human is always player 0
        
        # Board setup
        self.board_size = 10
        self.cell_size = 40
        
        # Colors
        self.colors = {
            'water': '#3498db',
            'ship': '#2c3e50',
            'hit': '#e74c3c',
            'miss': '#95a5a6',
            'hover': '#f39c12',
            'valid_placement': '#27ae60',
            'invalid_placement': '#e74c3c'
        }
        
        # Ship data
        self.ships = [5, 4, 3, 3, 2]  # Carrier, Battleship, Cruiser, Cruiser, Destroyer
        self.ship_names = ["Aircraft Carrier (5)", "Battleship (4)", "Cruiser (3)", "Cruiser (3)", "Destroyer (2)"]
        
        self.setup_ui()
        self.load_ai()
        self.start_new_game()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Title
        title_font = font.Font(family="Arial", size=24, weight="bold")
        title_label = tk.Label(self.root, text="🚢 Battleships vs AlphaZero AI", 
                              font=title_font, bg='#2c3e50', fg='white')
        title_label.pack(pady=10)
        
        # Main frame
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(expand=True, fill='both', padx=20, pady=10)
        
        # Left panel - Your board
        left_frame = tk.Frame(main_frame, bg='#34495e', relief='raised', bd=2)
        left_frame.pack(side='left', padx=10, pady=10, fill='both', expand=True)
        
        # Right panel - Enemy board (AI)
        right_frame = tk.Frame(main_frame, bg='#34495e', relief='raised', bd=2)
        right_frame.pack(side='right', padx=10, pady=10, fill='both', expand=True)
        
        # Your board
        your_label = tk.Label(left_frame, text="🏠 Your Fleet", 
                             font=('Arial', 16, 'bold'), bg='#34495e', fg='white')
        your_label.pack(pady=5)
        
        self.your_board_frame = tk.Frame(left_frame, bg='#34495e')
        self.your_board_frame.pack(pady=10)
        
        # Enemy board
        enemy_label = tk.Label(right_frame, text="🎯 Enemy Waters", 
                              font=('Arial', 16, 'bold'), bg='#34495e', fg='white')
        enemy_label.pack(pady=5)
        
        self.enemy_board_frame = tk.Frame(right_frame, bg='#34495e')
        self.enemy_board_frame.pack(pady=10)
        
        # Status panel
        status_frame = tk.Frame(main_frame, bg='#2c3e50')
        status_frame.pack(side='bottom', fill='x', pady=10)
        
        self.status_label = tk.Label(status_frame, text="Welcome! Place your ships to begin.", 
                                    font=('Arial', 12), bg='#2c3e50', fg='white', wraplength=800)
        self.status_label.pack(pady=5)
        
        # Ship placement instructions
        self.instruction_label = tk.Label(status_frame, text="", 
                                         font=('Arial', 10), bg='#2c3e50', fg='#ecf0f1')
        self.instruction_label.pack(pady=2)
        
        # Control buttons
        button_frame = tk.Frame(status_frame, bg='#2c3e50')
        button_frame.pack(pady=10)
        
        self.new_game_btn = tk.Button(button_frame, text="🆕 New Game", 
                                     command=self.start_new_game, bg='#3498db', fg='white',
                                     font=('Arial', 10, 'bold'), padx=20)
        self.new_game_btn.pack(side='left', padx=5)
        
        self.auto_place_btn = tk.Button(button_frame, text="🎲 Auto Place Ships", 
                                       command=self.auto_place_ships, bg='#f39c12', fg='white',
                                       font=('Arial', 10, 'bold'), padx=20)
        self.auto_place_btn.pack(side='left', padx=5)
        
        self.rotate_btn = tk.Button(button_frame, text="🔄 Rotate Ship", 
                                   command=self.toggle_ship_direction, bg='#9b59b6', fg='white',
                                   font=('Arial', 10, 'bold'), padx=20)
        self.rotate_btn.pack(side='left', padx=5)
        
        # Ship direction state
        self.ship_direction_vertical = True
        
        self.create_boards()
        
    def create_boards(self):
        """Create the game boards"""
        # Clear existing boards
        for widget in self.your_board_frame.winfo_children():
            widget.destroy()
        for widget in self.enemy_board_frame.winfo_children():
            widget.destroy()
            
        # Your board (where your ships are)
        self.your_buttons = []
        for i in range(self.board_size):
            row = []
            for j in range(self.board_size):
                btn = tk.Button(self.your_board_frame, 
                               width=4, height=2,
                               bg=self.colors['water'],
                               command=lambda r=i, c=j: self.on_your_board_click(r, c))
                btn.grid(row=i, column=j, padx=1, pady=1)
                row.append(btn)
            self.your_buttons.append(row)
            
        # Enemy board (where you attack)
        self.enemy_buttons = []
        for i in range(self.board_size):
            row = []
            for j in range(self.board_size):
                btn = tk.Button(self.enemy_board_frame,
                               width=4, height=2,
                               bg=self.colors['water'],
                               command=lambda r=i, c=j: self.on_enemy_board_click(r, c))
                btn.grid(row=i, column=j, padx=1, pady=1)
                row.append(btn)
            self.enemy_buttons.append(row)
            
        # Add coordinate labels
        # Column labels (A-J)
        for j in range(self.board_size):
            label = tk.Label(self.your_board_frame, text=chr(65+j), 
                           font=('Arial', 8, 'bold'), bg='#34495e', fg='white')
            label.grid(row=self.board_size, column=j)
            
            label = tk.Label(self.enemy_board_frame, text=chr(65+j), 
                           font=('Arial', 8, 'bold'), bg='#34495e', fg='white')
            label.grid(row=self.board_size, column=j)
            
        # Row labels (1-10)
        for i in range(self.board_size):
            label = tk.Label(self.your_board_frame, text=str(i+1), 
                           font=('Arial', 8, 'bold'), bg='#34495e', fg='white')
            label.grid(row=i, column=self.board_size)
            
            label = tk.Label(self.enemy_board_frame, text=str(i+1), 
                           font=('Arial', 8, 'bold'), bg='#34495e', fg='white')
            label.grid(row=i, column=self.board_size)
    
    def load_ai(self):
        """Load the trained AI policy"""
        try:
            # Try to load the best model first
            self.ai_policy = torch.load('models/agent_best.mypolicy', map_location='cpu', weights_only=False)
            self.ai_policy.eval()
            self.status_label.config(text="✅ AI loaded successfully! Ready to play.")
        except Exception as e:
            try:
                # Fall back to current model if best doesn't exist
                self.ai_policy = torch.load('models/agent_current.mypolicy', map_location='cpu', weights_only=False)
                self.ai_policy.eval()
                self.status_label.config(text="✅ AI loaded successfully! Ready to play.")
            except Exception as e2:
                self.status_label.config(text=f"⚠️ Could not load AI: {e2}")
                self.ai_policy = None
    
    def start_new_game(self):
        """Start a new game"""
        self.game = Battleships()
        self.setup_phase = True
        self.user_ships_placed = False
        self.current_ship_index = 0
        self.ship_placement_start = None
        
        # Reset board colors
        for i in range(self.board_size):
            for j in range(self.board_size):
                self.your_buttons[i][j].config(bg=self.colors['water'], text='')
                self.enemy_buttons[i][j].config(bg=self.colors['water'], text='')
        
        self.update_status("🚢 Place your ships! Click and drag to position them.")
        self.update_instructions(f"Place {self.ship_names[0]} - Click start position, then end position")
        
        # Enable/disable buttons
        self.auto_place_btn.config(state='normal')
        self.rotate_btn.config(state='normal')
    
    def toggle_ship_direction(self):
        """Toggle between vertical and horizontal ship placement"""
        self.ship_direction_vertical = not self.ship_direction_vertical
        direction = "Vertical" if self.ship_direction_vertical else "Horizontal"
        self.rotate_btn.config(text=f"🔄 {direction}")
        
    def auto_place_ships(self):
        """Automatically place ships for the user"""
        if not self.setup_phase:
            return
            
        # Generate random valid ship placements
        attempts = 0
        max_attempts = 1000
        
        while attempts < max_attempts:
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
            test_game = Battleships()
            if test_game.place(boats, directions):
                # Success! Apply to our game
                self.game = test_game
                self.visualize_your_ships()
                self.complete_ship_placement()
                return
                
            attempts += 1
        
        self.update_status("❌ Could not auto-place ships. Try manual placement.")
    
    def on_your_board_click(self, row, col):
        """Handle clicks on your board (ship placement)"""
        if not self.setup_phase or self.user_ships_placed:
            return
        
        if self.ship_placement_start is None:
            # First click - select start position
            self.ship_placement_start = (row, col)
            self.your_buttons[row][col].config(bg=self.colors['hover'])
            self.update_instructions(f"Now click the end position for {self.ship_names[self.current_ship_index]}")
        else:
            # Second click - try to place ship
            self.place_ship(self.ship_placement_start, (row, col))
            
    def place_ship(self, start_pos, end_pos):
        """Place a ship between two positions"""
        start_row, start_col = start_pos
        end_row, end_col = end_pos
        ship_length = self.ships[self.current_ship_index]
        
        # Determine if placement is valid
        if start_row == end_row:  # Horizontal
            if abs(end_col - start_col) + 1 == ship_length:
                # Valid horizontal placement
                min_col = min(start_col, end_col)
                self.place_ship_at_position(start_row, min_col, False)
            else:
                self.invalid_placement()
        elif start_col == end_col:  # Vertical
            if abs(end_row - start_row) + 1 == ship_length:
                # Valid vertical placement
                min_row = min(start_row, end_row)
                self.place_ship_at_position(min_row, start_col, True)
            else:
                self.invalid_placement()
        else:
            self.invalid_placement()
    
    def place_ship_at_position(self, row, col, vertical):
        """Place ship at specific position"""
        ship_length = self.ships[self.current_ship_index]
        
        # Check if position is valid in the game
        test_positions = []
        temp_game = copy(self.game)
        
        try:
            # Try to place this ship
            result = temp_game.place([(col, row)], [vertical])
            if result:
                # Success! Update visual and game state
                self.game = temp_game
                self.visualize_ship(row, col, ship_length, vertical)
                self.current_ship_index += 1
                self.ship_placement_start = None
                
                if self.current_ship_index >= len(self.ships):
                    self.complete_ship_placement()
                else:
                    self.update_instructions(f"Place {self.ship_names[self.current_ship_index]} - Click start position, then end position")
            else:
                self.invalid_placement()
        except:
            self.invalid_placement()
    
    def visualize_ship(self, row, col, length, vertical):
        """Visualize a placed ship on the board"""
        for i in range(length):
            if vertical:
                self.your_buttons[row + i][col].config(bg=self.colors['ship'], text='⚓')
            else:
                self.your_buttons[row][col + i].config(bg=self.colors['ship'], text='⚓')
    
    def invalid_placement(self):
        """Handle invalid ship placement"""
        self.ship_placement_start = None
        # Reset board colors
        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.your_buttons[i][j]['bg'] == self.colors['hover']:
                    self.your_buttons[i][j].config(bg=self.colors['water'])
        
        self.update_status("❌ Invalid ship placement! Try again.")
        self.update_instructions(f"Place {self.ship_names[self.current_ship_index]} - Click start position, then end position")
    
    def complete_ship_placement(self):
        """Complete the ship placement phase"""
        self.setup_phase = False
        self.user_ships_placed = True
        
        # Disable placement buttons
        self.auto_place_btn.config(state='disabled')
        self.rotate_btn.config(state='disabled')
        
        # Place AI ships
        self.place_ai_ships()
        
        # Start the game
        self.update_status("⚔️ Battle begins! Click on the enemy board to attack.")
        self.update_instructions("Your turn - Click a position on the enemy board to fire!")
    
    def place_ai_ships(self):
        """Place AI ships randomly"""
        attempts = 0
        max_attempts = 1000
        
        while attempts < max_attempts:
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
            
            # Try to place AI ships
            if self.game.place(boats, directions):
                return
                
            attempts += 1
        
        self.update_status("❌ Could not place AI ships. Starting new game...")
        self.start_new_game()
    
    def visualize_your_ships(self):
        """Visualize all your ships after auto-placement"""
        # Get ship positions from game state
        ship_positions = self.game.ship_positions[0]  # Human is player 0
        
        for pos, ship_idx in ship_positions.items():
            row, col = pos
            self.your_buttons[row][col].config(bg=self.colors['ship'], text='⚓')
    
    def on_enemy_board_click(self, row, col):
        """Handle clicks on enemy board (attacks)"""
        if self.setup_phase or not self.user_ships_placed:
            return
        
        if self.game.score is not None:
            return  # Game over
        
        # Check if position already attacked
        if self.enemy_buttons[row][col]['text'] != '':
            self.update_status("⚠️ You already fired at this position!")
            return
        
        # Make human move
        self.make_human_move(row, col)
        
        # Check if game is over
        if self.game.score is not None:
            self.handle_game_over()
            return
        
        # AI turn
        self.root.after(1000, self.make_ai_move)  # Delay for dramatic effect
    
    def make_human_move(self, row, col):
        """Make a move for the human player"""
        result = self.game.fire((row, col))
        
        if result:
            # Check if it was a hit or miss
            if self.game.state[0, 1, row, col] == 1:  # Hit
                self.enemy_buttons[row][col].config(bg=self.colors['hit'], text='💥')
                self.update_status(f"🎯 HIT at {chr(65+col)}{row+1}! AI's turn...")
            else:  # Miss
                self.enemy_buttons[row][col].config(bg=self.colors['miss'], text='💧')
                self.update_status(f"💧 Miss at {chr(65+col)}{row+1}. AI's turn...")
        else:
            self.update_status("❌ Invalid move!")
    
    def make_ai_move(self):
        """Make a move for the AI"""
        if self.game.score is not None:
            return
        
        try:
            if self.ai_policy is not None:
                # Use trained AI
                self.ai_mcts = MCTS.Node(copy(self.game))
                
                # Run MCTS for AI decision
                for _ in range(50):  # Reduced for faster play
                    if self.ai_mcts.game.score is None:
                        self.ai_mcts.explore(self.ai_policy)
                
                # Get best move
                next_node, _ = self.ai_mcts.get_best_child()
                ai_move = next_node.game.last_move
            else:
                # Random move as fallback
                ai_move = self.get_random_ai_move()
            
            if ai_move:
                row, col = ai_move
                self.game.fire(ai_move)
                
                # Update your board to show where AI attacked
                if self.game.state[1, 1, row, col] == 1:  # AI hit your ship
                    self.your_buttons[row][col].config(bg=self.colors['hit'], text='💥')
                    self.update_status(f"💥 AI HIT your ship at {chr(65+col)}{row+1}! Your turn.")
                else:  # AI missed
                    self.your_buttons[row][col].config(bg=self.colors['miss'], text='💧')
                    self.update_status(f"💧 AI missed at {chr(65+col)}{row+1}. Your turn!")
            
            # Check if game is over
            if self.game.score is not None:
                self.handle_game_over()
                
        except Exception as e:
            print(f"AI move error: {e}")
            # Fallback to random move
            ai_move = self.get_random_ai_move()
            if ai_move:
                self.game.fire(ai_move)
    
    def get_random_ai_move(self):
        """Get a random valid move for AI"""
        valid_moves = []
        for i in range(10):
            for j in range(10):
                if self.game.state[1, 1, i, j] == 0:  # Not yet fired
                    valid_moves.append((i, j))
        
        if valid_moves:
            return random.choice(valid_moves)
        return None
    
    def handle_game_over(self):
        """Handle game over"""
        score = self.game.score
        if score == 1:  # Human wins (we're player 1 when attacking)
            title = "🎉 Victory!"
            message = "Congratulations! You defeated the AI!"
        elif score == -1:  # AI wins
            title = "💀 Defeat!"
            message = "The AI has sunk all your ships. Better luck next time!"
        else:
            title = "🤝 Draw!"
            message = "It's a draw!"
        
        messagebox.showinfo(title, message)
        self.update_status(f"Game Over! {message}")
    
    def update_status(self, message):
        """Update the status message"""
        self.status_label.config(text=message)
    
    def update_instructions(self, message):
        """Update the instruction message"""
        self.instruction_label.config(text=message)
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()

def main():
    """Main function to start the game"""
    game = BattleshipsGUI()
    game.run()

if __name__ == "__main__":
    main()
