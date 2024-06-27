import os
from tqdm import tqdm
from utils.geocoding_utils import compute_api_distance
from utils.metric_utils import compute_basic_metrics, bootstrap_f1_error_bars, compute_withheld_leaked
from utils.format_utils import print_table

# args for experiments
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("--basic_metrics", action="store_true",
                    help="Calculate basic metrics")
parser.add_argument("--privacy_utility", action="store_true",
                    help="Calculate withheld and leaked proportions")
parser.add_argument("--geocoding_distance", action="store_true",
                    help="Calculate geocoding distance error")
parser.add_argument("--all", action="store_true", help="Run all experiments")
parser.add_argument("--recompute_geocoding_results",
                    action="store_true", help="Recompute geocoding results")
args = parser.parse_args()

GRANULARITIES = ["country", "city", "neighborhood",
                 "exact_location_name", "exact_gps_coordinates"]


def get_agent_results(results_dir):
    agent_results = {}
    for filename in os.listdir(results_dir):
        if filename.endswith(".jsonl"):
            # find index where granularity starts
            granularity_idx = filename.find("_granularity=")
            if granularity_idx == -1:
                raise ValueError(
                    "Granularity not found in filename: ", filename)
            granularity = filename[granularity_idx +
                                   len("_granularity="): -len(".jsonl")]
            model_name = f"{filename[:granularity_idx]}_{granularity}"
            agent_results[model_name] = {
                "granularity": granularity, "filename": os.path.join(results_dir, filename)}
    return agent_results


if __name__ == "__main__":
    # gather results from all models
    baselines_results = get_agent_results("moderation_decisions_baselines")
    base_model_results = get_agent_results("moderation_decisions_prompted")
    finetuned_model_results = get_agent_results(
        "moderation_decisions_finetuned")

    # Combine all results
    all_model_results = {**baselines_results, **
                         base_model_results, **finetuned_model_results}

    # Run experiments:
    if args.basic_metrics or args.all:
        # Experiment #1a: Basic Metrics
        granularity_results_basic = {granularity: []
                                     for granularity in GRANULARITIES}
        print('Calculating basic metrics...')
        for model, model_results_dict in tqdm(all_model_results.items()):
            granularity, filename = model_results_dict["granularity"], model_results_dict["filename"]
            recall, precision, f1 = compute_basic_metrics(
                granularity=granularity, answers_file=filename)
            granularity_results_basic[granularity].append(
                {"model": model, "recall": recall, "precision": precision, "f1": f1})

        # Experiment 1b: Error Bars with Bootstrap Method
        granularity_results_bootstrap = {
            granularity: [] for granularity in GRANULARITIES}
        print('Calculating errors using bootstrap method...')
        for model, model_results_dict in tqdm(all_model_results.items()):
            granularity, filename = model_results_dict["granularity"], model_results_dict["filename"]
            mean_f1, std_f1 = bootstrap_f1_error_bars(granularity=granularity,
                                                      answers_file=filename)
            granularity_results_bootstrap[granularity].append(
                {"model": model, "mean_f1": mean_f1, "std_f1": std_f1})

        # print formatted table
        column_display_names_basic = ['Agent', 'Recall', 'Precision', 'F1']
        column_keys_basic = ['model', 'recall', 'precision', 'f1']
        column_widths_basic = [65, 10, 10, 20]
        print_table('Experiment #1: Basic Metrics', granularity_results_basic, column_display_names_basic,
                    column_keys_basic, column_widths_basic, baselines_results,
                    base_model_results, finetuned_model_results, granularity_results_bootstrap)

    if args.privacy_utility or args.all:
        # EXPERIMENT #2: Privacy-Utility Tradeoff
        granularity_results_withhold_leak = {
            granularity: [] for granularity in GRANULARITIES}
        print('Calculating withheld and leaked proportions...')
        for model, model_results_dict in all_model_results.items():
            granularity, filename = model_results_dict["granularity"], model_results_dict["filename"]
            withheld_proportion, leaked_proportion = compute_withheld_leaked(
                filename, granularity)
            granularity_results_withhold_leak[granularity].append(
                {"model": model, "withheld_proportion": withheld_proportion, "leaked_proportion": leaked_proportion})

        # print formatted table
        column_display_names_withhold_leak = [
            'Agent', 'Withheld Proportion', 'Leaked Proportion']
        column_keys_withhold_leak = [
            'model', 'withheld_proportion', 'leaked_proportion']
        column_widths_withhold_leak = [60, 20, 20]
        print_table('Experiment #2: Privacy-Utility Tradeoff', granularity_results_withhold_leak,
                    column_display_names_withhold_leak, column_keys_withhold_leak, column_widths_withhold_leak, 
                    baselines_results, base_model_results, finetuned_model_results)

    if args.geocoding_distance or args.all:
        # # EXPERIMENT #3: Geocoding Distance Error
        granularity_results_api_distance = {granularity: [
        ] for granularity in GRANULARITIES if granularity != "exact_gps_coordinates"}
        print('Calculating geocoding distance error...')
        for model, model_results_dict in tqdm(all_model_results.items()):
            granularity, filename = model_results_dict["granularity"], model_results_dict["filename"]
            if granularity == "exact_gps_coordinates":
                continue
            distance_thresholds, all_distances = compute_api_distance(
                filename, granularity, model_name=model, recompute=args.recompute_geocoding_results)
            total_guesses = distance_thresholds['all']
            results_dict = {"agent": model}
            results_dict.update({f"within {threshold} km": f"{round(num_guesses / total_guesses * 100, 1)} %" for threshold,
                                num_guesses in distance_thresholds.items() if threshold != 'all'})
            granularity_results_api_distance[granularity].append(results_dict)

        # print a formatted table
        column_display_names_api_distance = [
            key.title() for key in granularity_results_api_distance["country"][0].keys()]
        column_keys_api_distance = list(
            granularity_results_api_distance["country"][0].keys())
        column_widths_api_distance = [65] + [15] * \
            (len(column_display_names_api_distance) - 1)
        print_table('Experiment #3: Geocoding Distance Error', granularity_results_api_distance,
                    column_display_names_api_distance, column_keys_api_distance, column_widths_api_distance, 
                    baselines_results, base_model_results, finetuned_model_results)
