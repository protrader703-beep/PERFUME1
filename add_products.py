import os
import django
import shutil

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "attar_store.settings")
django.setup()

from store.models import Product

media_dir = "/home/harvey/BUSINESS SITE/PERFUME/media/products"
os.makedirs(media_dir, exist_ok=True)

products_data = [
    {
        "name": "Oud Al Junaid",
        "description": "A profound and deeply resonant oud, harvested from the rarest agarwood. Features rich notes of dark leather, smoked woods, and a hint of dark chocolate. A truly royal fragrance.",
        "short_description": "Deep, smoky agarwood with leather notes.",
        "price": 14500.00,
        "stock": 15,
        "is_featured": True,
        "image_source": "/home/harvey/.gemini/antigravity/brain/8a82a568-7f6a-4eca-b189-190a57ce134d/oud_junaid_webp_1782370712829.png"
    },
    {
        "name": "Royal Amber",
        "description": "A warm, glowing amber fragrance that wraps you in luxury. Blends pure amber resin with Madagascar vanilla, tonka bean, and a whisper of golden honey.",
        "short_description": "Warm amber, vanilla, and golden honey.",
        "price": 12000.00,
        "stock": 25,
        "is_featured": True,
        "image_source": "/home/harvey/.gemini/antigravity/brain/8a82a568-7f6a-4eca-b189-190a57ce134d/royal_amber_webp_1782370726166.png"
    },
    {
        "name": "Majestic Musk",
        "description": "A crystal clear, ethereal musk. Clean, powdery, and intensely elegant. Opens with white floral accords and settles into a breathtaking, long-lasting pure musk base.",
        "short_description": "Clean, powdery, and elegant white musk.",
        "price": 8500.00,
        "stock": 50,
        "is_featured": True,
        "image_source": "/home/harvey/.gemini/antigravity/brain/8a82a568-7f6a-4eca-b189-190a57ce134d/majestic_musk_webp_1782370738018.png"
    }
]

for p_data in products_data:
    p, created = Product.objects.get_or_create(name=p_data["name"], defaults={
        "description": p_data["description"],
        "short_description": p_data["short_description"],
        "price": p_data["price"],
        "stock": p_data["stock"],
        "is_featured": p_data["is_featured"],
    })
    
    if created or not p.image:
        dest_filename = os.path.basename(p_data["image_source"])
        dest_path = os.path.join(media_dir, dest_filename)
        shutil.copy2(p_data["image_source"], dest_path)
        p.image.name = "products/" + dest_filename
        p.save()

print("Products added successfully!")
