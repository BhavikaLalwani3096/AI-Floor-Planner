"""
catalog.py - Curated Kohler Product Catalog with spatial, aesthetic, and plumbing metadata.
All dimensions are standardized in feet.
"""

KOHLER_CATALOG = [
    # ==================== TOILETS ====================
    {
        "sku": "K-77767IN-0",
        "name": "Kohler ModernLife Edge Wall-Hung Toilet",
        "category": "toilet",
        "style": "Modern Minimalist",
        "tier": "Essential",
        "finish": "Honed White",
        "price_inr": 28500,
        "width": 1.3,
        "depth": 1.8,
        "height": 1.4,
        "clearance_front": 2.0,
        "clearance_sides": 0.8,
        "mount": "wall_hung",
        "drain_type": "wall_drain",
        "watersense": True,
        "gpf": 1.1
    },
    {
        "sku": "K-5722IN-0",
        "name": "Kohler Veil Wall-Hung Dual-Flush Toilet",
        "category": "toilet",
        "style": "Modern Minimalist",
        "tier": "Sculptural",
        "finish": "Gloss White with Concealed Tank",
        "price_inr": 62000,
        "width": 1.35,
        "depth": 2.0,
        "height": 1.4,
        "clearance_front": 2.0,
        "clearance_sides": 0.8,
        "mount": "wall_hung",
        "drain_type": "wall_drain",
        "watersense": True,
        "gpf": 1.0
    },
    {
        "sku": "K-26154IN-0",
        "name": "Kohler Brazn Wall-Hung Intelligent Toilet",
        "category": "toilet",
        "style": "Modern Minimalist",
        "tier": "High-Tech",
        "finish": "Honed Black",
        "price_inr": 185000,
        "width": 1.4,
        "depth": 2.1,
        "height": 1.5,
        "clearance_front": 2.2,
        "clearance_sides": 1.0,
        "mount": "wall_hung",
        "drain_type": "wall_drain",
        "watersense": True,
        "gpf": 1.0
    },

    # ==================== VANITIES ====================
    {
        "sku": "K-99514IN-F69",
        "name": "Kohler Poplin 24\" Floating Vanity",
        "category": "vanity",
        "style": "Modern Minimalist",
        "tier": "Essential",
        "finish": "Claro Walnut & Quartz",
        "price_inr": 54000,
        "width": 2.0,
        "depth": 1.6,
        "height": 2.8,
        "clearance_front": 2.5,
        "clearance_sides": 0.2,
        "mount": "wall_hung",
        "drain_type": "wall_drain",
        "watersense": False,
        "gpf": None
    },
    {
        "sku": "K-99522IN-1WA",
        "name": "Kohler Jacquard 36\" Sculptural Vanity",
        "category": "vanity",
        "style": "Modern Minimalist",
        "tier": "Sculptural",
        "finish": "Fluted Black & Marble",
        "price_inr": 92000,
        "width": 3.0,
        "depth": 1.8,
        "height": 2.9,
        "clearance_front": 2.5,
        "clearance_sides": 0.3,
        "mount": "floor_mounted",
        "drain_type": "wall_drain",
        "watersense": False,
        "gpf": None
    },
    {
        "sku": "K-33553IN-2MB",
        "name": "Kohler Forefront 48\" Double Basin Luxury Vanity",
        "category": "vanity",
        "style": "Modern Minimalist",
        "tier": "High-Tech",
        "finish": "Matte White Quartz with Sensor LED",
        "price_inr": 145000,
        "width": 4.0,
        "depth": 1.9,
        "height": 2.9,
        "clearance_front": 2.8,
        "clearance_sides": 0.4,
        "mount": "wall_hung",
        "drain_type": "wall_drain",
        "watersense": False,
        "gpf": None
    },

    # ==================== FAUCETS ====================
    {
        "sku": "K-14402IN-4AND-BL",
        "name": "Kohler Purist Tall Basin Mixer",
        "category": "faucet",
        "style": "Modern Minimalist",
        "tier": "Essential",
        "finish": "Matte Black",
        "price_inr": 36000,
        "width": 0.4,
        "depth": 0.6,
        "height": 1.1,
        "clearance_front": 0.5,
        "clearance_sides": 0.2,
        "mount": "deck_mount",
        "drain_type": "integrated",
        "watersense": True,
        "gpm": 1.2
    },
    {
        "sku": "K-23511IN-BL",
        "name": "Kohler Parallel Wall-Mount Basin Spout",
        "category": "faucet",
        "style": "Modern Minimalist",
        "tier": "Sculptural",
        "finish": "Matte Black",
        "price_inr": 44000,
        "width": 0.5,
        "depth": 0.8,
        "height": 0.4,
        "clearance_front": 0.5,
        "clearance_sides": 0.2,
        "mount": "wall_mount",
        "drain_type": "integrated",
        "watersense": True,
        "gpm": 1.2
    },
    {
        "sku": "K-108K60-BL",
        "name": "Kohler Sensate Touchless Sensor Basin Faucet",
        "category": "faucet",
        "style": "Modern Minimalist",
        "tier": "High-Tech",
        "finish": "Matte Black",
        "price_inr": 68000,
        "width": 0.4,
        "depth": 0.7,
        "height": 1.0,
        "clearance_front": 0.5,
        "clearance_sides": 0.2,
        "mount": "deck_mount",
        "drain_type": "integrated",
        "watersense": True,
        "gpm": 1.0
    },

    # ==================== SHOWERS & ENCLOSURES ====================
    {
        "sku": "K-706080-L-SHP",
        "name": "Kohler Levity Frameless Sliding Glass Shower Door",
        "category": "shower",
        "style": "Modern Minimalist",
        "tier": "Essential",
        "finish": "Clear Glass & Anodized Silver",
        "price_inr": 58000,
        "width": 3.0,
        "depth": 3.0,
        "height": 6.5,
        "clearance_front": 2.5,
        "clearance_sides": 0.0,
        "mount": "alcove",
        "drain_type": "floor_trap",
        "watersense": True,
        "gpm": 1.75
    },
    {
        "sku": "K-24717IN-BL",
        "name": "Kohler Rainduet Multi-Function Shower System",
        "category": "shower",
        "style": "Modern Minimalist",
        "tier": "Sculptural",
        "finish": "Matte Black Trim & Walk-In Glass Screen",
        "price_inr": 82000,
        "width": 3.5,
        "depth": 3.0,
        "height": 7.0,
        "clearance_front": 2.5,
        "clearance_sides": 0.0,
        "mount": "walk_in",
        "drain_type": "floor_trap",
        "watersense": True,
        "gpm": 1.75
    },
    {
        "sku": "K-26303IN-BL",
        "name": "Kohler Statement Digital Thermostatic Smart Shower",
        "category": "shower",
        "style": "Modern Minimalist",
        "tier": "High-Tech",
        "finish": "Matte Black Touchscreen Controller",
        "price_inr": 165000,
        "width": 4.0,
        "depth": 3.5,
        "height": 7.0,
        "clearance_front": 2.8,
        "clearance_sides": 0.0,
        "mount": "walk_in",
        "drain_type": "floor_trap",
        "watersense": True,
        "gpm": 1.5
    }
]


def get_products_by_filter(category=None, style=None, tier=None, max_price=None):
    """Retrieve catalog items matching constraints with safe fallback."""
    results = KOHLER_CATALOG
    if category:
        results = [p for p in results if p["category"] == category]
    if style:
        style_match = [p for p in results if p["style"] == style]
        if style_match:
            results = style_match
    if tier:
        tier_match = [p for p in results if p["tier"] == tier]
        if tier_match:
            results = tier_match
    if max_price:
        results = [p for p in results if p["price_inr"] <= max_price]
    return results