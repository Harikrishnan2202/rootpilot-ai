import type { Metadata, Viewport } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'RootPilot AI - Incident Root Cause Analyzer',
  description: 'AI-powered incident intelligence for SRE teams. Detect, explain, and prevent system failures.',
  keywords: 'AI, SRE, incident analysis, root cause, observability, monitoring',
  authors: [{ name: 'RootPilot AI' }],
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  themeColor: '#0a0a0f',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className="antialiased bg-black">
        <div className="grid-bg min-h-screen">
          {children}
        </div>
      </body>
    </html>
  )
}
