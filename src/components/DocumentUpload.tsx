import { type ChangeEvent } from "react";

type DocumentUploadProps = {
  label: string;
  required: boolean;
  file: File | null;
  uploaded: boolean;
  onChange: (event: ChangeEvent<HTMLInputElement>) => void;
};

export default function DocumentUpload({ label, required, file, uploaded, onChange }: DocumentUploadProps) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-white">{label}</span>
          {required ? (
            <span className="rounded-full bg-[#FF5C5C]/20 px-2 py-0.5 text-[10px] font-semibold text-[#FF5C5C]">
              Required
            </span>
          ) : (
            <span className="rounded-full bg-white/10 px-2 py-0.5 text-[10px] font-semibold text-muted">
              Optional
            </span>
          )}
        </div>
        {(file || uploaded) && <span className="text-xs text-[#2EE59D]">✓ Selected</span>}
      </div>
      <label className="mt-3 flex cursor-pointer items-center gap-3 rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-xs text-muted transition hover:border-white/20">
        <input
          type="file"
          accept="image/png,image/jpeg,application/pdf"
          onChange={onChange}
          className="hidden"
        />
        <span className="rounded-full bg-white/10 px-3 py-1 text-[10px] font-semibold text-white">
          Choose File
        </span>
        <span className="flex-1 truncate">
          {file ? file.name : `Upload ${label.toLowerCase()} (PNG, JPG, PDF)`}
        </span>
      </label>
    </div>
  );
}
