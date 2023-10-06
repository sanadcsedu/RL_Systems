# import gym
from environment import environment
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.distributions import Categorical
import torch.multiprocessing as mp
import time
import numpy as np 
import pdb
import os

# Hyperparameters
n_train_processes = 3
learning_rate = 0.0002
update_interval = 5
gamma = 0.98
max_train_ep = 2000
max_test_ep = 501


class ActorCritic(nn.Module):
    def __init__(self):
        super(ActorCritic, self).__init__()
        self.fc1 = nn.Linear(47, 128)
        self.fc_pi = nn.Linear(128, 64)
        self.fc_v = nn.Linear(128, 1)

    def pi(self, x, softmax_dim=0):
        x = F.relu(self.fc1(x))
        x = self.fc_pi(x)
        prob = F.softmax(x, dim=softmax_dim)
        return prob

    def v(self, x):
        x = F.relu(self.fc1(x))
        v = self.fc_v(x)
        return v


def train(fname, global_model, rank):
    local_model = ActorCritic()
    local_model.load_state_dict(global_model.state_dict())

    optimizer = optim.Adam(global_model.parameters(), lr=learning_rate)

    env = environment()
    env.make(fname)

    for n_epi in range(max_train_ep):
        done = False
        s = env.reset()
        # print("here {}".format(n_epi))
        while not done:
            s_lst, a_lst, r_lst = [], [], []
            for t in range(update_interval):
                prob = local_model.pi(torch.from_numpy(s).float())
                m = Categorical(prob)
                a = m.sample().item()
                # print(m)
                # s_prime, r, done, truncated, info = env.step(a)
                s_prime, r, done = env.step(a)

                s_lst.append(s)
                a_lst.append([a])
                r_lst.append(r)

                s = s_prime
                if done:
                    break
            # print(s_prime)
            # s_final = torch.tensor(s_prime, dtype=torch.float)
            prob = local_model.v(torch.from_numpy(s_prime).float()).detach()
            a = prob.max()
            # print("a {}".format(a))
            # R = 0.0 if done else a
            R = a
            td_target_lst = []
            for reward in r_lst[::-1]:
                R = gamma * R + reward
                td_target_lst.append([R])
            td_target_lst.reverse()
            # print(len(td_target_lst))
            # print(len(s_lst))
            
            s_batch, a_batch, td_target = torch.tensor(np.array(s_lst), dtype=torch.float), torch.tensor(np.array(a_lst)), \
                torch.tensor(np.array(td_target_lst))
            # print("s ", s_batch.size())
            # print("td", td_target.size())
            advantage = td_target - local_model.v(s_batch)
            pi = local_model.pi(s_batch, softmax_dim=1)
            pi_a = pi.gather(1, a_batch)
            # print("s -> ", local_model.v(s_batch).size())
            # print("td -> ", td_target.detach().size())
            loss = -torch.log(pi_a) * advantage.detach() + \
                F.smooth_l1_loss(local_model.v(s_batch), td_target.detach())

            optimizer.zero_grad()
            loss.mean().backward()
            for global_param, local_param in zip(global_model.parameters(), local_model.parameters()):
                global_param._grad = local_param.grad
            optimizer.step()
            local_model.load_state_dict(global_model.state_dict())

    # env.close()
    # print("Training process {} reached maximum episode.".format(rank))


def test(fname, global_model):
    env = environment()
    print("Maximum Achievable Reward", env.make(fname))
    score = 0.0
    print_interval = 20

    for n_epi in range(max_test_ep):
        done = False
        s = env.reset()
        while not done:
            # print(s)
            prob = global_model.pi(torch.from_numpy(s).float())
            a = Categorical(prob).sample().item()
            # s_prime, r, done, truncated, info = env.step(a)
            s_prime, r, done = env.step(a)

            s = s_prime
            score += r

        if n_epi % print_interval == 0 and n_epi != 0:
            print("# of episode :{}, avg score : {:.1f}".format(
                n_epi, score/print_interval))
            score = 0.0
            time.sleep(1)
    # env.close()


if __name__ == '__main__':

    filenames = os.listdir(os.getcwd() + '/interactions/')
    file_paths = [os.path.join(os.getcwd() + '/interactions/', filename) for filename in filenames]
    global_model = ActorCritic()
    global_model.share_memory()
    for fname in file_paths:
        print(fname)
        processes = []
        for rank in range(n_train_processes + 1):  # + 1 for test process
            if rank == 0:
                p = mp.Process(target=test, args=(fname, global_model,))
            else:
                p = mp.Process(target=train, args=(fname, global_model, rank,))
            p.start()
            processes.append(p)
        for p in processes:
            p.join()