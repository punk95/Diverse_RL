from model import Nu_NN
import torch
import numpy as np


class Algo_Param():
    def __init__(self, gamma=0.9):
        self.gamma = gamma


class Dice_Eval_Buffer():

    def __init__(self, nu_param, algo_param, deterministic_env=True, averege_next_nu = True,
                 discrete_policy=True, save_path = "temp", load_path="temp" ):

        self.nu_param = nu_param
        self.algo_param = algo_param


        self.nu_network = Nu_NN(nu_param, save_path=save_path, load_path=load_path)
        self.nu_optimizer = torch.optim.Adam(self.nu_network.parameters(), lr=self.nu_param.l_r)


        #
        self.f = lambda x: torch.abs(x)**2/2

    def train_dice(self, data1, data2):

        self.debug_V = {"x**2":None, "linear": None}
        state1 = data1.state
        action1 = data1.action

        state2 = data2.state
        action2 = data2.action

        weight1 = torch.Tensor(self.algo_param.gamma ** data1.time_step).to(self.nu_param.device)
        weight2 = torch.Tensor(self.algo_param.gamma ** data2.time_step).to(self.nu_param.device)

        # reshaping the weight tensor to facilitate the elmentwise multiplication operation
        no_data1 = weight1.size()[0]
        no_data2 = weight2.size()[0]

        weight1 = torch.reshape(weight1, [no_data1, 1])
        weight2 = torch.reshape(weight2, [no_data2, 1])

        nu1 = self.nu_network(state1, action1)
        nu2 = self.nu_network(state2, action2)

        unweighted_nu_loss_1 = self.f(nu1)
        unweighted_nu_loss_2 = nu2

        loss_1 = torch.sum(weight1 * unweighted_nu_loss_1) / torch.sum(weight1)
        loss_2 = torch.sum(weight2 * unweighted_nu_loss_2) / torch.sum(weight2)

        self.debug_V["x**2"] = torch.sum(weight1*unweighted_nu_loss_1)/torch.sum(weight1)
        self.debug_V["linear"] = loss_2


        loss = loss_1 - loss_2

        self.nu_optimizer.zero_grad()
        loss.backward()
        self.nu_optimizer.step()

    def debug(self):
        return self.debug_V["x**2"], self.debug_V["linear"]


    def get_state_action_density_ratio(self, data):

        nu = self.nu_network(data.state, data.action)
        return nu



