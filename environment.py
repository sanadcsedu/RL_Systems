import numpy as np
import json 
import pdb 
import os

class environment:
    def __init__(self):
        self.states = []
        self.actions = []
        self.reward = []
        self.rule2index = {}
        self.input_dim = None
        self.states_temp = []

    def set_rules(self):
        #Encoding information that we want to keep in states
        mark = ["point", "bar", "tick"] # mark = ["point", "bar", "tick", "line", "circle", "area"] 
        aggregate = ["count", "mean", "sum"]
        bin = ["True"]
        attributes = ['Title', 'US_Gross', 'Worldwide_Gross', 'US_DVD_Sales', 'Production_Budget', 'Release_Date', 'MPAA_Rating', 'Running_Time_min', 'Distributor', 'Source', 'Major_Genre', 'Creative_Type', 'Director', 'Rotten_Tomatoes_Rating', 'IMDB_Rating', 'IMDB_Votes']
        type = ["nominal", "quantitative"] # type = ["nominal", "quantitative", "ordinal", "temporal"]
        
        idx = 0
        for i, r in enumerate(mark):
            self.rule2index[r] = idx
            idx += 1
        for i, r in enumerate(aggregate):
            thisrule = 'x -> ' + r
            self.rule2index[thisrule] = idx
            idx += 1
        for i, r in enumerate(aggregate):
            thisrule = 'y -> ' + r
            self.rule2index[thisrule] = idx
            idx += 1
        for i, r in enumerate(bin):
            thisrule = 'x -> ' + r
            self.rule2index[thisrule] = idx
            idx += 1
        for i, r in enumerate(bin):
            thisrule = 'y -> ' + r
            self.rule2index[thisrule] = idx
            idx += 1
        for i, r in enumerate(attributes):
            thisrule = 'x -> ' + r
            self.rule2index[thisrule] = idx
            idx += 1
        for i, r in enumerate(attributes):
            thisrule = 'y -> ' + r
            self.rule2index[thisrule] = idx
            idx += 1
        for i, r in enumerate(type):
            thisrule = 'x -> ' + r
            self.rule2index[thisrule] = idx
            idx += 1
        for i, r in enumerate(type):
            thisrule = 'y -> ' + r
            self.rule2index[thisrule] = idx
            idx += 1

        self.input_dim = len(self.rule2index)
    
    def create_env(self):
        length = len(self.states_temp)
        for idx in range(length - 1):  
            # print("Current {}".format([idx for idx, value in enumerate(self.states_temp[idx]) if value == 1]))          
            indices = self.find_action(self.states_temp[idx], self.states_temp[idx + 1])
            # print("Target {}".format([idx for idx, value in enumerate(self.states_temp[idx + 1]) if value == 1]))
            cur_state = self.states_temp[idx]
            self.states.append(np.copy(cur_state))
            flag = True
            for i, indice in enumerate(indices):
                flag = False
                cur_state[indice] = 1 - cur_state[indice]
                
                self.actions.append(indice)
                if i == len(indices) - 1:
                    self.reward.append(1)
                else:
                    
                    self.states.append(np.copy(cur_state))
                    # print([idx2 for idx2, value in enumerate(self.states[len(self.states) - 1]) if value == 1])
                    self.reward.append(0)
                    # pdb.set_trace()
                # cur_state = new_state
            if(flag):
                self.states.pop()
        
        # length = len(self.states)
        # pdb.set_trace()
        # for idx in range(length - 1):
        #     print("index, ", idx)
        #     print([idx2 for idx2, value in enumerate(self.states[idx]) if value == 1])
        #     print(self.actions[idx])
        #     print(self.reward[idx])

    def find_action(self, prev_state, cur_state):
        action = np.abs(prev_state - cur_state)
        indices = [idx for idx, value in enumerate(action) if value == 1]
        # pdb.set_trace()
        return indices

    # // The following function will convert the vegalite encoding into a one-hot vector
    def encode2(self, sentence):
        one_hot = np.zeros(self.input_dim, dtype=np.float)
        json_obj = json.loads(sentence.replace('\n', '').replace(' ', ''))
        one_hot[self.rule2index[json_obj['mark']]] = 1
        if 'x' in json_obj['encoding']:
            if 'type' in json_obj['encoding']['x']:
                this_rule = 'x -> ' + json_obj['encoding']['x']['type']
                one_hot[self.rule2index[this_rule]] = 1
            if 'aggregate' in json_obj['encoding']['x']:
                this_rule = 'x -> ' + json_obj['encoding']['x']['aggregate']
                one_hot[self.rule2index[this_rule]] = 1
            if 'field' in json_obj['encoding']['x']:
                this_rule = 'x -> ' + json_obj['encoding']['x']['field']
                one_hot[self.rule2index[this_rule]] = 1
            if 'bin' in json_obj['encoding']['x']:
                this_rule = 'x -> ' + 'True'
                one_hot[self.rule2index[this_rule]] = 1
            
        if 'y' in json_obj['encoding']:
            if 'type' in json_obj['encoding']['y']:
                this_rule = 'y -> ' + json_obj['encoding']['y']['type']
                one_hot[self.rule2index[this_rule]] = 1
            if 'aggregate' in json_obj['encoding']['y']:
                this_rule = 'y -> ' + json_obj['encoding']['y']['aggregate']
                one_hot[self.rule2index[this_rule]] = 1
            if 'field' in json_obj['encoding']['y']:
                this_rule = 'y -> ' + json_obj['encoding']['y']['field']
                one_hot[self.rule2index[this_rule]] = 1
            if 'bin' in json_obj['encoding']['y']:
                this_rule = 'y -> True'
                one_hot[self.rule2index[this_rule]] = 1
        return one_hot
        # pdb.set_trace()
    
    def reset(self):
        self.idx = 0
        return self.states[0]

    def step(self, action):
        reward = 0
        # print("taken action: ", action)
        if np.array_equal(action, self.actions[self.idx]): #action == self.actions[self.idx]:
            reward = self.reward[self.idx]
        self.idx += 1
        if self.idx + 2 == len(self.states):
            return self.states[self.idx + 1], reward, True
        else:
            return self.states[self.idx], reward, False #s_prime, reward, done 

# if __name__ == "__main__":    
    def make(self, filename):
        # print(filename)
        self.set_rules()
        with open(filename, "r") as input:
            json_list = json.load(input)  # Load the entire list from the file
            for entry in json_list:
                one_hot_state = self.encode2(entry)
                # Process each JSON entry separately
                # print([idx for idx, value in enumerate(one_hot_state) if value == 1])
                self.states_temp.append(one_hot_state)
            #Converts the continous state-action space to discrete state-action space
            self.create_env()
        total_reward = 0
        for idx in range(len(self.reward)):
            total_reward += self.reward[idx] 
        return total_reward
    
if __name__ == "__main__":
    filenames = os.listdir(os.getcwd() + '/interactions/')
    file_paths = [os.path.join(os.getcwd() + '/interactions/', filename) for filename in filenames]

    for fname in file_paths:
        print(fname)
        env = environment()
        env.make(fname)
        pdb.set_trace()
        print(env.reset())