import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' })

export const metadata: Metadata = {
  title: 'RootPilot AI - Incident Root Cause Analyzer',
  description: 'AI-powered incident intelligence for SRE teams. Detect, explain, and prevent system failures.',
  keywords: 'AI, SRE, incident analysis, root cause, observability, monitoring',
  authors: [{ name: 'RootPilot AI' }],
  viewport: 'width=device-width, initial-scale=1',
  themeColor: '#0a0a0f',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} antialiased bg-black`}>
        <div className="grid-bg min-h-screen">
          {children}
        </div>
      </body>
    </html>
  )
}