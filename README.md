# GPTGeoChat🌎: Benchmarking Conversational Geolocation 
Repository for "Granular Privacy Control for Geolocation with Vision Language Models"

## Main Datasets 🗎
### Downloads and Directory Structure ⬇️
The full human annotated GPTGeoChat and AI-generated GPTGeoChat<sub>Synthetic</sub> are available for download at the following links:
* GPTGeoChat: https://www.mediafire.com/file/rcr1wsmi70b01ah/human.zip/file
* GPTGeoChat<sub>Synthetic</sub>: https://www.mediafire.com/file/chvqvde6xm7ofqa/synthetic.zip/file

The directory structure of GPTGeoChat:
```
human
    │
    └───test
    │   │   
    │   └───annotations
    │   │       ...
    │   └───images
    │           ...
    │
    └───train
    │   │   
    │   └───annotations
    │   │       ...
    │   └───images
    │           ...
    │
    └───val
        │   
        └───annotations
        │       ...
        └───images
                ...
```
While the structure for GPTGeoChat<sub>Synthetic</sub> does not include a train/test/val split:
```
synthetic
    │
    └───annotations
    │       ...
    └───images
            ...
```
These datasets include both images and the associated conversations. Images are in files named `images/{id}.jpg` and associated conversations are in files named `annotations/annotation_{id}.json`. 

### Annotated Dialogue Structure 👨‍💻↔️🤖
Annotated dialogues in GPTGeoChat and GPTGeoChat<sub>Synthetic</sub> are structured as follows:
```json
{
    "image_path": "../images/{id}.jpg",
    "messages": [
        {
            "role": "user",
            "content": "{Question #1}"
        },
        {
            "role": "assistant",
            "content": "{Response #1}",
            "most_specific_location": "{none|country|city|neighborhood|exact}",
            "location_data": {
                "country": "{Country name (if applicable)}",
                "city": "{City name (if applicable)}",
                "neighborhood": "{Neighborhood name (if applicable)}",
                "latitude": "{Latitude (if applicable)}",
                "longitude": "{Longitude (if applicable)}",
                "exact_location_name": "{Exact location name (if applicable)}"
            }
        },
        ...
    ]
}
```
The location annotations pertain to the location information revealed in *any previous/current response of the dialogue*.

`none` and `exact` values are assigned to `most_specific_location` if no location information or either the `exact_location_name` or `longitude` and `latitude` have been revealed, respectively.

## Moderation Experiments 🧪
### Processed Data Files 🗂️
We provide moderation decisions for all baseline, finetuned, and prompted agents in `moderation_decisions_baselines`, `moderation_decisions_finetuned`, and `moderation_decisions_prompted`, respectively. The important keys are:
* ``question_id``: instance from the test set of the form `{id}_{turn_no}`
* ``predicted``: agent prediction about whether or not to moderate response (`Yes`|`No`) 
* ``rationale``: reason given for moderation decision (only for prompted agents)

### Running Experiments 🧑‍🔬
Follow the following steps to generate experimental results from the paper:
1. Clone the repository:
```bash 
git clone https://github.com/ethanm88/GPTGeoChat.git
```
2. Download GPTGeoChat:
```bash
wget https://download943.mediafire.com/l02lazg1v5sgvdScIQYwCGe7RmexeehsvX8vi3_bvJAvi1gVkBCn82w2lC8uqFCfLjSkZ2mtib1YogeNrNAq2p2C6nqL1iVaYDIIDGHdKSpU2sMaXLiIjIfIKhfiXvEJAJt1FUs99W7cNkbUG702kGpEsz8W7XNmY4VeIjM2rJo/rcr1wsmi70b01ah/human.zip
```
3. Unzip GPTGeoChat:
```bash
mkdir gptgeochat & unzip human.zip -d gptgeochat/ & rm human.zip
```
4. Generate Ground Truth Files. This will generate two directories, `moderation_decisions_ground_truth` and `gptgeochat/ground_truth_results` which aggregate ground truth results differently for efficient computation:
```bash
python generate_ground_truths.py
```
5. Run Experiments
```bash
python generate_eval_metrics.py [--basic_metrics] [--privacy_utility] [--geocoding_distance] [--all] [--recompute_geocoding_results]
```
Experiment Options:
* ``--all``: run all of the following experiments
* ``--basic_metrics``: calculate the precision, recall, f1-scores, and f1-score stderrs for binary moderation task. This data was used to generate Figure 3.
* ``--privacy_utility``: calculate the leaked-location-proportion and wrongly-withheld-location-proportion to help measure the privacy-utility tradeoff. This data was used to generate Figure 4.
* ``--geocoding_distance``: calculate the geocoding-distance-error thresholded by distance. This data was used to generate Figure 5. \
**Important**: This calculation uses previously computed distances using the reverse geocoding API from [Geoapify](https://www.geoapify.com/reverse-geocoding-api/). These files are saved under ``api_distance_responses``. If you want to recompute these, use the ``--recompute_geocoding_results`` flag. In this case you will need to generate an API key and set the environment variable:
```bash
export GEOAPIFY_API_KEY={your_api_key}
```

## Benchmark Your Agents 🚀
Benchmarking custom agents is easy! Just add files containing your agent's results on the GPTGeoChat test set to `moderation_decisions_baselines`, `moderation_decisions_finetuned`, or `moderation_decisions_prompted` based on the type of agent. These files should be named `{agent_name}_granularity={granularity}`. Running `generate_eval_metrics.py` with the correct arguments will then evaluate your agents. Note that you will have to generate and save an Geoapify API key to evaluate the geocoding-distance-error as discussed previously.

## Citation ✍️
