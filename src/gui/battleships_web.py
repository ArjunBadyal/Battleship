#!/usr/bin/env python3
"""
Web-based Battleships game using Flask
This creates a web interface that works in any environment
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
import json
import random
import numpy as np
import torch
from copy import copy
import os

# Import our game components
try:
    # Try relative imports first (when imported as module)
    from ..core.battleships import Battleships
    from ..ai import Alpha0
except ImportError:
    # Fall back to absolute imports (when run as script)
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from core.battleships import Battleships
    try:
        from ai import Alpha0
    except ImportError:
        Alpha0 = None

app = Flask(__name__, template_folder='templates')
app.secret_key = 'battleships_game_secret'

# Global game state
game_sessions = {}

class WebBattleshipsGame:
    def __init__(self, player1_type="human", player2_type="alphazero"):
        self.game = Battleships()
        self.ai_policy = None
        self.game_over = False
        self.current_player = 1  # 1 for player1, 2 for player2
        self.winner = None
        self.ships = [5, 4, 3, 3, 2]
        self.player1_type = player1_type  # "human", "alphazero", "random"
        self.player2_type = player2_type  # "human", "alphazero", "random"
        self.load_ai()
        self.setup_game()
    
    def load_ai(self):
        """Load the trained AI policy"""
        try:
            # Try to load the best model first
            model_path = os.path.join(os.path.dirname(__file__), '..', '..', 'models', 'agent_best.mypolicy')
            if Alpha0 and os.path.exists(model_path):
                self.ai_policy = torch.load(model_path, map_location='cpu', weights_only=False)
                self.ai_policy.eval()
                self.ai_status = "✅ AI Champion loaded!"
            else:
                # Fall back to current model
                model_path = os.path.join(os.path.dirname(__file__), '..', '..', 'models', 'agent_current.mypolicy')
                if Alpha0 and os.path.exists(model_path):
                    self.ai_policy = torch.load(model_path, map_location='cpu', weights_only=False)
                    self.ai_policy.eval()
                    self.ai_status = "✅ AI loaded!"
                else:
                    self.ai_status = "⚠️ AI not found - using random strategy"
        except Exception as e:
            self.ai_status = f"⚠️ AI error: {str(e)}"
    
    def setup_game(self):
        """Setup a new game with random ship placements"""
        self.game = Battleships()
        
        # Place human ships
        self.place_ships_for_player()
        # Place AI ships  
        self.place_ships_for_player()
        
        self.game_over = False
        self.current_player = 1
        self.winner = None
    
    def place_ships_for_player(self):
        """Place ships randomly for current player"""
        for attempt in range(100):
            boats = []
            directions = []
            
            for ship_length in self.ships:
                vertical = random.choice([True, False])
                directions.append(vertical)  # Use boolean directly, not integer
                
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
    
    def get_board_state(self):
        """Get current board state for frontend"""
        player1_board = []
        player2_board = []
        
        # Get sunk ships info
        player1_sunk_positions = self.get_sunk_ship_positions(player=0)  # Player 1 ships
        player2_sunk_positions = self.get_sunk_ship_positions(player=1)  # Player 2 ships
        
        for i in range(10):
            player1_row = []
            player2_row = []
            for j in range(10):
                # Player 1 board (defensive view)
                if self.game.state[1, 1, i, j] == 1:  # Player 2 hit Player 1's ship
                    if (i, j) in player1_sunk_positions:
                        player1_row.append('sunk')  # Ship is sunk
                    else:
                        player1_row.append('hit')   # Ship is hit but not sunk
                elif self.game.state[1, 1, i, j] == -1:  # Player 2 missed
                    player1_row.append('miss')
                elif self.game.state[0, 0, i, j] == 1:  # Player 1's ship (not hit yet)
                    # For AI vs AI, show ships; for human games, only show own ships
                    if self.player1_type != "human" and self.player2_type != "human":
                        player1_row.append('ship')  # Show ships in AI vs AI
                    elif self.current_player == 1:
                        player1_row.append('ship')  # Show own ships
                    else:
                        player1_row.append('water')  # Hide opponent ships
                else:
                    player1_row.append('water')
                
                # Player 2 board (defensive view)
                if self.game.state[0, 1, i, j] == 1:  # Player 1 hit Player 2's ship
                    if (i, j) in player2_sunk_positions:
                        player2_row.append('sunk')  # Ship is sunk
                    else:
                        player2_row.append('hit')   # Ship is hit but not sunk
                elif self.game.state[0, 1, i, j] == -1:  # Player 1 missed
                    player2_row.append('miss')
                elif self.game.state[1, 0, i, j] == 1:  # Player 2's ship (not hit yet)
                    # For AI vs AI, show ships; for human games, only show own ships
                    if self.player1_type != "human" and self.player2_type != "human":
                        player2_row.append('ship')  # Show ships in AI vs AI
                    elif self.current_player == 2:
                        player2_row.append('ship')  # Show own ships
                    else:
                        player2_row.append('water')  # Hide opponent ships
                else:
                    player2_row.append('water')
            
            player1_board.append(player1_row)
            player2_board.append(player2_row)
        
        return player1_board, player2_board
    
    def get_sunk_ship_positions(self, player):
        """Get positions of completely sunk ships for a player"""
        sunk_positions = set()
        
        # Get ship positions for the player
        ship_positions = self.game.ship_positions[player]
        
        # Group positions by ship
        ships_by_index = {}
        for pos, ship_idx in ship_positions.items():
            if ship_idx not in ships_by_index:
                ships_by_index[ship_idx] = []
            ships_by_index[ship_idx].append(pos)
        
        # Check each ship to see if it's completely sunk
        opponent = 1 - player  # The player doing the attacking
        for ship_idx, positions in ships_by_index.items():
            all_hit = True
            for pos in positions:
                row, col = pos
                if self.game.state[opponent, 1, row, col] != 1:  # Not hit
                    all_hit = False
                    break
            
            if all_hit:
                # This ship is completely sunk
                sunk_positions.update(positions)
        
        return sunk_positions
    
    def is_human_turn(self):
        """Check if it's a human player's turn"""
        if self.current_player == 1:
            return self.player1_type == "human"
        else:
            return self.player2_type == "human"
    
    def get_current_player_type(self):
        """Get the type of the current player"""
        if self.current_player == 1:
            return self.player1_type
        else:
            return self.player2_type
    
    def get_player_name(self, player_num):
        """Get display name for a player"""
        player_type = self.player1_type if player_num == 1 else self.player2_type
        if player_type == "human":
            return f"Player {player_num} (Human)"
        elif player_type == "alphazero":
            return f"Player {player_num} (AlphaZero AI)"
        elif player_type == "random":
            return f"Player {player_num} (Random AI)"
        return f"Player {player_num}"
    
    def make_human_move(self, row, col):
        """Make a move for a human player"""
        if self.game_over or not self.is_human_turn():
            return False, "Not your turn!"
        
        # Check if already attacked
        if self.current_player == 1:
            if self.game.state[0, 1, row, col] != 0:
                return False, "Already attacked this position!"
        else:
            if self.game.state[1, 1, row, col] != 0:
                return False, "Already attacked this position!"
        
        # Get sunk ships before the move
        opponent_player = 2 if self.current_player == 1 else 1
        enemy_sunk_before = self.get_sunk_ship_positions(player=opponent_player-1)
        
        # Make the attack
        if not self.game.fire((row, col)):
            return False, "Invalid move!"
        
        # Check if hit or miss
        if self.current_player == 1:
            hit = self.game.state[0, 1, row, col] == 1
        else:
            hit = self.game.state[1, 1, row, col] == 1
        
        # Get sunk ships after the move
        enemy_sunk_after = self.get_sunk_ship_positions(player=opponent_player-1)
        
        # Check if we sunk a new ship
        newly_sunk = enemy_sunk_after - enemy_sunk_before
        
        player_name = self.get_player_name(self.current_player)
        if newly_sunk:
            message = f"💀 {player_name} SUNK a ship at {chr(65+col)}{row+1}! Vessel destroyed!"
        elif hit:
            message = f"🎯 {player_name} HIT at {chr(65+col)}{row+1}! Keep firing!"
        else:
            message = f"💧 {player_name} missed at {chr(65+col)}{row+1}."
        
        # Check victory
        if self.check_victory():
            if self.winner == "player1":
                return True, f"🎉 VICTORY! {self.get_player_name(1)} wins!"
            else:
                return True, f"🎉 VICTORY! {self.get_player_name(2)} wins!"
        
        # Switch players
        self.current_player = 2 if self.current_player == 1 else 1
        return True, message
    
    def make_ai_move(self):
        """Make a move for the current AI player"""
        if self.game_over or self.is_human_turn():
            return False, "Not AI's turn!"
        
        current_type = self.get_current_player_type()
        
        # Get valid moves based on current player
        valid_moves = []
        for i in range(10):
            for j in range(10):
                if self.current_player == 1:
                    if self.game.state[0, 1, i, j] == 0:  # Player 1 hasn't attacked this position
                        valid_moves.append((i, j))
                else:
                    if self.game.state[1, 1, i, j] == 0:  # Player 2 hasn't attacked this position
                        valid_moves.append((i, j))
        
        if not valid_moves:
            return False, "No valid moves!"
        
        # Get sunk ships before move
        opponent_player = 2 if self.current_player == 1 else 1
        enemy_sunk_before = self.get_sunk_ship_positions(player=opponent_player-1)
        
        # Choose move based on AI type
        if current_type == "alphazero":
            ai_move = self.get_alphazero_move(valid_moves)
        else:  # random
            ai_move = random.choice(valid_moves)
        
        row, col = ai_move
        
        # Make AI attack
        if not self.game.fire(ai_move):
            return False, "AI move failed!"
        
        # Check result
        if self.current_player == 1:
            hit = self.game.state[0, 1, row, col] == 1
        else:
            hit = self.game.state[1, 1, row, col] == 1
        
        # Get sunk ships after move
        enemy_sunk_after = self.get_sunk_ship_positions(player=opponent_player-1)
        
        # Check if AI sunk a ship
        newly_sunk = enemy_sunk_after - enemy_sunk_before
        
        player_name = self.get_player_name(self.current_player)
        if newly_sunk:
            message = f"💀 {player_name} SANK a ship at {chr(65+col)}{row+1}! Vessel destroyed!"
        elif hit:
            message = f"💥 {player_name} HIT at {chr(65+col)}{row+1}!"
        else:
            message = f"💧 {player_name} missed at {chr(65+col)}{row+1}."
        
        # Check victory
        if self.check_victory():
            if self.winner == "player1":
                return True, f"🎉 VICTORY! {self.get_player_name(1)} wins!"
            else:
                return True, f"🎉 VICTORY! {self.get_player_name(2)} wins!"
        
        # Switch players
        self.current_player = 2 if self.current_player == 1 else 1
        return True, message
    
    def get_alphazero_move(self, valid_moves):
        """Get a move using AlphaZero AI"""
        if self.ai_policy:
            try:
                # Use the smart AI move as fallback for now
                return self.get_smart_ai_move(valid_moves)
            except Exception:
                return random.choice(valid_moves)
        else:
            return self.get_smart_ai_move(valid_moves)
    
    def get_smart_ai_move(self, valid_moves):
        """Get a smart AI move"""
        player_idx = 0 if self.current_player == 1 else 1
        
        # Look for hits to follow up on
        for i in range(10):
            for j in range(10):
                if self.game.state[player_idx, 1, i, j] == 1:  # Previous hit by current player
                    # Check adjacent cells
                    for di, dj in [(0,1), (0,-1), (1,0), (-1,0)]:
                        ni, nj = i + di, j + dj
                        if (0 <= ni < 10 and 0 <= nj < 10 and 
                            self.game.state[player_idx, 1, ni, nj] == 0):
                            if (ni, nj) in valid_moves:
                                return (ni, nj)
        
        # Random move
        return random.choice(valid_moves)
    
    def check_victory(self):
        """Check if game is over by counting sunk ships"""
        total_ships = len(self.ships)  # 5 ships total
        
        player1_sunk_ships = self.count_sunk_ships(player=1)  # Ships player 1 sunk
        player2_sunk_ships = self.count_sunk_ships(player=0)  # Ships player 2 sunk
        
        if player1_sunk_ships >= total_ships:
            self.game_over = True
            self.winner = "player1"
            return True
        elif player2_sunk_ships >= total_ships:
            self.game_over = True
            self.winner = "player2"
            return True
        return False
    
    def get_stats(self):
        """Get game statistics"""
        player1_hits = int(np.sum(self.game.state[0, 1] == 1))
        player2_hits = int(np.sum(self.game.state[1, 1] == 1))
        
        # Count sunk ships
        player1_sunk_ships = self.count_sunk_ships(player=1)  # Ships player 1 sunk
        player2_sunk_ships = self.count_sunk_ships(player=0)  # Ships player 2 sunk
        
        return {
            'player1_hits': player1_hits,
            'player2_hits': player2_hits,
            'player1_sunk_ships': player1_sunk_ships,
            'player2_sunk_ships': player2_sunk_ships,
            'player1_name': self.get_player_name(1),
            'player2_name': self.get_player_name(2),
            'current_player': self.current_player,
            'current_player_name': self.get_player_name(self.current_player),
            'total_targets': sum(self.ships),
            'total_ships': len(self.ships),
            'game_over': self.game_over,
            'winner': self.winner,
            'is_human_turn': self.is_human_turn(),
            'ai_status': self.ai_status
        }
    
    def count_sunk_ships(self, player):
        """Count the number of completely sunk ships for a player"""
        # Get ship positions for the player
        ship_positions = self.game.ship_positions[player]
        
        # Group positions by ship
        ships_by_index = {}
        for pos, ship_idx in ship_positions.items():
            if ship_idx not in ships_by_index:
                ships_by_index[ship_idx] = []
            ships_by_index[ship_idx].append(pos)
        
        # Count completely sunk ships
        opponent = 1 - player  # The player doing the attacking
        sunk_count = 0
        
        for ship_idx, positions in ships_by_index.items():
            all_hit = True
            for pos in positions:
                row, col = pos
                if self.game.state[opponent, 1, row, col] != 1:  # Not hit
                    all_hit = False
                    break
            
            if all_hit:
                sunk_count += 1
        
        return sunk_count

@app.route('/')
def index():
    """Main menu page"""
    return render_template('menu.html')

@app.route('/game')
def game():
    """Game page"""
    return render_template('battleships.html')

@app.route('/api/new_game', methods=['POST'])
def new_game():
    """Start a new game with specified player types"""
    session_id = request.remote_addr
    
    data = request.get_json() if request.is_json else {}
    player1_type = data.get('player1_type', 'human')
    player2_type = data.get('player2_type', 'alphazero')
    
    game_sessions[session_id] = WebBattleshipsGame(player1_type, player2_type)
    
    game = game_sessions[session_id]
    your_board, enemy_board = game.get_board_state()
    stats = game.get_stats()
    
    return jsonify({
        'success': True,
        'your_board': your_board,
        'enemy_board': enemy_board,
        'stats': stats,
        'message': f"🚢 New battle ready! {stats['current_player_name']}'s turn."
    })

@app.route('/api/ai_move', methods=['POST'])
def ai_move():
    """Make an AI move (for AI vs AI games or when it's AI's turn)"""
    session_id = request.remote_addr
    if session_id not in game_sessions:
        return jsonify({'success': False, 'message': 'No active game!'})
    
    game = game_sessions[session_id]
    
    if game.game_over:
        return jsonify({'success': False, 'message': 'Game is over!'})
    
    if game.is_human_turn():
        return jsonify({'success': False, 'message': 'It\'s a human player\'s turn!'})
    
    success, message = game.make_ai_move()
    
    if not success:
        return jsonify({'success': False, 'message': message})
    
    your_board, enemy_board = game.get_board_state()
    stats = game.get_stats()
    
    return jsonify({
        'success': True,
        'your_board': your_board,
        'enemy_board': enemy_board,
        'stats': stats,
        'message': message
    })

@app.route('/api/attack', methods=['POST'])
def attack():
    """Handle human attack"""
    session_id = request.remote_addr
    if session_id not in game_sessions:
        return jsonify({'success': False, 'message': 'No active game!'})
    
    data = request.get_json()
    row, col = data['row'], data['col']
    
    game = game_sessions[session_id]
    success, message = game.make_human_move(row, col)
    
    if not success:
        return jsonify({'success': False, 'message': message})
    
    your_board, enemy_board = game.get_board_state()
    stats = game.get_stats()
    
    response = {
        'success': True,
        'your_board': your_board,
        'enemy_board': enemy_board,
        'stats': stats,
        'message': message
    }
    
    # If game is over, don't make AI move
    if game.game_over:
        return jsonify(response)
    
    # If next player is AI, make AI move automatically
    if not game.is_human_turn():
        ai_success, ai_message = game.make_ai_move()
        if ai_success:
            your_board, enemy_board = game.get_board_state()
            stats = game.get_stats()
            response.update({
                'your_board': your_board,
                'enemy_board': enemy_board,
                'stats': stats,
                'ai_message': ai_message
            })
    
    return jsonify(response)

@app.route('/api/status')
def status():
    """Get current game status"""
    session_id = request.remote_addr
    if session_id not in game_sessions:
        return jsonify({'success': False, 'message': 'No active game!'})
    
    game = game_sessions[session_id]
    your_board, enemy_board = game.get_board_state()
    stats = game.get_stats()
    
    return jsonify({
        'success': True,
        'your_board': your_board,
        'enemy_board': enemy_board,
        'stats': stats
    })

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    print("🚢 Starting Battleships Web Server...")
    print("🌐 Open your browser and go to: http://localhost:5000")
    print("🎯 Click enemy waters to attack!")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
