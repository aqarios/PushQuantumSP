import numpy as np
import matplotlib.pyplot as plt

x = range(10, 101, 10)

cplex_lidars = np.load('presentation/cplex_lidars.npy')
simulated_lidars = np.load('presentation/simulated_lidars.npy')
devide_lidars = np.load('presentation/devide_lidars.npy')

simulated_lidars -= cplex_lidars.astype(np.int8)
devide_lidars -= cplex_lidars.astype(np.int8)

#plt.plot(x, cplex_lidars, label='CPLEX LIDARS', marker='o')
plt.plot(x, simulated_lidars, label='Simulation without decomposition', marker='s')
plt.plot(x, devide_lidars, label='Simulation with decomposition', marker='s')

# Add labels, title, and legend
plt.xlabel('System Size')
plt.ylabel('Offset to optimal solution')
plt.legend()

# Show grid
plt.grid(True)

plt.savefig('presentation/lidars.pdf')
# Show the plot
plt.show()
