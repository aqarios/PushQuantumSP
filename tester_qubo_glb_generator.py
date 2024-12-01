import neal
import os
from time import sleep, time

from data.sp_data import SPData
from models.luna_qubo_binary import QuboSPBinary as SPQuboBinary
from evaluation.evaluation import SPEvaluation
from plotting.sp_plot import SPPlot

from luna_sdk import LunaSolve
from luna_sdk.schemas.optimization_formats.bqm import BQMSchema
from luna_sdk.schemas.qpu_token import QpuToken, TokenProvider
from luna_sdk.schemas.enums.status import StatusEnum

os.environ["LUNA_ENCRYPTION_KEY"] = "YOUR_API_KEY="
api_key="YOUR_API_KEY"
ls = LunaSolve(api_key=api_key)


params = {"version": 1, "num_cols": 5, "rad_max": 5}
data = SPData().gen_problem(**params)


# params = {"lidar_density": 0.1, "street_point_density": 0.1}
# data = SPData().create_problem_from_glb_file(**params)


# params = {"version": 3, "num_cols": 50, "rad_max": 2.4}
# data = SPData.gen_problem(**params)


# plt = SPPlot(data).plot_problem()
# plt.show()

qubo_model_bin = SPQuboBinary(data)
optimization = ls.optimization.create_from_qubo(name="qubo_test", matrix=qubo_model_bin.get_qubo_list())

# Set your token to access D-Wave's hardware
# personal_token = ls.qpu_token.create(
#     name="dwawe_token_2",
#     provider="dwave",
#     token="DEV-a253e7748836b4e404ce5ceadb0ffde70fd7b91e",
#     token_type="personal"
# )

job = ls.solution.create(
    optimization_id=optimization.id,
    solver_name="SAGA+",
    provider="dwave",
    qpu_tokens=TokenProvider(
        dwave=QpuToken(
            source="personal", 
            name="dwawe_token_2")
    ),
    solver_parameters={
        # 'p_size': 40,
        # 'mut_rate': 0.3,
        # 'rec_rate': 2
        "p_size": 40,
        "p_inc_num": 5,
        "p_max": 160,
        "pct_random_states": 0.5,
        "mut_rate": 0.5,
        "rec_rate": 2,
        "rec_method": "random_crossover",
        "select_method": "simple",
        "target": None,
        "atol": 0.0,
        "rtol": 0.0,
        "timeout": 60.0,
        "max_iter": 100,
        "num_sweeps": 10,
        "num_sweeps_inc_factor": 1.2,
        "num_sweeps_inc_max": 7000,
        "beta_range_type": "default",
        "beta_range": None,
    }
)
start_time = time()

while True:
    solution = ls.solution.get(job.id)
    elapsed_time = time() - start_time
    if solution.status == StatusEnum.IN_PROGRESS:
        print("Job is still in progress, time elapsed: ", round(elapsed_time, 1))
        sleep(3)  # Wait for 3 seconds before checking again
    else:
        print(f"Job finished with status: {solution.status}")
        break

best = ls.solution.get_best_result(solution).sample
answer = qubo_model_bin.invert_luna_solution(best)

evaluation = SPEvaluation(data, answer)
print(f"solution clean: {evaluation.solution}")

print(f"objective = {evaluation.get_objective()}")
for constraint, violations in evaluation.check_solution().items():
    if len(violations) > 0:
        print(f"constraint {constraint} was violated {len(violations)} times")

plt = SPPlot(data, evaluation).plot_solution(hide_never_covered = True)
plt.show()
