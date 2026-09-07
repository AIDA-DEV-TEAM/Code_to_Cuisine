"""
Application Configuration — Code to Cuisine AI Culinary Engine.
International, cuisine-agnostic configuration.
"""

# ─── App ───────────────────────────────────────────────────────────────────
APP_NAME = "Code to Cuisine — AI Culinary Engine"
APP_VERSION = "4.0.0"
APP_DESCRIPTION = "Multi-agent AI recipe engine for any cuisine, any ingredients"

UI_PAGE_TITLE = APP_NAME
UI_PAGE_ICON = "🍽️"
UI_LAYOUT = "wide"

# ─── LLM ──────────────────────────────────────────────────────────────────
LLM_MODEL_NAME = "openai/gpt-oss-120b"
LLM_TIMEOUT = 180.0
LLM_MAX_RETRIES = 3
LLM_DEFAULT_TEMPERATURE = 0.3
LLM_PRECISE_TEMPERATURE = 0.1
LLM_IDEATION_TEMPERATURE = 0.85
LLM_CREATIVE_TEMPERATURE = 0.7
LLM_MAX_TOKENS = 8000

# ─── Workflow ─────────────────────────────────────────────────────────────
WORKFLOW_MAX_VALIDATION_RETRIES = 3
WORKFLOW_ENABLE_FALLBACK_RECIPES = True
NUM_DISH_OPTIONS = 5               # 4-5 recipe suggestions
CHALLENGE_TIMELINE_MINUTES = 60   # 60-minute cook limit

# ─── Cuisines — Balanced global list (alphabetical, no bias) ──────────────
SUPPORTED_CUISINES = [
    "American",
    "Brazilian",
    "Chinese",
    "Ethiopian",
    "French",
    "Greek",
    "Indian",
    "Italian",
    "Japanese",
    "Korean",
    "Lebanese",
    "Mexican",
    "Moroccan",
    "Persian",
    "Peruvian",
    "Spanish",
    "Thai",
    "Turkish",
    "Vietnamese",
    "West African",
    "Let AI decide",
]

# ─── Cuisine Flavor Pairing Map ───────────────────────────────────────────
# "uniform"    → maximize shared flavor compounds (harmonic, cohesive)
# "contrasting"→ build orthogonal layers through spice & acid contrast
CUISINE_PAIRING_MAP = {
    "American":     "uniform",
    "Brazilian":    "contrasting",
    "Chinese":      "contrasting",
    "Ethiopian":    "contrasting",
    "French":       "uniform",
    "Greek":        "uniform",
    "Indian":       "contrasting",
    "Italian":      "uniform",
    "Japanese":     "uniform",
    "Korean":       "contrasting",
    "Lebanese":     "contrasting",
    "Mexican":      "contrasting",
    "Moroccan":     "contrasting",
    "Persian":      "contrasting",
    "Peruvian":     "contrasting",
    "Spanish":      "uniform",
    "Thai":         "contrasting",
    "Turkish":      "contrasting",
    "Vietnamese":   "contrasting",
    "West African": "contrasting",
    "Let AI decide": "contrasting",
}

# ─── Cuisine flavor identity descriptions (used in prompts) ───────────────
CUISINE_FLAVOR_IDENTITY = {
    "American":     "Bold, hearty, BBQ-smoked, sweet-savory balance, comfort-driven",
    "Brazilian":    "Tropical, farofa-rich, slow-cooked feijoada depth, citrus-bright",
    "Chinese":      "Umami-forward, wok-hei char, sweet-sour-salty trinity, ginger-scallion base",
    "Ethiopian":    "Berbere-spiced, slow-braised, injera-tangy, earthy lentil depth",
    "French":       "Butter-enriched, herbes de Provence, classical stock reductions, delicate",
    "Greek":        "Olive-oil-drenched, lemon-bright, oregano-scented, fresh and clean",
    "Indian":       "Tadka-layered, whole-spice-bloomed, tamarind-jaggery sweet-sour, ghee-rich",
    "Italian":      "Tomato-bright, basil-herbed, al-dente texture, Parmesan umami depth",
    "Japanese":     "Dashi umami, mirin-sake glaze, clean-minimal, wasabi-sharp accent",
    "Korean":       "Gochujang-spicy, doenjang-fermented, sesame-nutty, garlic-heavy",
    "Lebanese":     "Sumac-tangy, za'atar-herbed, pomegranate molasses sweet-sour, tahini-rich",
    "Mexican":      "Chili-layered, cumin-earthy, lime-bright, slow mole complexity",
    "Moroccan":     "Ras el hanout-warm, preserved lemon-bright, honey-sweet, saffron-golden",
    "Persian":      "Rose water-floral, saffron-golden, pomegranate-tart, herb-generous",
    "Peruvian":     "Aji amarillo-fruity-hot, huacatay-herbal, citrus-bright ceviche acid",
    "Spanish":      "Smoked paprika-deep, saffron-golden, olive-oil-rich, Iberian umami",
    "Thai":         "Lemongrass-citrus, galangal-sharp, fish sauce-funky, coconut-cream-sweet",
    "Turkish":      "Bulgur-nutty, pomegranate-tart, cumin-earthy, yogurt-tangy",
    "Vietnamese":   "Fish sauce-funky, lime-bright, fresh herb-forward, nuoc cham-balanced",
    "West African": "Palm oil-rich, fermented locust bean-funky, scotch bonnet-hot, starchy base",
    "Let AI decide": "Choose the most suitable cuisine for the given ingredients",
}

# ─── Appliances ───────────────────────────────────────────────────────────
SUPPORTED_APPLIANCES = [
    "Stovetop / Gas hob",
    "Oven / Grill",
    "Pressure Cooker / Instant Pot",
    "Wok",
    "Cast Iron Pan / Skillet",
    "Steamer",
    "Air Fryer",
    "Slow Cooker",
    "Blender / Food Processor",
    "Microwave",
    "Grill / Barbecue",
    "Tawa / Griddle",
    "Tandoor",
]

SUPPORTED_SKILL_LEVELS = ["Beginner", "Intermediate", "Advanced", "Professional"]

SUPPORTED_DIETARY_RESTRICTIONS = [
    "Vegetarian",
    "Vegan",
    "Pescatarian",
    "Gluten-Free",
    "Dairy-Free",
    "Nut-Free",
    "Egg-Free",
    "Low-Sodium",
    "Low-Carb / Keto",
    "Halal",
    "Kosher",
]

CHEF_CONTEXT_OPTIONS = [
    "Everyday home cooking",
    "Fine dining / Restaurant-quality",
    "Street food / Casual",
    "Festive / Celebration",
    "Quick weeknight meal",
    "Competition / Showcase",
    "Comfort food",
    "Health-conscious",
]

SUPPORTED_CHEF_TECHNIQUES = [
    "Sautéing",
    "Braising",
    "Roasting",
    "Steaming",
    "Deep frying",
    "Stir-frying (Wok)",
    "Grilling / Char-grilling",
    "Slow-cooking",
    "Poaching",
    "Blanching",
    "Marinating",
    "Fermenting / Pickling",
    "Smoking",
    "Sous-vide",
    "Caramelising",
    "Emulsifying (sauces)",
    "Tempering (spices / chocolate)",
    "Flambéing",
]

# ─── Comprehensive global ingredient suggestions (veg + non-veg) ──────────
GLOBAL_INGREDIENT_SUGGESTIONS = sorted([
    # ── Proteins — Animal ──
    "Chicken breast", "Chicken thigh", "Chicken drumstick", "Whole chicken",
    "Beef mince / Ground beef", "Beef steak (sirloin)", "Beef brisket", "Lamb chops",
    "Lamb mince", "Pork belly", "Pork loin", "Bacon", "Ham", "Prosciutto",
    "Salmon fillet", "Tuna (fresh)", "Tuna (canned)", "Cod fillet", "Sea bass",
    "Mackerel", "Sardines", "Anchovies", "Prawns / Shrimp", "Crab meat",
    "Lobster", "Squid / Calamari", "Clams", "Mussels", "Scallops",
    "Duck breast", "Turkey breast", "Quail", "Venison",
    "Eggs", "Egg yolks",

    # ── Proteins — Plant ──
    "Tofu (firm)", "Tofu (silken)", "Tempeh", "Seitan / Wheat gluten",
    "Paneer", "Halloumi",
    "Red lentils", "Green lentils", "Brown lentils", "Black lentils (beluga)",
    "Chickpeas (canned)", "Chickpeas (dried)", "Black beans", "Kidney beans",
    "Cannellini beans", "Pinto beans", "Edamame", "Mung beans", "Adzuki beans",
    "Green peas", "Split peas", "Fava beans",

    # ── Dairy & Alternatives ──
    "Whole milk", "Skimmed milk", "Oat milk", "Almond milk", "Coconut milk",
    "Heavy cream", "Sour cream", "Greek yogurt", "Plain yogurt", "Crème fraîche",
    "Butter", "Ghee", "Cream cheese", "Ricotta", "Mascarpone",
    "Parmesan", "Cheddar", "Mozzarella", "Gruyère", "Feta cheese",
    "Blue cheese", "Brie", "Goat cheese",

    # ── Vegetables ──
    "Onion", "Red onion", "Spring onion / Scallion", "Shallot", "Leek",
    "Garlic", "Ginger", "Galangal", "Lemongrass",
    "Tomato", "Cherry tomato", "Sun-dried tomato", "Tomato paste / Purée",
    "Bell pepper (red)", "Bell pepper (yellow)", "Bell pepper (green)",
    "Chilli / Jalapeño", "Green chilli", "Red chilli", "Scotch bonnet",
    "Carrot", "Celery", "Parsnip", "Turnip", "Beetroot",
    "Broccoli", "Cauliflower", "Romanesco", "Brussels sprouts",
    "Cabbage", "Red cabbage", "Savoy cabbage", "Bok choy / Pak choi",
    "Spinach", "Kale", "Swiss chard", "Rocket / Arugula", "Watercress",
    "Lettuce", "Iceberg lettuce", "Romaine lettuce",
    "Courgette / Zucchini", "Aubergine / Eggplant", "Cucumber",
    "Mushroom (button)", "Portobello mushroom", "Shiitake mushroom",
    "Oyster mushroom", "Dried porcini mushroom",
    "Sweet potato", "Potato", "Purple potato", "Baby potatoes",
    "Corn / Maize", "Baby corn", "Sweetcorn (canned)",
    "Green beans / French beans", "Asparagus", "Peas (frozen)",
    "Artichoke", "Fennel", "Radicchio", "Endive",
    "Pumpkin / Butternut squash", "Acorn squash", "Yam", "Cassava / Yuca",
    "Plantain", "Taro", "Lotus root",
    "Bamboo shoots (canned)", "Water chestnuts", "Bean sprouts",
    "Okra", "Jackfruit (young / green)",

    # ── Fruits ──
    "Lemon", "Lime", "Orange", "Grapefruit", "Yuzu",
    "Apple", "Pear", "Mango", "Papaya", "Pineapple", "Guava",
    "Banana", "Plantain", "Passion fruit", "Lychee", "Longan",
    "Pomegranate", "Pomelo", "Tamarind", "Dates", "Figs (fresh)", "Figs (dried)",
    "Grapes", "Raisins / Sultanas", "Dried cranberries", "Prunes",
    "Apricot (fresh)", "Apricot (dried)", "Peach", "Nectarine", "Plum",
    "Strawberries", "Blueberries", "Raspberries", "Blackberries",
    "Cherry", "Avocado", "Coconut (fresh)", "Coconut flakes",
    "Dried mango", "Dried apricot", "Currants",

    # ── Grains & Starches ──
    "Basmati rice", "Jasmine rice", "Short-grain rice", "Brown rice",
    "Arborio rice (risotto)", "Black rice", "Wild rice",
    "Pasta (spaghetti)", "Pasta (penne)", "Pasta (tagliatelle)", "Pasta (fusilli)",
    "Egg noodles", "Rice noodles", "Udon noodles", "Soba noodles",
    "Couscous", "Bulgur wheat", "Freekeh", "Farro", "Spelt",
    "Quinoa", "Millet", "Buckwheat", "Polenta / Cornmeal",
    "Plain flour / All-purpose flour", "Bread flour", "Whole wheat flour",
    "Cornflour / Cornstarch", "Rice flour", "Chickpea flour (besan)",
    "Bread (sourdough)", "Flatbread / Pita", "Tortillas", "Naan",
    "Rolled oats", "Barley",

    # ── Oils & Fats ──
    "Olive oil", "Extra virgin olive oil", "Vegetable oil", "Sunflower oil",
    "Sesame oil (toasted)", "Coconut oil", "Avocado oil", "Peanut oil",
    "Butter", "Ghee", "Lard", "Duck fat",

    # ── Herbs (fresh) ──
    "Basil", "Thai basil", "Coriander / Cilantro", "Flat-leaf parsley",
    "Curly parsley", "Mint", "Spearmint", "Rosemary", "Thyme", "Sage",
    "Tarragon", "Chives", "Dill", "Oregano", "Bay leaves (fresh)",
    "Curry leaves", "Kaffir lime leaves",

    # ── Spices & Dry seasonings ──
    "Salt", "Black pepper", "White pepper", "Chilli flakes", "Cayenne pepper",
    "Paprika (smoked)", "Paprika (sweet)", "Cumin (ground)", "Cumin seeds",
    "Coriander (ground)", "Coriander seeds", "Turmeric", "Garam masala",
    "Cardamom (green)", "Cardamom (black)", "Cinnamon stick", "Cinnamon (ground)",
    "Cloves", "Star anise", "Fennel seeds", "Fenugreek seeds",
    "Mustard seeds", "Dried chilli", "Szechuan peppercorn",
    "Sumac", "Za'atar", "Ras el hanout", "Harissa paste",
    "Curry powder", "Madras curry powder", "Chinese five spice",
    "Gochugaru (Korean chilli flakes)", "Dried oregano", "Dried thyme",
    "Herbes de Provence", "Bay leaves (dried)", "Saffron", "Vanilla pod",
    "Vanilla extract", "Nutmeg", "Allspice",

    # ── Condiments & Pastes ──
    "Soy sauce", "Tamari (gluten-free soy)", "Fish sauce", "Oyster sauce",
    "Hoisin sauce", "Worcestershire sauce", "Tabasco / Hot sauce",
    "Sriracha", "Gochujang (Korean chilli paste)", "Miso paste (white)",
    "Miso paste (red)", "Doenjang (fermented soybean paste)",
    "Tahini", "Peanut butter", "Almond butter",
    "Tomato ketchup", "Mustard (Dijon)", "Mustard (wholegrain)",
    "Mayonnaise", "Horseradish", "Wasabi", "Pomegranate molasses",
    "Tamarind paste", "Rose water", "Orange blossom water",

    # ── Vinegars & Acids ──
    "White wine vinegar", "Red wine vinegar", "Rice wine vinegar",
    "Apple cider vinegar", "Balsamic vinegar", "Sherry vinegar",
    "Lemon juice", "Lime juice",

    # ── Sweeteners ──
    "Sugar (white / granulated)", "Brown sugar", "Icing sugar", "Caster sugar",
    "Honey", "Maple syrup", "Agave syrup", "Molasses", "Golden syrup",
    "Jaggery / Palm sugar", "Coconut sugar", "Stevia",

    # ── Stocks & Liquids ──
    "Chicken stock / Broth", "Beef stock / Broth", "Vegetable stock",
    "Fish stock", "Dashi stock", "Coconut milk", "Coconut cream",
    "White wine", "Red wine", "Sake", "Mirin", "Beer / Ale",
    "Water",

    # ── Nuts & Seeds ──
    "Almonds (whole)", "Almond flakes", "Cashews", "Walnuts", "Pecans",
    "Pistachios", "Pine nuts", "Macadamia nuts", "Hazelnuts",
    "Peanuts", "Sesame seeds (white)", "Sesame seeds (black)",
    "Pumpkin seeds", "Sunflower seeds", "Chia seeds", "Flaxseeds",
    "Poppy seeds",

    # ── Dried Goods & Other ──
    "Dark chocolate (70%+)", "Milk chocolate", "White chocolate",
    "Cocoa powder", "Baking powder", "Baking soda", "Yeast (instant)",
    "Gelatine", "Agar agar",
    "Dried wakame seaweed", "Nori sheets", "Kombu",
    "Capers", "Olives (green)", "Olives (black)", "Gherkins / Pickles",
    "Canned tomatoes (chopped)", "Canned tomatoes (whole)",
    "Bread crumbs", "Panko bread crumbs",
])

# ─── Common "basics" that users often forget to select ────────────────────
INGREDIENT_BASICS_REMINDER = [
    "Salt", "Black pepper", "Water", "Olive oil", "Vegetable oil",
    "Sugar (white / granulated)", "Butter", "Garlic", "Onion",
]
