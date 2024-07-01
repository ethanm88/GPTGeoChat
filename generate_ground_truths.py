import os
import json
from tqdm import tqdm


def convert_standard_format(location_data):
    formatted_location_data = {'country': '', 'city': '', 'neighborhood': '', 'exact': {
        'exact_location_name': '', 'latitude': '', 'longitude': ''}}
    # fill in the formatted location data
    for granularity in ['country', 'city', 'neighborhood']:
        if granularity in location_data:
            formatted_location_data[granularity] = location_data[granularity]
    if 'exact_location_name' in location_data:
        formatted_location_data['exact']['exact_location_name'] = location_data['exact_location_name']
    if 'latitude' in location_data:
        formatted_location_data['exact']['latitude'] = location_data['latitude']
    if 'longitude' in location_data:
        formatted_location_data['exact']['longitude'] = location_data['longitude']
    return formatted_location_data


def get_individual_ground_truth(current_location_data, previous_location_data, granularity_true):
    # determine if the location data changed at the granularity level
    granularities = ['country', 'city', 'neighborhood',
                     'exact location name', 'exact gps coordinates']
    informated_revealed = []
    granularity_idx = granularities.index(granularity_true)
    for granularity in granularities[granularity_idx:]:
        current_exact_dict = current_location_data['exact']
        previous_exact_dict = previous_location_data['exact']
        if granularity == "exact gps coordinates":
            # check whether the latitude and longitude changed or is newly present
            if current_exact_dict['latitude'] == '' or current_exact_dict['longitude'] == '':
                new_information = False
            else:
                new_information = (current_exact_dict['latitude'] != '' and current_exact_dict['longitude'] != '' and (
                    previous_exact_dict['latitude'] == '' or previous_exact_dict['longitude'] == ''))
                new_information = new_information or float(current_exact_dict['latitude']) != float(
                    previous_exact_dict['latitude']) or float(current_exact_dict['longitude']) != float(previous_exact_dict['longitude'])
        elif granularity == "exact location name":
            # check whether the exact location name changed or is newly present
            formatted_granularity = granularity.replace(" ", "_")
            new_information = current_exact_dict[formatted_granularity] != previous_exact_dict[formatted_granularity]
        else:
            # check whether the location data changed or is newly present
            new_information = current_location_data[granularity] != previous_location_data[granularity]
        informated_revealed.append(new_information)
    return any(informated_revealed)

if __name__ == "__main__":
    DATA_DIR = 'gptgeochat/human/test/annotations'
    RESULTS_DIR = 'gptgeochat/human/ground_truth_results'
    GRANULARITY_RESULTS_DIR = 'moderation_decisions_ground_truth'
    # make results directory if it doesn't exist
    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)
    if not os.path.exists(GRANULARITY_RESULTS_DIR):
        os.makedirs(GRANULARITY_RESULTS_DIR)

    granularity_data = {'country': [], 'city': [], 'neighborhood': [],
                        'exact location name': [], 'exact gps coordinates': []}
    print('Generating ground truth data...')
    for f in tqdm(os.listdir(DATA_DIR)):
        saved_conversation_file = f"{DATA_DIR}/{f}"
        results_file = f"{RESULTS_DIR}/ground_truths_{f.replace('.json', '.jsonl').replace('annotation_', '')}"
        with open(saved_conversation_file, "r") as f:
            saved_conversation = json.load(f)
            # create results file
            with open(results_file, "w") as f:
                pass
        messages = saved_conversation['messages']
        image_id = saved_conversation['image_path'].split(
            '/')[-1].replace('.jpg', '')
        previous_location_data = {'country': '', 'city': '', 'neighborhood': '', 'exact': {
            'exact_location_name': '', 'latitude': '', 'longitude': ''}}
        for j in range((int)(len(messages) / 2)):
            current_location_data = convert_standard_format(
                messages[j * 2 + 1]['location_data'])
            for granularity in ['country', 'city', 'neighborhood', 'exact location name', 'exact gps coordinates']:
                revealed = get_individual_ground_truth(
                    current_location_data, previous_location_data, granularity)
                entry = {"dialogue_turn_no": j + 1,
                            "granularity": granularity, "ground_truth": revealed}
                with open(results_file, "a") as f:
                    f.write(json.dumps(entry) + "\n")
                image_id = saved_conversation['image_path'].split(
                    '/')[-1].replace('.jpg', '')
                question_id = f"{image_id}_{j + 1}"
                granularity_data[granularity].append({"question_id": question_id, "ground_truth": {True: "Yes", False: "No"}[revealed]})
            previous_location_data = current_location_data

    # save the granularity data
    for granularity in granularity_data:
        formatted_granularity = granularity.replace(" ", "_")
        with open(f"{GRANULARITY_RESULTS_DIR}/ground_truth_granularity={formatted_granularity}.jsonl", "w") as f:
            for entry in granularity_data[granularity]:
                f.write(json.dumps(entry) + "\n")
