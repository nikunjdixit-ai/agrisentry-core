import React from "react";
import { AlertOctagon, X, RefreshCw } from "lucide-react";
import { useTranslation } from "../i18n";

interface ErrorBannerProps {
  message: string;
  onRetry?: () => void;
  onDismiss: () => void;
}

export const ErrorBanner: React.FC<ErrorBannerProps> = ({
  message,
  onRetry,
  onDismiss,
}) => {
  const { t } = useTranslation();

  return (
    <div className="bg-rose-50 border border-rose-200 rounded-2xl p-4 sm:p-5 shadow-xs transition-all">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3">
          <div className="w-8 h-8 rounded-xl bg-rose-100 text-rose-600 flex items-center justify-center shrink-0 mt-0.5">
            <AlertOctagon className="w-5 h-5" />
          </div>
          <div className="space-y-1">
            <h4 className="text-sm font-bold text-rose-950">
              {t.error.title}
            </h4>
            <p className="text-xs text-rose-800 leading-relaxed">{message}</p>
            {message.includes("FastAPI server") && (
              <p className="text-[11px] font-mono text-rose-700 bg-rose-100/70 p-2 rounded-lg mt-2">
                {t.error.serverHint}
              </p>
            )}
          </div>
        </div>

        <div className="flex items-center gap-1 shrink-0">
          {onRetry && (
            <button
              type="button"
              onClick={onRetry}
              className="p-1.5 rounded-lg text-rose-700 hover:bg-rose-100 transition-colors"
              title={t.error.retry}
              aria-label={t.error.retry}
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          )}
          <button
            type="button"
            onClick={onDismiss}
            className="p-1.5 rounded-lg text-rose-500 hover:bg-rose-100 transition-colors"
            title={t.error.dismiss}
            aria-label={t.error.dismiss}
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};
