import { useEffect, useRef, useState } from "react";
import { Upload } from "lucide-react";
import { api } from "../api/client";
import { PageHeader, Panel, StatusPill, EmptyState } from "../components/ui";

export default function Documents() {
  const [docs, setDocs] = useState<any[]>([]);
  const [uploading, setUploading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  async function load() {
    setDocs(await api.documents());
  }

  useEffect(() => {
    load();
  }, []);

  async function onFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      await api.uploadDocument(file);
      await load();
    } finally {
      setUploading(false);
      if (inputRef.current) inputRef.current.value = "";
    }
  }

  return (
    <div>
      <PageHeader
        title="Document Processing"
        subtitle="Upload PDFs, Word docs, CSVs, or text files — they're chunked, embedded, and indexed for RAG automatically."
        action={
          <label className="bg-signal text-bg rounded-md px-4 py-2 text-sm font-medium flex items-center gap-2 cursor-pointer">
            <Upload size={15} /> {uploading ? "Uploading…" : "Upload document"}
            <input ref={inputRef} type="file" className="hidden" onChange={onFile} accept=".pdf,.docx,.csv,.txt,.md,.json" />
          </label>
        }
      />
      <div className="p-8">
        {docs.length === 0 ? (
          <EmptyState title="No documents yet" description="Uploaded files are chunked and embedded into the vector store for retrieval-augmented generation." />
        ) : (
          <Panel className="divide-y divide-border">
            {docs.map((d) => (
              <div key={d.id} className="flex items-center justify-between px-4 py-3 text-sm">
                <div>
                  <div>{d.filename}</div>
                  <div className="text-[11px] text-text-dim font-mono mt-0.5">{d.file_type} · {d.num_chunks} chunks</div>
                </div>
                <StatusPill status={d.status} />
              </div>
            ))}
          </Panel>
        )}
      </div>
    </div>
  );
}
