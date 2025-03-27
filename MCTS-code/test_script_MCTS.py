from FOONLoader import FOONInitialLoader
from FOON_class import Object
import search  # Import the search module that contains search_BFS
import copy
def main():
    # Load FOON data using FOONInitialLoader
    loader = FOONInitialLoader('FOON.pkl', 'utensils.txt', 'goal_nodes.json', 'kitchen.json')

    # Load FOON data
    foon_functional_units, foon_object_nodes, foon_object_to_FU_map = loader.fetch_foon_structure()

    # Monkey patch the FOON data into the search module
    search.foon_functional_units = foon_functional_units
    search.foon_object_nodes = foon_object_nodes
    search.foon_object_to_FU_map = foon_object_to_FU_map

    # Load utensils
    utensils = loader.gather_utensils()
    search.utensils = utensils

    # Load kitchen items
    kitchen_items = loader.load_kitchen_inventory()
    
    kitchen_items_copy = copy.deepcopy(kitchen_items)


    # Load goal nodes
    goal_nodes = loader.retrieve_goal_nodes()
    for node in goal_nodes:
        node_object = Object(node["label"])
        node_object.states = node["states"]
        node_object.ingredients = node["ingredients"]
        node_object.container = node["container"]
        # Check if the goal object exists in FOON's object nodes
        goal_node_found = False
        # Iterate over foon_object_nodes to find matching objects
        for foon_object in foon_object_nodes:
            if foon_object.check_object_equal(node_object):
                goal_node_found = True
                output_task_tree = search.search_MCTS(kitchen_items_copy, foon_object)

                # Save the result to a file
                search.save_paths_to_file(output_task_tree, f'test_script_MCTS_output_MCTS_{node["label"]}.txt')
                break
        if not goal_node_found:
            print(f"The goal node '{node['label']}' does not exist in FOON.")

if __name__ == '__main__':
    main()
