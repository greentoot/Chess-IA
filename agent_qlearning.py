import random
import numpy as np
import pickle

class QLearningAgent:
    def __init__(self, alpha=0.1, gamma=0.99, epsilon=0.2):
        self.q_table = {}  
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon

    def get_state_key(self, board, color_board, current_player):
        return tuple(board.flatten()), tuple(color_board.flatten()), current_player

    def choose_action(self, state, valid_actions):
        state_key = self.get_state_key(*state)

        if not valid_actions:
            return None  

        if random.random() < self.epsilon:
            return random.choice(valid_actions)

        q_values = [self.q_table.get((state_key, a), 0) for a in valid_actions]
        max_q = max(q_values)
        best_actions = [a for a, q in zip(valid_actions, q_values) if q == max_q]
        return random.choice(best_actions)


    def learn(self, state, action, reward, next_state, done, valid_next_actions):
        state_key = self.get_state_key(*state)
        next_key = self.get_state_key(*next_state)

        q_sa = self.q_table.get((state_key, action), 0)

        if done:
            target = reward
        else:
            next_qs = [self.q_table.get((next_key, a), 0) for a in valid_next_actions]
            target = reward + self.gamma * max(next_qs, default=0)

        self.q_table[(state_key, action)] = q_sa + self.alpha * (target - q_sa)

    def save(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self.q_table, f)

    def load(self, filename):
        with open(filename, 'rb') as f:
            self.q_table = pickle.load(f)



#Q(s,a)←Q(s,a)+α⋅(target−Q(s,a))