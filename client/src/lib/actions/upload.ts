"use server";

import { ApiRequestError, apiUpload } from "@/lib/api-client";

/**
 * Forward a file upload to the API. The browser sends FormData to this action;
 * the action streams it onward. Returns the server-side path the job will
 * reference (the API constrains it to the uploads dir).
 */
export async function uploadFileAction(
  form: FormData,
): Promise<{ uploadPath: string }> {
  const file = form.get("file");
  if (!(file instanceof File)) throw new Error("No file provided");
  try {
    const { upload_path } = await apiUpload<{ upload_path: string }>(
      "/api/upload",
      form,
    );
    return { uploadPath: upload_path };
  } catch (error) {
    if (error instanceof ApiRequestError) throw new Error(error.detail);
    throw error instanceof Error ? error : new Error("Upload failed");
  }
}
