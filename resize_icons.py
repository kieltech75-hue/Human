from PIL import Image

def make(size):
    im = Image.open("human-icon.png").convert("RGBA")
    im.thumbnail((size, size), Image.LANCZOS)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(im, ((size - im.width) // 2, (size - im.height) // 2), im)
    out.save(f"human-icon-{size}.png")

if __name__ == "__main__":
    make(128)
    make(512)
