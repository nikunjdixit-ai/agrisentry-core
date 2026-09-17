import React, { useEffect, useRef, useState } from "react";
import { Detection } from "../api/types";
import { ZoomIn, ZoomOut, RotateCcw, Eye, Layers } from "lucide-react";
import { useTranslation } from "../i18n";

interface BoundingBoxCanvasProps {
  imageUrl: string;
  detections: Detection[];
  severity?: string;
}

export const BoundingBoxCanvas: React.FC<BoundingBoxCanvasProps> = ({
  imageUrl,
  detections,
  severity,
}) => {
  const { t } = useTranslation();
  const containerRef = useRef<HTMLDivElement>(null);
  const imgRef = useRef<HTMLImageElement>(null);
  const [scale, setScale] = useState<{ scaleX: number; scaleY: number }>({
    scaleX: 1,
    scaleY: 1,
  });
  const [isImgLoaded, setIsImgLoaded] = useState<boolean>(false);
  const [showOverlay, setShowOverlay] = useState<boolean>(true);
  const [zoomLevel, setZoomLevel] = useState<number>(1);

  const updateScale = () => {
    if (!imgRef.current) return;
    const { naturalWidth, naturalHeight, clientWidth, clientHeight } = imgRef.current;

    if (naturalWidth > 0 && naturalHeight > 0 && clientWidth > 0 && clientHeight > 0) {
      setScale({
        scaleX: clientWidth / naturalWidth,
        scaleY: clientHeight / naturalHeight,
      });
    }
  };

  useEffect(() => {
    updateScale();
    window.addEventListener("resize", updateScale);
    return () => window.removeEventListener("resize", updateScale);
  }, [isImgLoaded, imageUrl, zoomLevel]);

  // Zoom handlers
  const handleZoomIn = () => setZoomLevel((prev) => Math.min(prev + 0.25, 2.5));
  const handleZoomOut = () => setZoomLevel((prev) => Math.max(prev - 0.25, 1));
  const handleResetZoom = () => setZoomLevel(1);

  // Color mapping based on severity
  const getBoxColor = () => {
    switch (severity?.toLowerCase()) {
      case "high":
        return {
          border: "border-rose-500",
          bg: "bg-rose-500/25",
          pill: "bg-rose-600 text-white",
          dot: "bg-rose-500",
        };
      case "moderate":
        return {
          border: "border-amber-500",
          bg: "bg-amber-500/25",
          pill: "bg-amber-600 text-white",
          dot: "bg-amber-500",
        };
      default:
        return {
          border: "border-emerald-500",
          bg: "bg-emerald-500/25",
          pill: "bg-emerald-600 text-white",
          dot: "bg-emerald-500",
        };
    }
  };

  const boxColors = getBoxColor();

  return (
    <div className="bg-white border border-slate-200/80 rounded-2xl p-3 sm:p-4 shadow-xs space-y-3">
      {/* Top Toolbar: Toggle and Zoom */}
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-100 pb-2.5">
        <div className="flex items-center gap-1.5">
          <button
            type="button"
            onClick={() => setShowOverlay(true)}
            className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-bold transition-all ${
              showOverlay
                ? "bg-emerald-600 text-white shadow-xs"
                : "bg-slate-100 text-slate-600 hover:bg-slate-200"
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            <span>{t.diagnosis.overlayViewToggle}</span>
          </button>
          <button
            type="button"
            onClick={() => setShowOverlay(false)}
            className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-bold transition-all ${
              !showOverlay
                ? "bg-emerald-600 text-white shadow-xs"
                : "bg-slate-100 text-slate-600 hover:bg-slate-200"
            }`}
          >
            <Eye className="w-3.5 h-3.5" />
            <span>{t.diagnosis.originalImageToggle}</span>
          </button>
        </div>

        {/* Zoom Controls */}
        <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-lg text-slate-700">
          <button
            type="button"
            onClick={handleZoomIn}
            disabled={zoomLevel >= 2.5}
            title={t.diagnosis.zoomIn}
            aria-label={t.diagnosis.zoomIn}
            className="p-1 rounded-md hover:bg-white hover:text-slate-900 transition-colors disabled:opacity-40"
          >
            <ZoomIn className="w-3.5 h-3.5" />
          </button>
          <span className="text-[10px] font-mono font-bold px-1.5 min-w-[36px] text-center">
            {Math.round(zoomLevel * 100)}%
          </span>
          <button
            type="button"
            onClick={handleZoomOut}
            disabled={zoomLevel <= 1}
            title={t.diagnosis.zoomOut}
            aria-label={t.diagnosis.zoomOut}
            className="p-1 rounded-md hover:bg-white hover:text-slate-900 transition-colors disabled:opacity-40"
          >
            <ZoomOut className="w-3.5 h-3.5" />
          </button>
          {zoomLevel > 1 && (
            <button
              type="button"
              onClick={handleResetZoom}
              title={t.diagnosis.resetZoom}
              aria-label={t.diagnosis.resetZoom}
              className="p-1 rounded-md hover:bg-white hover:text-slate-900 transition-colors"
            >
              <RotateCcw className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>

      {/* Main Image Viewport with Pan/Zoom container */}
      <div
        ref={containerRef}
        className="relative w-full rounded-xl overflow-auto bg-slate-950 flex items-center justify-center select-none shadow-inner max-h-[460px]"
      >
        <div
          style={{
            transform: `scale(${zoomLevel})`,
            transformOrigin: "center center",
            transition: "transform 0.15s ease-out",
          }}
          className="relative inline-block"
        >
          <img
            ref={imgRef}
            src={imageUrl}
            alt="Analyzed Leaf"
            onLoad={() => {
              setIsImgLoaded(true);
              updateScale();
            }}
            className="max-h-[440px] w-auto object-contain block mx-auto pointer-events-none"
          />

          {/* Render Bounding Boxes */}
          {showOverlay &&
            isImgLoaded &&
            detections &&
            detections.map((det, index) => {
              const { x1, y1, x2, y2 } = det.bbox;

              const left = x1 * scale.scaleX;
              const top = y1 * scale.scaleY;
              const width = Math.max(8, (x2 - x1) * scale.scaleX);
              const height = Math.max(8, (y2 - y1) * scale.scaleY);

              return (
                <div
                  key={index}
                  style={{
                    left: `${left}px`,
                    top: `${top}px`,
                    width: `${width}px`,
                    height: `${height}px`,
                  }}
                  className={`absolute border-2 ${boxColors.border} ${boxColors.bg} transition-all duration-150 rounded-xs pointer-events-none`}
                >
                  {/* Box Tag Label */}
                  <div
                    className={`absolute -top-6 left-0 px-2 py-0.5 rounded-sm text-[10px] font-bold tracking-tight shadow-md flex items-center gap-1 ${boxColors.pill} whitespace-nowrap`}
                  >
                    <span>{det.display_name || det.class_name}</span>
                    <span className="opacity-90">({(det.confidence * 100).toFixed(1)}%)</span>
                  </div>
                </div>
              );
            })}
        </div>
      </div>

      {/* Bottom Footer: Detected lesion count & Legend */}
      <div className="flex flex-wrap items-center justify-between text-xs text-slate-500 pt-1 gap-2">
        <div className="flex items-center gap-2">
          <span className={`w-2.5 h-2.5 rounded-full ${boxColors.dot}`} />
          <span className="font-semibold text-slate-700">
            {detections?.length || 0} {t.diagnosis.lesionsCountLabel}
          </span>
        </div>
        <div className="text-[11px] text-slate-400 font-medium">
          Scaled dynamically to native image coordinates
        </div>
      </div>
    </div>
  );
};
