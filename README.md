# Plant Manager for Home Assistant

A production-quality custom Home Assistant integration for managing plant care tasks with AI-generated care profiles.

## Features

- **AI-Powered Plant Profiles**: Automatically generate complete care profiles using OpenAI-compatible LLMs
- **Dynamic Task Management**: Support for any number of care tasks (watering, fertilizing, pruning, etc.)
- **Growth Stage Tracking**: Adjust care intervals automatically based on plant growth stages
- **Automatic Notifications**: Get notified when tasks become overdue
- **Device-Based Architecture**: Each plant appears as its own device with dedicated entities
- **Fully Async**: Modern async/await architecture throughout

## Installation

1. Copy the `custom_components/plant_manager` directory to your Home Assistant `custom_components` folder
2. Restart Home Assistant
3. Go to Settings > Devices & Services > Add Integration
4. Search for "Plant Manager"
5. Enter your OpenAI-compatible API credentials

## Configuration

### Initial Setup

On first setup, you'll be asked to configure:
- **API Key**: Your OpenAI API key (or compatible provider)
- **API Endpoint**: Default is `https://api.openai.com/v1`
- **Model**: Default is `gpt-4o-mini`

### Adding Plants

After initial setup, add plants by entering their name:
- Orange Habanero
- Sungold Tomato
- Thai Basil
- Monstera Deliciosa

The AI will automatically generate:
- Common and scientific names
- Care profile (light, temperature, humidity, soil)
- List of care tasks with intervals
- Growth stages with task overrides

## Entities

For each plant and task, the following entities are created:

### Sensors
- **Days Since [Task]**: Number of days since the task was last completed
- **Next Due [Task]**: Timestamp of when the task is next due

### Binary Sensors
- **[Task] Overdue**: On when the task is overdue

### Buttons
- **Complete [Task]**: Press to mark the task as completed

## Services

### `plant_manager.complete_task`
Mark a care task as completed.

```yaml
service: plant_manager.complete_task
data:
  plant_id: "abc123"
  task_id: "water"
```

### `plant_manager.set_growth_stage`
Change the growth stage of a plant.

```yaml
service: plant_manager.set_growth_stage
data:
  plant_id: "abc123"
  stage_id: "flowering"
```

## Architecture

### Core Components

- **Storage Layer** (`storage.py`): Persistent data using HA Storage API
- **AI Provider** (`ai_provider.py`, `openai_provider.py`): Pluggable AI backends
- **Data Models** (`models.py`): Type-safe dataclasses
- **Coordinator** (`coordinator.py`): Central data hub using DataUpdateCoordinator
- **Entities**: Dynamic entity creation based on AI-returned tasks
- **Notification Manager** (`notification_manager.py`): Automatic overdue notifications

### Extensibility

The architecture is designed to support future features:
- Additional AI providers (Ollama, Anthropic, Gemini)
- ESPHome soil sensors
- Bluetooth plant sensors
- Weather integration
- Image storage and photo history
- Calendar integration
- AI chat about specific plants
- Statistics and timelines

## Example Automation

```yaml
automation:
  - alias: "Water Reminder via Phone"
    trigger:
      - platform: state
        entity_id: binary_sensor.monstera_water_overdue
        to: "on"
    action:
      - service: notify.mobile_app
        data:
          title: "Time to Water"
          message: "Your Monstera needs watering!"
```

## Data Storage

All plant data is stored locally in `.storage/plant_manager.storage.json`. The AI is only called once per plant during creation.

## Requirements

- Home Assistant 2024.1 or newer
- OpenAI-compatible API (OpenAI, Ollama, LM Studio, etc.)
- Python 3.11+

## License

MIT

## Support

For issues and feature requests, please open an issue on GitHub.
