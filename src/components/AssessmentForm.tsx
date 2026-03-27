import { type ChangeEvent } from "react";
import { motion } from "framer-motion";
import FormInput from "./FormInput";
import DocumentUpload from "./DocumentUpload";
import type { AssessmentInput } from "@/lib/api";
import { employmentOptions, getDocumentRequirements } from "@/lib/assistantHelpers";

type FormData = {
  income: string;
  expenses: string;
  employmentType: AssessmentInput["employment_type"];
  jobTenure: string;
  name: string;
  employer: string;
  mobile: string;
};

type AssessmentFormProps = {
  formData: FormData;
  setFormData: React.Dispatch<React.SetStateAction<FormData>>;
  payslipFile: File | null;
  bankStatementFile: File | null;
  onFileChange: (event: ChangeEvent<HTMLInputElement>, type: "payslip" | "bank_statement") => void;
  errorMessage: string | null;
  loading: boolean;
  onSubmit: () => void;
};

export default function AssessmentForm({
  formData,
  setFormData,
  payslipFile,
  bankStatementFile,
  onFileChange,
  errorMessage,
  loading,
  onSubmit,
}: AssessmentFormProps) {
  const requirements = getDocumentRequirements(formData.employmentType);

  const update = <K extends keyof FormData>(key: K, value: FormData[K]) => {
    setFormData((prev) => ({ ...prev, [key]: value }));
  };

  return (
    <motion.div
      whileHover={{ y: -4 }}
      transition={{ type: "spring", stiffness: 120, damping: 16 }}
      className="glass glow-border mx-auto w-full max-w-2xl rounded-3xl p-8"
    >
      <p className="text-xs uppercase tracking-[0.3em] text-muted">New Assessment</p>
      <h2 className="mt-3 text-xl font-semibold text-white">Run Credit Evaluation</h2>
      <div className="mt-6 grid gap-5">
        <div className="grid gap-4 sm:grid-cols-2">
          <FormInput
            label="Monthly Income"
            type="number"
            value={formData.income}
            onChange={(val) => update("income", val)}
            min={0}
          />
          <FormInput
            label="Monthly Expenses"
            type="number"
            value={formData.expenses}
            onChange={(val) => update("expenses", val)}
            min={0}
          />
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label htmlFor="employment-type" className="text-xs uppercase tracking-[0.25em] text-muted">
              Employment Type
            </label>
            <select
              id="employment-type"
              value={formData.employmentType}
              onChange={(e) => update("employmentType", e.target.value as AssessmentInput["employment_type"])}
              className="mt-3 w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none focus:border-[#4F7FFF]/70 focus:ring-2 focus:ring-[#4F7FFF]/30"
            >
              {employmentOptions.map((option) => (
                <option key={option} value={option} className="bg-[#0A0F1F]">
                  {option}
                </option>
              ))}
            </select>
          </div>
          <FormInput
            label="Job Tenure (Years)"
            type="number"
            value={formData.jobTenure}
            onChange={(val) => update("jobTenure", val)}
            min={0}
            step={0.5}
          />
        </div>
        <div className="grid gap-4 sm:grid-cols-3">
          <FormInput
            label="Full Name"
            value={formData.name}
            onChange={(val) => update("name", val)}
            placeholder="John Doe"
          />
          <FormInput
            label="Employer"
            value={formData.employer}
            onChange={(val) => update("employer", val)}
            placeholder="Company Name"
          />
          <FormInput
            label="Mobile"
            type="tel"
            value={formData.mobile}
            onChange={(val) => update("mobile", val)}
            placeholder="+1234567890"
          />
        </div>

        {/* Documents */}
        <div>
          <label className="text-xs uppercase tracking-[0.25em] text-muted">Documents</label>
          <div className="mt-3 grid gap-3 sm:grid-cols-2">
            {(requirements.payslip.required || !requirements.bankStatement.required) && (
              <DocumentUpload
                label={requirements.payslip.label}
                required={requirements.payslip.required}
                file={payslipFile}
                uploaded={false}
                onChange={(e) => onFileChange(e, "payslip")}
              />
            )}
            {(requirements.bankStatement.required || formData.employmentType !== "Full-time") && (
              <DocumentUpload
                label={requirements.bankStatement.label}
                required={requirements.bankStatement.required}
                file={bankStatementFile}
                uploaded={false}
                onChange={(e) => onFileChange(e, "bank_statement")}
              />
            )}
          </div>
        </div>
      </div>

      {errorMessage && (
        <div className="mt-5 rounded-2xl border border-[#FF5C5C]/30 bg-[#FF5C5C]/10 px-4 py-3 text-xs text-[#FF5C5C]">
          {errorMessage}
        </div>
      )}

      <button
        id="submit-assessment-btn"
        onClick={onSubmit}
        disabled={loading}
        className="ripple mt-8 w-full rounded-2xl bg-gradient-to-r from-[#4F7FFF] to-[#9B6BFF] px-6 py-4 text-sm font-semibold uppercase tracking-wide text-white shadow-lg shadow-[#4F7FFF]/30 transition hover:brightness-110 disabled:opacity-40 focus:outline-none focus:ring-2 focus:ring-[#4F7FFF]/60"
      >
        Run Assessment
      </button>
    </motion.div>
  );
}
