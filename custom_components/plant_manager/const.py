"""Constants for Plant Manager integration."""

DOMAIN = "plant_manager"

CONF_AI_ENDPOINT = "ai_endpoint"
CONF_AI_API_KEY = "ai_api_key"
CONF_AI_MODEL = "ai_model"
CONF_PLANT_NAME = "plant_name"
CONF_GROWTH_STAGE = "growth_stage"

DEFAULT_AI_ENDPOINT = "https://api.openai.com/v1"
DEFAULT_AI_MODEL = "gpt-4o-mini"

ATTR_PLANT_ID = "plant_id"
ATTR_TASK_ID = "task_id"
ATTR_LAST_COMPLETED = "last_completed"
ATTR_DAYS_SINCE = "days_since"
ATTR_NEXT_DUE = "next_due"
ATTR_OVERDUE = "overdue"

NOTIFICATION_ID_PREFIX = "plant_manager_"

UPDATE_INTERVAL_SECONDS = 300
