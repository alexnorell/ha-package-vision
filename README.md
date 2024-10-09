# Package Detection Integration with Home Assistant

This project integrates a package detection system using [Roboflow's Inference Pipeline](https://roboflow.com/) with [Home Assistant](https://www.home-assistant.io/). When a package is detected in the video feed, the system updates a binary sensor in Home Assistant, allowing you to trigger automations like notifications or recording events.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Roboflow Integration](#roboflow-integration)
- [Prerequisites](#prerequisites)
- [Home Assistant Setup](#home-assistant-setup)
  - [1. Create an `input_boolean` Entity](#1-create-an-input_boolean-entity)
  - [2. Create a Template Binary Sensor](#2-create-a-template-binary-sensor)
- [Environment Variables](#environment-variables)
- [Installation](#installation)
- [Usage](#usage)
- [Automations](#automations)
  - [1. Send Notification When Package Detected](#1-send-notification-when-package-detected)
  - [2. Reset Notification Status at Sunrise and Sunset](#2-reset-notification-status-at-sunrise-and-sunset)
- [Troubleshooting](#troubleshooting)
- [Notes](#notes)
- [License](#license)

## Introduction

This script uses Roboflow's machine learning capabilities to detect packages in a video feed. Upon detection, it updates a binary sensor in Home Assistant, which can be used to trigger various automations like sending notifications, turning on lights, or recording footage.

## Features

- Real-time package detection using a video feed.
- Integration with Home Assistant to update sensor states.
- Sends a single notification per detection period, preventing multiple alerts.
- Resets notification status at sunrise and sunset.
- Customizable via environment variables for security and flexibility.
- Modular code with clear documentation and error handling.

## Roboflow Integration

[Roboflow](https://roboflow.com/) is a platform that simplifies the process of building and deploying computer vision models. It provides tools for:

- Annotating and managing image datasets.
- Training machine learning models for object detection, classification, and segmentation.
- Deploying models to various environments, including edge devices and the web.

In this project, Roboflow's Inference Pipeline is used to process the video feed and detect packages in real-time. The inference pipeline leverages a pre-trained model or a custom model you have developed in Roboflow.

**Benefits of Using Roboflow:**

- **Ease of Use:** Simplifies the machine learning workflow with user-friendly tools.
- **Flexibility:** Supports custom models tailored to your specific use case.
- **Deployment Options:** Offers various deployment methods, making it suitable for different environments.

For more information, visit the [Roboflow website](https://roboflow.com/) and explore their [documentation](https://docs.roboflow.com/).

## Prerequisites

- **Python 3.6+**
- **Home Assistant** instance running and accessible.
- **Roboflow Account** with an API key and a configured workflow.
- **Camera or Video Feed** accessible by the script.
- **Required Python Libraries**: `requests`, and any dependencies required by Roboflow's `InferencePipeline`.

## Home Assistant Setup

To integrate the package detection with Home Assistant, you'll need to set up `input_boolean` entities and a template `binary_sensor`.

### 1. Create an `input_boolean` Entity

The `input_boolean` acts as a virtual switch that represents whether a package is detected.

1. **Edit your `configuration.yaml` file**:

   Add the following lines:

   ```yaml
   input_boolean:
     package_detected:
       name: Package Detected
     package_notification_sent:
       name: Package Notification Sent
       initial: off
   ```

   - `package_detected`: Represents the detection state.
   - `package_notification_sent`: Tracks whether a notification has been sent to prevent duplicate alerts.

2. **Restart Home Assistant**:

   After saving the file, restart Home Assistant to apply the changes.

### 2. Create a Template Binary Sensor

Create a binary sensor that reflects the state of the `input_boolean.package_detected`.

1. **Add to your `configuration.yaml`**:

   ```yaml
   binary_sensor:
     - platform: template
       sensors:
         package_detected:
           friendly_name: "Package Detected"
           device_class: occupancy  # You can choose an appropriate device class
           value_template: "{{ is_state('input_boolean.package_detected', 'on') }}"
   ```

2. **Restart Home Assistant Again**:

   Restart Home Assistant to load the new binary sensor.

## Environment Variables

The script uses environment variables for configuration. Set the following variables in your environment:

### Roboflow Configuration

- `VIDEO_FEED`: URL or path to your video feed.
- `API_KEY`: Your Roboflow API key.
- `WORKSPACE_NAME`: Your Roboflow workspace name.
- `WORKFLOW_ID`: The ID of your Roboflow workflow.

### Home Assistant Configuration

- `ACCESS_TOKEN`: Your Home Assistant long-lived access token.
- `HOME_ASSISTANT_URL`: The URL of your Home Assistant instance (e.g., `http://localhost:8123`).

### Example (Linux/macOS)

```bash
export VIDEO_FEED="http://your_camera_feed"
export API_KEY="your_roboflow_api_key"
export WORKSPACE_NAME="your_workspace_name"
export WORKFLOW_ID="your_workflow_id"
export ACCESS_TOKEN="your_home_assistant_access_token"
export HOME_ASSISTANT_URL="http://your_home_assistant_url:8123"
```

### Example (Windows Command Prompt)

```cmd
set VIDEO_FEED=http://your_camera_feed
set API_KEY=your_roboflow_api_key
set WORKSPACE_NAME=your_workspace_name
set WORKFLOW_ID=your_workflow_id
set ACCESS_TOKEN=your_home_assistant_access_token
set HOME_ASSISTANT_URL=http://your_home_assistant_url:8123
```

## Installation

1. **Clone the Repository or Download the Script**:

   Save the script code to a file, e.g., `package_detection.py`.

2. **Install Required Python Packages**:

   ```bash
   pip install requests
   # Install additional dependencies required by 'InferencePipeline'
   ```

3. **Ensure Environment Variables Are Set**:

   Set the environment variables as described above.

## Usage

Run the script using Python:

```bash
python package_detection.py
```

The script will:

- Start the inference pipeline using the provided video feed.
- Process each frame to detect packages.
- Update the Home Assistant binary sensor based on package detection.

### How It Works

- **`package_inference` Function**:

  - Called on each frame processed by the inference pipeline.
  - Checks for detected packages.
  - Updates the Home Assistant sensor accordingly.

- **Home Assistant Sensor Updates**:

  - **Package Detected**: `input_boolean.package_detected` is turned **ON**.
  - **No Package Detected**: `input_boolean.package_detected` is turned **OFF**.

## Automations

### 1. Send Notification When Package Detected

This automation sends a notification when a package is detected and remains detected for at least 30 seconds. It ensures that only one notification is sent per detection period.

```yaml
alias: Package Delivered
description: "Send a notification when a package is detected for at least 30 seconds."
trigger:
  - platform: state
    entity_id: input_boolean.package_detected
    from: "off"
    to: "on"
    for:
      hours: 0
      minutes: 0
      seconds: 30
condition:
  - condition: state
    entity_id: input_boolean.package_notification_sent
    state: "off"
action:
  - service: notify.YOUR_NOTIFICATION_SERVICE
    data:
      message: "There's a package on the front porch."
      title: "Package Delivered"
  - service: input_boolean.turn_on
    target:
      entity_id: input_boolean.package_notification_sent
mode: single
```

**Instructions:**

- **Replace `YOUR_NOTIFICATION_SERVICE`** with your actual notification service (e.g., `notify.mobile_app_your_device`).
- This automation checks if the `package_notification_sent` helper is `'off'` before sending a notification.
- After sending the notification, it sets `package_notification_sent` to `'on'` to prevent further notifications until reset.

### 2. Reset Notification Status at Sunrise and Sunset

This automation resets the notification status at sunrise and sunset, allowing notifications to be sent again after these events.

```yaml
alias: Reset Package Notification at Sunrise and Sunset
description: "Resets the package notification helper at sunrise and sunset."
trigger:
  - platform: sun
    event: sunrise
  - platform: sun
    event: sunset
action:
  - service: input_boolean.turn_off
    target:
      entity_id: input_boolean.package_notification_sent
mode: single
```

**Instructions:**

- This automation turns off the `package_notification_sent` helper at sunrise and sunset.
- It ensures that a new notification can be sent after these events if a package is detected.

### Adding Automations to Home Assistant

1. **Using the UI:**

   - Go to **Settings** > **Automations & Scenes**.
   - Click **"Create Automation"**.
   - Choose **"Start with an empty automation"**.
   - Use the YAML editor to paste the automation code.
   - Save the automation.

2. **Editing `automations.yaml` Directly:**

   - Open your `automations.yaml` file in a text editor.
   - Paste the automation code.
   - Save the file.
   - Reload automations by going to **Developer Tools** > **YAML** and clicking **"Reload Automations"**.

## Troubleshooting

- **Environment Variables Not Set**:

  Ensure all required environment variables are set. The script will raise an error if any are missing.

- **Home Assistant Connection Issues**:

  - Verify that `HOME_ASSISTANT_URL` is correct and accessible.
  - Check that your `ACCESS_TOKEN` is valid.

- **Roboflow Inference Issues**:

  - Confirm your `API_KEY`, `WORKSPACE_NAME`, and `WORKFLOW_ID` are correct.
  - Ensure the video feed is accessible and functioning.

- **Dependencies Not Installed**:

  Install all required Python packages using `pip`.

- **Permissions**:

  Ensure the script has the necessary permissions to access the video feed and network resources.

## Notes

- **Security**:

  - Keep your access tokens secure.
  - Do not expose sensitive information in logs or version control systems.

- **Customizations**:

  - Adjust the `device_class` in the binary sensor configuration to change how it appears in Home Assistant.
  - Modify the `package_inference` function to suit your detection logic.

- **Extensibility**:

  - Integrate additional actions in the `package_inference` function, such as logging or triggering other services.
  - Expand automations in Home Assistant to react to package detection events.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

*This README provides comprehensive setup and usage instructions for integrating package detection with Home Assistant, including automations to control notification frequency and an overview of Roboflow integration.*