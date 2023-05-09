"""
Documentation for the types of connection codes the server accepts
and returns.
"""


import enum


class STANDARDS(str, enum.Enum):
    """
    Standard messages.
    """
    RESPONSE_NOT_IMPLEMENTED = "Response for this action is not implemented"
    REQUEST_NOT_IMPLEMENTED = "Request for this action is not implemented"


actions = {
    "CONNECTION_CODE": {
        "info": "Action for responding with a HTTP status code",
        "expected_request": {
            "info": STANDARDS.REQUEST_NOT_IMPLEMENTED,
            "parameters": {}
        },
        "expected_response": {
            "info": "The code parameter will use HTTP status codes",
            "parameters": {
                "action": "string",
                "payload": {
                    "code": "integer",
                    "message": "string"
                }
            }
        }
    },
    "GLOBAL_MESSAGE": {
        "info": "Action for sending a message to all connected users within the whole application.",
        "expected_request": {
            "parameters": {
                "action": "string",
                "payload": {
                    "message": "string"
                }
            }
        },
        "expected_response": {
            "parameters": {
                "action": "string",
                "payload": {
                    "message": "string"
                }
            }
        }
    },
    "RECIPE_MATCH": {
        "info": "Action where a match is received",
        "expected_request": {
            "info": STANDARDS.REQUEST_NOT_IMPLEMENTED,
            "parameters": {}
        },
        "expected_response": {
            "info": "payload -> recipe is the same response object as when getting a recipe",
            "parameters": {
                "action": "string",
                "payload": {
                    "message": "string",
                    "recipe": "json"
                }
            }
        }
    },
    "RECIPE_SWIPE": {
        "info": "Action for liking a recipe",
        "expected_request": {
            "parameters": {
                "action": "string",
                "payload": {
                    "like": "boolean",
                    "recipe_id": "integer"
                }
            }
        },
        "expected_response": {
            "info": STANDARDS.RESPONSE_NOT_IMPLEMENTED,
            "parameters": {}
        }
    },
    "SESSION_MESSAGE": {
        "info": "Action for sending a message to all connected users within a session.",
        "expected_request": {
            "parameters": {
                "action": "string",
                "payload": {
                    "message": "string"
                }
            }
        },
        "expected_response": {
            "parameters": {
                "action": "string",
                "payload": {
                    "message": "string"
                }
            }
        }
    },
    "SESSION_STATUS_UPDATE": {
        "info": "Action for updating the session status.",
        "expected_request": {
            "parameters": {
                "action": "string",
                "payload": {
                    "status": "string"
                }
            }
        },
        "expected_response": {
            "parameters": {
                "action": "string",
                "payload": {
                    "status": "string"
                }
            }
        }
    },
}
