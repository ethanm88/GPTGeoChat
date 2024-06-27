GRANULARITY_DISPLAY_NAMES = {'country': 'Country', 'city': 'City', 'neighborhood': 'Neighborhood', 'exact_location_name': 'Exact Location Name', 'exact_gps_coordinates': 'Exact GPS Coordinates'}
class Colors:
    RED = '\033[91m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    END = '\033[0m'
    
def print_table(table_title, granularity_results, column_display_names, column_keys, column_widths, baseline_results, base_model_results, finetuned_model_results, bootstrap_results=None):
    # Print table title
    print("=" * (sum(column_widths) + len(column_widths) - 1))
    print(table_title)
    print("=" * (sum(column_widths) + len(column_widths) - 1))
    # Print results for each granularity
    for granularity, results in granularity_results.items():
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
                if key == 'f1' and bootstrap_results:
                    value = f"{result[key]:.2f} +/- {bootstrap_results[granularity][0]['std_f1']:.2f}"
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
                    print(f"{color}{tag}{Colors.END} {value:<{width-len(tag)}}", end=' ')
                else:
                    print(f"{value:<{width}}", end=' ')
            print()

        print("=" * (sum(column_widths) + len(column_widths) - 1))
        print()