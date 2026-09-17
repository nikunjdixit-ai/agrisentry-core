import { DiagnosisApiResponse, DiagnosisParams } from "./types";

/**
 * Base API URL configured via Vite environment variable with a robust local fallback.
 */
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

/**
 * Submits an uploaded crop leaf image along with optional crop, region, and query
 * parameters to the AgriSentry backend /diagnosis endpoint.
 *
 * Enforces multipart/form-data without manually overriding the browser's Content-Type boundary.
 */
export async function diagnoseCrop(params: DiagnosisParams): Promise<DiagnosisApiResponse> {
  const { image, crop, region, query, language } = params;

  if (!image) {
    throw new Error("Please select an image file to analyze.");
  }

  const formData = new FormData();
  formData.append("image", image);

  if (crop && crop.trim().length > 0) {
    formData.append("crop", crop.trim());
  } else {
    formData.append("crop", "unknown");
  }

  if (region && region.trim().length > 0) {
    formData.append("region", region.trim());
  } else {
    formData.append("region", "unknown");
  }

  if (query && query.trim().length > 0) {
    formData.append("query", query.trim());
  } else {
    formData.append("query", "");
  }

  if (language && language.trim().length > 0) {
    formData.append("language", language.trim());
  } else {
    formData.append("language", "en");
  }

  const endpoint = `${API_BASE_URL.replace(/\/+$/, "")}/diagnosis`;

  try {
    const response = await fetch(endpoint, {
      method: "POST",
      body: formData,
      // Note: We intentionally do NOT set the 'Content-Type' header here.
      // The browser automatically sets multipart/form-data along with the dynamic multipart boundary string.
    });

    if (!response.ok) {
      let errorMessage = `Server responded with status ${response.status}`;
      try {
        const errorData = await response.json();
        if (errorData && typeof errorData.detail === "string") {
          errorMessage = errorData.detail;
        } else if (errorData && typeof errorData.message === "string") {
          errorMessage = errorData.message;
        }
      } catch {
        // Response body was not JSON; use default status text
        errorMessage = response.statusText || errorMessage;
      }
      throw new Error(errorMessage);
    }

    const data: DiagnosisApiResponse = await response.json();
    return data;
  } catch (err: unknown) {
    if (err instanceof Error) {
      // Re-throw with descriptive context if network connection fails
      if (err.message.includes("Failed to fetch") || err.message.includes("NetworkError")) {
        throw new Error(
          `Unable to reach AgriSentry API at ${API_BASE_URL}. Ensure the FastAPI server is running (e.g. uvicorn api.main:app --port 8000).`
        );
      }
      throw err;
    }
    throw new Error("An unexpected error occurred during diagnosis.");
  }
}

/**
 * Health check helper to test backend connectivity.
 */
export async function checkApiHealth(): Promise<boolean> {
  try {
    const endpoint = `${API_BASE_URL.replace(/\/+$/, "")}/health`;
    const response = await fetch(endpoint, { method: "GET" });
    if (!response.ok) return false;
    const data = await response.json();
    return data.status === "healthy";
  } catch {
    return false;
  }
}
