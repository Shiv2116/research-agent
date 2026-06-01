import { useMemo, useState } from 'react'
import { generateReport, getDownloadUrl } from './api'

export default function App() {
    const [companyName, setCompanyName] = useState('')
    const [file, setFile] = useState(null)
    const [loading, setLoading] = useState(false)
    const [message, setMessage] = useState('')
    const [pdfUrl, setPdfUrl] = useState('')

    const canGenerate = useMemo(() => companyName.trim() && file && !loading, [companyName, file, loading])

    const handleGenerate = async (event) => {
        event.preventDefault()
        if (!companyName.trim() || !file) {
            setMessage('Please enter a company name and upload a PDF, TXT, or CSV file.')
            return
        }

        setLoading(true)
        setMessage('Preparing report...')
        setPdfUrl('')

        try {
            const result = await generateReport(companyName.trim(), file)
            setPdfUrl(getDownloadUrl(result.pdf_url))
            setMessage('Report generated successfully.')
        } catch (error) {
            setMessage(error.message || 'Something went wrong while generating the report.')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="min-h-screen bg-[radial-gradient(circle_at_top_left,_rgba(59,130,246,0.24),_transparent_36%),radial-gradient(circle_at_top_right,_rgba(15,118,110,0.16),_transparent_24%),linear-gradient(180deg,_#f8fafc_0%,_#eef2ff_100%)] text-slate-900">
            <div className="mx-auto flex min-h-screen max-w-6xl items-center px-4 py-10 sm:px-6 lg:px-8">
                <div className="grid w-full gap-8 lg:grid-cols-[1.05fr_0.95fr]">
                    <section className="overflow-hidden rounded-[2rem] border border-white/70 bg-white/80 shadow-soft backdrop-blur-xl">
                        <div className="border-b border-slate-200/80 bg-[linear-gradient(135deg,_#0f172a,_#1e3a8a)] px-8 py-7 text-white">
                            <div className="inline-flex items-center rounded-full border border-white/20 bg-white/10 px-3 py-1 text-xs font-medium uppercase tracking-[0.24em] text-slate-200">
                                Financial Research MVP
                            </div>
                            <h1 className="mt-5 max-w-xl text-4xl font-semibold tracking-tight sm:text-5xl" style={{ fontFamily: 'Source Serif 4, Georgia, serif' }}>
                                Upload a financial document and generate a report instantly.
                            </h1>
                            <p className="mt-4 max-w-2xl text-sm leading-6 text-slate-200/90 sm:text-base">
                                The backend extracts text locally, calls DeepSeek when available, builds chart snapshots, and renders a downloadable PDF modeled after the sample report.
                            </p>
                        </div>

                        <form onSubmit={handleGenerate} className="space-y-5 px-8 py-8">
                            <div>
                                <label className="mb-2 block text-sm font-semibold text-slate-700">Company Name</label>
                                <input
                                    type="text"
                                    value={companyName}
                                    onChange={(event) => setCompanyName(event.target.value)}
                                    placeholder="e.g. JSW Energy"
                                    className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none transition focus:border-sky-400 focus:bg-white focus:ring-4 focus:ring-sky-100"
                                />
                            </div>

                            <div>
                                <label className="mb-2 block text-sm font-semibold text-slate-700">Financial Context Document</label>
                                <label className="flex min-h-36 cursor-pointer flex-col items-center justify-center rounded-3xl border-2 border-dashed border-slate-200 bg-slate-50 px-5 py-6 text-center transition hover:border-sky-400 hover:bg-sky-50/60">
                                    <input
                                        type="file"
                                        accept=".pdf,.txt,.csv"
                                        onChange={(event) => setFile(event.target.files?.[0] || null)}
                                        className="hidden"
                                    />
                                    <div className="text-base font-semibold text-slate-800">{file ? file.name : 'Drop or choose a PDF, TXT, or CSV file'}</div>
                                    <div className="mt-2 text-sm text-slate-500">The file stays local on your machine and is parsed by the FastAPI backend.</div>
                                </label>
                            </div>

                            <div className="flex flex-col gap-3 sm:flex-row">
                                <button
                                    type="submit"
                                    disabled={!canGenerate}
                                    className="inline-flex items-center justify-center rounded-2xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
                                >
                                    {loading ? (
                                        <span className="inline-flex items-center gap-2">
                                            <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                                            Generating
                                        </span>
                                    ) : (
                                        'Generate Report'
                                    )}
                                </button>

                                <a
                                    href={pdfUrl || '#'}
                                    onClick={(event) => {
                                        if (!pdfUrl) event.preventDefault()
                                    }}
                                    target="_blank"
                                    rel="noreferrer"
                                    className={`inline-flex items-center justify-center rounded-2xl border px-5 py-3 text-sm font-semibold transition ${pdfUrl ? 'border-sky-200 bg-sky-50 text-sky-900 hover:border-sky-300 hover:bg-sky-100' : 'pointer-events-none border-slate-200 bg-slate-100 text-slate-400'
                                        }`}
                                >
                                    Download Report
                                </a>
                            </div>

                            <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-600">
                                {message || 'Upload a document to generate a PDF report.'}
                            </div>
                        </form>
                    </section>

                    <aside className="flex flex-col justify-between rounded-[2rem] border border-slate-200/70 bg-slate-950 px-8 py-8 text-white shadow-soft">
                        <div>
                            <div className="inline-flex rounded-full bg-emerald-400/15 px-3 py-1 text-xs font-semibold uppercase tracking-[0.24em] text-emerald-300">
                                MVP Flow
                            </div>
                            <h2 className="mt-5 text-3xl font-semibold tracking-tight" style={{ fontFamily: 'Source Serif 4, Georgia, serif' }}>
                                Simple pipeline, local storage, immediate download.
                            </h2>
                            <div className="mt-6 grid gap-4 text-sm text-slate-300">
                                <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                                    <div className="font-semibold text-white">1. Upload</div>
                                    <div className="mt-1 leading-6">Company name plus PDF, TXT, or CSV enters the FastAPI backend as a normal form upload.</div>
                                </div>
                                <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                                    <div className="font-semibold text-white">2. Analyze</div>
                                    <div className="mt-1 leading-6">The document is parsed, summarized with DeepSeek, and converted into metrics plus research highlights.</div>
                                </div>
                                <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                                    <div className="font-semibold text-white">3. Export</div>
                                    <div className="mt-1 leading-6">Charts and a three-page PDF are created under the backend generated folder and exposed through a download endpoint.</div>
                                </div>
                            </div>
                        </div>

                        <div className="mt-8 rounded-3xl border border-sky-400/20 bg-[linear-gradient(135deg,_rgba(14,165,233,0.15),_rgba(15,23,42,0.45))] p-5 text-sm text-slate-200">
                            If DeepSeek is not configured, the app falls back to a local extraction path so the MVP still produces a report.
                        </div>
                    </aside>
                </div>
            </div>
        </div>
    )
}
