import Link from "next/link";

import { isDatabaseConfigured, listExperiments } from "@/lib/experiment-store";
import { getCurrentUser } from "@/lib/supabase/server";

export default async function ExperimentsPage() {
  const persistenceEnabled = isDatabaseConfigured();
  const user = await getCurrentUser();
  const experiments = persistenceEnabled && user ? await listExperiments(user.id) : [];

  return <main className="min-h-screen bg-[#fafaf9] px-6 py-12 text-[#161614] lg:px-8"><div className="mx-auto max-w-5xl"><header className="flex items-center justify-between"><Link className="font-semibold" href="/">ML Lab</Link><Link className="rounded-lg bg-[#161614] px-4 py-2.5 text-sm font-medium text-white" href="/experiments/new">New experiment</Link></header><p className="mt-14 text-xs font-semibold tracking-[0.15em] text-[#697b68]">EXPERIMENT HISTORY</p><h1 className="mt-3 text-4xl font-semibold tracking-[-0.045em]">Your saved experiments</h1>{!persistenceEnabled ? <div className="mt-8 rounded-xl border border-[#e3e2dc] bg-white p-6"><h2 className="font-semibold">Connect PostgreSQL to save results</h2><p className="mt-2 max-w-xl text-sm leading-6 text-[#706f68]">Set <code>DATABASE_URL</code> to a Supabase or other Postgres connection string, then run <code>npx prisma migrate dev</code>. Anonymous experimentation remains available without a database.</p></div> : !user ? <div className="mt-8 rounded-xl border border-[#e3e2dc] bg-white p-6"><h2 className="font-semibold">Sign in to see your history</h2><Link className="mt-4 inline-block rounded-lg bg-[#161614] px-4 py-2.5 text-sm font-medium text-white" href="/login">Continue with Google</Link></div> : experiments.length === 0 ? <p className="mt-8 text-[#706f68]">No saved experiments yet.</p> : <div className="mt-8 space-y-3">{experiments.map((experiment) => <article className="rounded-xl border border-[#e3e2dc] bg-white p-5" key={experiment.id}><h2 className="font-semibold">{experiment.name}</h2><p className="mt-1 text-sm text-[#706f68]">{experiment.problemType} · {experiment.targetColumn} · {experiment.dataset.name}</p></article>)}</div>}</div></main>;
}
