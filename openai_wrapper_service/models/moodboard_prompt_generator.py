from typing import Any, Dict, List
from pydantic import BaseModel
from typing import List, Dict, Any


class MoodboardPromptsRequest(BaseModel):
    no_of_prompts: int = 1
    brand_details: List[Dict[str, Any]]
    project_details: List[Dict[str, Any]]

    class Config:
        json_schema_extra = {
            "example": {
                "no_of_prompts": 5,
                "brand_details": [
                    {
                        "brand_name": "EcoSphere",
                        "brand_category": ["Sustainability", "Eco-Friendly Products"],
                        "brand_description": "EcoSphere is a leading provider of environmentally friendly products aimed at reducing carbon footprints and promoting sustainable living.",
                        "brand_colors": ["#00A86B", "#FFD700", "#FFFFFF"],
                        "brand_fonts": ["Roboto", "Open Sans"],
                        "target_audience": [
                            "Environmentally conscious individuals",
                            "Eco-friendly businesses",
                        ],
                        "brand_tone": "Informative, Empowering, Trustworthy",
                        "mission_statement": "To inspire and empower individuals and organizations to adopt sustainable practices for a greener planet.",
                    }
                ],
                "project_details": [
                    {
                        "name": "Green Living Campaign",
                        "category": ["Digital Marketing", "Content Creation"],
                        "campaign_ideas": "Launch a series of short videos showcasing eco-friendly practices, featuring tips for reducing waste, and highlighting EcoSphere products in use.",
                        "visuals": "Bright and vibrant visuals with green tones, clean aesthetics, and photos of people using EcoSphere products in real-life scenarios.",
                        "output_size_options": [
                            "1080x1080 (Instagram post)",
                            "1920x1080 (YouTube video)",
                            "1080x1920 (Instagram story/Reels)",
                        ],
                        "aspirations": "Position EcoSphere as a go-to brand for sustainability enthusiasts and drive a 30% increase in website traffic.",
                        "competitor_details": "Competitors include brands like Patagonia, Green Works, and Seventh Generation, which focus on eco-friendly products and marketing strategies.",
                        "additional_details": "The campaign should integrate user-generated content to increase authenticity. Incorporate hashtags like #EcoSphereLife and #GreenLivingChallenge to encourage audience participation.",
                        "team_responsibilities": {
                            "Creative Team": "Develop campaign visuals and content.",
                            "Marketing Team": "Plan and execute digital ad strategies.",
                            "Analytics Team": "Track and report campaign performance.",
                        },
                    }
                ],
            }
        }


class MoodboardPromptsResponse(BaseModel):
    image_prompts: List[str]
