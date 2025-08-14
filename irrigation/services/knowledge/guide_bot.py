from difflib import get_close_matches
from django.urls import reverse
from django.template.loader import render_to_string
from django.utils.functional import lazy
from enum import Enum


class ResourceType(Enum):
    """Enumeration for different resource types in the help system"""
    ROUTE = 'route'
    INFO = 'info'
    COMMAND = 'command'
    WIDGET = 'widget'
    HELP = 'help'
    CHAT = 'chat'  # New type for chatbot interactions


class IrrigationGuide:
    """Intelligent help system for irrigation management application"""

    def __init__(self):
        """Initialize all knowledge bases with lazy URL resolution"""
        self.resources = {
            ResourceType.ROUTE: self._load_knowledge(),
            ResourceType.INFO: self._load_informational_pages(),
            ResourceType.COMMAND: self._load_control_commands(),
            ResourceType.WIDGET: self._load_dashboard_widgets(),
            ResourceType.HELP: self._load_help_resources(),
            ResourceType.CHAT: self._load_chat_responses()  # New chatbot responses
        }

    def _lazy_reverse(self, view_name):
        """Lazy version of reverse to avoid URL resolution during import"""
        return lazy(reverse, str)(view_name)

    def _load_knowledge(self):
        """Load application routes and navigation information with lazy URLs"""
        return {
            "dashboard": {
                "url": self._lazy_reverse('dashboard'),
                "description": "Main system dashboard showing current status and overview",
                "keywords": ["dashboard", "home", "main page", "status", "overview"],
                "icon": "fa-tachometer-alt",
                "category": "Monitoring"
            },
            "control panel": {
                "url": self._lazy_reverse('control-panel'),
                "description": "Manual control for pumps and valves with real-time adjustments",
                "keywords": ["control", "manual", "pump", "valve", "switch"],
                "icon": "fa-sliders-h",
                "category": "Control"
            },
            "analytics": {
                "url": self._lazy_reverse('visualize-data'),
                "description": "View charts and graphs of historical irrigation data",
                "keywords": ["analytics", "charts", "graphs", "history", "data"],
                "icon": "fa-chart-line",
                "category": "Analysis"
            },
            "download data": {
                "url": self._lazy_reverse('dashboard'),
                "description": "Export sensor data as CSV or Excel for further analysis",
                "keywords": ["download", "export", "get data", "csv", "excel"],
                "icon": "fa-file-export",
                "category": "Data"
            },
            "help": {
                "url": self._lazy_reverse('help'),
                "description": "Access documentation and support resources",
                "keywords": ["help", "support", "documentation", "faq"],
                "icon": "fa-question-circle",
                "category": "Support"
            },
            "privacy": {
                "url": self._lazy_reverse('privacy'),
                "description": "View our privacy policy and data handling practices",
                "keywords": ["privacy", "policy", "data", "protection"],
                "icon": "fa-shield-alt",
                "category": "Legal"
            },
            "terms": {
                "url": self._lazy_reverse('terms'),
                "description": "View terms of service for using our system",
                "keywords": ["terms", "service", "agreement", "legal"],
                "icon": "fa-file-contract",
                "category": "Legal"
            },
            "about": {
                "url": self._lazy_reverse('about'),
                "description": "Learn about our system, team, and achievements",
                "keywords": ["about", "information", "team", "developer"],
                "icon": "fa-info-circle",
                "category": "Information"
            },
            "contact": {
                "url": self._lazy_reverse('contact'),
                "description": "Get in touch with our team for support and inquiries",
                "keywords": ["contact", "support", "help", "email", "phone"],
                "icon": "fa-envelope",
                "category": "Support"
            },
            "profile": {
                "url": self._lazy_reverse('profile'),
                "description": "View and manage your user account settings",
                "keywords": ["profile", "account", "settings", "user"],
                "icon": "fa-user",
                "category": "Account"
            },
            "chatbot": {
                "url": self._lazy_reverse('chatbot'),
                "description": "Interactive help assistant for the irrigation system",
                "keywords": ["chat", "bot", "assistant", "help", "ask"],
                "icon": "fa-robot",
                "category": "Support"
            }
        }

    def _load_informational_pages(self):
        """Load static content pages including privacy and terms"""
        return {
            "about": {
                "template": "irrigation/about.html",
                "description": "Learn about our system, team, and achievements",
                "keywords": ["about", "information", "team", "developer"],
                "icon": "fa-info-circle",
                "category": "Information",
                "content_sections": {
                    "system_overview": "How our irrigation system works",
                    "team": "Our development team",
                    "achievements": "System accomplishments"
                }
            },
            "contact": {
                "template": "irrigation/contact.html",
                "description": "Get in touch with our team for support and inquiries",
                "keywords": ["contact", "support", "help", "email", "phone"],
                "icon": "fa-envelope",
                "category": "Support",
                "contact_methods": {
                    "phone": {
                        "label": "Call Us",
                        "value": "+256 780 443345",
                        "icon": "fa-phone-alt",
                        "action": "tel:+256780443345"
                    },
                    "email": {
                        "label": "Email Us",
                        "value": "nduwayomorris@gmail.com",
                        "icon": "fa-envelope",
                        "action": "mailto:nduwayomorris@gmail.com"
                    },
                    "location": {
                        "label": "Visit Us",
                        "value": "Kyebando roundabout, Kampala City, Uganda",
                        "icon": "fa-map-marker-alt",
                        "action": "https://maps.google.com?q=Kyebando+roundabout,Kampala+City,Uganda"
                    }
                },
                "social_media": {
                    "facebook": "https://www.facebook.com/magnus.morris.79",
                    "twitter": "https://x.com/NduwayoMorris",
                    "linkedin": "https://www.linkedin.com/in/nduwayo-morris",
                    "whatsapp": "https://wa.me/+256780443345"
                }
            }
        }

    def _load_control_commands(self):
        """Load system control commands with enhanced emergency command details"""
        commands = {
            "pump": {
                "description": "Control the water pump (on/off)",
                "keywords": ["pump", "water pump", "activate pump"],
                "icon": "fa-tint",
                "parameters": {
                    "state": {
                        "type": "boolean",
                        "description": "True to turn on, False to turn off",
                        "required": True
                    }
                }
            },
            "valve": {
                "description": "Control irrigation valves (open/close)",
                "keywords": ["valve", "water valve", "open valve"],
                "icon": "fa-faucet",
                "parameters": {
                    "state": {
                        "type": "boolean",
                        "description": "True to open, False to close",
                        "required": True
                    }
                }
            },
            "emergency": {
                "description": "Activate or deactivate emergency stop (immediately shuts down all systems)",
                "keywords": ["emergency", "stop", "shutdown", "safety"],
                "icon": "fa-exclamation-triangle",
                "parameters": {
                    "activate": {
                        "type": "boolean",
                        "description": "True to activate emergency stop, False to reset",
                        "required": True
                    }
                },
                "safety_warning": "Emergency stop will immediately shut down all irrigation systems. Only use in case of actual emergency!",
                "confirmation_required": True
            }
        }

        # Add more commands as needed
        commands.update({
            "mode": {
                "description": "Switch between automatic and manual modes",
                "keywords": ["mode", "switch mode", "automatic", "manual"],
                "icon": "fa-cogs",
                "parameters": {
                    "manual": {
                        "type": "boolean",
                        "description": "True for manual mode, False for automatic",
                        "required": True
                    }
                }
            },
            "threshold": {
                "description": "Set the moisture threshold for automatic irrigation",
                "keywords": ["threshold", "moisture level", "set threshold"],
                "icon": "fa-percentage",
                "parameters": {
                    "value": {
                        "type": "number",
                        "description": "Percentage value (0-100)",
                        "required": True
                    }
                }
            },
            "schedule": {
                "description": "Schedule an irrigation event",
                "keywords": ["schedule", "timer", "plan irrigation"],
                "icon": "fa-clock",
                "parameters": {
                    "time": {
                        "type": "datetime",
                        "description": "When to start irrigation",
                        "required": True
                    },
                    "duration": {
                        "type": "number",
                        "description": "Duration in minutes",
                        "required": True
                    }
                }
            }
        })

        return commands

    def _load_dashboard_widgets(self):
        """Load dashboard monitoring widgets with enhanced details"""
        return {
            "temperature": {
                "description": "Current ambient temperature reading",
                "keywords": ["temp", "heat", "weather"],
                "icon": "fa-temperature-high",
                "unit": "°C",
                "normal_range": "15-35°C",
                "alert_thresholds": {
                    "high": 40,
                    "low": 10
                },
                "widget_type": "gauge",
                "refresh_rate": 5  # seconds
            },
            "humidity": {
                "description": "Current ambient humidity level",
                "keywords": ["moisture", "air", "weather"],
                "icon": "fa-water",
                "unit": "%",
                "normal_range": "30-70%",
                "alert_thresholds": {
                    "high": 80,
                    "low": 20
                },
                "widget_type": "gauge",
                "refresh_rate": 5
            },
            "soil moisture": {
                "description": "Current soil moisture content",
                "keywords": ["soil", "ground", "water"],
                "icon": "fa-leaf",
                "unit": "%",
                "normal_range": "20-60%",
                "alert_thresholds": {
                    "high": 70,
                    "low": 15
                },
                "widget_type": "gauge",
                "refresh_rate": 5
            },
            "pump status": {
                "description": "Current state of the water pump",
                "keywords": ["pump", "water", "irrigation"],
                "icon": "fa-tint",
                "states": {
                    True: "ON",
                    False: "OFF"
                },
                "widget_type": "status",
                "control": True  # Can be controlled from widget
            },
            "valve status": {
                "description": "Current state of the irrigation valve",
                "keywords": ["valve", "water", "flow"],
                "icon": "fa-faucet",
                "states": {
                    True: "OPEN",
                    False: "CLOSED"
                },
                "widget_type": "status",
                "control": True
            },
            "connection status": {
                "description": "System connection status",
                "keywords": ["connection", "online", "offline", "status"],
                "icon": "fa-plug",
                "states": {
                    True: "ONLINE",
                    False: "OFFLINE"
                },
                "widget_type": "indicator"
            }
        }

    def _load_help_resources(self):
        """Load help documentation resources"""
        return {
            "user manual": {
                "description": "Complete system documentation and user guide",
                "keywords": ["manual", "guide", "documentation"],
                "icon": "fa-book",
                "url": self._lazy_reverse('download_user_manual'),
                "content": "The user manual provides comprehensive instructions for setting up, configuring, and troubleshooting the irrigation system."
            },
            "faq": {
                "description": "Frequently asked questions and answers",
                "keywords": ["questions", "answers", "troubleshooting"],
                "icon": "fa-question",
                "questions": [
                    {
                        "question": "How do I reset my system?",
                        "answer": "Use the reset button in the control panel or activate the emergency stop function"
                    },
                    {
                        "question": "How often should I water my plants?",
                        "answer": "Our system automatically adjusts watering schedules based on soil moisture levels, weather forecasts, and plant requirements."
                    },
                    {
                        "question": "Can I manually override the automated system?",
                        "answer": "Yes, you can switch to manual mode in the Control Panel to activate or deactivate irrigation as needed."
                    }
                ]
            }
        }

    def _load_chat_responses(self):
        """Load predefined chatbot responses and templates"""
        return {
            "greeting": {
                "response": "Hello! I'm your irrigation assistant. How can I help you today?",
                "suggestions": ["How do I control the pump?", "What's my soil moisture?", "Emergency stop help"]
            },
            "emergency_info": {
                "response": "The emergency stop immediately shuts down all irrigation systems. Only use in actual emergencies!",
                "follow_up": "Would you like to activate the emergency stop now?",
                "actions": [
                    {
                        "text": "Activate Emergency",
                        "command": "emergency true"
                    },
                    {
                        "text": "Reset Emergency",
                        "command": "emergency false"
                    }
                ]
            },
            "default_error": {
                "response": "I didn't understand that. Try asking about specific features like pumps, valves, or emergency controls.",
                "suggestions": ["Pump control", "Valve settings", "System status"]
            }
        }

    def find_best_match(self, query):
        """Find the most relevant resource for a user query with enhanced matching"""
        query = query.lower().strip()

        # First check for exact matches in all resource types
        for resource_type in ResourceType:
            for name, data in self.resources[resource_type].items():
                if query == name.lower():
                    return name, resource_type

                # Check if query matches any keyword exactly
                if any(query == kw.lower() for kw in data.get("keywords", [])):
                    return name, resource_type

        # Then check for partial matches in keywords
        for resource_type in ResourceType:
            for name, data in self.resources[resource_type].items():
                if any(kw in query for kw in data.get("keywords", [])):
                    return name, resource_type

        # Finally use fuzzy matching as fallback
        all_names = []
        for resource_type in ResourceType:
            all_names.extend(self.resources[resource_type].keys())

        matches = get_close_matches(query, all_names, n=1, cutoff=0.6)
        if matches:
            for resource_type in ResourceType:
                if matches[0] in self.resources[resource_type]:
                    return matches[0], resource_type

        return None, None

    def get_help_response(self, query, request=None):
        """Generate a complete help response for a user query with chatbot formatting"""
        resource_name, resource_type = self.find_best_match(query)

        if not resource_name:
            # Try to match chatbot-specific responses
            if "emergency" in query.lower():
                return self._format_chat_response("emergency_info")
            elif any(greet in query.lower() for greet in ["hello", "hi", "hey"]):
                return self._format_chat_response("greeting")

            return {
                "matched": False,
                "type": "error",
                "query": query,
                "message": "I couldn't find an exact match for your query.",
                "suggestions": self.get_suggestions(query),
                "response_template": "bot_error"  # For frontend formatting
            }

        resource_data = self.resources[resource_type][resource_name]
        response = {
            "matched": True,
            "type": resource_type.value,
            "query": query,
            "resource": {
                "name": resource_name,
                "description": resource_data["description"],
                "icon": resource_data.get("icon", "fa-question-circle")
            },
            "suggestions": self.get_suggestions(query),
            "response_template": self._get_response_template(resource_type)
        }

        # Add type-specific details
        if resource_type == ResourceType.ROUTE:
            response["resource"]["url"] = str(resource_data["url"])
            response["resource"]["category"] = resource_data["category"]

        elif resource_type == ResourceType.INFO:
            response["resource"]["template"] = resource_data["template"]
            if request:
                response["resource"]["content"] = render_to_string(
                    resource_data["template"], {}, request=request
                )
            if "content_sections" in resource_data:
                response["resource"]["sections"] = resource_data["content_sections"]
            if resource_name == "contact":
                response["resource"]["contact_methods"] = resource_data.get("contact_methods", {})
                response["resource"]["social_media"] = resource_data.get("social_media", {})

        elif resource_type == ResourceType.COMMAND:
            response["resource"].update({
                "parameters": resource_data["parameters"],
                "examples": self._get_command_examples(resource_name)
            })
            if "safety_warning" in resource_data:
                response["resource"]["safety_warning"] = resource_data["safety_warning"]
            if "confirmation_required" in resource_data:
                response["resource"]["confirmation_required"] = resource_data["confirmation_required"]

        elif resource_type == ResourceType.WIDGET:
            response["resource"]["details"] = self._get_widget_details(resource_name)

        elif resource_type == ResourceType.HELP:
            if "url" in resource_data:
                response["resource"]["url"] = str(resource_data["url"])
            if "questions" in resource_data:
                response["resource"]["questions"] = resource_data["questions"]
            if "content" in resource_data:
                response["resource"]["content"] = resource_data["content"]

        return response

    def _format_chat_response(self, response_key):
        """Format a predefined chatbot response"""
        chat_data = self.resources[ResourceType.CHAT].get(response_key, {})
        response = {
            "matched": True,
            "type": "chat",
            "response_key": response_key,
            "response": chat_data.get("response", ""),
            "response_template": "chat_response"
        }

        if "suggestions" in chat_data:
            response["suggestions"] = [
                {"name": s, "type": "chat_suggestion"}
                for s in chat_data["suggestions"]
            ]

        if "actions" in chat_data:
            response["actions"] = chat_data["actions"]

        return response

    def _get_response_template(self, resource_type):
        """Get the appropriate frontend template for the response type"""
        templates = {
            ResourceType.ROUTE: "route_response",
            ResourceType.INFO: "info_response",
            ResourceType.COMMAND: "command_response",
            ResourceType.WIDGET: "widget_response",
            ResourceType.HELP: "help_response",
            ResourceType.CHAT: "chat_response"
        }
        return templates.get(resource_type, "default_response")

    def _get_command_examples(self, command_name):
        """Generate usage examples for commands"""
        examples = {
            "pump": [
                "Turn on the pump",
                "Activate water pump",
                "Stop the pump",
                "Set pump to ON"
            ],
            "valve": [
                "Open irrigation valve",
                "Close the water valve",
                "Set valve to OPEN"
            ],
            "emergency": [
                "Activate emergency stop",
                "Trigger emergency shutdown",
                "Reset emergency stop",
                "Disable emergency mode"
            ],
            "mode": [
                "Switch to manual mode",
                "Set to automatic mode",
                "Change to manual control"
            ],
            "threshold": [
                "Set threshold to 40%",
                "Change moisture threshold to 35",
                "Adjust watering threshold"
            ]
        }
        return examples.get(command_name, [])

    def get_suggestions(self, query):
        """Get related resource suggestions based on query with scoring"""
        query_words = set(query.lower().split())
        suggestions = []

        for resource_type in ResourceType:
            for name, data in self.resources[resource_type].items():
                # Skip chatbot responses for general suggestions
                if resource_type == ResourceType.CHAT:
                    continue

                # Score based on word matches
                name_words = set(name.lower().split())
                keyword_words = set(kw.lower() for kw in data.get("keywords", []))
                score = len(query_words & name_words) + len(query_words & keyword_words)

                if score > 0:
                    suggestion = {
                        "name": name,
                        "score": score,
                        "icon": data.get("icon", "fa-link"),
                        "type": resource_type.value
                    }
                    if resource_type == ResourceType.ROUTE:
                        suggestion["url"] = str(data["url"])
                    suggestions.append(suggestion)

        # Return top 3 suggestions by score
        return sorted(suggestions, key=lambda x: x["score"], reverse=True)[:3]

    def get_all_resources(self):
        """Get all available resources across all categories"""
        resources = []

        for resource_type in ResourceType:
            # Skip chatbot responses for the resource listing
            if resource_type == ResourceType.CHAT:
                continue

            for name, data in self.resources[resource_type].items():
                resource = {
                    "name": name,
                    "description": data["description"],
                    "icon": data.get("icon", "fa-question-circle"),
                    "type": resource_type.value
                }
                if resource_type == ResourceType.ROUTE:
                    resource["url"] = str(data["url"])
                resources.append(resource)

        return resources