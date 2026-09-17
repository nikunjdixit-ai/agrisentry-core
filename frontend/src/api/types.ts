export interface BoundingBox {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

export interface Detection {
  class_id: number;
  class_name: string;
  display_name: string;
  crop: string;
  confidence: number;
  bbox: BoundingBox;
}

export interface SeverityDetails {
  level: string;
  affected_area_percent: number;
  method: string;
}

export interface VisionDiagnosis {
  status: "success" | "no_detection" | "error" | string;
  model: string;
  model_version: string;
  crop: string;
  disease: string | null;
  disease_display_name: string | null;
  confidence: number;
  severity: "low" | "moderate" | "high" | "unknown" | string;
  severity_details: SeverityDetails;
  detections: Detection[];
  recommendation_context?: {
    crop: string;
    disease: string | null;
    confidence: number;
  };
  inference_time_ms: number;
  message: string;
}

export interface WeatherForecast {
  location: string;
  forecast_days: number;
  temperature_c: number;
  humidity_percent: number;
  wind_speed_kmph: number;
  precipitation_probability: number;
  spraying_suitability: string;
  warnings: string[];
}

export interface VendorOption {
  dealer_name: string;
  region: string;
  item_type: string;
  stock: string;
  cibrc_registration: string;
  formulation: string;
  batch_expiry: string;
  unit_price: number;
  compliance: string;
}

export interface MandiPrices {
  crop: string;
  state: string;
  district?: string | null;
  modal_price_per_quintal: number;
  min_price: number;
  max_price: number;
  arrival_trend: string;
  market_yard: string;
}

export interface RagContextItem {
  title: string;
  content: string;
  crop_type: string;
  region: string;
  problem_category: string;
  compliance_safety_level: string;
  disease_name?: string;
  source_name?: string;
  source_url?: string;
  retrieval_date?: string;
  is_general_advisory?: boolean;
  match_level?: "exact" | "disease_level" | "fallback" | string;
  cultural_precautions?: string;
  sanitation_guidance?: string;
  moisture_irrigation_guidance?: string;
  non_chemical_management?: string;
  chemical_treatment?: string;
  cibrc_registration_details?: string;
  phi_safety_limitations?: string;
  content_hi?: string;
}

export interface WorkflowDiagnosticResult {
  status?: string;
  crop?: string;
  disease?: string;
  disease_display_name?: string;
  confidence?: number;
  weather?: WeatherForecast;
  treatment_advisories?: string[];
  primary_advisory?: string;
  advisory_title?: string;
  source_name?: string;
  source_url?: string;
  retrieval_date?: string;
  match_level?: "exact" | "disease_level" | "fallback" | string;
  is_general_advisory?: boolean;
  advisory_doc?: RagContextItem;
  [key: string]: unknown;
}

export interface WorkflowResult {
  diagnostic_result?: WorkflowDiagnosticResult;
  rag_context?: RagContextItem[];
  vendor_options?: VendorOption[];
  mandi_prices?: MandiPrices;
  current_step?: string;
  verification_flag?: boolean;
  verification_notes?: string;
  evidence_score?: number;
}

export interface DiagnosisApiResponse {
  status: "success" | "partial_success" | "error" | string;
  language?: string;
  diagnosis: VisionDiagnosis;
  workflow?: WorkflowResult;
  message?: string;
  workflow_error?: string;
}

export interface DiagnosisParams {
  image: File;
  crop?: string;
  region?: string;
  query?: string;
  language?: string;
}
