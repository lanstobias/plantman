# Installation Guide

## Prerequisites

- Home Assistant 2024.1 or newer
- OpenAI API key (or compatible provider like Ollama, LM Studio)
- Basic familiarity with Home Assistant custom components

## Installation Steps

### 1. Copy Files

Copy the entire `custom_components/plant_manager` directory to your Home Assistant configuration directory:

```
/config/custom_components/plant_manager/
```

Your directory structure should look like:
```
/config/
  ├── custom_components/
  │   └── plant_manager/
  │       ├── __init__.py
  │       ├── manifest.json
  │       ├── config_flow.py
  │       ├── const.py
  │       ├── coordinator.py
  │       ├── models.py
  │       ├── storage.py
  │       ├── ai_provider.py
  │       ├── openai_provider.py
  │       ├── notification_manager.py
  │       ├── entity.py
  │       ├── sensor.py
  │       ├── binary_sensor.py
  │       ├── button.py
  │       ├── services.yaml
  │       ├── strings.json
  │       └── translations/
  │           └── en.json
  ├── configuration.yaml
  └── ...
```

### 2. Restart Home Assistant

Restart Home Assistant completely to load the new integration.

### 3. Add Integration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for **Plant Manager**
4. Click on it to start configuration

### 4. Configure AI Provider

On first setup, enter your AI provider credentials:

- **API Key**: Your OpenAI API key (get one at https://platform.openai.com)
- **API Endpoint**: `https://api.openai.com/v1` (default)
- **Model**: `gpt-4o-mini` (default, or use `gpt-4o` for better results)

#### Using Alternative Providers

**Ollama (local AI)**:
- API Endpoint: `http://localhost:11434/v1`
- API Key: `ollama` (any value works)
- Model: `llama3.1` or your installed model

**LM Studio (local AI)**:
- API Endpoint: `http://localhost:1234/v1`
- API Key: `lm-studio` (any value works)
- Model: Your loaded model name

### 5. Add Your First Plant

1. After AI setup, you'll see the "Add Plant" screen
2. Enter a plant name like:
   - `Monstera Deliciosa`
   - `Orange Habanero`
   - `Thai Basil`
   - `Sungold Tomato`
3. Click **Submit**

The AI will generate a complete care profile. This may take 5-15 seconds.

### 6. Add More Plants

To add additional plants:
1. Go back to **Settings** → **Devices & Services**
2. Find **Plant Manager**
3. Click **Add Plant** again
4. Repeat for each plant

## Verifying Installation

After adding a plant, you should see:

1. **Device**: A new device named after your plant
2. **Sensors**: Days since and next due date for each task
3. **Binary Sensors**: Overdue status for each task
4. **Buttons**: Complete task buttons for each task

Example entities for a "Monstera Deliciosa" with standard tasks:
- `sensor.monstera_deliciosa_water_days_since`
- `sensor.monstera_deliciosa_water_next_due`
- `binary_sensor.monstera_deliciosa_water_overdue`
- `button.monstera_deliciosa_complete_water`
- (Similar entities for fertilize, prune, rotate, etc.)

## Troubleshooting

### Integration Not Found

- Ensure files are in the correct directory
- Restart Home Assistant completely
- Check logs for errors: **Settings** → **System** → **Logs**

### AI Connection Failed

- Verify API key is correct
- Check endpoint URL (must include `/v1` for OpenAI)
- Ensure internet connectivity
- For local providers, verify the service is running

### No Entities Created

- Check Home Assistant logs for errors
- Verify the AI returned valid JSON
- Try adding the plant again
- Try a different model if using a local provider

### Entities Not Updating

- Check that the coordinator is running (look for errors in logs)
- Verify storage file exists: `.storage/plant_manager.storage.json`
- Restart the integration: **Devices & Services** → **Plant Manager** → **⋮** → **Reload**

## Next Steps

After installation:
1. Complete initial tasks to start tracking
2. Set up automations (see `EXAMPLES.md`)
3. Configure growth stages via integration options
4. Add dashboard cards to monitor your plants

## Uninstallation

To remove the integration:
1. Remove all plant devices: **Devices & Services** → **Plant Manager** → Select device → **Delete**
2. Remove the integration: **Devices & Services** → **Plant Manager** → **Delete**
3. Delete the `custom_components/plant_manager` directory
4. Restart Home Assistant
