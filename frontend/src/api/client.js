import axios from "axios";

const API_BASE_URL = "http://localhost:8000";

const api = axios.create({ baseURL: API_BASE_URL });

export async function fetchWardrobe(ownerId) {
  const res = await api.get("/wardrobe/", { params: { owner_id: ownerId } });
  return res.data;
}

export function getTryOnImageUrl(userId, itemIds) {
  const params = new URLSearchParams();
  itemIds.forEach((id) => params.append("item_ids", id));
  return `${API_BASE_URL}/tryon/${userId}?${params.toString()}`;
}

export default api;