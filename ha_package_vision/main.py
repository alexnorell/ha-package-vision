import argparse
import logging
import os
import time

import requests
from inference import InferencePipeline

# -----------------------------
# Configuration Variables
# -----------------------------

# Roboflow Configuration
VIDEO_FEED = os.environ.get("VIDEO_FEED")
API_KEY = os.environ.get("API_KEY")
WORKSPACE_NAME = os.environ.get("WORKSPACE_NAME")
WORKFLOW_ID = os.environ.get("WORKFLOW_ID")

# Home Assistant Configuration
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
HOME_ASSISTANT_URL = os.environ.get("HOME_ASSISTANT_URL")

# HTTP Headers for Home Assistant API requests
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json",
}

# -----------------------------
# Home Assistant Control Functions
# -----------------------------


def turn_on_package_detected():
    """
    Sends a request to Home Assistant to turn ON the 'package_detected' input_boolean.
    """
    url = f"{HOME_ASSISTANT_URL}/api/services/input_boolean/turn_on"
    data = {"entity_id": "input_boolean.package_detected"}
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to turn ON sensor: {e}")


def turn_off_package_detected():
    """
    Sends a request to Home Assistant to turn OFF the 'package_detected' input_boolean.
    """
    url = f"{HOME_ASSISTANT_URL}/api/services/input_boolean/turn_off"
    data = {"entity_id": "input_boolean.package_detected"}
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to turn OFF sensor: {e}")


# -----------------------------
# Inference Callback Function
# -----------------------------


def package_inference(result, video_frame):
    """
    Callback function that processes the inference results.

    Args:
        result (dict): The result dictionary containing inference outputs.
        video_frame (ndarray): The current video frame being processed.

    This function checks the number of packages detected in the frame and
    updates the Home Assistant sensor accordingly.
    """
    # Get the list of detected objects
    confidences = result["output"].confidence
    coordinates = result["output"].xyxy
    valid_detections = []
    for detection in range(len(confidences)):
        confidence = confidences[detection]
        # TODO: Move this custom logic to the workflow.
        if confidence < 0.5:
            continue
        coord = coordinates[detection]
        if coord[0] > 300:
            valid_detections.append((confidence, coord))
    number_of_packages = len(valid_detections)
    logging.info(f"Found {number_of_packages} package{'s' if number_of_packages > 1 else ''}")
    if number_of_packages:
        logging.debug(f"Valid detections: {valid_detections}")
    # If there are packages detected, send a request to Home Assistant to turn ON the sensor
    if number_of_packages > 0:
        # If one or more packages are detected, turn ON the sensor
        turn_on_package_detected()
    else:
        # If no packages are detected, turn OFF the sensor
        turn_off_package_detected()


# -----------------------------
# Main Function
# -----------------------------


def main():
    """
    Main function to initialize and start the inference pipeline.
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Package Detection Script")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    # Configure logging
    logging_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=logging_level, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # Validate that all required environment variables are set
    required_vars = {
        "VIDEO_FEED": VIDEO_FEED,
        "API_KEY": API_KEY,
        "WORKSPACE_NAME": WORKSPACE_NAME,
        "WORKFLOW_ID": WORKFLOW_ID,
        "ACCESS_TOKEN": ACCESS_TOKEN,
        "HOME_ASSISTANT_URL": HOME_ASSISTANT_URL,
    }
    for var_name, value in required_vars.items():
        if not value:
            logging.error(f"Environment variable '{var_name}' is not set.")
            raise ValueError(f"Environment variable '{var_name}' is not set.")

    # Initialize the inference pipeline
    pipeline = InferencePipeline.init_with_workflow(
        api_key=API_KEY,
        workspace_name=WORKSPACE_NAME,
        workflow_id=WORKFLOW_ID,
        video_reference=VIDEO_FEED,
        on_prediction=package_inference,
        max_fps=0.2,
    )
    try:
        # Start the inference pipeline
        pipeline.start()
        # Keep the main thread alive while the pipeline is running
        pipeline.join()
    except KeyboardInterrupt:
        # Gracefully terminate the pipeline on interruption
        pipeline.terminate()
        logging.info("Pipeline terminated by user.")
        exit(0)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        pipeline.terminate()
        exit(1)


# -----------------------------
# Entry Point
# -----------------------------

if __name__ == "__main__":
    main()
