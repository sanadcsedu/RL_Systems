import numpy as np
import json 
import pdb 

class environment:
    def __init__(self):
        self.states = []
        self.actions = []
        self.reward = []

        rules = []
        with open('rules-cfg.txt', 'r') as inputs:
            for line in inputs:
                line = line.strip()
                rules.append(line)
        self.rules = rules
        self.idx = 0

        self.input_dim = len(rules)
        self.rule2index = {}
        for i, r in enumerate(rules):
            self.rule2index[r] = i

        self.attributes = [
  ["Title", "str", "nominal"], 
  ["US_Gross", "num", "quantitative"], 
  ["Worldwide_Gross", "num", "quantitative"], 
  ["US_DVD_Sales", "num", "quantitative"], 
  ["Production_Budget", "num", "quantitative"], 
  ["Release_Date", "str", "nominal"], 
  ["MPAA_Rating", "str", "nominal"], 
  ["Running_Time_min", "num", "quantitative"], 
  ["Distributor", "str", "nominal"], 
  ["Source", "str", "nominal"], 
  ["Major_Genre", "str", "nominal"],
  ["Creative_Type", "str", "nominal"], 
  ["Director", "str", "nominal"], 
  ["Rotten_Tomatoes_Rating", "num", "quantitative"], 
  ["IMDB_Rating", "num", "quantitative"], 
  ["IMDB_Votes", "num", "quantitative"]]
        
    
    def take_step(self, state):
        self.states.append(state)
        length = len(self.states)
        if(length > 1):
            self.actions.append(self.find_action(self.states[length-1], self.states[length-2]))

    def find_action(self, prev_state, cur_state):
        action = np.abs(prev_state - cur_state)
        return action

    def assign_reward(self, reward):
        self.reward.append(reward)

    def get_rules(self, node, parentkey, rules):
        thisrule = parentkey + ' -> ' + ' "+" '.join(sorted(node.keys()))
        rules.append(thisrule)

        for k in sorted(node.keys()):
            v = node[k]
            if type(v) is dict:
                self.get_rules(v, k, rules)
            else:
                rules.append(k + ' -> ' + '"' + str(v) + '"')

    # // The following function will convert the vegalite encoding into a one-hot vector
    def encode2(self, sentence):
        one_hot = np.zeros(self.input_dim, dtype=np.int32)
        json_obj = json.loads(sentence.replace('\n', '').replace(' ', ''))
        json_obj = self.online_converter(json_obj)
        # pdb.set_trace()
        # json_obj = json.loads(sentence)
        # pdb.set_trace()
        sentence_rules = [] 
        self.get_rules(json_obj, 'root', sentence_rules)
        # indices = [self.rule2index[r] for r in sentence_rules]
        indices = [self.rule2index.get(r, 0) for r in sentence_rules] #If the key is not found then using 0

        # print(indices)
        # pdb.set_trace()
        one_hot[indices] = 1
        return one_hot
    
    # // The following function will convert the vegalite encoding into a 
    #processed vegalite encoding, replacing field names with str/num
    def online_converter(self, json_data):
        try:
            # Create a mapping of field names to their corresponding replacements
            field_mapping = {attr[0]: attr[1] for attr in self.attributes}

            # Helper function to recursively update field values in the JSON object
            def update_fields(obj):
                if isinstance(obj, dict):
                    # If the object is a dictionary, iterate through its items
                    for key, value in obj.items():
                        if key == 'field' and value in field_mapping:
                            # Replace the 'field' value with its corresponding replacement
                            obj[key] = field_mapping[value]
                        elif isinstance(value, (dict, list)):
                            update_fields(value)
                elif isinstance(obj, list):
                    for item in obj:
                        update_fields(item)

            update_fields(json_data)
            return json_data
        except json.JSONDecodeError:
        # Handle JSON parsing errors here
            return None

    def reset(self):
        self.idx = 0
        return self.states[0]

    def step(self, action):
        reward = 0
        print("taken action: ", action)
        if np.array_equal(action, self.actions[self.idx]): #action == self.actions[self.idx]:
            reward = 1
        self.idx += 1
        if self.idx + 1 == len(self.states):
            return None, 1, True
        else:
            return self.states[self.idx], reward, False #s_prime, reward, done 

# if __name__ == "__main__":
    def make(self):
        with open('pro13_ace_interactions.json', "r") as input:
            json_list = json.load(input)  # Load the entire list from the file
            for entry in json_list:
                # Process each JSON entry separately
                self.take_step(self.encode2(entry))

if __name__ == "__main__":
    env = environment()
    env.make()
    done = False
    while not done:
        s_prime, reward, done = env.step(None)
        print(s_prime)