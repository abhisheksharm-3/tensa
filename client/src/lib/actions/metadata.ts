"use server";

import { ApiRequestError, apiRequest } from "@/lib/api-client";
import type { Metadata } from "@/types/job";

/** Resolve a URL's title/thumbnail/duration via the API (single items + playlists). */
export async function fetchMetadataAction(url: string): Promise<Metadata> {
  try {
    return await apiRequest<Metadata>("/api/metadata", {
      method: "POST",
      body: { url },
    });
  } catch (error) {
    if (error instanceof ApiRequestError) throw new Error(error.detail);
    throw error instanceof Error ? error : new Error("Could not read metadata");
  }
}
