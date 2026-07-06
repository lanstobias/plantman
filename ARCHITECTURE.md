# Architecture Documentation

## Overview

Plant Manager is a Home Assistant custom integration that uses AI to generate plant care profiles and manages recurring care tasks with automatic notifications.

## Core Design Principles

1. **Dynamic Entity Creation**: Entities are created based on AI-returned task lists, not hardcoded assumptions
2. **Device-Centric**: Each plant is a Device with multiple related entities
3. **AI Abstraction**: Pluggable AI provider interface for future extensibility
4. **Type Safety**: Full type hints and dataclasses throughout
5. **Async First**: All operations are async/await
6. **Clean Separation**: Clear boundaries between storage, coordination, AI, and presentation

## Component Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Home Assistant                          │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Config Flow                             │  │
│  │  - AI Setup (first time)                             │  │
│  │  - Add Plant (subsequent)                            │  │
│  │  - Options Flow (change growth stage)                │  │
│  └────────────┬─────────────────────────────────────────┘  │
│               │                                             │
│               ▼                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Coordinator                             │  │
│  │  - DataUpdateCoordinator                             │  │
│  │  - Central data hub                                  │  │
│  │  - Task completion logic                             │  │
│  │  - Growth stage management                           │  │
│  └────┬────────────────┬──────────────────┬─────────────┘  │
│       │                │                  │                 │
│       ▼                ▼                  ▼                 │
│  ┌─────────┐     ┌─────────┐       ┌──────────────────┐   │
│  │ Storage │     │   AI    │       │   Notification   │   │
│  │   API   │     │Provider │       │     Manager      │   │
│  └─────────┘     └─────────┘       └──────────────────┘   │
│       │                │                  │                 │
│       ▼                ▼                  ▼                 │
│  ┌─────────┐     ┌─────────┐       ┌──────────────────┐   │
│  │  JSON   │     │ OpenAI  │       │   Persistent     │   │
│  │  File   │     │   API   │       │  Notifications   │   │
│  └─────────┘     └─────────┘       └──────────────────┘   │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Entity Platforms                        │  │
│  │                                                      │  │
│  │  Sensor:          Binary Sensor:     Button:        │  │
│  │  - Days Since     - Overdue          - Complete     │  │
│  │  - Next Due                                          │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Plant Addition Flow

```
User Input (Plant Name)
    ↓
Config Flow
    ↓
Coordinator.async_add_plant()
    ↓
AI Provider.get_plant_profile()
    ↓
OpenAI API (JSON Response)
    ↓
PlantProfile (validated)
    ↓
Create Plant + Tasks + Stages
    ↓
Storage.async_add_plant()
    ↓
Coordinator.async_refresh()
    ↓
Entities Created Dynamically
```

### 2. Task Completion Flow

```
Button Press
    ↓
Button.async_press()
    ↓
Coordinator.async_complete_task()
    ↓
Update Task.last_completed = now()
    ↓
Storage.async_update_plant()
    ↓
Coordinator.async_refresh()
    ↓
Entity States Update
    ↓
Notification Manager (removes overdue notification)
```

### 3. Update Cycle

```
Timer (every 5 minutes)
    ↓
Coordinator._async_update_data()
    ↓
Storage.get_all_plants()
    ↓
Return plant dict
    ↓
Entities recalculate state
    ↓
Notification Manager checks overdue
    ↓
Create/Remove notifications as needed
```

## File Structure

```
custom_components/plant_manager/
├── __init__.py                 # Integration setup, service handlers
├── manifest.json               # Integration metadata
├── const.py                    # Constants
│
├── models.py                   # Data models
│   ├── Task                    # Care task with interval
│   ├── GrowthStage            # Growth stage with task overrides
│   ├── PlantProfile           # AI-generated profile
│   └── Plant                   # Complete plant entity
│
├── storage.py                  # Storage API wrapper
│   └── PlantStorage           # Load/save/update plants
│
├── ai_provider.py             # Abstract provider interface
│   └── PlantInfoProvider      # ABC for AI providers
│
├── openai_provider.py         # OpenAI implementation
│   └── OpenAIPlantInfoProvider
│
├── coordinator.py             # Data coordinator
│   └── PlantCoordinator       # DataUpdateCoordinator subclass
│
├── notification_manager.py    # Notification system
│   └── NotificationManager    # Track/create/remove notifications
│
├── entity.py                  # Base entity class
│   └── PlantEntity            # CoordinatorEntity subclass
│
├── sensor.py                  # Sensor platform
│   ├── TaskDaysSinceSensor    # Days since completion
│   └── TaskNextDueSensor      # Next due timestamp
│
├── binary_sensor.py           # Binary sensor platform
│   └── TaskOverdueSensor      # Overdue status
│
├── button.py                  # Button platform
│   └── CompleteTaskButton     # Complete task action
│
├── config_flow.py             # Config and options flow
│   ├── PlantManagerConfigFlow
│   └── PlantManagerOptionsFlow
│
├── services.yaml              # Service definitions
├── strings.json               # UI strings
└── translations/
    └── en.json                # English translations
```

## Data Models

### Task

```python
@dataclass
class Task:
    id: str                     # e.g., "water", "fertilize"
    name: str                   # e.g., "Water", "Fertilize"
    interval_days: int          # Base interval
    last_completed: datetime | None
    
    # Computed properties:
    # - days_since_completed()
    # - next_due_date()
    # - is_overdue()
```

### GrowthStage

```python
@dataclass
class GrowthStage:
    id: str                     # e.g., "seedling"
    name: str                   # e.g., "Seedling"
    task_overrides: dict[str, int]  # task_id -> interval override
```

### PlantProfile

```python
@dataclass
class PlantProfile:
    common_name: str
    scientific_name: str
    variety: str
    description: str
    light_requirements: str
    temperature: str
    humidity: str
    soil: str
    harvest_info: str
    common_issues: str
    tasks: list[dict]           # Raw task definitions
    growth_stages: list[dict]   # Raw stage definitions
```

### Plant

```python
@dataclass
class Plant:
    id: str                     # UUID
    name: str                   # User-provided name
    profile: PlantProfile       # AI-generated profile
    tasks: list[Task]           # Active task instances
    growth_stages: list[GrowthStage]
    current_stage_id: str | None
    created_at: datetime
```

## Storage Format

Stored in `.storage/plant_manager.storage.json`:

```json
{
  "version": 1,
  "data": {
    "plants": {
      "abc-123-uuid": {
        "id": "abc-123-uuid",
        "name": "Monstera Deliciosa",
        "profile": { ... },
        "tasks": [
          {
            "id": "water",
            "name": "Water",
            "interval_days": 7,
            "last_completed": "2026-07-01T10:00:00"
          }
        ],
        "growth_stages": [ ... ],
        "current_stage_id": "mature",
        "created_at": "2026-06-01T12:00:00"
      }
    }
  }
}
```

## AI Provider Interface

### Abstract Interface

```python
class PlantInfoProvider(ABC):
    @abstractmethod
    async def get_plant_profile(self, plant_name: str) -> PlantProfile:
        """Get plant profile from AI."""
```

### OpenAI Implementation

- Uses `openai` Python SDK
- Structured prompt returns JSON only
- Validates response structure
- Configurable endpoint/model for compatibility

### Future Providers

The interface supports adding:
- **OllamaProvider**: Local LLMs
- **AnthropicProvider**: Claude API
- **GeminiProvider**: Google's Gemini
- **CachedProvider**: Lookup from curated database
- **HybridProvider**: Database + AI fallback

## Entity Naming Convention

```
{domain}.{plant_name_slug}_{task_id}_{entity_type}

Examples:
- sensor.monstera_deliciosa_water_days_since
- sensor.monstera_deliciosa_water_next_due
- binary_sensor.monstera_deliciosa_water_overdue
- button.monstera_deliciosa_complete_water
```

## Notification System

### Tracking

- Listens to coordinator updates
- Compares current overdue tasks vs active notifications
- Creates notifications for new overdue tasks
- Removes notifications for completed tasks

### Notification ID Format

```
plant_manager_{plant_id}_{task_id}

Example: plant_manager_abc-123-uuid_water
```

### Automatic Cleanup

- Notifications removed when task completed
- Notifications removed when plant deleted
- All notifications cleaned up on integration unload

## Services

### complete_task

```yaml
service: plant_manager.complete_task
data:
  plant_id: "abc-123-uuid"
  task_id: "water"
```

### set_growth_stage

```yaml
service: plant_manager.set_growth_stage
data:
  plant_id: "abc-123-uuid"
  stage_id: "flowering"
```

## Extension Points

### 1. Additional AI Providers

Implement `PlantInfoProvider` interface:
```python
class CustomProvider(PlantInfoProvider):
    async def get_plant_profile(self, plant_name: str) -> PlantProfile:
        # Your implementation
```

### 2. Additional Entity Types

Add new platforms in `PLATFORMS`:
```python
PLATFORMS = [..., Platform.IMAGE, Platform.CALENDAR]
```

### 3. Sensor Integration

Coordinators can incorporate external sensors:
```python
# In coordinator update:
soil_moisture = hass.states.get('sensor.soil_moisture')
if soil_moisture and soil_moisture.state > 60:
    # Auto-complete watering
```

### 4. Image Storage

Add to `Plant` model:
```python
@dataclass
class Plant:
    ...
    images: list[PlantImage]
```

### 5. Statistics

Add to `Task` model:
```python
@dataclass
class Task:
    ...
    completion_history: list[datetime]
```

## Performance Considerations

- **AI Calls**: Only on plant creation, cached in storage
- **Update Interval**: 5 minutes, configurable
- **Entity Count**: ~4 entities per task per plant
- **Storage**: JSON file, loaded once on startup
- **Notifications**: O(n) where n = number of tasks across all plants

## Testing Recommendations

1. **Unit Tests**: Models, storage, AI provider
2. **Integration Tests**: Coordinator logic, entity creation
3. **End-to-End**: Full config flow → entity creation → task completion
4. **AI Mocking**: Mock AI responses for consistent testing

## Future Architecture Enhancements

1. **Multiple AI Profiles**: Cache multiple AI results, let user choose
2. **Task Templates**: Reusable task definitions
3. **Plant Groups**: Group plants by location/type
4. **History Dashboard**: Track completion patterns
5. **AI Chat**: Ask questions about specific plants
6. **Weather Integration**: Adjust watering based on weather
7. **Calendar Sync**: Export care schedule to calendar
8. **Photo Timeline**: Weekly photo capture and storage
