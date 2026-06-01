const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export async function generateReport(companyName, file) {
    const formData = new FormData()
    formData.append('company_name', companyName)
    formData.append('uploaded_file', file)

    const response = await fetch(`${API_BASE_URL}/generate-report`, {
        method: 'POST',
        body: formData,
    })

    if (!response.ok) {
        const errorPayload = await response.json().catch(() => ({}))
        throw new Error(errorPayload.detail || 'Failed to generate report')
    }

    return response.json()
}

export function getDownloadUrl(pdfUrl) {
    if (!pdfUrl) return ''
    return `${API_BASE_URL}${pdfUrl}`
}
