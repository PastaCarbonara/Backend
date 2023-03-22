class STANDARDS:
    RESPONSE_NOT_IMPLEMENTED = "Response for this action is not implemented" 
    REQUEST_NOT_IMPLEMENTED = "Request for this action is not implemented" 

actions = {
    "REQUEST_SESSION_MESSAGE": {
        "info": "Action for sending a message to all connected users within a session.",
        "expected_request": {
            "paramaters": {
                "action": "string",
                "payload": {
                    "message": "string"
                }
            }
        },
        "expected_response": {
            "info": STANDARDS.RESPONSE_NOT_IMPLEMENTED,
            "parameters": {}
        }
    },
    "REQUEST_GLOBAL_MESSAGE": {
        "info": "Action for sending a message to all connected users within the whole application.",
        "expected_request": {
            "paramaters": {
                "action": "string",
                "payload": {
                    "message": "string"
                }
            }
        },
        "expected_response": {
            "info": STANDARDS.RESPONSE_NOT_IMPLEMENTED,
            "parameters": {}
        }
    },
    "REQUEST_RECIPE_LIKE": {
        "info": "Action for liking a recipe",
        "expected_request": {
            "paramaters": {
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
    "RESPONSE_CONNECTION_CODE": {
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
    "RESPONSE_SESSION_MESSAGE": {
        "info": "Action where a message was sent to all connections within the session",
        "expected_request": {
            "info": STANDARDS.REQUEST_NOT_IMPLEMENTED,
            "parameters": {}
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
    "RESPONSE_GLOBAL_MESSAGE": {
        "info": "Action where a message was sent to all connections within the whole application",
        "expected_request": {
            "info": STANDARDS.REQUEST_NOT_IMPLEMENTED,
            "parameters": {}
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
    "RESPONSE_RECIPE_MATCH": {
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
}