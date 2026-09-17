import React, { useState } from "react";
import { WorkflowResult } from "../api/types";
import {
  CloudRain,
  TrendingUp,
  Store,
  Wind,
  Droplets,
  Thermometer,
  Check,
  ChevronDown,
  ChevronUp,
  Info,
  BadgeAlert,
} from "lucide-react";
import { useTranslation } from "../i18n";

interface MultiAgentInsightsProps {
  workflow?: WorkflowResult;
}

export const MultiAgentInsights: React.FC<MultiAgentInsightsProps> = ({ workflow }) => {
  const { t } = useTranslation();
  const [expandedVendor, setExpandedVendor] = useState<boolean>(false);

  if (!workflow) return null;

  const weather = workflow.diagnostic_result?.weather;
  const mandi = workflow.mandi_prices;
  const vendors = workflow.vendor_options || [];

  const hasAnyData = weather || (mandi && mandi.modal_price_per_quintal) || vendors.length > 0;
  if (!hasAnyData) return null;

  return (
    <div className="space-y-3.5">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
            {t.insights.title}
          </h3>
          <p className="text-[11px] text-slate-400 font-medium">
            {t.insights.subtitle}
          </p>
        </div>
        <div className="inline-flex items-center gap-1 text-[10px] font-bold text-amber-800 bg-amber-50 border border-amber-200 px-2 py-0.5 rounded-full">
          <BadgeAlert className="w-3 h-3 text-amber-600" />
          <span>{t.insights.demoBadge}</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* 1. 3-Day Field Weather & Spraying Suitability */}
        {weather && (
          <div className="bg-white border border-slate-200/80 rounded-2xl p-4 shadow-xs space-y-3 flex flex-col justify-between">
            <div className="space-y-2.5">
              <div className="flex items-center justify-between border-b border-slate-100 pb-2">
                <div className="flex items-center gap-1.5">
                  <CloudRain className="w-4 h-4 text-sky-600" />
                  <h4 className="text-xs font-bold text-slate-900 uppercase">
                    {t.insights.weatherTitle}
                  </h4>
                </div>
                <span
                  className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${
                    weather.spraying_suitability?.toLowerCase().includes("suitable")
                      ? "bg-emerald-50 text-emerald-700 border-emerald-300"
                      : "bg-amber-50 text-amber-700 border-amber-300"
                  }`}
                >
                  {weather.spraying_suitability?.toLowerCase().includes("suitable")
                    ? t.insights.suitable
                    : t.insights.unfavorable}
                </span>
              </div>

              {/* Weather Stats */}
              <div className="grid grid-cols-3 gap-1.5 text-center py-0.5">
                <div className="bg-slate-50 rounded-xl p-2 border border-slate-100">
                  <Thermometer className="w-3.5 h-3.5 text-amber-600 mx-auto" />
                  <span className="text-xs font-black text-slate-900 block mt-1">
                    {weather.temperature_c}°C
                  </span>
                  <span className="text-[10px] text-slate-400">{t.insights.temp}</span>
                </div>
                <div className="bg-slate-50 rounded-xl p-2 border border-slate-100">
                  <Droplets className="w-3.5 h-3.5 text-sky-600 mx-auto" />
                  <span className="text-xs font-black text-slate-900 block mt-1">
                    {weather.humidity_percent}%
                  </span>
                  <span className="text-[10px] text-slate-400">{t.insights.humidity}</span>
                </div>
                <div className="bg-slate-50 rounded-xl p-2 border border-slate-100">
                  <Wind className="w-3.5 h-3.5 text-slate-600 mx-auto" />
                  <span className="text-xs font-black text-slate-900 block mt-1">
                    {weather.wind_speed_kmph} km/h
                  </span>
                  <span className="text-[10px] text-slate-400">{t.insights.wind}</span>
                </div>
              </div>

              <div className="text-[11px] text-slate-500 flex items-center justify-between">
                <span className="capitalize truncate">
                  {weather.location || "Regional Hub"}
                </span>
                <span className="text-slate-600 font-semibold">
                  {t.insights.rainProb}: {weather.precipitation_probability}%
                </span>
              </div>
            </div>

            <div className="text-[10px] text-slate-400 border-t border-slate-100 pt-2 font-mono flex items-center justify-between">
              <span>{t.insights.weatherSource}</span>
              <span className="text-amber-700 bg-amber-50 px-1 rounded text-[9px]">Simulated</span>
            </div>
          </div>
        )}

        {/* 2. APMC Mandi Intelligence */}
        {mandi && mandi.modal_price_per_quintal && (
          <div className="bg-white border border-slate-200/80 rounded-2xl p-4 shadow-xs space-y-3 flex flex-col justify-between">
            <div className="space-y-2.5">
              <div className="flex items-center justify-between border-b border-slate-100 pb-2">
                <div className="flex items-center gap-1.5">
                  <TrendingUp className="w-4 h-4 text-emerald-600" />
                  <h4 className="text-xs font-bold text-slate-900 uppercase">
                    {t.insights.mandiTitle}
                  </h4>
                </div>
                <span className="text-[10px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
                  {mandi.arrival_trend || "Stable"}
                </span>
              </div>

              <div>
                <span className="text-[11px] text-slate-500 font-medium block">
                  {t.insights.modalPriceLabel} ({mandi.crop})
                </span>
                <div className="flex items-baseline gap-1.5 mt-0.5">
                  <span className="text-xl font-black text-slate-900">
                    ₹{mandi.modal_price_per_quintal.toLocaleString()}
                  </span>
                  <span className="text-xs text-slate-500 font-semibold">
                    {t.insights.perQuintal}
                  </span>
                </div>
                <div className="flex items-center gap-3 text-xs text-slate-500 mt-2">
                  <span>
                    {t.insights.minPrice}: ₹{mandi.min_price}
                  </span>
                  <span>•</span>
                  <span>
                    {t.insights.maxPrice}: ₹{mandi.max_price}
                  </span>
                </div>
              </div>

              <div className="text-[11px] text-slate-500 truncate">
                {mandi.market_yard || "APMC Yard"} ({mandi.state})
              </div>
            </div>

            <div className="text-[10px] text-slate-400 border-t border-slate-100 pt-2 font-mono flex items-center justify-between">
              <span>{t.insights.mandiSource}</span>
              <span className="text-amber-700 bg-amber-50 px-1 rounded text-[9px]">Benchmark</span>
            </div>
          </div>
        )}

        {/* 3. Authorized Input Suppliers */}
        {vendors.length > 0 && (
          <div className="bg-white border border-slate-200/80 rounded-2xl p-4 shadow-xs space-y-3 flex flex-col justify-between">
            <div className="space-y-2.5">
              <div className="flex items-center justify-between border-b border-slate-100 pb-2">
                <div className="flex items-center gap-1.5">
                  <Store className="w-4 h-4 text-indigo-600" />
                  <h4 className="text-xs font-bold text-slate-900 uppercase">
                    {t.insights.suppliersTitle}
                  </h4>
                </div>
                <span className="text-[10px] font-semibold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded-full border border-indigo-200">
                  {vendors.length} {t.insights.availableStock}
                </span>
              </div>

              <div className="space-y-2">
                {(expandedVendor ? vendors : vendors.slice(0, 1)).map((vendor, idx) => (
                  <div
                    key={idx}
                    className="bg-slate-50 border border-slate-200/80 rounded-xl p-2.5 flex items-center justify-between text-xs"
                  >
                    <div className="min-w-0 pr-2">
                      <span className="font-bold text-slate-900 block truncate">
                        {vendor.dealer_name}
                      </span>
                      <span className="text-[10px] text-slate-500 flex items-center gap-1 mt-0.5">
                        <Check className="w-3 h-3 text-emerald-600 shrink-0" />
                        <span className="truncate">{vendor.cibrc_registration || t.insights.cibrcFilter}</span>
                      </span>
                    </div>
                    <div className="text-right shrink-0">
                      <span className="font-black text-slate-900 block">
                        ₹{vendor.unit_price}
                      </span>
                      <span className="text-[10px] text-emerald-700 font-semibold">
                        {vendor.stock || "In Stock"}
                      </span>
                    </div>
                  </div>
                ))}

                {vendors.length > 1 && (
                  <button
                    type="button"
                    onClick={() => setExpandedVendor(!expandedVendor)}
                    className="w-full text-[11px] font-semibold text-indigo-600 hover:text-indigo-800 flex items-center justify-center gap-1 py-1 transition-colors"
                  >
                    <span>{expandedVendor ? "Show Less" : `View All (${vendors.length}) Dealers`}</span>
                    {expandedVendor ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                  </button>
                )}
              </div>
            </div>

            <div className="text-[10px] text-slate-400 border-t border-slate-100 pt-2 font-mono flex items-center justify-between">
              <span>{t.insights.suppliersSource}</span>
              <span className="text-amber-700 bg-amber-50 px-1 rounded text-[9px]">Sample Catalog</span>
            </div>
          </div>
        )}
      </div>

      <div className="flex items-center gap-1.5 text-[11px] text-slate-400 px-1">
        <Info className="w-3 h-3 text-slate-400 shrink-0" />
        <span>{t.insights.simulatedNotice}</span>
      </div>
    </div>
  );
};
