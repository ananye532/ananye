import { useEffect, useRef, type ReactNode } from "react";
import { Button } from "./button";

export function ConfirmDialog({ open, title, description, confirmLabel = "Delete", onConfirm, onCancel, loading }: {
  open: boolean; title: string; description: ReactNode; confirmLabel?: string; onConfirm: () => void; onCancel: () => void; loading?: boolean;
}) {
  const ref = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    const d = ref.current;
    if (!d) return;
    if (open && !d.open) d.showModal();
    if (!open && d.open) d.close();
  }, [open]);
  return (
    <dialog ref={ref} onCancel={(e) => { e.preventDefault(); onCancel(); }}
      className="m-auto w-[calc(100%-2rem)] max-w-md rounded-2xl border border-border bg-surface p-0 text-fg shadow-pop backdrop:bg-black/40 backdrop:backdrop-blur-[2px]">
      <div className="p-6">
        <h2 className="text-base font-semibold">{title}</h2>
        <div className="mt-2 text-sm text-fg-2">{description}</div>
        <div className="mt-6 flex justify-end gap-2">
          <Button variant="secondary" onClick={onCancel}>Cancel</Button>
          <Button variant="danger" onClick={onConfirm} loading={loading}>{confirmLabel}</Button>
        </div>
      </div>
    </dialog>
  );
}
