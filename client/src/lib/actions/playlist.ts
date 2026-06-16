"use server";

import { ApiRequestError, apiRequest } from "@/lib/api-client";
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
    if (error instanceof ApiRequestError) throw new Error(error.detail);
    throw error instanceof Error ? error : new Error("Failed to load playlist");
  }
}
