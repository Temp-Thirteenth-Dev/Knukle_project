# Deployment Guide (Render)

We have converted the application into a fully-fledged Web App (Flask + Glassmorphism UI).
To deploy it on entirely free tier servers like Render:

### Using Render.com
1. **GitHub**: Push this entire `KnuckleAuthSystem` folder into a new GitHub repository.
2. Sign up on [Render.com](https://render.com/).
3. Click **New +** -> **Web Service** -> **Build and deploy from a Git repository**.
4. Connect the GitHub repository you just uploaded.
5. In the Create Web Service page, use the following settings:
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Instance Type:** `Free`
6. Click **Create Web Service**. 

Once deployed, the app will have a stunning web interface and all the SIFT comparison works purely on the backend. No Tkinter windows will pop up, and the server works headless!

> **Note**: Free tier Render instances have an ephemeral disk. The `database/` folder will reset if the server restarts. To prevent this, you can attach a free persistent disk to the repository path in Render settings, or just use it as a demo environment.
