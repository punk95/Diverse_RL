import numpy as np
import torch
import sys



from util.collect_trajectories import collect_data
from model import DiscretePolicyNN, NN_Paramters, Discrete_Q_Function_NN
from env.gridworld.environments import GridWalk
from env.gridworld.optimal_policy import Optim_Policy_Gridwalk
from util.density_ratio import get_policy_ratio
from env.gridworld.sub_optimal_policy import Sub_Optim_Policy_Gridwalk
from dual_dice import Dice, Algo_Param
from dual_dice_eval_buffer import Dice_Eval_Buffer


from util.count_frequency import collect_freqency
from util.q_learning_to_policy import Q_learner_Policy


policy_param = NN_Paramters(state_dim=2, action_dim=5, hidden_layer_dim=[6, 6], non_linearity=torch.tanh, device= torch.device("cpu"))
nu_param = NN_Paramters(state_dim=2, action_dim=5, hidden_layer_dim=[6, 6], non_linearity=torch.tanh, device=torch.device("cpu"), l_r=0.0001)
algo_param = Algo_Param()
algo_param.gamma = 0.995


grid_size = 10
env = GridWalk(grid_size, False)




V = Dice_Eval_Buffer(nu_param, algo_param)

Buffer2 = torch.load("Q_models/behaviour_buffer_1")
Buffer1 = torch.load("Q_models/behaviour_buffer_3")


no_iterations = 30000


for i in range(no_iterations):

    data1 = Buffer1.sample(400)
    data2 = Buffer2.sample(400)
    V.train_dice(data1, data2)

    if i % 1000 == 0:
        print(i)

        print(V.debug())
        V.nu_network.save("nu_eval_buff/dice/nu_3")