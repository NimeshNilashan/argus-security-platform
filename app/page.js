export default function Home() {
  return (
      <main className="min-h-screen bg-black text-white">
        <div
            className="pointer-events-none fixed inset-0 opacity-5"
            style={{
              backgroundImage:
                  "linear-gradient(to right, white 1px, transparent 1px), linear-gradient(to bottom, white 1px, transparent 1px)",
              backgroundSize: "56px 56px",
            }}
        />

        {/* Header */}
        <header className="sticky top-0 z-10 border-b border-white/10 bg-black/80 backdrop-blur">
          <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
            <div className="flex items-center gap-3">
              <span className="font-mono text-lg font-semibold tracking-tight">ARGUS</span>
              <span className="hidden items-center gap-1.5 rounded border border-white/10 px-2 py-0.5 font-mono text-[10px] uppercase tracking-widest text-gray-500 sm:flex">

            </span>
            </div>
            <button className="cursor-pointer font-bold rounded font-mono text-sm text-gray-400 transition hover:text-cyan-400 focus:outline-none focus-visible:ring-2 focus-visible:ring-cyan-400 focus-visible:ring-offset-2 focus-visible:ring-offset-black">
              [ Sign in ]
            </button>
          </div>
        </header>

        {/* Hero */}
        <section className="mx-auto max-w-6xl px-6 py-20 md:py-28">
          <div className="grid gap-12 md:grid-cols-12 md:items-center">
            <div className="md:col-span-7">

              <h2 className="mt-5 text-4xl font-semibold leading-[1.1] tracking-tight sm:text-5xl">
                Everything scanning your
                <br />
                network, in one terminal.
              </h2>
              <p className="mt-6 max-w-lg text-base leading-relaxed text-gray-400">
                Sentinel runs OSINT reconnaissance, port scanning, file-integrity
                checks, and log analysis side by side — with an AI layer that
                flags what actually needs a human look.
              </p>
              <div className="mt-9 flex flex-wrap items-center gap-5">
                <button className="rounded bg-cyan-500 px-6 py-3 font-mono text-sm font-semibold text-black transition hover:bg-cyan-400 focus:outline-none focus-visible:ring-2 focus-visible:ring-cyan-400 focus-visible:ring-offset-2 focus-visible:ring-offset-black">
                  Run a scan
                </button>
                <a
                    href="#modules"
                    className="rounded font-mono text-sm text-gray-400 underline decoration-white/20 underline-offset-4 transition hover:text-white focus:outline-none focus-visible:ring-2 focus-visible:ring-cyan-400 focus-visible:ring-offset-2 focus-visible:ring-offset-black"
                >
                  View the modules →
                </a>
              </div>
            </div>


          </div>
        </section>

        {/* Modules  */}
        <section id="modules" className="mx-auto max-w-6xl px-6 pb-28">
          <div className="mb-10 border-b border-white/10 pb-6">
            <h3 className="mt-2 text-2xl font-semibold">The four engines</h3>
          </div>

          <div className="grid gap-px overflow-hidden rounded border border-white/10 bg-white/10 sm:grid-cols-2">
            {[
              {
                id: "MOD-01",
                title: "OSINT Recon",
                desc: "Discover domains, DNS records, and external exposure before an attacker does.",
                tag: "whois · dns · subdomains",
              },
              {
                id: "MOD-02",
                title: "Port Scanner",
                desc: "Multi-threaded scans across the full port range, with service fingerprinting.",
                tag: "1–65535 · multi-threaded",
              },
              {
                id: "MOD-03",
                title: "File Integrity",
                desc: "Hash every watched file and flag the exact byte that changed.",
                tag: "sha-256 diffing",
              },
              {
                id: "MOD-04",
                title: "Log Analysis",
                desc: "Score incoming logs for anomalies instead of just keyword matching.",
                tag: "detects suspicious activity",
              },
            ].map((item) => (
                <div key={item.id} className="bg-black p-7 transition hover:bg-white/5">
                  <div className="flex items-baseline justify-between">
                    <h4 className="font-mono text-sm font-semibold uppercase tracking-wide">{item.title}</h4>
                    <span className="font-mono text-xs text-gray-600">{item.id}</span>
                  </div>
                  <p className="mt-3 text-sm leading-relaxed text-gray-400">{item.desc}</p>
                  <p className="mt-4 font-mono text-xs text-cyan-400/70">{item.tag}</p>
                </div>
            ))}
          </div>
        </section>

        {/* Footer  */}
        <footer className="border-t border-white/10 px-6 py-8">
          <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 font-mono text-xs text-gray-600 sm:flex-row">
            <span>ARGUS — built as a security capstone by <span className="text-cyan-400/70"><a href="https://www.linkedin.com/in/nimesh-nilashan/">Nimesh Nilashan</a> </span> </span>
            <span>© 2026</span>
          </div>
        </footer>
      </main>
  );
}