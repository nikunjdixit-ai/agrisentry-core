import React, { useState } from "react";
import { VisionDiagnosis, WorkflowResult } from "../api/types";
import {
  AlertTriangle,
  CheckCircle2,
  Clock,
  ShieldAlert,
  Cpu,
  HelpCircle,
  ArrowRightCircle,
  Camera,
  ChevronDown,
  ChevronUp,
  Sliders,
  Layers,
} from "lucide-react";
import { useTranslation } from "../i18n";

interface DiagnosisCardProps {
  diagnosis: VisionDiagnosis;
  workflow?: WorkflowResult;
}

export const DiagnosisCard: React.FC<DiagnosisCardProps> = ({ diagnosis, workflow }) => {
  const { t } = useTranslation();
  const [showTechDetails, setShowTechDetails] = useState<boolean>(false);

  const isHealthy =
    diagnosis.disease_display_name?.toLowerCase().includes("healthy") ||
    diagnosis.disease?.toLowerCase().includes("healthy");

  const isNoDetection = diagnosis.status === "no_detection";
  const isLowConfidence = diagnosis.confidence > 0 && diagnosis.confidence < 0.70;

  // Severity styling with distinct color and non-color textual label
  const getSeverityBadge = (level: string) => {
    switch (level?.toLowerCase()) {
      case "low":
        return {
          bg: "bg-emerald-100 text-emerald-800 border-emerald-300",
          dot: "bg-emerald-500",
          label: t.diagnosis.severityLow,
        };
      case "moderate":
        return {
          bg: "bg-amber-100 text-amber-800 border-amber-300",
          dot: "bg-amber-500",
          label: t.diagnosis.severityModerate,
        };
      case "high":
        return {
          bg: "bg-rose-100 text-rose-800 border-rose-300",
          dot: "bg-rose-500",
          label: t.diagnosis.severityHigh,
        };
      default:
        return {
          bg: "bg-slate-100 text-slate-700 border-slate-300",
          dot: "bg-slate-400",
          label: t.diagnosis.severityUnknown,
        };
    }
  };

  const severityBadge = getSeverityBadge(diagnosis.severity);

  if (isNoDetection) {
    return (
      <div className="bg-amber-50 border border-amber-200/90 rounded-2xl p-5 shadow-xs space-y-3">
        <div className="flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
          <div className="space-y-1.5">
            <h3 className="text-sm font-bold text-amber-950">
              {t.diagnosis.noPathologyDetected}
            </h3>
            <p className="text-xs text-amber-800 leading-relaxed">
              {diagnosis.message || t.diagnosis.noPathologyDetails}
            </p>
            <div className="flex items-center gap-1.5 text-xs text-amber-900 font-semibold bg-amber-100/60 p-2 rounded-lg border border-amber-200">
              <Camera className="w-4 h-4 text-amber-700 shrink-0" />
              <span>{t.diagnosis.noPathologyHint}</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Determine recommended next action strictly using backend context
  const primaryAdvisory = workflow?.diagnostic_result?.primary_advisory;
  const isFallback =
    !primaryAdvisory ||
    primaryAdvisory.toLowerCase().includes("national advisory") ||
    primaryAdvisory.toLowerCase().includes("consult local agricultural extension officer") ||
    primaryAdvisory.toLowerCase().includes("no sufficiently relevant advisory");

  const recommendedNextAction = isHealthy
    ? t.diagnosis.nextActionHealthy
    : !isFallback && primaryAdvisory
    ? t.diagnosis.nextActionDisease
    : t.diagnosis.nextActionFallback;

  return (
    <div className="bg-white border border-slate-200/80 rounded-2xl p-5 sm:p-6 shadow-xs space-y-5">
      {/* Top row: Status, Severity & Device */}
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-100 pb-3">
        <div className="flex items-center gap-2">
          {isHealthy ? (
            <div className="flex items-center gap-1.5 text-emerald-800 text-xs font-bold bg-emerald-50 border border-emerald-200 px-2.5 py-1 rounded-full">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span>{t.diagnosis.healthyCanopy}</span>
            </div>
          ) : (
            <div className="flex items-center gap-1.5 text-rose-800 text-xs font-bold bg-rose-50 border border-rose-200 px-2.5 py-1 rounded-full">
              <ShieldAlert className="w-4 h-4 text-rose-600" />
              <span>{t.diagnosis.pathologyIdentified}</span>
            </div>
          )}

          <div
            className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold border ${severityBadge.bg}`}
          >
            <span className={`w-1.5 h-1.5 rounded-full ${severityBadge.dot}`} />
            <span>{severityBadge.label}</span>
          </div>
        </div>

        {/* Inference Latency & Device */}
        <div className="flex items-center gap-2 text-[11px] text-slate-500 font-medium">
          <span className="flex items-center gap-1 bg-slate-50 px-2 py-0.5 rounded-md border border-slate-200">
            <Clock className="w-3 h-3 text-slate-400" />
            <span>{diagnosis.inference_time_ms} ms</span>
          </span>
          <span className="flex items-center gap-1 bg-slate-50 px-2 py-0.5 rounded-md border border-slate-200">
            <Cpu className="w-3 h-3 text-slate-400" />
            <span>CPU</span>
          </span>
        </div>
      </div>

      {/* Primary Diagnosis Header */}
      <div>
        <span className="text-xs font-bold uppercase tracking-wider text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-md border border-emerald-200/60">
          {t.crops[diagnosis.crop] || diagnosis.crop}
        </span>
        <h2 className="text-xl sm:text-2xl font-black text-slate-900 tracking-tight mt-1.5">
          {diagnosis.disease_display_name || diagnosis.disease}
        </h2>
        <p className="text-xs text-slate-500 font-mono mt-0.5">
          {t.diagnosis.modelLabel}: {diagnosis.model} (v{diagnosis.model_version})
        </p>
      </div>

      {/* Low-Confidence Warning if confidence < 70% */}
      {isLowConfidence && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-3.5 text-xs text-amber-900 space-y-1">
          <div className="flex items-center gap-1.5 font-bold text-amber-950">
            <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
            <span>{t.diagnosis.lowConfidenceWarningTitle}</span>
          </div>
          <p className="leading-relaxed text-amber-800">
            {t.diagnosis.lowConfidenceWarningDesc}
          </p>
          <p className="font-semibold text-amber-900 pt-0.5">
            {t.diagnosis.retakeImageSuggestion}
          </p>
        </div>
      )}

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
        {/* Detection Confidence Card */}
        <div className="bg-slate-50 border border-slate-200/80 rounded-xl p-3">
          <span className="text-[11px] text-slate-500 font-medium block">
            {t.diagnosis.confidenceLabel}
          </span>
          <span className="text-lg font-black text-slate-900 block mt-0.5">
            {(diagnosis.confidence * 100).toFixed(1)}%
          </span>
          <div className="w-full bg-slate-200 h-1.5 rounded-full mt-1.5 overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-300 ${
                diagnosis.confidence >= 0.85
                  ? "bg-emerald-500"
                  : diagnosis.confidence >= 0.70
                  ? "bg-amber-500"
                  : "bg-rose-500"
              }`}
              style={{ width: `${Math.min(100, diagnosis.confidence * 100)}%` }}
            />
          </div>
        </div>

        {/* Estimated Affected Area Card */}
        <div className="bg-slate-50 border border-slate-200/80 rounded-xl p-3">
          <span className="text-[11px] text-slate-500 font-medium block">
            {t.diagnosis.canopyCoverageLabel}
          </span>
          <span className="text-lg font-black text-slate-900 block mt-0.5">
            {diagnosis.severity_details?.affected_area_percent ?? 0}%
          </span>
          <span className="text-[10px] text-slate-400 block truncate mt-0.5" title={t.diagnosis.heuristicMethod}>
            {t.diagnosis.heuristicMethod}
          </span>
        </div>

        {/* Total Bounding Boxes */}
        <div className="col-span-2 sm:col-span-1 bg-slate-50 border border-slate-200/80 rounded-xl p-3">
          <span className="text-[11px] text-slate-500 font-medium block">
            {t.diagnosis.regionsDetectedLabel}
          </span>
          <span className="text-lg font-black text-slate-900 block mt-0.5">
            {diagnosis.detections?.length || 0}
          </span>
          <span className="text-[10px] text-slate-400 block truncate mt-0.5">
            YOLOv8n-detect
          </span>
        </div>
      </div>

      {/* Prominent Section: Recommended Next Action */}
      <div className="bg-emerald-50/70 border border-emerald-200 rounded-xl p-4 space-y-1.5">
        <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-950 uppercase tracking-wider">
          <ArrowRightCircle className="w-4 h-4 text-emerald-700 shrink-0" />
          <span>{t.diagnosis.nextActionTitle}</span>
        </div>
        <p className="text-xs sm:text-sm text-emerald-900 leading-relaxed font-medium">
          {recommendedNextAction}
        </p>
      </div>

      {/* Section: Why this result? */}
      <div className="bg-slate-50 border border-slate-200/80 rounded-xl p-4 space-y-2">
        <div className="flex items-center gap-1.5 text-xs font-bold text-slate-800 uppercase tracking-wider">
          <HelpCircle className="w-3.5 h-3.5 text-slate-500 shrink-0" />
          <span>{t.diagnosis.whyTitle}</span>
        </div>
        <ul className="text-xs text-slate-600 space-y-1.5 pl-4 list-disc">
          <li>{t.diagnosis.whyLesionFound}</li>
          <li>
            {t.diagnosis.whyConfidenceExplanation} ({(diagnosis.confidence * 100).toFixed(1)}%)
          </li>
          <li>
            {t.diagnosis.whySeverityExplanation} ({diagnosis.severity_details?.affected_area_percent ?? 0}%)
          </li>
        </ul>
        <p className="text-[11px] text-slate-400 italic pt-1 border-t border-slate-200/60">
          {t.diagnosis.whyHeuristicNotice}
        </p>
      </div>

      {/* Technical Details & Model Architecture Drawer */}
      <div className="border-t border-slate-100 pt-2">
        <button
          type="button"
          onClick={() => setShowTechDetails(!showTechDetails)}
          className="w-full flex items-center justify-between text-xs text-slate-500 hover:text-slate-800 font-semibold py-1 transition-colors"
        >
          <span className="flex items-center gap-1.5">
            <Sliders className="w-3.5 h-3.5 text-emerald-600" />
            <span>{t.diagnosis.technicalDetailsTitle}</span>
          </span>
          {showTechDetails ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </button>

        {showTechDetails && (
          <div className="mt-2.5 bg-slate-50 border border-slate-200 rounded-xl p-3.5 text-xs text-slate-600 space-y-2 font-mono">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              <div className="flex justify-between border-b border-slate-200/60 pb-1">
                <span className="text-slate-400 font-sans">{t.diagnosis.architectureLabel}:</span>
                <span className="font-bold text-slate-800">YOLOv8n-detect</span>
              </div>
              <div className="flex justify-between border-b border-slate-200/60 pb-1">
                <span className="text-slate-400 font-sans">{t.diagnosis.deviceLabel}:</span>
                <span className="font-bold text-slate-800">CPU-Only (device=cpu)</span>
              </div>
              <div className="flex justify-between border-b border-slate-200/60 pb-1">
                <span className="text-slate-400 font-sans">{t.diagnosis.classesCountLabel}:</span>
                <span className="font-bold text-slate-800">38 Classes</span>
              </div>
              <div className="flex justify-between border-b border-slate-200/60 pb-1">
                <span className="text-slate-400 font-sans">{t.diagnosis.datasetLabel}:</span>
                <span className="font-bold text-slate-800">PlantVillage (Clean Split)</span>
              </div>
            </div>
            <div className="pt-1 text-[11px] text-slate-400 font-sans flex items-center gap-1.5">
              <Layers className="w-3 h-3 text-slate-400 shrink-0" />
              <span>Detections mapped to image natural dimensions dynamically (no distortion).</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
