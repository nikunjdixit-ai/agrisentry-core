import { useState } from "react";
import { Header } from "./components/Header";
import { WorkflowStepper } from "./components/WorkflowStepper";
import { ImageUpload } from "./components/ImageUpload";
import { InputControls } from "./components/InputControls";
import { BoundingBoxCanvas } from "./components/BoundingBoxCanvas";
import { DiagnosisCard } from "./components/DiagnosisCard";
import { AdvisoryCard } from "./components/AdvisoryCard";
import { MultiAgentInsights } from "./components/MultiAgentInsights";
import { LoadingState } from "./components/LoadingState";
import { ErrorBanner } from "./components/ErrorBanner";
import { diagnoseCrop } from "./api/client";
import { DiagnosisApiResponse } from "./api/types";
import { useTranslation } from "./i18n";
import { Leaf, Eye, ShieldCheck } from "lucide-react";

export function App() {
  const { t, language } = useTranslation();

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [crop, setCrop] = useState<string>("");
  const [region, setRegion] = useState<string>("Punjab");
  const [query, setQuery] = useState<string>("");
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [apiError, setApiError] = useState<string | null>(null);
  const [diagnosisData, setDiagnosisData] = useState<DiagnosisApiResponse | null>(null);

  // Workflow stages: 1 = Upload, 2 = Analyze, 3 = Action & Advisory
  const currentStage: 1 | 2 | 3 = isProcessing ? 2 : diagnosisData ? 3 : 1;

  const handleFileSelect = (file: File) => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    setSelectedFile(file);
    setPreviewUrl(URL.createObjectURL(file));
    setApiError(null);
    setDiagnosisData(null);
  };

  const handleClear = () => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    setSelectedFile(null);
    setPreviewUrl(null);
    setDiagnosisData(null);
    setApiError(null);
  };

  const handleResetAll = () => {
    handleClear();
    setCrop("");
    setRegion("Punjab");
    setQuery("");
  };

  const handleDiagnose = async () => {
    if (!selectedFile) return;

    setIsProcessing(true);
    setApiError(null);

    try {
      const response = await diagnoseCrop({
        image: selectedFile,
        crop,
        region,
        query,
        language,
      });
      setDiagnosisData(response);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setApiError(err.message);
      } else {
        setApiError("An unexpected error occurred while communicating with the diagnostic server.");
      }
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      <Header />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 space-y-6">
        {/* Banner Alert if error occurred */}
        {apiError && (
          <ErrorBanner
            message={apiError}
            onRetry={handleDiagnose}
            onDismiss={() => setApiError(null)}
          />
        )}

        {/* Farmer Workflow Stepper */}
        <WorkflowStepper currentStage={currentStage} />

        {/* Dashboard Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Left Column: Image Ingestion & Controls (5 cols on lg) */}
          <div className="lg:col-span-5 space-y-5">
            {/* Upload Card */}
            <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs space-y-3">
              <div className="flex items-center justify-between">
                <h2 className="text-sm font-bold text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
                  <Leaf className="w-4 h-4 text-emerald-600" />
                  <span>{t.upload.title}</span>
                </h2>
                <span className="text-[11px] text-slate-400 font-medium">
                  {t.upload.stepIndicator}
                </span>
              </div>

              <ImageUpload
                selectedFile={selectedFile}
                previewUrl={previewUrl}
                onFileSelect={handleFileSelect}
                onClear={handleClear}
                disabled={isProcessing}
              />
            </div>

            {/* Input Controls Card */}
            <InputControls
              crop={crop}
              setCrop={setCrop}
              region={region}
              setRegion={setRegion}
              query={query}
              setQuery={setQuery}
              onDiagnose={handleDiagnose}
              onReset={handleResetAll}
              isProcessing={isProcessing}
              hasImage={!!selectedFile}
            />

            {/* Precision Agronomy Guidance Tips */}
            <div className="bg-emerald-50/70 border border-emerald-200/70 rounded-2xl p-4 text-xs text-emerald-950 space-y-2">
              <span className="font-bold flex items-center gap-1.5 text-emerald-900">
                <ShieldCheck className="w-4 h-4 text-emerald-600" />
                <span>{t.controls.tipsTitle}</span>
              </span>
              <ul className="list-disc list-inside text-emerald-800/90 space-y-1.5 pl-1 leading-relaxed">
                <li>{t.controls.tip1}</li>
                <li>{t.controls.tip2}</li>
                <li>{t.controls.tip3}</li>
              </ul>
            </div>
          </div>

          {/* Right Column: Dynamic Diagnostics & Insights (7 cols on lg) */}
          <div className="lg:col-span-7 space-y-5">
            {/* State 1: Currently Processing */}
            {isProcessing && <LoadingState />}

            {/* State 2: Diagnosis Result Ready */}
            {!isProcessing && diagnosisData && (
              <div className="space-y-5">
                {/* 1. Bounding Box Visualizer */}
                {previewUrl && (
                  <div className="bg-white border border-slate-200 rounded-2xl p-4 sm:p-5 shadow-xs space-y-3">
                    <div className="flex items-center justify-between text-xs text-slate-500 pb-1">
                      <span className="font-bold text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
                        <Eye className="w-4 h-4 text-emerald-600" />
                        <span>{t.diagnosis.title}</span>
                      </span>
                      <span className="text-[11px] font-medium bg-slate-100 px-2.5 py-0.5 rounded-full text-slate-700">
                        {diagnosisData.diagnosis?.detections?.length || 0} {t.diagnosis.regionsDetectedLabel}
                      </span>
                    </div>

                    <BoundingBoxCanvas
                      imageUrl={previewUrl}
                      detections={diagnosisData.diagnosis.detections}
                      severity={diagnosisData.diagnosis.severity}
                    />
                  </div>
                )}

                {/* 2. Core Diagnosis Metric Card */}
                <DiagnosisCard
                  diagnosis={diagnosisData.diagnosis}
                  workflow={diagnosisData.workflow}
                />

                {/* 3. Actionable Advisory Card */}
                <AdvisoryCard workflow={diagnosisData.workflow} />

                {/* 4. Multi-Agent Ecosystem Insights */}
                <MultiAgentInsights workflow={diagnosisData.workflow} />
              </div>
            )}

            {/* State 3: Empty State (Waiting for user upload) */}
            {!isProcessing && !diagnosisData && (
              <div className="bg-white border border-slate-200 rounded-2xl p-8 sm:p-12 text-center shadow-xs space-y-4">
                <div className="w-16 h-16 rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center mx-auto border border-emerald-100 shadow-xs">
                  <Leaf className="w-8 h-8" />
                </div>
                <div className="space-y-2 max-w-md mx-auto">
                  <h3 className="text-base font-bold text-slate-800">
                    {t.emptyState.title}
                  </h3>
                  <p className="text-xs text-slate-500 leading-relaxed">
                    {t.emptyState.description}
                  </p>
                </div>
                <div className="pt-2 flex flex-wrap items-center justify-center gap-2 text-[11px] text-slate-500 font-medium">
                  <span className="bg-slate-50 border border-slate-200 px-3 py-1 rounded-full">
                    {t.emptyState.cropsBadge}
                  </span>
                  <span className="bg-slate-50 border border-slate-200 px-3 py-1 rounded-full">
                    {t.emptyState.pathologiesBadge}
                  </span>
                  <span className="bg-slate-50 border border-slate-200 px-3 py-1 rounded-full">
                    {t.emptyState.speedBadge}
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 mt-auto py-4 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>{t.footer.tagline}</span>
          <span className="font-mono text-[11px] text-slate-400">
            {t.footer.engine}
          </span>
        </div>
      </footer>
    </div>
  );
}

export default App;
