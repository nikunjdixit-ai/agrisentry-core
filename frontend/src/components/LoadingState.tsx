import React from "react";
import { Loader2, Scan, Database, Network } from "lucide-react";
import { useTranslation } from "../i18n";

export const LoadingState: React.FC = () => {
  const { t } = useTranslation();

  return (
    <div className="bg-white border border-slate-200/80 rounded-2xl p-8 sm:p-12 text-center shadow-xs space-y-6">
      <div className="relative w-20 h-20 mx-auto flex items-center justify-center">
        {/* Outer spinning ring */}
        <Loader2 className="w-20 h-20 text-emerald-600 animate-spin opacity-40 absolute inset-0" />
        {/* Inner scan icon */}
        <div className="w-12 h-12 rounded-2xl bg-emerald-100 text-emerald-700 flex items-center justify-center shadow-inner animate-pulse">
          <Scan className="w-6 h-6" />
        </div>
      </div>

      <div className="space-y-1">
        <h3 className="text-base sm:text-lg font-extrabold text-slate-900">
          {t.loading.title}
        </h3>
        <p className="text-xs text-slate-500 max-w-md mx-auto leading-relaxed">
          {t.loading.description}
        </p>
      </div>

      {/* Pipeline Steps Indicator */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 max-w-xl mx-auto text-left">
        <div className="bg-emerald-50/70 border border-emerald-200 rounded-xl p-3 flex items-center gap-2.5">
          <Scan className="w-4 h-4 text-emerald-600 shrink-0 animate-spin" />
          <div className="min-w-0">
            <span className="text-[11px] font-bold text-emerald-950 block truncate">
              {t.loading.step1Title}
            </span>
            <span className="text-[10px] text-emerald-800 block truncate">
              {t.loading.step1Desc}
            </span>
          </div>
        </div>

        <div className="bg-emerald-50/70 border border-emerald-200 rounded-xl p-3 flex items-center gap-2.5">
          <Database className="w-4 h-4 text-emerald-600 shrink-0 animate-pulse" />
          <div className="min-w-0">
            <span className="text-[11px] font-bold text-emerald-950 block truncate">
              {t.loading.step2Title}
            </span>
            <span className="text-[10px] text-emerald-800 block truncate">
              {t.loading.step2Desc}
            </span>
          </div>
        </div>

        <div className="bg-emerald-50/70 border border-emerald-200 rounded-xl p-3 flex items-center gap-2.5">
          <Network className="w-4 h-4 text-emerald-600 shrink-0 animate-pulse" />
          <div className="min-w-0">
            <span className="text-[11px] font-bold text-emerald-950 block truncate">
              {t.loading.step3Title}
            </span>
            <span className="text-[10px] text-emerald-800 block truncate">
              {t.loading.step3Desc}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
