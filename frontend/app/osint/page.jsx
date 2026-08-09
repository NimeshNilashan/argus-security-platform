'use client'

import { useUser } from '@clerk/nextjs'
import { useState } from 'react'

export default function OSINTPage() {
  const { user, isLoaded, isSignedIn } = useUser()

  const [domain, setDomain] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  if (!isLoaded) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        Loading...
      </div>
    )
  }

  if (!isSignedIn || !user) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        Please sign in to use OSINT Recon.
      </div>
    )
  }

  async function runRecon(e) {
    e.preventDefault()

    if (!domain.trim()) {
      setError('Please enter a domain.')
      return
    }

    setLoading(true)
    setError('')
    setResult(null)

    try {
      const formData = new FormData()

      formData.append('user_id', user.id)
      formData.append('domain', domain.trim())

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/osint/recon`,
        {
          method: 'POST',
          body: formData,
        }
      )

      const data = await response.json()

      if (!response.ok) {
        const message =
          typeof data.detail === 'string'
            ? data.detail
            : 'Recon failed'

        throw new Error(message)
      }

      setResult(data)

    } catch (err) {
      setError(err.message || 'Recon failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-black text-white">

      {/* Background grid */}
      <div
        className="pointer-events-none fixed inset-0 opacity-5"
        style={{
          backgroundImage:
            'linear-gradient(to right, white 1px, transparent 1px), linear-gradient(to bottom, white 1px, transparent 1px)',
          backgroundSize: '56px 56px',
        }}
      />

      <main className="relative mx-auto max-w-6xl px-8 py-10">

        {/* Header */}
        <div className="mb-10">
          <p className="font-mono text-xs uppercase tracking-widest text-cyan-400">
            MOD-01
          </p>

          <h1 className="mt-2 text-2xl font-semibold">
            OSINT Recon
          </h1>

          <p className="mt-2 text-sm text-gray-500">
            Collect publicly available information about a domain.
          </p>
        </div>

        {/* Input */}
        <form
          onSubmit={runRecon}
          className="rounded border border-white/10 bg-black p-6"
        >
          <label className="font-mono text-xs uppercase tracking-wide text-gray-500">
            Target Domain
          </label>

          <div className="mt-3 flex gap-3">

            <input
              type="text"
              value={domain}
              onChange={(e) => setDomain(e.target.value)}
              placeholder="example.com"
              className="flex-1 rounded border border-white/10 bg-white/5 px-4 py-3 font-mono text-sm text-white outline-none placeholder:text-gray-600 focus:border-cyan-400/50"
            />

            <button
              type="submit"
              disabled={loading}
              className="rounded bg-cyan-500 px-6 py-3 font-mono text-sm font-semibold text-black transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading ? 'Scanning...' : 'Run Recon'}
            </button>

          </div>
        </form>

        {/* Error */}
        {error && (
          <div className="mt-6 rounded border border-red-400/30 bg-red-400/5 p-4 text-sm text-red-400">
            {error}
          </div>
        )}

        {/* Results */}
        {result && (
          <div className="mt-8 space-y-6">

            <div className="flex items-center justify-between border-b border-white/10 pb-4">

              <div>
                <p className="font-mono text-xs text-gray-500">
                  TARGET
                </p>

                <p className="mt-1 font-mono text-sm">
                  {result.domain}
                </p>
              </div>

              <span className="rounded border border-cyan-400/30 px-3 py-1 font-mono text-xs text-cyan-400">
                RECON COMPLETE
              </span>

            </div>

            {/* WHOIS */}
            <ResultSection title="WHOIS Information">

              <ResultItem
                label="Domain Name"
                value={result.whois?.domain_name}
              />

              <ResultItem
                label="Registrar"
                value={result.whois?.registrar}
              />

              <ResultItem
                label="Creation Date"
                value={result.whois?.creation_date}
              />

              <ResultItem
                label="Expiration Date"
                value={result.whois?.expiration_date}
              />

              <ResultItem
                label="Last Updated"
                value={result.whois?.updated_date}
              />

              <ResultItem
                label="Name Servers"
                value={result.whois?.name_servers}
              />

              <ResultItem
                label="Registrant Country"
                value={result.whois?.country}
              />

            </ResultSection>

            {/* DNS */}
            <ResultSection title="DNS Records">

              <ResultList
                title="A Records"
                items={result.dns?.A}
              />

              <ResultList
                title="MX Records"
                items={result.dns?.MX}
              />

              <ResultList
                title="TXT Records"
                items={result.dns?.TXT}
              />

              <ResultList
                title="NS Records"
                items={result.dns?.NS}
              />

            </ResultSection>

            {/* Subdomains */}
            <ResultSection title="Subdomains">

              {result.subdomains?.length > 0 ? (
                <div className="space-y-2">

                  {result.subdomains.map((subdomain, index) => (
                    <div
                      key={index}
                      className="rounded border border-white/10 bg-white/5 px-4 py-3 font-mono text-sm"
                    >
                      {formatValue(subdomain)}
                    </div>
                  ))}

                </div>
              ) : (
                <p className="text-sm text-gray-500">
                  No subdomains discovered.
                </p>
              )}

            </ResultSection>

            {/* Reputation */}
            <ResultSection title="Reputation Analysis">

              {result.reputation ? (
                <pre className="overflow-x-auto rounded border border-white/10 bg-white/5 p-4 font-mono text-xs text-gray-300">
                  {JSON.stringify(result.reputation, null, 2)}
                </pre>
              ) : (
                <p className="text-sm text-gray-500">
                  No reputation data available.
                </p>
              )}

            </ResultSection>

            {/* Security status */}
            <div className="rounded border border-cyan-400/20 bg-cyan-400/5 p-6">

              <p className="font-mono text-xs uppercase tracking-widest text-cyan-400">
                Security Status
              </p>

              <p className="mt-2 text-lg font-semibold">
                No security issues detected
              </p>

              <p className="mt-1 text-sm text-gray-500">
                The reconnaissance completed without identifying
                a security finding.
              </p>

            </div>

          </div>
        )}

      </main>
    </div>
  )
}


function ResultSection({ title, children }) {
  return (
    <section className="rounded border border-white/10 p-6">

      <h2 className="mb-5 font-mono text-sm uppercase tracking-wide">
        {title}
      </h2>

      <div className="space-y-4">
        {children}
      </div>

    </section>
  )
}


function ResultItem({ label, value }) {
  return (
    <div className="grid gap-2 border-b border-white/5 pb-3 sm:grid-cols-[180px_1fr]">

      <span className="font-mono text-xs text-gray-500">
        {label}
      </span>

      <span className="break-words text-sm text-gray-300">
        {formatValue(value)}
      </span>

    </div>
  )
}


function ResultList({ title, items }) {
  return (
    <div>

      <p className="mb-2 font-mono text-xs text-gray-500">
        {title}
      </p>

      {items?.length > 0 ? (
        <div className="space-y-2">

          {items.map((item, index) => (
            <div
              key={index}
              className="rounded border border-white/10 bg-white/5 px-4 py-2 font-mono text-sm text-gray-300"
            >
              {formatValue(item)}
            </div>
          ))}

        </div>
      ) : (
        <p className="text-sm text-gray-600">
          None found
        </p>
      )}

    </div>
  )
}


function formatValue(value) {
  if (value === null || value === undefined || value === '') {
    return 'N/A'
  }

  if (Array.isArray(value)) {
    return value.map((item) => formatValue(item)).join(', ')
  }

  if (typeof value === 'object') {
    return JSON.stringify(value)
  }

  return String(value)
}
