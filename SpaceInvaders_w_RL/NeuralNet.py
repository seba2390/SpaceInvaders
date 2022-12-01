import torch


class DeepQNetwork(torch.nn.Module):
    def __init__(self, lr: float, input_size: int,
                 nr_actions: int, nr_consecutive_frames: int = 1, seed: int = 0):
        super(DeepQNetwork, self).__init__()

        self.seed = seed  # For rng reproducibility
        torch.manual_seed(self.seed)

        self.lr = lr
        self.input_size = input_size
        self.nr_actions = nr_actions
        self.nr_consecutive_frames = nr_consecutive_frames

        # ----------- Defining Layers in Neural Net ------------ #
        self.lin1 = torch.nn.Linear(in_features=self.input_size, out_features=self.input_size*20)
        self.lin2 = torch.nn.Linear(in_features=self.input_size*20, out_features=self.nr_actions)
        self.rectifier = torch.nn.ReLU()

        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        print("Using device: ", self.device.type)
        self.to(self.device)

    def forward(self, state: torch.Tensor) -> torch.Tensor:
        state = state.to(self.device)
        state = self.rectifier(self.lin1(state))
        state = self.lin2(state)
        return state