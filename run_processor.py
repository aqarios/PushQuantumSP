api_key = "9d4a2fd3449a4f27a535fb6e2f0ee570"
dwave_key = "DEV-d70ca880a10551a48f433e67a785dbed56d751e8"

from luna_sdk import LunaSolve
from luna_sdk.schemas import TravellingSalesmanProblem

from luna_sdk.schemas.optimization_formats.bqm import BQMSchema

# ls = LunaSolve(api_key=api_key)
# lq = LunaQ(api_key=api_key)

def do_optimization(Q):

    ls = LunaSolve(api_key=api_key)
    case = 2
    if case ==1:
        from luna_sdk.schemas.qpu_token import QpuToken, TokenProvider
        optimization = ls.optimization.create_from_qubo(name="My QUBO", matrix=Q)

        # Example of using QA using the D-Wave backend in LunaSolve
        solution = ls.solution.create(
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
                        "timeout": 1000,
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
    elif case == 2:
        optimization = ls.optimization.create_from_qubo(name="My QUBO", matrix=Q)
                

        # # Alternatively, define your QUBO as BQM
        # bqm_data = {
        #     "linear": {"0": 4.0, "1": -2.0, "2": 6.0, "3": 2.0, "4": 5.0},
        #     "quadratic": {("3", "1"): 2.0, ("3", "2"): -6.0, ("4", "0"): -4.0},
        #     "vartype": "BINARY"
        # }

        # bqm = BQMSchema(**bqm_data)

        # # Upload your BQM to LunaSolve
        # optimization = ls.optimization.create_from_bqm(name="My BQM", bqm=bqm)

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
        job = ls.solution.create_blocking(
            encryption_key = "/WeNsI3W5FicFninWZeggZh5jFoAlvCISazcEkxlkr8=",
            optimization_id=optimization.id,
            solver_name="SAGA+", # classical version
            # solver_name="QAGA+",
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