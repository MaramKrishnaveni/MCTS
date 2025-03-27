import pickle
import json
from FOON_class import Object
from collections import defaultdict
import random
import math
random.seed(42)



def check_if_exist_in_kitchen(kitchen_items, ingredient):
    """
    parameters: a list of all kitchen items,
                an ingredient to be searched in the kitchen
    returns: True if ingredient exists in the kitchen
    """
    for item in kitchen_items:
        if item["label"] == ingredient.label \
                and sorted(item["states"]) == sorted(ingredient.states) \
                and sorted(item["ingredients"]) == sorted(ingredient.ingredients) \
                and item["container"] == ingredient.container:
            return True
    return False


class MCTSNode:
    def __init__(self, fu_index, parent=None):
        self.fu_index = fu_index
        self.parent = parent
        self.children = []
        self.wins = 0
        self.visits = 0
        self.untried_actions = []  

class MCTSStats:
    def __init__(self):
        self.fu_stats = defaultdict(lambda: {
            'visits': 0,
            'wins': 0,
            'parent': None,
            'children': []
        })
        self.total_simulations = 0
        self.tree_root = None

    def get_uct_score(self, fu_index, functional_units, c_param=1.414):
        stats = self.fu_stats[fu_index]
        if stats['visits'] == 0:
            return float('inf')

        wi = stats['wins']
        ni = stats['visits']
        t = self.total_simulations

        exploitation = self._calculate_exploitation(wi, ni)
        exploration = self._calculate_exploration(t, ni, c_param)
        uct_score = exploitation + exploration

        self._print_uct_details(fu_index, functional_units, wi, ni, t, exploitation, exploration, uct_score)
        return uct_score

    def _calculate_exploitation(self, wins, visits):
        return wins / visits if visits > 0 else 0

    def _calculate_exploration(self, total_simulations, visits, c_param):
        return c_param * math.sqrt(math.log(total_simulations) / visits) if visits > 0 else float('inf')

    def _print_uct_details(self, fu_index, functional_units, wi, ni, t, exploitation, exploration, uct_score):
        functional_unit = functional_units[fu_index]
        input_objects = ', '.join([obj.label for obj in functional_unit.input_nodes])
        output_objects = ', '.join([obj.label for obj in functional_unit.output_nodes])
        
        with open('uct_logs.txt', 'a') as log_file:
            log_file.write(f"\nUCT Score for FU {fu_index}:\n")
            log_file.write(f"------------------------------------\n")
            log_file.write(f"Input Objects: {input_objects}\n")
            log_file.write(f"Output Objects: {output_objects}\n")
            log_file.write(f"Wins/Visits: {wi}/{ni}\n")
            log_file.write(f"exploitation:{exploitation}\n")
            log_file.write(f"exploration:{exploration}\n")
            log_file.write(f"UCT Score: {uct_score:.4f}\n")

    def update_stats(self, fu_index, success, ancestors=None):
        if fu_index is None:
            return

        current = fu_index
        while current is not None:
            stats = self.fu_stats[current]
            stats['visits'] += 1
            if success:
                stats['wins'] += 1
            current = stats['parent']

        self.total_simulations += 1

def read_motion_rates(filepath='motion.txt'):
    motion_rates = {}
    with open(filepath, 'r') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) == 2:
                motion, rate = parts
                try:
                    motion_rates[motion.strip()] = float(rate)
                except ValueError:
                    print(f"Warning: Could not parse rate for motion {motion}")
    return motion_rates

def simulate_execution(functional_unit, motion_rates, kitchen_items, functional_units, object_nodes, ancestors=None):
    """Simulates the execution of a functional unit and its prerequisites"""
    if not functional_unit:
        return False

    success = True
    current_ancestors = ancestors.copy() if ancestors else []

    # Check motion success probability
    if not _check_motion_success(functional_unit, motion_rates):
        return False

    # Check input nodes
    for input_node in functional_unit.input_nodes:
        if not check_if_exist_in_kitchen(kitchen_items, input_node):
            input_success = _simulate_input(
                input_node,
                functional_units,
                motion_rates,
                kitchen_items,
                object_nodes,
                functional_unit,
                current_ancestors
            )
            if not input_success:
                success = False
                break

    return success

def _check_motion_success(functional_unit, motion_rates):
    motion = functional_unit.motion_node
    if motion in motion_rates:
        return random.random() < motion_rates[motion]
    return True

def _simulate_input(input_node, functional_units, motion_rates, kitchen_items, object_nodes, current_unit, ancestors):
    if not hasattr(input_node, 'id'):
        return False

    input_candidates = foon_object_to_FU_map.get(input_node.id, [])
    if not input_candidates:
        return False

    if current_unit in ancestors:
        return False

    current_ancestors = ancestors.copy()
    current_ancestors.append(current_unit)

    selected_unit = random.choice(input_candidates)
    return simulate_execution(
        functional_units[selected_unit],
        motion_rates,
        kitchen_items,
        functional_units,
        object_nodes,
        current_ancestors
    )

def select_candidate_mcts(candidate_units, kitchen_items, functional_units, object_nodes, motion_rates, mcts_stats, k_simulations=1000):
    """Main MCTS implementation following the required steps"""
    # Initialize root node
    root = MCTSNode(None)
    root.untried_actions = candidate_units.copy()

    for _ in range(k_simulations):
        # Selection Phase
        node = root
        while node.untried_actions == [] and node.children:
            node = _select_uct_child(node, mcts_stats, functional_units)

        # Expansion Phase
        if node.untried_actions:
            fu_index = random.choice(node.untried_actions)
            node.untried_actions.remove(fu_index)
            new_node = MCTSNode(fu_index, parent=node)
            node.children.append(new_node)
            node = new_node

        # Simulation Phase
        if node.fu_index is not None:
            success = simulate_execution(
                functional_units[node.fu_index],
                motion_rates,
                kitchen_items,
                functional_units,
                object_nodes,
                _get_ancestors(node)
            )

            # Backpropagation Phase
            while node is not None:
                node.visits += 1
                if success:
                    node.wins += 1
                mcts_stats.update_stats(node.fu_index, success)
                node = node.parent

    # Select best child based on visit count and win rate
    best_child = max(root.children, 
                    key=lambda c: (c.wins / c.visits) if c.visits > 0 else 0)
    return best_child.fu_index

def _select_uct_child(node, mcts_stats, functional_units):
    """Selects child node with highest UCT score"""
    return max(node.children,
              key=lambda c: mcts_stats.get_uct_score(c.fu_index, functional_units))

def _get_ancestors(node):
    """Returns list of ancestor nodes"""
    ancestors = []
    current = node
    while current.parent:
        ancestors.append(current.fu_index)
        current = current.parent
    return ancestors

def read_universal_foon(filepath='FOON.pkl'):
    """
        parameters: path of universal foon (pickle file)
        returns: a map. key = object, value = list of functional units
    """
    pickle_data = pickle.load(open(filepath, 'rb'))
    functional_units = pickle_data["functional_units"]
    object_nodes = pickle_data["object_nodes"]
    object_to_FU_map = pickle_data["object_to_FU_map"]

    return functional_units, object_nodes, object_to_FU_map

def search_MCTS(kitchen_items=[], goal_node=None):
    """Main MCTS search function"""
    reference_task_tree = []
    items_to_search = [goal_node.id]
    items_already_searched = []
    
    mcts_stats = MCTSStats()
    motion_rates = read_motion_rates()

    while items_to_search:
        current_item_index = items_to_search.pop(0)
        
        if current_item_index in items_already_searched:
            continue
            
        items_already_searched.append(current_item_index)
        current_item = foon_object_nodes[current_item_index]

        if not check_if_exist_in_kitchen(kitchen_items, current_item):
            candidate_units = foon_object_to_FU_map[current_item_index]
            
            selected_candidate_idx = select_candidate_mcts(
                candidate_units,
                kitchen_items,
                foon_functional_units,
                foon_object_nodes,
                motion_rates,
                mcts_stats
            )

            if selected_candidate_idx in reference_task_tree:
                continue

            reference_task_tree.append(selected_candidate_idx)

            # Process input nodes
            for node in foon_functional_units[selected_candidate_idx].input_nodes:
                node_idx = node.id
                if node_idx not in items_to_search:
                    flag = True
                    if node.label in utensils and len(node.ingredients) == 1:
                        for node2 in foon_functional_units[selected_candidate_idx].input_nodes:
                            if (node2.label == node.ingredients[0] and 
                                node2.container == node.label):
                                flag = False
                                break
                    if flag:
                        items_to_search.append(node_idx)

    reference_task_tree.reverse()
    return [foon_functional_units[i] for i in reference_task_tree]

def save_paths_to_file(task_tree, path):
    """Saves the generated task tree to a file"""
    print('Writing generated task tree to', path)
    with open(path, 'w') as _file:
        _file.write('//\n')
        for FU in task_tree:
            _file.write(FU.get_FU_as_text() + "\n")



if __name__ == '__main__':
    foon_functional_units, foon_object_nodes, foon_object_to_FU_map = read_universal_foon(
    )

    utensils = []
    with open('utensils.txt', 'r') as f:
        for line in f:
            utensils.append(line.rstrip())

    kitchen_items = json.load(open('kitchen.json'))

    goal_nodes = json.load(open("goal_nodes.json"))

    for node in goal_nodes:
        node_object = Object(node["label"])
        node_object.states = node["states"]
        node_object.ingredients = node["ingredients"]
        node_object.container = node["container"]
        goal_node_found = False
        for object in foon_object_nodes:
            if object.check_object_equal(node_object):
                 #BFS
                goal_node_found = True
                output_task_tree = search_MCTS(kitchen_items, object)
                save_paths_to_file(output_task_tree,
                                   'output_MCTS_{}.txt'.format(node["label"]))
                break
    if not goal_node_found:
            print(f"The goal node '{node['label']}' does not exist in FOON.")
