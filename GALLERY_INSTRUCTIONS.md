# Gallery Section Update Instructions

The gallery section on the home page (`templates/schools/home.html`) is designed to showcase campus life using images and videos. Here is how you can update them:

## 1. Updating Images
Find the `<img>` tags within the `<div class="gallery-item">` blocks. Replace the `src` attribute with your own image URL or local path.

```html
<div class="gallery-item">
  <img src="YOUR_IMAGE_URL_HERE" alt="Description">
  <div class="gallery-overlay">
    <div class="small fw-semibold">Your Caption Here</div>
  </div>
</div>
```

**Recommended Size:** 800x450px (16:9 Aspect Ratio)

---

## 2. Updating Videos
Find the `<video>` tags. Replace the `<source src="...">` attribute with your video URL or path.

```html
<div class="gallery-item">
  <video muted loop onmouseover="this.play()" onmouseout="this.pause()">
    <source src="YOUR_VIDEO_URL_HERE" type="video/mp4">
  </video>
  <div class="gallery-overlay">
    <div class="small fw-semibold"><i class="bi bi-play-circle me-1"></i> Your Caption Here</div>
  </div>
</div>
```

**Note:** The videos are set to `muted` and `loop` by default. They will automatically play when the user hovers over them (`onmouseover`) and pause when the mouse leaves (`onmouseout`).

---

## 3. Adding New Items
To add more items, simply copy one of the `col-md-6 col-lg-4` blocks and paste it within the `<div class="row g-4">` container.

## 4. Local Files
If you want to use files stored on your server:
1. Place your images/videos in the `static/` directory (e.g., `static/images/gallery/`).
2. Update the `src` attribute to use the Django static tag:
   - `src="{% static 'images/gallery/my-image.jpg' %}"`
   - `src="{% static 'videos/campus-tour.mp4' %}"`
