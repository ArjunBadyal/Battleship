#!/usr/bin/env python3
"""
Enhanced Battleships GUI with AI integration
Beautiful interface with clickable boards and smart AI opponent
"""

import tkinter as tk
from tkinter import messagebox, ttk
import numpy as np
import torch
import random
from copy import copy
import time

# Import our game components
from battleships import Battleships
try:
    import Alpha0
    import MCTS
except ImportError:
    print("Warning: Alpha0 or MCTS not available, using random AI")

class BattleshipsGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🚢 Battleships - Human vs AI")
        self.root.geometry("1000x700")
        self.root.configure(bg='#1a252f')
        self.root.resizable(False, False)
        
        # Game state
        self.game = None
        self.ai_policy = None
        self.game_over = False
        self.human_turn = True
        
        # Board configuration
        self.board_size = 10
        self.cell_size = 35
        self.ships = [5, 4, 3, 3, 2]
        
        # Colors and styling
        self.colors = {
            'water': '#2980b9',
            'ship': '#34495e', 
            'hit': '#e74c3c',
            'miss': '#7f8c8d',
            'unknown': '#5d6d7e',
            'bg_primary': '#1a252f',
            'bg_secondary': '#2c3e50',
            'text_primary': '#ecf0f1',
            'text_secondary': '#bdc3c7',
            'accent': '#3498db'
        }
        
        self.setup_ui()
        self.load_ai()
        self.new_game()
        
    def setup_ui(self):
        """Create the user interface"""
        # Main title
        title_frame = tk.Frame(self.root, bg=self.colors['bg_primary'])
        title_frame.pack(fill='x', pady=10)
        
        title_label = tk.Label(title_frame, text="🚢 BATTLESHIPS", 
                              font=('Arial Black', 24), 
                              bg=self.colors['bg_primary'], 
                              fg=self.colors['text_primary'])
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame, text="Human vs AlphaZero AI", 
                                 font=('Arial', 12), 
                                 bg=self.colors['bg_primary'], 
                                 fg=self.colors['text_secondary'])
        subtitle_label.pack()
        
        # Main game area
        main_frame = tk.Frame(self.root, bg=self.colors['bg_primary'])
        main_frame.pack(expand=True, fill='both', padx=20, pady=10)
        
        # Left side - Your Fleet
        left_panel = tk.Frame(main_frame, bg=self.colors['bg_secondary'], relief='raised', bd=3)
        left_panel.pack(side='left', padx=10, pady=5, fill='both', expand=True)
        
        your_title = tk.Label(left_panel, text="🏠 YOUR FLEET", 
                             font=('Arial', 14, 'bold'),
                             bg=self.colors['bg_secondary'], 
                             fg=self.colors['text_primary'])
        your_title.pack(pady=8)
        
        self.your_board_frame = tk.Frame(left_panel, bg=self.colors['bg_secondary'])
        self.your_board_frame.pack(pady=10)
        
        # Right side - Enemy Waters  
        right_panel = tk.Frame(main_frame, bg=self.colors['bg_secondary'], relief='raised', bd=3)
        right_panel.pack(side='right', padx=10, pady=5, fill='both', expand=True)
        
        enemy_title = tk.Label(right_panel, text="🎯 ENEMY WATERS", 
                              font=('Arial', 14, 'bold'),
                              bg=self.colors['bg_secondary'], 
                              fg=self.colors['text_primary'])
        enemy_title.pack(pady=8)
        
        self.enemy_board_frame = tk.Frame(right_panel, bg=self.colors['bg_secondary'])
        self.enemy_board_frame.pack(pady=10)
        
        # Bottom status and controls
        bottom_frame = tk.Frame(self.root, bg=self.colors['bg_primary'])
        bottom_frame.pack(side='bottom', fill='x', pady=10)
        
        # Status display
        self.status_label = tk.Label(bottom_frame, text="Initializing game...", 
                                    font=('Arial', 11, 'bold'),
                                    bg=self.colors['bg_primary'], 
                                    fg=self.colors['accent'],
                                    wraplength=800)
        self.status_label.pack(pady=5)
        
        # Game stats
        stats_frame = tk.Frame(bottom_frame, bg=self.colors['bg_primary'])
        stats_frame.pack(pady=5)
        
        self.human_hits_label = tk.Label(stats_frame, text="Your Hits: 0", 
                                        font=('Arial', 10),
                                        bg=self.colors['bg_primary'], 
                                        fg=self.colors['text_secondary'])
        self.human_hits_label.pack(side='left', padx=20)
        
        self.ai_hits_label = tk.Label(stats_frame, text="AI Hits: 0", 
                                     font=('Arial', 10),
                                     bg=self.colors['bg_primary'], 
                                     fg=self.colors['text_secondary'])
        self.ai_hits_label.pack(side='right', padx=20)
        
        # Control buttons
        button_frame = tk.Frame(bottom_frame, bg=self.colors['bg_primary'])
        button_frame.pack(pady=8)
        
        self.new_game_btn = tk.Button(button_frame, text="🆕 New Game", 
                                     command=self.new_game,
                                     bg=self.colors['accent'], fg='white',
                                     font=('Arial', 10, 'bold'),
                                     padx=20, pady=5,
                                     relief='raised', bd=2)
        self.new_game_btn.pack(side='left', padx=5)
        
        self.hint_btn = tk.Button(button_frame, text="💡 Hint", 
                                 command=self.show_hint,
                                 bg='#f39c12', fg='white',
                                 font=('Arial', 10, 'bold'),
                                 padx=20, pady=5,
                                 relief='raised', bd=2)
        self.hint_btn.pack(side='left', padx=5)
        
        self.create_boards()
        
    def create_boards(self):
        """Create the game boards with coordinate labels"""
        # Clear existing boards
        for widget in self.your_board_frame.winfo_children():
            widget.destroy()
        for widget in self.enemy_board_frame.winfo_children():
            widget.destroy()
        
        # Create grid frames
        your_grid = tk.Frame(self.your_board_frame, bg=self.colors['bg_secondary'])
        your_grid.pack()
        
        enemy_grid = tk.Frame(self.enemy_board_frame, bg=self.colors['bg_secondary'])
        enemy_grid.pack()
        
        # Column headers (A-J)
        tk.Label(your_grid, text="", width=2, bg=self.colors['bg_secondary']).grid(row=0, column=0)
        tk.Label(enemy_grid, text="", width=2, bg=self.colors['bg_secondary']).grid(row=0, column=0)
        
        for j in range(self.board_size):
            tk.Label(your_grid, text=chr(65+j), font=('Arial', 9, 'bold'),
                    bg=self.colors['bg_secondary'], fg=self.colors['text_secondary'], width=3).grid(row=0, column=j+1)
            tk.Label(enemy_grid, text=chr(65+j), font=('Arial', 9, 'bold'),
                    bg=self.colors['bg_secondary'], fg=self.colors['text_secondary'], width=3).grid(row=0, column=j+1)
        
        # Row headers and buttons
        self.your_buttons = []
        self.enemy_buttons = []
        
        for i in range(self.board_size):
            # Row numbers
            tk.Label(your_grid, text=str(i+1), font=('Arial', 9, 'bold'),
                    bg=self.colors['bg_secondary'], fg=self.colors['text_secondary'], width=2).grid(row=i+1, column=0)
            tk.Label(enemy_grid, text=str(i+1), font=('Arial', 9, 'bold'),
                    bg=self.colors['bg_secondary'], fg=self.colors['text_secondary'], width=2).grid(row=i+1, column=0)
            
            your_row = []
            enemy_row = []
            
            for j in range(self.board_size):
                # Your board (defensive)
                your_btn = tk.Button(your_grid, width=3, height=1,
                                   bg=self.colors['water'], 
                                   state='disabled',
                                   relief='raised', bd=1)
                your_btn.grid(row=i+1, column=j+1, padx=1, pady=1)
                your_row.append(your_btn)
                
                # Enemy board (offensive)
                enemy_btn = tk.Button(enemy_grid, width=3, height=1,
                                    bg=self.colors['unknown'],
                                    command=lambda r=i, c=j: self.attack(r, c),
                                    relief='raised', bd=1)
                enemy_btn.grid(row=i+1, column=j+1, padx=1, pady=1)
                enemy_row.append(enemy_btn)
                
            self.your_buttons.append(your_row)
            self.enemy_buttons.append(enemy_row)
    
    def load_ai(self):
        """Load the trained AI policy"""
        try:
            self.ai_policy = torch.load('6-6-4-pie-0.mypolicy', map_location='cpu')
            self.ai_policy.eval()
            self.update_status("✅ AI Champion loaded and ready for battle!")
        except Exception as e:
            self.update_status("⚠️ AI not found - using random strategy")
            self.ai_policy = None
    
    def new_game(self):
        """Start a new game"""
        self.game = Battleships()
        self.game_over = False
        self.human_turn = True
        
        # Reset UI
        self.update_status("🚢 Setting up the battlefield...")
        self.reset_boards()
        self.update_stats()
        
        # Place ships automatically
        self.root.after(500, self.setup_ships)
    
    def reset_boards(self):
        """Reset all board buttons to default state"""
        for i in range(self.board_size):
            for j in range(self.board_size):
                # Reset your board
                self.your_buttons[i][j].config(
                    bg=self.colors['water'], 
                    text='',
                    state='disabled'
                )
                # Reset enemy board
                self.enemy_buttons[i][j].config(
                    bg=self.colors['unknown'], 
                    text='',
                    state='normal'
                )
    
    def setup_ships(self):
        """Automatically place ships for both players"""
        # Place human ships
        if self.place_ships_for_player():
            self.display_human_ships()
            # Place AI ships
            if self.place_ships_for_player():
                self.update_status("⚔️ Battle stations! Click on enemy waters to attack.")
                return
        
        # If ship placement failed, try again
        self.update_status("❌ Ship placement failed. Retrying...")
        self.root.after(1000, self.setup_ships)
    
    def place_ships_for_player(self):
        """Place ships for current player"""
        for attempt in range(100):
            boats = []
            directions = []
            
            for ship_length in self.ships:
                vertical = random.choice([True, False])
                directions.append(vertical)
                
                if vertical:
                    x = random.randint(0, 9)
                    y = random.randint(0, 10 - ship_length)
                else:
                    x = random.randint(0, 10 - ship_length) 
                    y = random.randint(0, 9)
                
                boats.append((x, y))
            
            if self.game.place(boats, directions):
                return True
        
        return False
    
    def display_human_ships(self):
        """Display human ships on the defensive board"""
        for i in range(10):
            for j in range(10):
                if self.game.state[0, 0, i, j] == 1:  # Human ship
                    self.your_buttons[i][j].config(
                        bg=self.colors['ship'], 
                        text='⚓',
                        fg='white'
                    )
    
    def attack(self, row, col):
        """Handle human attack on enemy board"""
        if self.game_over or not self.human_turn:
            return
        
        # Check if position already attacked
        if self.enemy_buttons[row][col]['text'] != '':
            self.update_status("⚠️ You've already attacked this position!")
            return
        
        # Make the attack
        if not self.game.fire((row, col)):
            self.update_status("❌ Invalid attack!")
            return
        
        # Update enemy board based on result
        if self.game.state[0, 1, row, col] == 1:  # Hit
            self.enemy_buttons[row][col].config(
                bg=self.colors['hit'], 
                text='💥',
                state='disabled'
            )
            self.update_status(f"🎯 DIRECT HIT at {chr(65+col)}{row+1}! Excellent shooting!")
        else:  # Miss
            self.enemy_buttons[row][col].config(
                bg=self.colors['miss'], 
                text='💧',
                state='disabled'
            )
            self.update_status(f"💧 Splash at {chr(65+col)}{row+1}. AI's turn...")
        
        self.update_stats()
        
        # Check win condition
        if self.check_victory():
            return
        
        # AI turn
        self.human_turn = False
        self.root.after(1500, self.ai_attack)
    
    def ai_attack(self):
        """Handle AI attack"""
        if self.game_over:
            return
        
        # Get AI move
        ai_move = self.get_ai_move()
        if not ai_move:
            return
        
        row, col = ai_move
        
        # Make AI attack
        if not self.game.fire(ai_move):
            self.human_turn = True
            return
        
        # Update your board
        if self.game.state[1, 1, row, col] == 1:  # AI hit your ship
            self.your_buttons[row][col].config(
                bg=self.colors['hit'], 
                text='💥'
            )
            self.update_status(f"💥 AI HITS your ship at {chr(65+col)}{row+1}! Brace for impact!")
        else:  # AI missed
            self.your_buttons[row][col].config(
                bg=self.colors['miss'], 
                text='💧'
            )
            self.update_status(f"💧 AI misses at {chr(65+col)}{row+1}. Your turn to strike back!")
        
        self.update_stats()
        
        # Check win condition
        if self.check_victory():
            return
        
        # Back to human turn
        self.human_turn = True
    
    def get_ai_move(self):
        """Get AI move (smart or random)"""
        # Find valid moves
        valid_moves = []
        for i in range(10):
            for j in range(10):
                if self.game.state[1, 1, i, j] == 0:  # Not yet attacked by AI
                    valid_moves.append((i, j))
        
        if not valid_moves:
            return None
        
        # Use smart AI if available, otherwise random
        if self.ai_policy:
            try:
                # Simple greedy strategy: look for hits to follow up on
                for i in range(10):
                    for j in range(10):
                        if self.game.state[1, 1, i, j] == 1:  # Previous hit
                            # Check adjacent cells
                            for di, dj in [(0,1), (0,-1), (1,0), (-1,0)]:
                                ni, nj = i + di, j + dj
                                if (0 <= ni < 10 and 0 <= nj < 10 and 
                                    self.game.state[1, 1, ni, nj] == 0):
                                    return (ni, nj)
            except:
                pass
        
        # Fallback to random
        return random.choice(valid_moves)
    
    def check_victory(self):
        """Check if game is over and handle victory"""
        total_ship_cells = sum(self.ships)  # 17
        
        human_hits = np.sum(self.game.state[0, 1] == 1)
        ai_hits = np.sum(self.game.state[1, 1] == 1)
        
        if human_hits >= total_ship_cells:
            self.game_over = True
            self.update_status("🎉 VICTORY! You've sunk the enemy fleet!")
            messagebox.showinfo("🎉 VICTORY!", 
                              "Congratulations, Admiral! You've successfully sunk the entire enemy fleet!")
            self.disable_enemy_board()
            return True
        elif ai_hits >= total_ship_cells:
            self.game_over = True
            self.update_status("💀 DEFEAT! The AI has sunk your entire fleet!")
            messagebox.showinfo("💀 DEFEAT!", 
                              "The AI has proven superior this time. Your fleet has been destroyed!")
            self.disable_enemy_board()
            return True
        
        return False
    
    def disable_enemy_board(self):
        """Disable all enemy board buttons"""
        for i in range(10):
            for j in range(10):
                self.enemy_buttons[i][j].config(state='disabled')
    
    def update_stats(self):
        """Update the game statistics display"""
        if self.game:
            human_hits = np.sum(self.game.state[0, 1] == 1)
            ai_hits = np.sum(self.game.state[1, 1] == 1)
            
            self.human_hits_label.config(text=f"Your Hits: {human_hits}/17")
            self.ai_hits_label.config(text=f"AI Hits: {ai_hits}/17")
    
    def update_status(self, message):
        """Update the status message"""
        self.status_label.config(text=message)
    
    def show_hint(self):
        """Show a helpful hint"""
        if self.game_over:
            messagebox.showinfo("💡 Hint", "Start a new game to continue playing!")
            return
        
        hints = [
            "🎯 Look for patterns in your hits to find ship orientations!",
            "🚢 Ships can't be placed diagonally - they're horizontal or vertical.",
            "💡 After a hit, try attacking adjacent squares systematically.",
            "⚓ Each fleet has: 1 Carrier (5), 1 Battleship (4), 2 Cruisers (3), 1 Destroyer (2)",
            "🔍 Ships cannot touch each other, not even diagonally.",
            "💪 Keep track of which areas you've cleared completely!"
        ]
        
        messagebox.showinfo("💡 Tactical Hint", random.choice(hints))
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

def main():
    """Main entry point"""
    try:
        game = BattleshipsGame()
        game.run()
    except Exception as e:
        print(f"Error starting game: {e}")
        messagebox.showerror("Error", f"Could not start game: {e}")

if __name__ == "__main__":
    main()
