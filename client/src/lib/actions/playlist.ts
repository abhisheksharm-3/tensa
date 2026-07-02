"use server";

import { apiRequest, rethrowApiError } from "@/lib/api-client";
import type { PlaylistItem } from "@/types/job";

export async function fetchPlaylistInfoAction(
  url: string,
): Promise<{ title: string | null; items: PlaylistItem[]; total: number }> {
  try {
    return await apiRequest<{
      title: string | null;
      items: PlaylistItem[];
      total: number;
    }>("/api/playlist/info", { method: "POST", body: { url } });
  } catch (error) {
    rethrowApiError(error, "Failed to load playlist");
  }
}
