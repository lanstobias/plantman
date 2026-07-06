# Quick Start Guide

Get Plant Manager running in 5 minutes.

## 1. Install

```bash
# Copy to your Home Assistant config directory
cp -r custom_components/plant_manager /config/custom_components/
```

## 2. Restart Home Assistant

```bash
# Restart HA to load the integration
# Settings → System → Restart
```

## 3. Add Integration

1. Settings → Devices & Services
2. + Add Integration
3. Search: **Plant Manager**

## 4. Configure AI

Enter your API details:

**OpenAI:**
- Key: `sk-...`
- Endpoint: `https://api.openai.com/v1`
- Model: `gpt-4o-mini`

**Ollama (local):**
- Key: `ollama`
- Endpoint: `http://localhost:11434/v1`
- Model: `llama3.1`

## 5. Add Your First Plant

- Enter: `Monstera Deliciosa`
- Wait 5-10 seconds
- Done!

## 6. Check Entities

Go to the new device to see:
- Days since sensors
- Next due sensors
- Overdue binary sensors
- Complete task buttons

## 7. Complete Your First Task

1. Press **Complete Water** button
2. Watch notification disappear
3. See "Days Since" reset to 0

## Next Steps

- Add more plants (repeat step 5)
- Set up automations (see `EXAMPLES.md`)
- Configure dashboard cards
- Change growth stages (device → ⚙️ → Configure)

## Troubleshooting

**Integration not found?**
```bash
# Check files are in the right place
ls /config/custom_components/plant_manager/
# Should see: __init__.py, manifest.json, etc.
```

**AI connection failed?**
- Verify API key
- Check endpoint URL
- Test with `curl`:
```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_KEY"
```

**No entities created?**
- Check logs: Settings → System → Logs
- Search for: `plant_manager`
- Look for JSON parsing errors

## Files Reference

- **Installation**: `INSTALL.md` - Detailed setup
- **Examples**: `EXAMPLES.md` - Automations & cards  
- **Architecture**: `ARCHITECTURE.md` - Technical docs
- **Summary**: `PROJECT_SUMMARY.md` - Project overview

## API Keys

Get a free OpenAI API key:
- https://platform.openai.com/api-keys
- $5 credit for new accounts
- ~$0.01 per plant with gpt-4o-mini

## Common Tasks

**Add another plant:**
1. Devices & Services → Plant Manager
2. Add Entry → Add Plant

**Change growth stage:**
1. Go to plant device
2. Click ⚙️ (Configure)
3. Select plant and new stage

**Complete task via service:**
```yaml
service: plant_manager.complete_task
data:
  plant_id: "your-plant-id"
  task_id: "water"
```

**Find plant ID:**
```yaml
# In Developer Tools → States
# Search for: binary_sensor.monstera_deliciosa_water_overdue
# Look at attributes → plant_id
```

## Dashboard Card Template

```yaml
type: entities
title: My Plants
entities:
  - binary_sensor.monstera_deliciosa_water_overdue
  - button.monstera_deliciosa_complete_water
  - binary_sensor.basil_water_overdue
  - button.basil_complete_water
```

## Automation Template

```yaml
automation:
  - alias: "Plant Reminder"
    trigger:
      - platform: state
        entity_id: binary_sensor.monstera_deliciosa_water_overdue
        to: "on"
    action:
      - service: notify.mobile_app_phone
        data:
          message: "Water your Monstera!"
```

That's it! You're ready to manage your plants with AI. 🌱
