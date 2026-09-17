import React, { useEffect, useState } from "react";
import { Sprout, Activity, ShieldCheck, Cpu, Globe } from "lucide-react";
import { checkApiHealth } from "../api/client";
import { useTranslation } from "../i18n";

export const Header: React.FC = () => {
  const { t, language, setLanguage } = useTranslation();
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null);

  useEffect(() => {
    let isMounted = true;
    checkApiHealth().then((isHealthy) => {
      if (isMounted) setBackendOnline(isHealthy);
    });
    const interval = setInterval(() => {
      checkApiHealth().then((isHealthy) => {
        if (isMounted) setBackendOnline(isHealthy);
      });
    }, 15000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  return (
    <header className="bg-white border-b border-slate-200/80 sticky top-0 z-30 shadow-xs backdrop-blur-md bg-white/95">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3 flex flex-wrap items-center justify-between gap-3">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-600 to-green-500 flex items-center justify-center text-white shadow-md shadow-emerald-500/20 shrink-0">
            <Sprout className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-extrabold text-slate-900 tracking-tight">
                {t.header.title}
              </h1>
              <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-emerald-100/80 text-emerald-800 border border-emerald-200">
                {t.header.version}
              </span>
            </div>
            <p className="text-xs text-slate-500 hidden sm:block">
              {t.header.subtitle}
            </p>
          </div>
        </div>

        {/* Right Section: Badges & Language Selector */}
        <div className="flex items-center gap-2 sm:gap-3 flex-wrap">
          {/* Architecture Badges */}
          <div className="hidden lg:flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-100 text-slate-600 border border-slate-200/80 text-xs font-medium">
            <Cpu className="w-3.5 h-3.5 text-slate-500" />
            <span>{t.header.cpuBadge}</span>
          </div>

          <div className="hidden lg:flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-100 text-slate-600 border border-slate-200/80 text-xs font-medium">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
            <span>{t.header.ragBadge}</span>
          </div>

          {/* Backend Status Pill */}
          <div
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border transition-colors ${
              backendOnline === true
                ? "bg-emerald-50 text-emerald-700 border-emerald-300"
                : backendOnline === false
                ? "bg-rose-50 text-rose-700 border-rose-300"
                : "bg-amber-50 text-amber-700 border-amber-300"
            }`}
            title={backendOnline ? "FastAPI Backend is reachable" : "Backend unreachable on port 8000"}
          >
            <Activity
              className={`w-3.5 h-3.5 ${
                backendOnline === true
                  ? "text-emerald-600 animate-pulse"
                  : backendOnline === false
                  ? "text-rose-600"
                  : "text-amber-600"
              }`}
            />
            <span className="text-[11px] sm:text-xs">
              {backendOnline === true
                ? t.header.backendConnected
                : backendOnline === false
                ? t.header.backendOffline
                : t.header.backendChecking}
            </span>
          </div>

          {/* Bilingual Language Selector */}
          <div className="inline-flex items-center bg-slate-100 p-0.5 rounded-xl border border-slate-200 shadow-inner">
            <Globe className="w-3.5 h-3.5 text-slate-400 ml-2 mr-1 hidden sm:block" />
            <button
              type="button"
              onClick={() => setLanguage("en")}
              aria-label="Switch to English language"
              className={`px-2.5 py-1 rounded-lg text-xs font-bold transition-all ${
                language === "en"
                  ? "bg-white text-emerald-800 shadow-xs"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              English
            </button>
            <button
              type="button"
              onClick={() => setLanguage("hi")}
              aria-label="हिंदी भाषा चुनें"
              className={`px-2.5 py-1 rounded-lg text-xs font-bold transition-all ${
                language === "hi"
                  ? "bg-emerald-600 text-white shadow-xs"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              हिंदी
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};
