"use server";

import { apiRequest, rethrowApiError } from "@/lib/api-client";
import type { Metadata } from "@/types/job";

/** Resolve a URL's title/thumbnail/duration via the API (single items + playlists). */
export async function fetchMetadataAction(url: string): Promise<Metadata> {
  try {
    return await apiRequest<Metadata>("/api/metadata", {
      method: "POST",
      body: { url },
    });
  } catch (error) {
    rethrowApiError(error, "Could not read metadata");
  }
}
