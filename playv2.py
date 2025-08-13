from env_minichess import MiniChessEnv6x6
from agent_qlearning import QLearningAgent

agent_white = QLearningAgent()
agent_black = QLearningAgent()

episodes = 100000000

for episode in range(1, episodes + 1):
    env = MiniChessEnv6x6()
    state = env.get_state()
    done = False
    turn = 0

    while not done:
        valid_moves = env.get_valid_moves()
        if not valid_moves:
            print("Aucun coup possible, match nul.")
            break

        agent = agent_white if state[2] == 1 else agent_black
        action = agent.choose_action(state, valid_moves)
        next_state, reward, done = env.step(action)

        next_valid_moves = env.get_valid_moves() if not done else []
        agent.learn(state, action, reward, next_state, done, next_valid_moves)

        state = next_state
        turn += 1

    if episode == episodes:
        print(f"Episode {episode} terminé en {turn} tours.")
        agent_white.save("model/white_agent.pkl")
        agent_black.save("model/black_agent.pkl")
