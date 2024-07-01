GRANULARITY_DISPLAY_NAMES = {'country': 'Country', 'city': 'City', 'neighborhood': 'Neighborhood',
                             'exact_location_name': 'Exact Location Name', 'exact_gps_coordinates': 'Exact GPS Coordinates'}


class Colors:
    RED = '\033[91m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    END = '\033[0m'


def sort_models_results(results, baselines, base_models, finetuned_models):
    baseline_results = [
        result for result in results if result['model'] in baselines]
    base_model_results = [
        result for result in results if result['model'] in base_models]
    finetuned_model_results = [
        result for result in results if result['model'] in finetuned_models]
    # sort results array by the model key in each dict
    baseline_results = sorted(baseline_results, key=lambda x: x['model'])
    base_model_results = sorted(base_model_results, key=lambda x: x['model'])
    finetuned_model_results = sorted(
        finetuned_model_results, key=lambda x: x['model'])
    sorted_results = baseline_results + base_model_results + finetuned_model_results
    return sorted_results


def print_table(table_title, granularity_results, column_display_names, column_keys, column_widths, baseline_results, base_model_results, finetuned_model_results, stderr_key=None):
    # Print table title
    print("=" * (sum(column_widths) + len(column_widths) - 1))
    print(table_title)
    print("=" * (sum(column_widths) + len(column_widths) - 1))
    # Print results for each granularity
    for granularity, results in granularity_results.items():
        # sort results array by the model key in each dict
        results = sort_models_results(
            results, baseline_results, base_model_results, finetuned_model_results)
        print("=" * (sum(column_widths) + len(column_widths) - 1))
        print(f"Granularity: {GRANULARITY_DISPLAY_NAMES[granularity]}")
        print("=" * (sum(column_widths) + len(column_widths) - 1))

        # Print column headers
        for display_name, width in zip(column_display_names, column_widths):
            print(f"{display_name:<{width}}", end=' ')
        print()
        print("=" * (sum(column_widths) + len(column_widths) - 1))

        for result in results:
            for key, width in zip(column_keys, column_widths):
                tag = None
                color = Colors.END  # Default color
                if stderr_key and stderr_key == key:
                    value = f"{result[key]:.2f} +/- {result[f'{key}_stderr']:.2f}"
                elif key == 'model':
                    value = result[key]
                    if value in baseline_results:
                        tag = '(baseline)'
                        color = Colors.RED  # Change color based on tag
                    elif value in base_model_results:
                        tag = '(prompted agent)'
                        color = Colors.BLUE  # Change color based on tag
                    elif value in finetuned_model_results:
                        tag = '(finetuned agent)'
                        color = Colors.YELLOW  # Change color based on tag
                    for g in GRANULARITY_DISPLAY_NAMES:
                        if g in value:
                            value = value.replace(f"_{g}", "")
                            break
                else:
                    value = result[key]
                    if isinstance(value, float):
                        value = f"{value:.2f}"

                # Print value
                if tag:
                    print(
                        f"{color}{tag}{Colors.END} {value:<{width-len(tag)}}", end=' ')
                else:
                    print(f"{value:<{width}}", end=' ')
            print()

        print("=" * (sum(column_widths) + len(column_widths) - 1))
        print()
