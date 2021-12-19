work_order_schema = {
    "type": "object",
    "properties": {
        "product": {
            "type": "integer",
            "minimum": 0
        },
        "production": {
            "type": "number",
            "minimum": 0
        },
        "time": {
            "type": "number",
            "minimum": 0
        }
    },
    "required": ["product", "production"]
}

metric_schema = {
    "type": "object",
    "properties": {
        "id": {
            "type": "integer",
            "minimum": 0
        },
        "val": {
            "type": "number"
        },
        "time": {
            "type": "number",
            "minimum": 0
        }
    },
    "required": ["id", "val"]
}