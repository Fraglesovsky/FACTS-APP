from moviepy.video.fx.resize import resize
from moviepy.video.fx.all import crop
from PIL import Image

def custom_resize(clip, newsize=None, height=None, width=None, apply_to_mask=True):
    """
    Funkcja opakowująca dla resize w MoviePy.
    """
    def resize_with_lanczos(pic, newsize):
        return Image.fromarray(pic).resize(newsize, Image.Resampling.LANCZOS)

    return resize(clip, newsize=newsize, height=height, width=width, apply_to_mask=apply_to_mask)

def crop_to_6_19(image_path):
    """
    Przycina obraz do proporcji 6:19.
    
    :param image_path: Ścieżka do obrazu.
    :return: Ścieżka do przyciętego obrazu.
    """
    img = Image.open(image_path)
    width, height = img.size

    # Oblicz nowe wymiary dla proporcji 6:19
    target_width = width
    target_height = int(width * 19 / 6)

    if target_height > height:
        target_height = height
        target_width = int(height * 6 / 19)

    left = (width - target_width) / 2
    top = (height - target_height) / 2
    right = (width + target_width) / 2
    bottom = (height + target_height) / 2

    # Przytnij obraz
    img_cropped = img.crop((left, top, right, bottom))

    # Zapisz przycięty obraz
    cropped_image_path = image_path.replace(".jpg", "_cropped.jpg")
    img_cropped.save(cropped_image_path)
    
    print(f"Obraz przycięty i zapisany jako: {cropped_image_path}")
    return cropped_image_path
    


