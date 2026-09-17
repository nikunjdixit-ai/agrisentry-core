import React from "react";
import { WorkflowResult } from "../api/types";
import {
  BookOpen,
  ShieldCheck,
  AlertCircle,
  FileText,
  AlertTriangle,
  UserCheck,
  ShieldAlert,
  Database,
  ArrowRightCircle,
  CheckCircle2,
  HelpCircle,
  ExternalLink,
  Calendar,
  Building2,
} from "lucide-react";
import { useTranslation } from "../i18n";

interface AdvisoryCardProps {
  workflow?: WorkflowResult;
}

export const AdvisoryCard: React.FC<AdvisoryCardProps> = ({ workflow }) => {
  const { t } = useTranslation();

  if (!workflow) return null;

  const diagnosticResult = workflow.diagnostic_result;
  const primaryAdvisory = diagnosticResult?.primary_advisory;
  const treatmentAdvisories = diagnosticResult?.treatment_advisories || [];
  const verificationFlag = Boolean(workflow.verification_flag);
  const evidenceScore = workflow.evidence_score ?? 0;
  const verificationNotes = workflow.verification_notes || "";

  // Extract authoritative source and tier metadata
  const primaryDoc = workflow.rag_context && workflow.rag_context.length > 0 ? workflow.rag_context[0] : undefined;
  const matchLevel =
    diagnosticResult?.match_level ||
    primaryDoc?.match_level ||
    (verificationFlag ? "exact" : "fallback");

  const isExact = matchLevel === "exact" && verificationFlag;
  const isDiseaseLevel = matchLevel === "disease_level";
  const isFallback = matchLevel === "fallback" || !verificationFlag;

  const isGeneralAdvisory = Boolean(
    diagnosticResult?.is_general_advisory ||
    primaryDoc?.is_general_advisory ||
    isDiseaseLevel
  );

  const sourceName =
    diagnosticResult?.source_name ||
    primaryDoc?.source_name ||
    "ICAR / National Extension";

  const sourceUrl =
    diagnosticResult?.source_url ||
    primaryDoc?.source_url ||
    "https://icar.org.in";

  const retrievalDate =
    diagnosticResult?.retrieval_date ||
    primaryDoc?.retrieval_date ||
    "2026-09-17";

  // Determine healthy status
  const isHealthy = Boolean(
    diagnosticResult?.disease_display_name?.toLowerCase().includes("healthy") ||
    diagnosticResult?.disease?.toLowerCase().includes("healthy") ||
    diagnosticResult?.status === "healthy"
  );

  const recommendedNextAction = isHealthy
    ? t.diagnosis.nextActionHealthy
    : !isFallback && primaryAdvisory
    ? t.diagnosis.nextActionDisease
    : t.diagnosis.nextActionFallback;

  return (
    <div className="bg-white border border-slate-200/80 rounded-2xl p-5 sm:p-6 shadow-xs space-y-5">
      {/* Header with Verification Pill */}
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-100 pb-3">
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-xl bg-emerald-100 text-emerald-700 flex items-center justify-center shrink-0">
            <BookOpen className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm sm:text-base font-bold text-slate-900">
              {t.advisory.title}
            </h3>
            <p className="text-[11px] text-slate-500">
              {t.advisory.subtitle}
            </p>
          </div>
        </div>

        {/* Verification Status Pill */}
        <div
          className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold border ${
            isExact
              ? "bg-emerald-50 text-emerald-800 border-emerald-300"
              : isDiseaseLevel
              ? "bg-blue-50 text-blue-800 border-blue-300"
              : "bg-amber-50 text-amber-800 border-amber-300"
          }`}
        >
          {isExact ? (
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
          ) : isDiseaseLevel ? (
            <AlertTriangle className="w-3.5 h-3.5 text-blue-600" />
          ) : (
            <ShieldAlert className="w-3.5 h-3.5 text-amber-600" />
          )}
          <span>
            {isExact
              ? t.advisory.matchLevelExact
              : isDiseaseLevel
              ? t.advisory.matchLevelGeneral
              : t.advisory.matchLevelFallback}
          </span>
        </div>
      </div>

      {/* 6 Structured Subsections */}
      <div className="space-y-4">
        {/* Section 1: Recommended Next Action */}
        <div className="bg-emerald-50/80 border border-emerald-200 rounded-xl p-4 space-y-1.5 shadow-2xs">
          <div className="flex items-center gap-2 text-xs font-bold text-emerald-950 uppercase tracking-wider">
            <ArrowRightCircle className="w-4 h-4 text-emerald-700 shrink-0" />
            <span>{t.advisory.recommendedNextActionTitle}</span>
          </div>
          <p className="text-xs sm:text-sm text-emerald-900 font-medium leading-relaxed pl-6">
            {recommendedNextAction}
          </p>
        </div>

        {/* Section 2: Immediate Precautions */}
        <div className="bg-slate-50 border border-slate-200/80 rounded-xl p-4 space-y-1.5">
          <div className="flex items-center gap-2 text-xs font-bold text-slate-800 uppercase tracking-wider">
            <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
            <span>{t.advisory.immediatePrecautionsTitle}</span>
          </div>
          <p className="text-xs text-slate-700 leading-relaxed pl-6">
            {t.advisory.immediatePrecautionsText}
          </p>
        </div>

        {/* Section 3: Recommended Consultation */}
        <div className="bg-slate-50 border border-slate-200/80 rounded-xl p-4 space-y-1.5">
          <div className="flex items-center gap-2 text-xs font-bold text-slate-800 uppercase tracking-wider">
            <UserCheck className="w-4 h-4 text-emerald-700 shrink-0" />
            <span>{t.advisory.consultationTitle}</span>
          </div>
          <p className="text-xs text-slate-700 leading-relaxed pl-6">
            {t.advisory.consultationText}
          </p>
        </div>

        {/* Section 4: Treatment Guidance (Real RAG, General Advisory, or Fallback) */}
        <div className="bg-slate-50 border border-slate-200/80 rounded-xl p-4 space-y-3">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div className="flex items-center gap-2 text-xs font-bold text-slate-900 uppercase tracking-wider">
              <FileText className="w-4 h-4 text-emerald-700 shrink-0" />
              <span>{t.advisory.treatmentGuidanceTitle}</span>
            </div>
            <span
              className={`text-[10px] font-semibold px-2.5 py-0.5 rounded-md border ${
                isExact
                  ? "bg-emerald-50 text-emerald-800 border-emerald-200"
                  : isDiseaseLevel
                  ? "bg-blue-50 text-blue-800 border-blue-200"
                  : "bg-amber-50 text-amber-800 border-amber-200"
              }`}
            >
              {isExact
                ? sourceName
                : isDiseaseLevel
                ? t.advisory.matchLevelGeneral
                : t.advisory.fallbackSourceNational}
            </span>
          </div>

          {/* General Disease-Level Advisory Warning Banner */}
          {isGeneralAdvisory && isDiseaseLevel && (
            <div className="flex items-start gap-2.5 p-3 bg-amber-50 border border-amber-300 rounded-xl text-xs text-amber-900 font-medium leading-relaxed">
              <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
              <span>{t.advisory.generalAdvisoryWarning}</span>
            </div>
          )}

          <div className="text-xs sm:text-sm text-slate-800 leading-relaxed pl-6 whitespace-pre-line">
            {primaryAdvisory ? (
              primaryAdvisory
            ) : (
              <span className="text-slate-500 italic">
                {t.advisory.treatmentUnavailable}
              </span>
            )}
          </div>
        </div>

        {/* Section 5: Referenced Extension Advisories (if available) */}
        {treatmentAdvisories.length > 0 && (
          <div className="space-y-2 pt-1">
            <div className="flex items-center gap-1.5 text-xs font-bold text-slate-700 uppercase tracking-wider">
              <Database className="w-3.5 h-3.5 text-slate-500" />
              <span>{t.advisory.referencedAdvisoriesTitle}</span>
            </div>
            <ul className="grid grid-cols-1 sm:grid-cols-2 gap-2 pl-2">
              {treatmentAdvisories.map((advisory, idx) => (
                <li
                  key={idx}
                  className="flex items-center gap-2 text-xs text-slate-700 bg-slate-50 border border-slate-200/80 px-3 py-2 rounded-lg"
                >
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-600 shrink-0" />
                  <span className="truncate">{advisory}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Section 6: Verification & Source Information */}
        <div className="bg-slate-50/80 border border-slate-200/80 rounded-xl p-4 space-y-2.5">
          <div className="flex items-center justify-between gap-2">
            <div className="flex items-center gap-1.5 text-xs font-bold text-slate-800 uppercase tracking-wider">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
              <span>{t.advisory.verificationSourceInfoTitle}</span>
            </div>
            <span className="text-[10px] font-mono text-slate-500">
              LangGraph Gate v1.0
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs text-slate-600 pl-5">
            <div className="flex items-center justify-between border-b border-slate-200/60 pb-1 sm:pr-4">
              <span className="text-slate-500 font-medium">{t.advisory.verificationStatusTitle}:</span>
              <span className="font-semibold text-slate-800">
                {isExact
                  ? t.advisory.verifiedText
                  : isDiseaseLevel
                  ? t.advisory.matchLevelGeneral
                  : t.advisory.unverifiedText}
              </span>
            </div>
            <div className="flex items-center justify-between border-b border-slate-200/60 pb-1">
              <span className="text-slate-500 font-medium">{t.advisory.evidenceScoreLabel}:</span>
              <span className="font-mono font-bold text-emerald-700">
                {(evidenceScore * 100).toFixed(0)}%
              </span>
            </div>

            <div className="flex items-center justify-between border-b border-slate-200/60 pb-1 sm:pr-4">
              <span className="text-slate-500 font-medium">{t.advisory.matchLevelLabel}:</span>
              <span className="font-semibold text-slate-800">
                {isExact
                  ? t.advisory.matchLevelExact
                  : isDiseaseLevel
                  ? t.advisory.matchLevelGeneral
                  : t.advisory.matchLevelFallback}
              </span>
            </div>

            <div className="flex items-center justify-between border-b border-slate-200/60 pb-1">
              <span className="text-slate-500 font-medium">{t.advisory.retrievalDateLabel}:</span>
              <span className="font-mono text-slate-700 flex items-center gap-1">
                <Calendar className="w-3 h-3 text-slate-400" />
                {retrievalDate}
              </span>
            </div>

            <div className="col-span-1 sm:col-span-2 flex flex-wrap items-center justify-between border-b border-slate-200/60 pb-1 gap-1">
              <span className="text-slate-500 font-medium flex items-center gap-1">
                <Building2 className="w-3 h-3 text-slate-400" />
                {t.advisory.sourceLabel}:
              </span>
              <div className="flex items-center gap-2">
                <span className="font-semibold text-slate-800">{sourceName}</span>
                {sourceUrl && (
                  <a
                    href={sourceUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-[11px] text-emerald-700 hover:text-emerald-800 underline font-medium"
                  >
                    <span>{t.advisory.sourceLinkText}</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                )}
              </div>
            </div>

            <div className="col-span-1 sm:col-span-2 pt-0.5 text-[11px] text-slate-500 flex items-start gap-1.5">
              <HelpCircle className="w-3.5 h-3.5 text-slate-400 shrink-0 mt-0.5" />
              <span>
                {verificationNotes ? `Gate Result: ${verificationNotes}. ` : ""}
                {isExact
                  ? "Retrieved and verified against accredited state agricultural university / ICAR repository."
                  : isDiseaseLevel
                  ? "Crop-specific advisory unavailable; verified against accredited general disease repository."
                  : "Local knowledge base did not have high similarity matches; national safety fallback advisory was applied."}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Statutory Safety Disclaimer */}
      <div className="flex items-start gap-2 text-[11px] text-slate-400 border-t border-slate-100 pt-3 leading-relaxed">
        <AlertCircle className="w-3.5 h-3.5 shrink-0 mt-0.5 text-slate-400" />
        <span>{t.advisory.disclaimer}</span>
      </div>
    </div>
  );
};
