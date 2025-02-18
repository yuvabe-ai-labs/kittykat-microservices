from typing import Any, Dict, List
from pydantic import BaseModel
from typing import List, Dict, Any


class MoodboardPromptsRequest(BaseModel):
    no_of_prompts: int = 3
    brand_details: List[Dict[str, Any]]
    project_details: List[Dict[str, Any]]
    visual_theme: Dict[str, Any]

    class Config:
        json_schema_extra = {
            "example": {
                "brand_details": [
                    {
                        "brand_category": ["Luxury Furniture", "Home Decor"],
                        "brand_colors": ["#4B0082", "#FFD700", "#FFFFFF"],
                        "brand_description": "SWYFT specializes in premium furniture collections designed to elevate modern living spaces with style and comfort.",
                        "brand_fonts": ["Montserrat", "Lora"],
                        "brand_name": "SWYFT",
                        "brand_tone": "Elegant, Modern, Approachable",
                        "mission_statement": "To bring timeless elegance and comfort into every home with innovative furniture solutions.",
                        "target_audience": [
                            "Homeowners seeking premium furniture",
                            "Interior design enthusiasts",
                        ],
                    }
                ],
                "no_of_prompts": 3,
                "project_details": [
                    {
                        "additional_details": "The campaign should highlight the premium quality and versatility of SWYFT furniture, featuring visually striking settings. Incorporate hashtags like #SWYFTLiving and #VelvetCollection.",
                        "aspirations": "Establish SWYFT as a leading furniture brand among Gen Z and Gen X, with a 20% increase in showroom visits.",
                        "campaign_ideas": "Showcase furniture in dimly lit, luxurious settings to emphasize rich textures and elegant designs, creating a unique mood.",
                        "category": ["Digital Marketing", "Product Photography"],
                        "competitor_details": "Competitors include brands like West Elm, Article, and Crate & Barrel, known for stylish and contemporary furniture.",
                        "name": "Velvet Elegance Campaign",
                        "output_size_options": [
                            "1080x1080 (Instagram post)",
                            "1920x1080 (YouTube video)",
                            "1080x1920 (Instagram story/Reels)",
                        ],
                        "team_responsibilities": {
                            "Creative Team": "Develop moodboard, visuals, and photoshoots.",
                            "Marketing Team": "Strategize and execute campaign rollout.",
                            "Analytics Team": "Track campaign performance and engagement metrics.",
                        },
                        "visuals": "Moody and dramatic settings with dark rooms and focused lighting highlighting the texture and color of the velvet furniture.",
                    }
                ],
            }
        }


class MoodboardPromptsResponse(BaseModel):
    image_prompts: List[str]
