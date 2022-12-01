import torch
import numpy as np
from NeuralNet import *
import collections
import random

# Tuple w. attributes
Transition = collections.namedtuple('Transition', ('state', 'action', 'next_state', 'reward', 'done_flag'))


# Memory representation for our agent
class ReplayMemory(object):
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.memory = collections.deque(maxlen=capacity)

    def push(self, state: torch.Tensor, action,
             next_state: torch.Tensor, reward: float, done_flag: bool):
        self.memory.append(Transition(state=state, action=action,
                                      next_state=next_state, reward=reward,
                                      done_flag=done_flag))

    def sample(self, batch_size: int):
        return random.sample(self.memory, batch_size)

    def __len__(self) -> int:
        return len(self.memory)


class Agent:
    def __init__(self, gamma: float, exploration_rate: float, lr: float, input_size: int,
                 batch_size: int, nr_actions: int, max_mem_size: int = 10000, nr_consecutive_frames: int = 4,
                 exploration_rate_min: float = 0.01, exploration_decay_rate: float = 5e-4, seed: int = 0):

        self.seed = seed
        torch.manual_seed(self.seed)
        random.seed(self.seed)

        # ------ Setting Hyper parameters ------ #
        self.gamma = gamma
        self.exploration_rate = exploration_rate
        self.exploration_rate_min = exploration_rate_min
        self.exploration_decay_rate = exploration_decay_rate
        self.exploration_rate_init = exploration_rate
        self.nr_consecutive_frames = nr_consecutive_frames
        self.mem_size = max_mem_size
        self.batch_size = batch_size
        self.lr = lr

        # ------ Setting Game characteristics ------ #
        self.nr_actions = nr_actions
        self.input_size = input_size
        self.action_space = [action for action in range(self.nr_actions)]

        # ------ Defining Neural nets ------ #
        self.policy_network = DeepQNetwork(lr=self.lr, input_size=self.input_size, nr_actions=self.nr_actions,
                                           nr_consecutive_frames=self.nr_consecutive_frames, seed=self.seed)
        self.target_network = DeepQNetwork(lr=self.lr, input_size=self.input_size, nr_actions=self.nr_actions,
                                           nr_consecutive_frames=self.nr_consecutive_frames, seed=self.seed)

        self.align_networks()  # Initially setting target params = policy params

        # ------ Defining memory ------ #
        self.memory = ReplayMemory(capacity=self.mem_size)

        # ------ Defining optimizer and loss function ------ #
        self.optimizer = torch.optim.Adam(self.policy_network.parameters(), lr=self.lr)

        self.loss_func = torch.nn.MSELoss() # Mean squared error (squared L2 norm)
        # self.loss_func = torch.nn.HuberLoss(delta=1.0)  # Smooth L1 for delta = 1.0
        self.device = self.policy_network.device

    @staticmethod
    def stretched_exponential(_episode, nr_episodes, eps_0, eps_min,
                              A=0.5, B=0.1, C=0.1):
        """https://medium.com/analytics-vidhya/stretched-exponential-decay-function-for-epsilon-greedy-algorithm-98da6224c22f"""
        standardized_time = (_episode - A * nr_episodes) / (B * nr_episodes)
        cosh = np.cosh(np.exp(-standardized_time))
        epsilon = eps_min + (eps_0 - eps_min) * (1.0 - (1.0 / cosh + (_episode * C / nr_episodes)))
        if epsilon > eps_min:
            return epsilon
        else:
            return eps_min

    @staticmethod
    def stretched_exponential_view(_episode, nr_episodes, eps_0, eps_min,
                                   A=0.5, B=0.1, C=0.1):
        """https://medium.com/analytics-vidhya/stretched-exponential-decay-function-for-epsilon-greedy-algorithm-98da6224c22f"""
        standardized_time = (_episode - A * nr_episodes) / (B * nr_episodes)
        cosh = np.cosh(np.exp(-standardized_time))
        epsilon = eps_min + (eps_0 - eps_min) * (1.0 - (1.0 / cosh + (_episode * C / nr_episodes)))
        return epsilon

    @staticmethod
    def linear(_episode, current_rate, eps_0, eps_min, decay_rate):
        if current_rate > eps_min:
            return eps_0 - decay_rate * _episode
        else:
            return eps_min

    @staticmethod
    def linear_view(_episode, eps_0, decay_rate):
        return eps_0 - decay_rate * _episode

    def linear_decay(self, episode):
        if self.exploration_rate > self.exploration_rate_min:
            return self.exploration_rate_init - self.exploration_decay_rate * episode
        else:
            return self.exploration_rate_min

    def exponential_decay(self, episode):
        return self.exploration_rate_min + (self.exploration_rate_init - self.exploration_rate_min) * np.exp(-episode*self.exploration_decay_rate)

    def align_networks(self) -> None:
        # Copying weights from policy net to target net
        self.target_network.load_state_dict(self.policy_network.state_dict())
        self.target_network.eval()

    def store_transition(self, state: torch.Tensor, action,
                         reward: float, new_state: torch.Tensor, done_flag: bool) -> None:

        # Storing transition in memory
        self.memory.push(state=state, action=action, next_state=new_state,
                         reward=reward, done_flag=done_flag)

    def choose_action(self, observation: torch.Tensor):
        assert type(observation) is torch.Tensor, f'Observation should be torch tensor but is: {type(observation)}.'
        if torch.rand(1).item() > self.exploration_rate:
            # Exploitation (relying on Q value)
            actions = self.policy_network.forward(observation)
            best_action = torch.argmax(actions).item()
            return best_action
        else:
            # Exploration (random action)
            rng_index = torch.randint(low=0, high=self.nr_actions, size=(1,)).item()
            random_action = self.action_space[rng_index]
            return random_action

    def update_exploration_rate(self,episode):
        """ Decreasing epsilon linearly"""
        #self.exploration_rate = self.linear_decay(episode=episode)
        self.exploration_rate = self.exponential_decay(episode=episode)

    def sample_memory(self):
        """ For collecting all state items in batch in torch tensors (batch_size, nr_channels, height, width)
            and rest in normal 1D tensor."""
        random_batch = self.memory.sample(batch_size=self.batch_size)
        grouped_transitions = Transition(*zip(*random_batch))

        state_batch = torch.cat(grouped_transitions.state).to(self.device)
        action_batch = torch.tensor(list(grouped_transitions.action)).reshape(-1, 1).to(self.device)  # To get column vector
        reward_batch = torch.tensor(list(grouped_transitions.reward)).reshape(-1, 1).to(self.device)  # To get column vector
        new_state_batch = torch.cat(grouped_transitions.next_state).to(self.device)
        terminal_batch = torch.tensor(list(grouped_transitions.done_flag)).reshape(-1, 1).to(self.device)  # To get column vector

        return state_batch, action_batch, reward_batch, new_state_batch, terminal_batch

    def learn(self,episode):
        """ first beginning learning process when
        non-zero memory is at least batch_size. """
        if self.memory.__len__() >= self.batch_size:
            # Getting memory samples
            state_batch, action_batch, reward_batch, new_state_batch, terminal_batch = self.sample_memory()

            # Calculating target Q values
            target_q_values = self.target_network.forward(new_state_batch)

            # Picking out max values for each
            max_target_q_values = torch.max(target_q_values, dim=1, keepdim=True).values

            # Calculating y_j according to "Algorithm 1: deep Q-learning with experience replay." in original paper
            target_q_values = reward_batch + self.gamma * max_target_q_values
            target_q_values[terminal_batch] = 0.0

            # Calculating all Q values
            q_values = self.policy_network(state_batch)

            # Taking out the ones corresponding to the action taken
            q_values = torch.gather(input=q_values, dim=1, index=action_batch)

            # Calculating loss
            loss = self.loss_func(q_values, target_q_values)

            # Gradient descent step
            self.optimizer.zero_grad()  # Clearing buffer
            loss.backward()
            self.optimizer.step()

            # Updating exploration rate
            self.update_exploration_rate(episode=episode)