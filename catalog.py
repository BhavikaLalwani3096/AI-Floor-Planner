"""
catalog.py - Expanded Kohler Catalog with Bathtubs, Storage, and Accessories.
All dimensions standardized in feet. Feature vectors: [Scale, Luxury, Minimalism, Eco-Priority].
"""

import math
from typing import List, Dict, Any

CATALOG = [
    # ==================== TOILETS ====================
    {
        "sku": "K-77767IN-0", "name": "ModernLife Edge Wall-Hung Toilet", "category": "toilet",
        "style": "Modern Minimalist", "finish": "Honed White", "price_inr": 28500,
        "width": 1.3, "depth": 1.8, "height": 1.4, "clearance_front": 2.0, "clearance_sides": 0.8,
        "mount": "wall_hung", "watersense": True, "vector": [0.3, 0.2, 0.9, 0.9]
    },
    {
        "sku": "K-5722IN-0", "name": "Veil Sculptural Wall-Hung Toilet", "category": "toilet",
        "style": "Modern Minimalist", "finish": "Gloss White", "price_inr": 62000,
        "width": 1.35, "depth": 2.0, "height": 1.4, "clearance_front": 2.0, "clearance_sides": 0.8,
        "mount": "wall_hung", "watersense": True, "vector": [0.5, 0.6, 0.8, 0.8]
    },
    {
        "sku": "K-26154IN-0", "name": "Brazn Intelligent Smart Toilet", "category": "toilet",
        "style": "Modern Minimalist", "finish": "Honed Black", "price_inr": 185000,
        "width": 1.4, "depth": 2.1, "height": 1.5, "clearance_front": 2.2, "clearance_sides": 1.0,
        "mount": "wall_hung", "watersense": True, "vector": [0.7, 1.0, 0.9, 0.7]
    },
    {
        "sku": "K-3981IN-0", "name": "Reach Compact Floor Toilet", "category": "toilet",
        "style": "Modern Minimalist", "finish": "White", "price_inr": 38000,
        "width": 1.4, "depth": 2.2, "height": 2.4, "clearance_front": 2.0, "clearance_sides": 0.8,
        "mount": "floor_mounted", "watersense": True, "vector": [0.4, 0.3, 0.7, 0.8]
    },

    # ==================== VANITIES ====================
    {
        "sku": "K-99514IN-F69", "name": "Poplin 24\" Floating Vanity", "category": "vanity",
        "style": "Modern Minimalist", "finish": "Claro Walnut & Quartz", "price_inr": 54000,
        "width": 2.0, "depth": 1.6, "height": 2.8, "clearance_front": 2.5, "clearance_sides": 0.2,
        "mount": "wall_hung", "watersense": False, "vector": [0.3, 0.4, 0.8, 0.5]
    },
    {
        "sku": "K-99522IN-1WA", "name": "Jacquard 36\" Sculptural Vanity", "category": "vanity",
        "style": "Modern Minimalist", "finish": "Fluted Black & Marble", "price_inr": 92000,
        "width": 3.0, "depth": 1.8, "height": 2.9, "clearance_front": 2.5, "clearance_sides": 0.3,
        "mount": "floor_mounted", "watersense": False, "vector": [0.6, 0.7, 0.9, 0.4]
    },
    {
        "sku": "K-33553IN-2MB", "name": "Forefront 48\" Double Vanity", "category": "vanity",
        "style": "Modern Minimalist", "finish": "Matte White Quartz", "price_inr": 145000,
        "width": 4.0, "depth": 1.9, "height": 2.9, "clearance_front": 2.8, "clearance_sides": 0.4,
        "mount": "wall_hung", "watersense": False, "vector": [0.9, 0.9, 0.9, 0.4]
    },
    {
        "sku": "K-2833IN-0", "name": "Ceric 30\" Minimalist Basin Console", "category": "vanity",
        "style": "Modern Minimalist", "finish": "Matte Grey", "price_inr": 68000,
        "width": 2.5, "depth": 1.7, "height": 2.8, "clearance_front": 2.5, "clearance_sides": 0.2,
        "mount": "wall_hung", "watersense": False, "vector": [0.4, 0.5, 0.9, 0.6]
    },

    # ==================== SHOWERS ====================
    {
        "sku": "K-706080-L-SHP", "name": "Levity Sliding Glass Enclosure", "category": "shower",
        "style": "Modern Minimalist", "finish": "Clear Glass & Silver", "price_inr": 58000,
        "width": 3.0, "depth": 3.0, "height": 6.5, "clearance_front": 2.5, "clearance_sides": 0.0,
        "mount": "alcove", "watersense": True, "vector": [0.5, 0.4, 0.8, 0.8]
    },
    {
        "sku": "K-24717IN-BL", "name": "Rainduet Walk-In Glass Screen", "category": "shower",
        "style": "Modern Minimalist", "finish": "Matte Black Trim", "price_inr": 82000,
        "width": 3.5, "depth": 3.0, "height": 7.0, "clearance_front": 2.5, "clearance_sides": 0.0,
        "mount": "walk_in", "watersense": True, "vector": [0.6, 0.7, 0.9, 0.8]
    },
    {
        "sku": "K-26303IN-BL", "name": "Statement Smart Digital Shower", "category": "shower",
        "style": "Modern Minimalist", "finish": "Touchscreen Controller", "price_inr": 165000,
        "width": 4.0, "depth": 3.5, "height": 7.0, "clearance_front": 2.8, "clearance_sides": 0.0,
        "mount": "walk_in", "watersense": True, "vector": [0.9, 1.0, 0.9, 0.7]
    },
    {
        "sku": "K-99899IN-CP", "name": "HydroChoice Flush Overhead Shower", "category": "shower",
        "style": "Modern Minimalist", "finish": "Chrome & Glass", "price_inr": 48000,
        "width": 3.0, "depth": 3.0, "height": 6.5, "clearance_front": 2.5, "clearance_sides": 0.0,
        "mount": "corner", "watersense": True, "vector": [0.4, 0.4, 0.8, 0.8]
    },

    # ==================== BATHTUBS (FOR LARGE SUITES) ====================
    {
        "sku": "K-8336IN-0", "name": "Ceric 60\" Freestanding Soaking Tub", "category": "bathtub",
        "style": "Modern Minimalist", "finish": "Lithocast Matte White", "price_inr": 195000,
        "width": 5.0, "depth": 2.6, "height": 2.0, "clearance_front": 2.5, "clearance_sides": 0.5,
        "mount": "freestanding", "watersense": False, "vector": [0.9, 0.9, 0.9, 0.6]
    },
    {
        "sku": "K-18480IN-0", "name": "Veil Sculptural Freestanding Tub", "category": "bathtub",
        "style": "Modern Minimalist", "finish": "Cast Acrylic Gloss White", "price_inr": 260000,
        "width": 5.5, "depth": 2.8, "height": 2.2, "clearance_front": 2.5, "clearance_sides": 0.5,
        "mount": "freestanding", "watersense": False, "vector": [1.0, 1.0, 0.9, 0.5]
    },
    {
        "sku": "K-11343IN-0", "name": "Underscore 60\" Alcove Soaking Tub", "category": "bathtub",
        "style": "Modern Minimalist", "finish": "White Acrylic", "price_inr": 85000,
        "width": 5.0, "depth": 2.5, "height": 1.8, "clearance_front": 2.2, "clearance_sides": 0.0,
        "mount": "alcove", "watersense": False, "vector": [0.7, 0.5, 0.8, 0.6]
    },

    # ==================== TALL STORAGE TOWERS ====================
    {
        "sku": "K-99538IN-F69", "name": "Poplin Tall Linen Tower", "category": "storage",
        "style": "Modern Minimalist", "finish": "Claro Walnut", "price_inr": 48000,
        "width": 1.5, "depth": 1.3, "height": 5.5, "clearance_front": 2.0, "clearance_sides": 0.2,
        "mount": "wall_hung", "watersense": False, "vector": [0.4, 0.5, 0.8, 0.7]
    },
    {
        "sku": "K-99540IN-1WA", "name": "Jacquard Fluted Storage Tower", "category": "storage",
        "style": "Modern Minimalist", "finish": "Fluted Black", "price_inr": 72000,
        "width": 1.8, "depth": 1.4, "height": 5.8, "clearance_front": 2.0, "clearance_sides": 0.2,
        "mount": "floor_mounted", "watersense": False, "vector": [0.6, 0.8, 0.9, 0.6]
    },

    # ==================== FAUCETS ====================
    {
        "sku": "K-14402IN-4AND-BL", "name": "Purist Tall Basin Mixer", "category": "faucet",
        "style": "Modern Minimalist", "finish": "Matte Black", "price_inr": 36000,
        "width": 0.4, "depth": 0.6, "height": 1.1, "clearance_front": 0.5, "clearance_sides": 0.2,
        "mount": "deck_mount", "watersense": True, "vector": [0.2, 0.6, 0.9, 0.8]
    },
    {
        "sku": "K-23511IN-BL", "name": "Parallel Wall-Mount Spout", "category": "faucet",
        "style": "Modern Minimalist", "finish": "Matte Black", "price_inr": 44000,
        "width": 0.5, "depth": 0.8, "height": 0.4, "clearance_front": 0.5, "clearance_sides": 0.2,
        "mount": "wall_mount", "watersense": True, "vector": [0.3, 0.7, 0.9, 0.8]
    },
    {
        "sku": "K-108K60-BL", "name": "Sensate Sensor Touchless Faucet", "category": "faucet",
        "style": "Modern Minimalist", "finish": "Matte Black", "price_inr": 68000,
        "width": 0.4, "depth": 0.7, "height": 1.0, "clearance_front": 0.5, "clearance_sides": 0.2,
        "mount": "deck_mount", "watersense": True, "vector": [0.4, 0.9, 0.8, 0.9]
    },
    {
        "sku": "K-72218IN-CP", "name": "Aleo Basin Mixer", "category": "faucet",
        "style": "Modern Minimalist", "finish": "Polished Chrome", "price_inr": 18500,
        "width": 0.4, "depth": 0.5, "height": 0.8, "clearance_front": 0.5, "clearance_sides": 0.2,
        "mount": "deck_mount", "watersense": True, "vector": [0.2, 0.3, 0.8, 0.8]
    }
]


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    dot = sum(a * b for a, b in zip(v1, v2))
    norm_a = math.sqrt(sum(a * a for a in v1))
    norm_b = math.sqrt(sum(b * b for b in v2))
    return dot / (norm_a * norm_b) if (norm_a and norm_b) else 0.0