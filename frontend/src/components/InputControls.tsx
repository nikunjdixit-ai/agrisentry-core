import React from "react";
import { Search, MapPin, Sparkles, RefreshCw, Info } from "lucide-react";
import { useTranslation } from "../i18n";

interface InputControlsProps {
  crop: string;
  setCrop: (crop: string) => void;
  region: string;
  setRegion: (region: string) => void;
  query: string;
  setQuery: (query: string) => void;
  onDiagnose: () => void;
  onReset: () => void;
  isProcessing: boolean;
  hasImage: boolean;
}

const CROPS_LIST = [
  "tomato",
  "potato",
  "apple",
  "corn",
  "grape",
  "bell pepper",
  "cherry",
  "strawberry",
  "peach",
  "cotton",
  "orange",
  "soybean",
  "squash",
];

const COMMON_REGIONS = [
  "Punjab",
  "Uttar Pradesh",
  "Maharashtra",
  "Haryana",
  "Madhya Pradesh",
  "Gujarat",
  "Karnataka",
  "Andhra Pradesh",
  "Tamil Nadu",
  "Rajasthan",
  "West Bengal",
];

export const InputControls: React.FC<InputControlsProps> = ({
  crop,
  setCrop,
  region,
  setRegion,
  query,
  setQuery,
  onDiagnose,
  onReset,
  isProcessing,
  hasImage,
}) => {
  const { t } = useTranslation();

  return (
    <div className="bg-white border border-slate-200/80 rounded-2xl p-4 sm:p-5 shadow-xs space-y-4">
      <div className="flex items-center justify-between border-b border-slate-100 pb-2.5">
        <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-1.5">
          <Info className="w-3.5 h-3.5 text-emerald-600" />
          <span>{t.controls.title}</span>
        </h2>
        <span className="text-[11px] text-slate-400 font-normal">
          {t.controls.subtitle}
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
        {/* Crop Selector */}
        <div>
          <label htmlFor="crop-select" className="block text-xs font-bold text-slate-700 mb-1">
            {t.controls.cropLabel}
          </label>
          <select
            id="crop-select"
            value={crop}
            onChange={(e) => setCrop(e.target.value)}
            disabled={isProcessing}
            aria-label={t.controls.cropLabel}
            className="w-full text-xs sm:text-sm bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-800 focus:outline-hidden focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 transition-all cursor-pointer disabled:opacity-50"
          >
            <option value="">{t.controls.cropAuto}</option>
            {CROPS_LIST.map((key) => (
              <option key={key} value={key}>
                {t.crops[key] || key}
              </option>
            ))}
          </select>
        </div>

        {/* Region Input / Suggestions */}
        <div>
          <label htmlFor="region-input" className="block text-xs font-bold text-slate-700 mb-1 flex items-center gap-1">
            <MapPin className="w-3.5 h-3.5 text-emerald-600" />
            <span>{t.controls.regionLabel}</span>
          </label>
          <input
            id="region-input"
            type="text"
            list="region-suggestions"
            value={region}
            onChange={(e) => setRegion(e.target.value)}
            placeholder={t.controls.regionPlaceholder}
            disabled={isProcessing}
            aria-label={t.controls.regionLabel}
            className="w-full text-xs sm:text-sm bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-800 placeholder-slate-400 focus:outline-hidden focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 transition-all disabled:opacity-50"
          />
          <datalist id="region-suggestions">
            {COMMON_REGIONS.map((r) => (
              <option key={r} value={r} />
            ))}
          </datalist>
        </div>
      </div>

      {/* Query Input */}
      <div>
        <label htmlFor="query-input" className="block text-xs font-bold text-slate-700 mb-1 flex items-center gap-1">
          <Search className="w-3.5 h-3.5 text-emerald-600" />
          <span>{t.controls.queryLabel}</span>
        </label>
        <input
          id="query-input"
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={t.controls.queryPlaceholder}
          disabled={isProcessing}
          aria-label={t.controls.queryLabel}
          className="w-full text-xs sm:text-sm bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-800 placeholder-slate-400 focus:outline-hidden focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 transition-all disabled:opacity-50"
        />
      </div>

      {/* Action Buttons */}
      <div className="pt-1 flex flex-col sm:flex-row items-center gap-2.5">
        <button
          type="button"
          onClick={onDiagnose}
          disabled={!hasImage || isProcessing}
          aria-busy={isProcessing}
          className={`w-full sm:flex-1 py-3 px-5 rounded-xl font-bold text-xs sm:text-sm flex items-center justify-center gap-2 shadow-sm transition-all duration-200 ${
            !hasImage || isProcessing
              ? "bg-slate-200 text-slate-400 cursor-not-allowed shadow-none"
              : "bg-emerald-600 hover:bg-emerald-700 text-white shadow-emerald-600/20 hover:shadow-md hover:scale-[1.005] active:scale-[0.995]"
          }`}
        >
          <Sparkles className="w-4 h-4 text-emerald-200" />
          <span>{isProcessing ? t.controls.analyzingBtn : t.controls.diagnoseBtn}</span>
        </button>

        {hasImage && !isProcessing && (
          <button
            type="button"
            onClick={onReset}
            className="w-full sm:w-auto py-3 px-4 rounded-xl border border-slate-200 hover:bg-slate-100 text-slate-600 text-xs sm:text-sm font-semibold transition-colors flex items-center justify-center gap-1.5"
            title={t.controls.resetBtn}
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>{t.controls.resetBtn}</span>
          </button>
        )}
      </div>
    </div>
  );
};
