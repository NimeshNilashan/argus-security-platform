'use client'

import { UserButton, useUser } from '@clerk/nextjs'
import { useEffect, useState } from 'react'

const NAV_ITEMS = [
    "OSINT",
    "Port Scanner",
    "File Integrity",
    "Log Analyzer",
    "AI Assistant",
]

const STAT_STYLE = {
    Findings: "border-cyan-400/40",
    "High Risk": "border-red-400",
    Scans: "border-cyan-400/40",
    Files: "border-cyan-400/40",
}

const ACTIVITY = [
    "OSINT scan completed",
    "Port scan completed",
    "Log analysis completed",
    "File integrity verified",
]

export default function Dashboard() {

    const { user, isLoaded } = useUser()

    const [stats, setStats] = useState({
        findings: 0,
        high_risk: 0,
        scans: 0,
        files: 0,
    })

    const [loading, setLoading] = useState(true)

    useEffect(() => {

        if (!isLoaded || !user) {
            return
        }

        async function loadDashboard() {

            try {

                const response = await fetch(
                    `${process.env.NEXT_PUBLIC_API_URL}/dashboard/summary?user_id=${user.id}`
                )

                if (!response.ok) {
                    throw new Error("Failed to load dashboard")
                }

                const data = await response.json()

                setStats(data.stats)

            } catch (error) {

                console.error("Dashboard error:", error)

            } finally {

                setLoading(false)

            }
        }

        loadDashboard()

    }, [isLoaded, user])

    const statCards = [
        {
            label: "Findings",
            value: stats.findings,
            accent: STAT_STYLE.Findings,
        },
        {
            label: "High Risk",
            value: stats.high_risk,
            accent: STAT_STYLE["High Risk"],
        },
        {
            label: "Scans",
            value: stats.scans,
            accent: STAT_STYLE.Scans,
        },
        {
            label: "Files",
            value: stats.files,
            accent: STAT_STYLE.Files,
        },
    ]

    return (

        <div className="flex min-h-screen bg-black text-white">

            {/* Background grid */}

            <div
                className="pointer-events-none fixed inset-0 opacity-5"
                style={{
                    backgroundImage:
                        "linear-gradient(to right, white 1px, transparent 1px), linear-gradient(to bottom, white 1px, transparent 1px)",
                    backgroundSize: "56px 56px",
                }}
            />

            {/* Sidebar */}

            <aside className="flex w-56 shrink-0 flex-col border-r border-white/10">

                <div className="border-b border-white/10 px-5 py-5">
                    <span className="font-mono text-lg font-semibold tracking-tight">
                        ARGUS
                    </span>
                </div>

                <nav className="flex-1 py-4">

                    {NAV_ITEMS.map((item) => (

                        <button
                            key={item}
                            className="flex w-full items-center gap-3 border-l-2 border-transparent px-5 py-2.5 text-left font-mono text-xs uppercase tracking-wide text-gray-500 transition hover:border-white/20 hover:text-gray-300"
                        >
                            {item}
                        </button>

                    ))}

                </nav>

                <div className="border-t border-white/10 px-5 py-4">
                    <UserButton />
                </div>

            </aside>

            {/* Main content */}

            <main className="flex-1 px-8 py-8">

                {/* Top bar */}

                <div className="mb-10 flex items-center justify-between">

                    <h1 className="text-xl font-semibold">
                        Welcome back, {user?.firstName || "User"}
                    </h1>

                </div>

                {/* Security overview */}

                <section className="mb-12">

                    <h2 className="text-lg font-semibold">
                        Security overview
                    </h2>

                    <div className="mt-6 grid gap-px overflow-hidden rounded border border-white/10 bg-white/10 sm:grid-cols-4">

                        {statCards.map((stat) => (

                            <div
                                key={stat.label}
                                className={`border-l-2 bg-black px-6 py-5 ${stat.accent}`}
                            >

                                <p className="font-mono text-xs uppercase tracking-wide text-gray-500">
                                    {stat.label}
                                </p>

                                <p className="mt-2 font-mono text-3xl font-semibold">
                                    {loading ? "..." : stat.value}
                                </p>

                            </div>

                        ))}

                    </div>

                </section>

                {/* Recent activity */}

                <section className="max-w-2xl">

                    <h2 className="text-lg font-semibold">
                        Recent activity
                    </h2>

                    <div className="mt-5 rounded border border-white/10">

                        {ACTIVITY.map((activity, index) => (

                            <div
                                key={index}
                                className="flex items-center gap-3 border-b border-white/10 px-5 py-3.5 font-mono text-sm text-gray-300 last:border-b-0"
                            >

                                <span className="text-cyan-400">
                                    ✓
                                </span>

                                {activity}

                            </div>

                        ))}

                    </div>

                </section>

            </main>

        </div>
    )
}