import dimod
import numpy as np
from tqdm import tqdm
import neal

from data.sp_data import SPData
from models import SPQuboBinary, SPCplex
from evaluation.evaluation import SPEvaluation
from plotting.sp_plot import SPPlot

config = {"num_reads": 1000, "num_sweeps": 1000}
solve_func = neal.SimulatedAnnealingSampler().sample_qubo

def run_on_dwave(data):
    from dwave.system import EmbeddingComposite, DWaveSampler

    qubo = SPQuboBinary(data)
    qubo_matrix = qubo.model

    qubo_dict = {
        (i, j): qubo_matrix[i, j]
        for i in range(len(qubo_matrix))
        for j in range(len(qubo_matrix))
        if qubo_matrix[i, j] != 0
    }
    bqm = dimod.BinaryQuadraticModel.from_qubo(qubo_dict)

    # TODO: add your token
    dwave_token = ""
    if len(dwave_token) == 0:
        print("Error: no dwave token")
        return

    sampler = EmbeddingComposite(DWaveSampler(token=dwave_token))
    response = sampler.sample(bqm, num_reads=100)

    best_solution = response.first.sample

    answer = {'solution': dict()}

    for i in range(len(qubo.usedLidars)):
        lidar_str = f"x_{qubo.usedLidars[i][0]}_{qubo.usedLidars[i][1]}_{qubo.usedLidars[i][2]}_{qubo.usedLidars[i][3]}_{qubo.usedLidars[i][4]}"
        i
        answer['solution'][lidar_str] = best_solution[i]

    return answer


def decompose_to_solution(data, coords, radius, alg="dwave"):
    problems = data.decompose(coords, radius)

    sub_solutions = []
    for p in problems:
        #plt = SPPlot(p).plot_problem()
        #plt.show()


        if len(p.G.nodes) == 0:
            continue

        if alg == "dwave":
            answer = run_on_dwave(p)
        elif alg == "sim":
            qubo_model_bin = SPQuboBinary(p)
            answer = qubo_model_bin.solve(solve_func, **config)
        elif alg == "cplex":
            cplex_model = SPCplex(p)
            answer = cplex_model.solve()
        else:
            return

        sub_solutions.append(answer['solution'])

        solution_dict = answer['solution']
        for key, value in solution_dict.items():
            if value==1:
                parts = key.split('_')
                lx=float(parts[1].replace("m", "-"))
                ly=float(parts[2].replace("m", "-"))
                lz=float(parts[3].replace("m", "-"))
                dir=float(parts[4].replace("m", "-"))
                pitch=float(parts[5].replace("m", "-"))

                node = (lx, ly, lz, dir, pitch)

                for prob in problems:
                    prob.G.remove_nodes_from(data.G.neighbors(node))
                    prob.listStreetPoints3D = [n for n in prob.G if len(n) == 3]


        #evaluation = SPEvaluation(p, answer['solution'])
        #plt = SPPlot(p, evaluation).plot_solution(hide_never_covered = True)
        #plt.show()



    answer = {'solution': dict()}

    for solution in sub_solutions:
        for node, val in solution.items():
            answer['solution'][node] = answer['solution'].get(node, 0) | int(val)

    return answer


def benchmark():
    cplex_lidars = []
    simulated_lidars = []
    devide_lidars = []

    for size in tqdm(range(10, 101, 10)):
        params = {"version": 3, "num_cols": size, "rad_max": 2.4}
        data = SPData().gen_problem(**params) 

        cplex_model = SPCplex(data)
        answer_cplex = cplex_model.solve()
        cplex_lidars.append(sum(answer_cplex['solution'].values()))

        data = SPData().gen_problem(**params) 

        qubo_model_bin = SPQuboBinary(data)
        answer_qubo = qubo_model_bin.solve(solve_func, **config)
        simulated_lidars.append(sum(answer_qubo['solution'].values()))

        data = SPData().gen_problem(**params) 

        answer_devicde = decompose_to_solution(data, coords, radius)
        devide_lidars.append(sum(answer_devicde['solution'].values()))

    np.save('presentation/cplex_lidars.npy', np.array(cplex_lidars))
    np.save('presentation/simulated_lidars.npy', np.array(simulated_lidars))
    np.save('presentation/devide_lidars.npy', np.array(devide_lidars))


def benchmark2():
    hw_lidars = []
    hw_decomp_lidars = []

    for size in tqdm(range(10, 31, 10)):
        params = {"version": 3, "num_cols": size, "rad_max": 2.4}

        data = SPData().gen_problem(**params) 

        answer_hw_decomp = decompose_to_solution(data, coords, radius)
        hw_decomp_lidars.append(sum(answer_hw_decomp['solution'].values()))
        np.save('presentation/hw_decomp_lidars.npy', np.array(hw_decomp_lidars))

    for size in tqdm(range(10, 31, 10)):
        params = {"version": 3, "num_cols": size, "rad_max": 2.4}
        data = SPData().gen_problem(**params) 

        answer_hw = run_on_dwave(data)
        hw_lidars.append(sum(answer_hw['solution'].values()))
        np.save('presentation/hw_lidars.npy', np.array(hw_lidars))

    np.save('presentation/hw_lidars.npy', np.array(hw_lidars))
    np.save('presentation/hw_decomp_lidars.npy', np.array(hw_decomp_lidars))


#benchmark2()
#exit()

def v3_30_compare():
    coords = [(1 + 4.5*i, 2) for i in range(23)]
    radius = 3
    params = {"version": 3, "num_cols": 30, "rad_max": 2.4}

    data = SPData().gen_problem(**params) 
    plt = SPPlot(data, coords=coords, radius=radius).plot_problem()
    plt.savefig("presentation/in.pdf")
    plt.show()

    cplex_model = SPCplex(data)
    answer_cplex = cplex_model.solve()
    evaluation = SPEvaluation(data, answer_cplex['solution'])
    for constraint, violations in evaluation.check_solution().items():
        if len(violations) > 0:
            print(f"constraint {constraint} was violated {len(violations)} times")
    plt = SPPlot(data, evaluation).plot_solution(hide_never_covered = True)
    plt.savefig("presentation/cplex_sol.pdf")
    plt.show()

    data = SPData().gen_problem(**params) 
    answer_decomp = decompose_to_solution(data, coords, radius, alg="sim")
    evaluation = SPEvaluation(data, answer_decomp['solution'])
    for constraint, violations in evaluation.check_solution().items():
        if len(violations) > 0:
            print(f"constraint {constraint} was violated {len(violations)} times")
    plt = SPPlot(data, evaluation).plot_solution(hide_never_covered = True)
    plt.savefig("presentation/decomp_sol.pdf")
    plt.show()


    data = SPData().gen_problem(**params) 
    qubo_model_bin = SPQuboBinary(data)
    answer_qubo = qubo_model_bin.solve(solve_func, **config)
    evaluation = SPEvaluation(data, answer_qubo['solution'])
    for constraint, violations in evaluation.check_solution().items():
        if len(violations) > 0:
            print(f"constraint {constraint} was violated {len(violations)} times")
    plt = SPPlot(data, evaluation, coords, radius).plot_solution(hide_never_covered = True)
    plt.savefig("presentation/sim_sol.pdf")
    plt.show()


# example:
coords = [(1 + 4.5*i, 2) for i in range(7)]
radius = 3

params = {"version": 3, "num_cols": 30, "rad_max": 2.4}
data = SPData().gen_problem(**params) 
plt = SPPlot(data, coords=coords, radius=radius).plot_problem()
plt.show()

answer = decompose_to_solution(data, coords, radius, alg="sim")

evaluation = SPEvaluation(data, answer['solution'])
for constraint, violations in evaluation.check_solution().items():
    if len(violations) > 0:
        print(f"constraint {constraint} was violated {len(violations)} times")
plt = SPPlot(data, evaluation).plot_solution(hide_never_covered = True)
plt.savefig("presentation/decomp_sol.pdf")
plt.show()
