# How to Add Custom Videos to the Gallery

To add your own videos to the school gallery, follow these instructions:

### 1. Upload Your Video to a Hosting Platform
Currently, the system supports embedding videos from **YouTube** or **Vimeo**. This is recommended to save server bandwidth and ensure fast loading times for users.

### 2. Get the Video URL
Copy the full URL of your video from the browser's address bar.
- **YouTube Example:** `https://www.youtube.com/watch?v=dQw4w9WgXcQ` or `https://youtu.be/dQw4w9WgXcQ`
- **Vimeo Example:** `https://vimeo.com/123456789`

### 3. Add to Gallery via Admin Panel
1. Log in to the Django Admin panel (usually at `/admin/`).
2. Navigate to **Schools** > **Gallery items**.
3. Click **Add Gallery item**.
4. Fill in the following fields:
   - **School:** Select the school this video belongs to.
   - **Title:** A short, descriptive title for the video.
   - **Description:** (Optional) A brief explanation of what the video shows.
   - **Media Type:** Select **Video**.
   - **Video URL:** Paste the URL you copied in Step 2.
   - **Is Featured:** Check this if you want the video to appear prominently (useful for future home page sections).
5. Click **Save**.

### 4. Viewing the Video
The video will automatically appear on the public **Gallery** page (`/gallery/`). The system will handle the embedding process automatically based on the URL provided.

---

### Pro Tips for Videos:
- **Privacy Settings:** Ensure your video is set to "Public" or "Unlisted" on YouTube/Vimeo so it can be embedded on your site.
- **Thumbnail:** The system uses the video provider's default thumbnail.
- **Title & Description:** Good titles and descriptions help parents and students find relevant content.
