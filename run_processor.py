api_key = "9d4a2fd3449a4f27a535fb6e2f0ee570"
dwave_key = "DEV-d70ca880a10551a48f433e67a785dbed56d751e8"

from luna_sdk import LunaSolve
from luna_sdk.schemas import TravellingSalesmanProblem

from luna_sdk.schemas.optimization_formats.bqm import BQMSchema

# ls = LunaSolve(api_key=api_key)
# lq = LunaQ(api_key=api_key)

def do_optimization(Q):

    ls = LunaSolve(api_key=api_key)
    case = 1
    if case ==1: # Use D-Wave backend
        from luna_sdk.schemas.qpu_token import QpuToken, TokenProvider
        optimization = ls.optimization.create_from_qubo(name="My QUBO", matrix=Q)

        # Example of using QA using the D-Wave backend in LunaSolve
        print("Solving the QUBO using the QA algorithm and the D-Wave backend")
        solution = ls.solution.create_blocking(
            encryption_key = "/WeNsI3W5FicFninWZeggZh5jFoAlvCISazcEkxlkr8=",
            optimization_id=optimization.id,
            solver_name="QA",
            provider="dwave",
            solver_parameters={
                "embedding": {
                    "chain_strength": None,
                    "chain_break_fraction": True,
                    "embedding_parameters": {
                        "max_no_improvement": 10,
                        "random_seed": None,
                        "timeout": 10,#1000,
                        "max_beta": None,
                        "tries": 10,
                        "inner_rounds": None,
                        "chainlength_patience": 10,
                        "max_fill": None,
                        "threads": 1,
                        "return_overlap": False,
                        "skip_initialization": False,
                        "initial_chains": (),
                        "fixed_chains": (),
                        "restrict_chains": (),
                        "suspend_chains": (),
                    },
                },
                "sampling_params": {
                    "anneal_offsets": None,
                    "anneal_schedule": None,
                    "annealing_time": None,
                    "auto_scale": None,
                    "fast_anneal": False,
                    "flux_biases": None,
                    "flux_drift_compensation": True,
                    "h_gain_schedule": None,
                    "initial_state": None,
                    "max_answers": None,
                    "num_reads": 1,
                    "programming_thermalization": None,
                    "readout_thermalization": None,
                    "reduce_intersample_correlation": False,
                    "reinitialize_state": None,
                },
            },
            qpu_tokens=TokenProvider(
                dwave=QpuToken(
                    source="inline",
                    token=dwave_key, #"<dwave token>",
                ),
            ),
        )
        print("Solution received")
        
        print(solution.head)

        best_result = ls.solution.get_best_result(solution)
        # print(best_result)
        return best_result
    elif case == 2: # Use LunaSolve backend
        optimization = ls.optimization.create_from_qubo(name="My QUBO", matrix=Q)
                

        # Set your token to access D-Wave's hardware
        # ls.qpu_token.create(
        #     name="My D-Wave Token",
        #     provider="dwave",
        #     token=api_key,
        #     token_type="personal",
        #     encryption_key = "/WeNsI3W5FicFninWZeggZh5jFoAlvCISazcEkxlkr8=",
        # )
        
        from luna_sdk.schemas.qpu_token import QpuToken, TokenProvider

        # Solve the QUBO using the QAGA+ algorithm and retrieve a job
        print("Solving the QUBO using LunaSolve's backend")
        job = ls.solution.create_blocking(
            encryption_key = "/WeNsI3W5FicFninWZeggZh5jFoAlvCISazcEkxlkr8=",
            optimization_id=optimization.id,
            # solver_name="SAGA+", # classical version
            solver_name="QA",
            provider="dwave",
            qpu_tokens=TokenProvider(
                dwave=QpuToken(
                    source="personal",
                    name="My D-Wave Token"
                )
            ),
            solver_parameters={
                'p_size': 40,
                'mut_rate': 0.3,
                'rec_rate': 2
            }
        )


        solution = ls.solution.get(job.id)

        print(solution.head)

        best_result = ls.solution.get_best_result(solution)
        # print(best_result)
        return best_result