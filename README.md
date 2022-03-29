# Epidemiological-social graph-based simulation

## Abstract


## Optimal PIP algorithm


## Structure
1. **Main.py** - Entry file to the project, running set of simulation to generate the results shown in the paper.
2. **edge.py** - Data Structure class, edge object of the graph object. 
3. **epidemiological_state.py** - Enum class for the SEIIRRD epidemiological model.
4. **graph.py** - Data Structure class, a classical graph object.
5. **multi_sim.py** - A technical class to run multiple instances of the same Simulator object.
6. **node.py** - Data Structure class, node object of the graph object and operating as individual in the population.
7. **params.py** - Enum class for the simulator's parameter values.
8. **plotter.py** - A plots generator central class.
9. **sim.py** - The main class in the project, responsible to run the simulation.
10. **sim_generator.py** - A class responsible to generate random instances with some pre-defined properties of the simulator.
11. **math_utils.py** - pre-compiled computational funcions.
12. **vaccine_reduction.py** - the infection factor reduction due to vaccine reduction. 

## Prerequisites
- Python          3.7
- numpy           1.20.2
- matplotlib      3.4.0
- pandas          1.2.3
- scipy           1.7.0
- numba           0.55.1
- seaborn         0.11.2
- NetworkX        2.6.2
- scikit-learn    1.0.2
- keras           2.8.0
- tuna            Latest
- line_profiler   Latest
- Flask           Latest
- Werkzeug        Latest
- yagmail         Latest

These can be found in the **requirements.txt** and easily installed using the "pip install requirements.txt" command in your terminal. 

## Usage 

1. Clone the repo
2. Install the '**requirements.txt**' file (pip install requirements.txt)
3. Run the '**main.py**' file (python main.py or python3 main.py)
4. Checkout the results in the "results" folder.
