we have implemented a  Monte Carlo Tree Search algorithm so that it can extract a task tree to prepare any dish existing in FOON. A task tree has the exact same structure of a subgraph.
Input:
program should have the following input:
1.	FOON (A .txt file)
2.	A goal object to search (An object name and its state)
3.	List of ingredients and utensils available in the kitchen (A kitchen file)
4.	Success rates in the motion.txt file
Task:

Implemention Rules based on the following steps

1.	 For each object i, simulate k random execution of subgraphs that producing object i; count how many were successful out of the k executions; select the function unit with the highest success counts.
a.	Decide the success or failure of a motion randomly using the success rates in the motion.txt file
b.	End a simulation with a motion failure is detected or the whole tree is successfully executed
2.	(25%) Implement exploitation and exploration
a.	Exploitation: Keep track of average success rate for each child (functional unit) from previous searches; prefer child that has previously lead to more success
b.	Exploration: Allow for exploration of relatively unvisited children (moves) too
c.	Combine these factors to compute a “score” for each child; pick child with highest score at each successive node in search

3.	 Recursively build task tree, where each round consists of:
a.	Selection: Starting at root, successively select best child nodes using scoring method until leaf node L reached
b.	Expansion: Create and add best (or random) new child node, C, of L
c.	Simulation: Perform a (random) task execution from C
d.	Backpropagation: Update score at C and all of C’s ancestors in search tree based on execution results
4.	Given a goal object g, run MCTS with simulation k=1,000, then generate the best task tree to make object g based on MCTS.

Outputs:
The task tree obtained using MCTS saved in a separate .txt file.
