import React, { useRef, useState } from "react";
import { UploadCloud, Image as ImageIcon, X, AlertCircle } from "lucide-react";
import { useTranslation } from "../i18n";

interface ImageUploadProps {
  selectedFile: File | null;
  previewUrl: string | null;
  onFileSelect: (file: File) => void;
  onClear: () => void;
  disabled?: boolean;
}

export const ImageUpload: React.FC<ImageUploadProps> = ({
  selectedFile,
  previewUrl,
  onFileSelect,
  onClear,
  disabled = false,
}) => {
  const { t } = useTranslation();
  const [isDragOver, setIsDragOver] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateAndHandle = (file: File) => {
    setValidationError(null);
    if (!file.type.startsWith("image/")) {
      setValidationError(t.upload.invalidTypeError);
      return;
    }
    // Limit to 20MB
    if (file.size > 20 * 1024 * 1024) {
      setValidationError(t.upload.maxSizeError);
      return;
    }
    onFileSelect(file);
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (!disabled) setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
    if (disabled) return;

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      validateAndHandle(e.dataTransfer.files[0]);
    }
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      validateAndHandle(e.target.files[0]);
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  return (
    <div className="w-full">
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={handleFileInputChange}
        disabled={disabled}
      />

      {!previewUrl ? (
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => !disabled && fileInputRef.current?.click()}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => {
            if (e.key === "Enter" || e.key === " ") {
              e.preventDefault();
              !disabled && fileInputRef.current?.click();
            }
          }}
          aria-label={t.upload.dropzoneText}
          className={`relative border-2 border-dashed rounded-2xl p-6 sm:p-8 text-center cursor-pointer transition-all duration-200 ${
            isDragOver
              ? "border-emerald-500 bg-emerald-50/70 scale-[1.01]"
              : "border-slate-300 hover:border-emerald-400 bg-slate-50/50 hover:bg-emerald-50/30"
          } ${disabled ? "opacity-50 cursor-not-allowed" : ""}`}
        >
          <div className="flex flex-col items-center justify-center gap-2.5">
            <div className="w-14 h-14 rounded-2xl bg-emerald-100 text-emerald-700 flex items-center justify-center shadow-xs">
              <UploadCloud className="w-7 h-7" />
            </div>
            <div>
              <p className="text-sm font-bold text-slate-800">
                {t.upload.dropzoneText}
              </p>
              <p className="text-xs text-slate-500 mt-0.5">
                {t.upload.dropzoneSubtext}
              </p>
            </div>
            <div className="mt-1 inline-flex items-center gap-1.5 px-3 py-1 rounded-md bg-white text-slate-600 text-xs font-medium border border-slate-200/80 shadow-xs">
              <ImageIcon className="w-3.5 h-3.5 text-emerald-600" />
              <span>{t.upload.dropzoneHint}</span>
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-white border border-slate-200 rounded-2xl p-3.5 shadow-xs">
          <div className="relative rounded-xl overflow-hidden bg-slate-950 flex items-center justify-center max-h-72 group">
            <img
              src={previewUrl}
              alt="Leaf Preview"
              className="max-h-72 w-auto object-contain transition-opacity duration-200"
            />
            {!disabled && (
              <button
                type="button"
                onClick={onClear}
                aria-label={t.upload.removeImage}
                className="absolute top-2.5 right-2.5 p-1.5 rounded-full bg-slate-900/80 hover:bg-slate-900 text-white backdrop-blur-xs transition-colors shadow-md"
                title={t.upload.removeImage}
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>

          {selectedFile && (
            <div className="mt-3 flex items-center justify-between text-xs text-slate-600 border-t border-slate-100 pt-2.5">
              <div className="flex items-center gap-2 truncate pr-2">
                <ImageIcon className="w-4 h-4 text-emerald-600 shrink-0" />
                <span className="font-semibold text-slate-800 truncate">
                  {selectedFile.name}
                </span>
                <span className="text-slate-400 shrink-0">({formatFileSize(selectedFile.size)})</span>
              </div>
              {!disabled && (
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="text-emerald-700 hover:text-emerald-800 font-bold shrink-0 transition-colors"
                >
                  {t.upload.changeImage}
                </button>
              )}
            </div>
          )}
        </div>
      )}

      {validationError && (
        <div className="mt-2.5 flex items-center gap-2 text-rose-700 text-xs bg-rose-50 border border-rose-200 px-3 py-2 rounded-lg">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{validationError}</span>
        </div>
      )}
    </div>
  );
};
