# Virtual Closet — AI-Powered Try-On
 
A virtual closet app: users upload a photo of themselves and photos of their own
clothes, then compose and "try on" outfits virtually.
 
## Roadmap
 
- **Phase 1 — 2D graphical try-on (MVP)**
  Overlay cut-out clothing images (PNG + alpha) onto the user's body keypoints,
  similar to character customization in video games. Layered rendering via
  Canvas/PixiJS.
- **Phase 2 — AI-based try-on**
  Diffusion-based virtual try-on (e.g. IDM-VTON / OOTDiffusion / CatVTON) for
  realistic garment texture and drape fitting to the user's body.
- **Phase 3 — Full 3D / AR**
  3D body reconstruction (SMPL/SMPL-X), garment draping, full 360° rotation,
  eventually exporting to WebXR / AR.
- **Phase 4 — Retail integration**
  Catalog of clothing from current retail offerings, virtual try-on before
  purchase.
## Stack (Phase 1)
 
**Backend:** FastAPI, PostgreSQL, MediaPipe Pose, SegFormer / rembg (segmentation),
S3-compatible storage (MinIO locally)
 
**Frontend:** React, Canvas API / PixiJS (2D layered rendering)
 
## Repo structure
 
```
virtual-closet/
├── backend/
│   ├── app/
│   │   ├── api/            # endpoints: users, wardrobe, tryons
│   │   ├── models/         # DB models: User, ClothingItem, Outfit
│   │   ├── services/
│   │   │   ├── segmentation.py
│   │   │   ├── pose.py
│   │   │   ├── warp.py
│   │   │   └── storage.py
│   │   └── main.py
│   ├── ml/
│   │   ├── notebooks/
│   │   └── weights/
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── Wardrobe/
│       │   ├── TryOnCanvas/
│       │   └── Upload/
│       └── pages/
├── docs/
│   └── roadmap.md
└── README.md
```
 
## Status
 
🚧 Early-stage project — repo structure and segmentation/pose pipeline in progress.
 
## Getting started (dev)
 
```bash
# backend
cd backend
python3.11 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate.bat on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
 
# frontend
cd frontend
npm install
npm run dev
```