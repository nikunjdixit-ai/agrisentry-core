import React from "react";
import { Upload, Sparkles, ShieldAlert, Check } from "lucide-react";
import { useTranslation } from "../i18n";

interface WorkflowStepperProps {
  currentStage: 1 | 2 | 3;
}

export const WorkflowStepper: React.FC<WorkflowStepperProps> = ({ currentStage }) => {
  const { t } = useTranslation();

  const steps = [
    {
      num: 1,
      title: t.workflow.step1Title,
      desc: t.workflow.step1Desc,
      icon: Upload,
    },
    {
      num: 2,
      title: t.workflow.step2Title,
      desc: t.workflow.step2Desc,
      icon: Sparkles,
    },
    {
      num: 3,
      title: t.workflow.step3Title,
      desc: t.workflow.step3Desc,
      icon: ShieldAlert,
    },
  ];

  return (
    <div className="bg-white border border-slate-200/80 rounded-2xl p-3.5 sm:p-4 shadow-xs">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {steps.map((step) => {
          const Icon = step.icon;
          const isCompleted = currentStage > step.num;
          const isActive = currentStage === step.num;

          return (
            <div
              key={step.num}
              className={`flex items-center gap-3 p-2.5 rounded-xl transition-all ${
                isActive
                  ? "bg-emerald-50/80 border border-emerald-300/80 shadow-xs"
                  : isCompleted
                  ? "bg-slate-50 border border-slate-200/60"
                  : "opacity-60 border border-transparent"
              }`}
            >
              <div
                className={`w-9 h-9 rounded-xl flex items-center justify-center shrink-0 font-bold text-xs transition-colors ${
                  isCompleted
                    ? "bg-emerald-600 text-white shadow-xs"
                    : isActive
                    ? "bg-emerald-600 text-white ring-4 ring-emerald-100 shadow-xs"
                    : "bg-slate-200 text-slate-600"
                }`}
              >
                {isCompleted ? <Check className="w-4 h-4 stroke-[3]" /> : <Icon className="w-4 h-4" />}
              </div>

              <div className="min-w-0">
                <span
                  className={`text-xs font-bold block truncate ${
                    isActive ? "text-emerald-950" : isCompleted ? "text-slate-800" : "text-slate-500"
                  }`}
                >
                  {step.title}
                </span>
                <span className="text-[11px] text-slate-500 block truncate">
                  {step.desc}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
