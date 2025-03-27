import json
import pickle

class FOONInitialLoader:
    def __init__(self, foon_file, utensils_file, goal_nodes_file, kitchen_file):
        self.foon_file = foon_file
        self.utensils_file = utensils_file
        self.goal_nodes_file = goal_nodes_file
        self.kitchen_file = kitchen_file

    # Retrieves and returns the FOON structure including functional units, object nodes, and mappings
    def fetch_foon_structure(self):
        print("Fetching FOON structure from the file...")
        with open(self.foon_file, 'rb') as f:
            foon_data = pickle.load(f)
        return foon_data['functional_units'], foon_data['object_nodes'], foon_data['object_to_FU_map']

    # Retrieves and returns the list of utensils from the utensils file
    def gather_utensils(self):
        print("\nGathering utensils...")
        with open(self.utensils_file) as f:
            utensils = [line.strip() for line in f]
        return utensils

    # Loads and returns goal nodes from the goal nodes JSON file
    def retrieve_goal_nodes(self):
        print("\nFetching goal nodes...")
        with open(self.goal_nodes_file) as f:
            goal_nodes = json.load(f)
        return goal_nodes

    # Loads and returns kitchen items from the kitchen items JSON file
    def load_kitchen_inventory(self):
        print("\nLoading kitchen inventory...")
        with open(self.kitchen_file) as f:
            kitchen_items = json.load(f)
        return kitchen_items
