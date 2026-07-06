# Usage Examples

## Dashboard Cards

### Entities Card - Single Plant

```yaml
type: entities
title: Monstera Deliciosa
entities:
  - entity: sensor.monstera_deliciosa_water_days_since
    name: Days Since Watering
  - entity: sensor.monstera_deliciosa_water_next_due
    name: Next Water Due
  - entity: binary_sensor.monstera_deliciosa_water_overdue
    name: Watering Overdue
  - entity: button.monstera_deliciosa_complete_water
    name: Water Now
  - entity: sensor.monstera_deliciosa_fertilize_days_since
    name: Days Since Fertilizing
  - entity: sensor.monstera_deliciosa_fertilize_next_due
    name: Next Fertilize Due
  - entity: button.monstera_deliciosa_complete_fertilize
    name: Fertilize Now
```

### Glance Card - Overview

```yaml
type: glance
title: Plant Status
entities:
  - entity: binary_sensor.monstera_deliciosa_water_overdue
    name: Monstera Water
  - entity: binary_sensor.basil_water_overdue
    name: Basil Water
  - entity: binary_sensor.tomato_water_overdue
    name: Tomato Water
  - entity: binary_sensor.monstera_deliciosa_fertilize_overdue
    name: Monstera Fertilize
```

### Conditional Card - Only Show Overdue

```yaml
type: conditional
conditions:
  - entity: binary_sensor.monstera_deliciosa_water_overdue
    state: "on"
card:
  type: entities
  title: Overdue Tasks
  entities:
    - entity: binary_sensor.monstera_deliciosa_water_overdue
      name: Monstera needs water!
    - entity: button.monstera_deliciosa_complete_water
      name: Mark as watered
```

### Markdown Card - Plant Info

```yaml
type: markdown
title: Monstera Care Guide
content: |
  **Scientific Name**: Monstera deliciosa
  
  **Light**: Bright indirect light
  **Temperature**: 65-75°F (18-24°C)
  **Humidity**: 60-80%
  
  **Current Tasks**:
  - Water: {{ states('sensor.monstera_deliciosa_water_days_since') }} days ago
  - Fertilize: {{ states('sensor.monstera_deliciosa_fertilize_days_since') }} days ago
```

## Automations

### Send Mobile Notification When Overdue

```yaml
automation:
  - alias: "Plant Care Reminder - Watering"
    description: "Notify when any plant needs watering"
    trigger:
      - platform: state
        entity_id:
          - binary_sensor.monstera_deliciosa_water_overdue
          - binary_sensor.basil_water_overdue
          - binary_sensor.tomato_water_overdue
        to: "on"
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "Plant Needs Water"
          message: "{{ trigger.to_state.attributes.friendly_name }} is overdue!"
          data:
            priority: high
            tag: "plant-water-{{ trigger.entity_id }}"
```

### Daily Morning Summary

```yaml
automation:
  - alias: "Plant Care Daily Summary"
    description: "Morning summary of plants needing care"
    trigger:
      - platform: time
        at: "08:00:00"
    condition:
      - condition: or
        conditions:
          - condition: state
            entity_id: binary_sensor.monstera_deliciosa_water_overdue
            state: "on"
          - condition: state
            entity_id: binary_sensor.monstera_deliciosa_fertilize_overdue
            state: "on"
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "Plant Care Today"
          message: "You have {{ expand(state_attr('automation.plant_care_daily_summary', 'entity_id')) | selectattr('state', 'eq', 'on') | list | count }} overdue tasks"
```

### Auto-Complete After Manual Watering

```yaml
automation:
  - alias: "Auto-Complete Plant Watering"
    description: "Automatically mark watering complete when moisture detected"
    trigger:
      - platform: numeric_state
        entity_id: sensor.monstera_soil_moisture
        above: 60
    condition:
      - condition: state
        entity_id: binary_sensor.monstera_deliciosa_water_overdue
        state: "on"
    action:
      - service: plant_manager.complete_task
        data:
          plant_id: "your-plant-id-here"
          task_id: "water"
      - service: notify.mobile_app_your_phone
        data:
          title: "Plant Watered"
          message: "Monstera watering automatically logged"
```

### Change Growth Stage Automatically

```yaml
automation:
  - alias: "Tomato - Switch to Flowering Stage"
    description: "Automatically switch tomato to flowering stage"
    trigger:
      - platform: time
        at: "00:00:00"
    condition:
      - condition: template
        value_template: "{{ (now() - state_attr('sensor.tomato_age', 'created_at') | as_datetime).days > 45 }}"
    action:
      - service: plant_manager.set_growth_stage
        data:
          plant_id: "your-plant-id-here"
          stage_id: "flowering"
```

### TTS Reminder

```yaml
automation:
  - alias: "Plant Care Voice Reminder"
    description: "Speak reminder when entering home"
    trigger:
      - platform: state
        entity_id: person.your_name
        to: "home"
    condition:
      - condition: state
        entity_id: binary_sensor.monstera_deliciosa_water_overdue
        state: "on"
    action:
      - service: tts.google_translate_say
        entity_id: media_player.living_room_speaker
        data:
          message: "Don't forget to water your Monstera!"
```

### LED Indicator

```yaml
automation:
  - alias: "Plant Care LED Indicator"
    description: "Turn on red LED when plants need care"
    trigger:
      - platform: state
        entity_id:
          - binary_sensor.monstera_deliciosa_water_overdue
          - binary_sensor.basil_water_overdue
    action:
      - choose:
          - conditions:
              - condition: or
                conditions:
                  - condition: state
                    entity_id: binary_sensor.monstera_deliciosa_water_overdue
                    state: "on"
                  - condition: state
                    entity_id: binary_sensor.basil_water_overdue
                    state: "on"
            sequence:
              - service: light.turn_on
                target:
                  entity_id: light.plant_care_indicator
                data:
                  color_name: red
                  brightness: 255
        default:
          - service: light.turn_off
            target:
              entity_id: light.plant_care_indicator
```

## Scripts

### Complete All Overdue Tasks

```yaml
script:
  complete_all_overdue_tasks:
    alias: "Complete All Overdue Plant Tasks"
    sequence:
      - service: plant_manager.complete_task
        data:
          plant_id: "monstera-id"
          task_id: "water"
      - service: plant_manager.complete_task
        data:
          plant_id: "monstera-id"
          task_id: "fertilize"
      - service: notify.mobile_app_your_phone
        data:
          title: "Plant Care Complete"
          message: "All tasks logged!"
```

### Weekly Plant Care Routine

```yaml
script:
  weekly_plant_care:
    alias: "Weekly Plant Care Routine"
    sequence:
      - service: plant_manager.complete_task
        data:
          plant_id: "monstera-id"
          task_id: "rotate"
      - delay: "00:00:02"
      - service: plant_manager.complete_task
        data:
          plant_id: "basil-id"
          task_id: "rotate"
      - delay: "00:00:02"
      - service: plant_manager.complete_task
        data:
          plant_id: "monstera-id"
          task_id: "mist"
```

## Node-RED Examples

### Flow: Complete Task via Button

```json
[
    {
        "id": "water_plant_button",
        "type": "inject",
        "name": "Water Monstera",
        "topic": "",
        "payload": "",
        "payloadType": "date",
        "repeat": "",
        "crontab": "",
        "once": false
    },
    {
        "id": "call_service",
        "type": "api-call-service",
        "name": "Complete Water Task",
        "server": "home_assistant",
        "service_domain": "plant_manager",
        "service": "complete_task",
        "data": "{\"plant_id\":\"monstera-id\",\"task_id\":\"water\"}",
        "dataType": "json"
    }
]
```

## Template Sensors

### Count Overdue Tasks

```yaml
template:
  - sensor:
      - name: "Total Overdue Plant Tasks"
        state: >
          {{ states.binary_sensor 
             | selectattr('entity_id', 'search', 'overdue') 
             | selectattr('state', 'eq', 'on') 
             | list | count }}
```

### Next Task Due

```yaml
template:
  - sensor:
      - name: "Next Plant Task"
        state: >
          {% set next = states.sensor 
             | selectattr('entity_id', 'search', 'next_due') 
             | rejectattr('state', 'eq', 'unavailable')
             | sort(attribute='state') 
             | first %}
          {{ next.attributes.friendly_name if next else 'None' }}
```
