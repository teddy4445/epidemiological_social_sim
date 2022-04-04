import os
import random
import pandas as pd

def func():
    data = []
    for predicted_delay_weeks in [1,7,14,21,28]:
        for influance_amount in [100000,1000000,10000000]:
            for influance_times in [1, 10, 100]:
                for strategy in ["Random", "Opinion leaders", "Anti-individuals", "Optimal"]:
                    for policy in ["masks", "social-distance", "vaccination", "combined"]:
                        reduced_r_zero = 0
                        data.append([predicted_delay_weeks, influance_amount, influance_times, strategy, policy, reduced_r_zero])
    df = pd.DataFrame(data=data,
                      columns=["predicted_delay_weeks","influance_amount","influance_times","strategy","policy","mean_reduced_r_zero"])
    df.to_csv(os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "paper_main_plot_data.csv"))

if __name__ == '__main__':
    func()
