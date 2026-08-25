const features = [
  {
    number: "01",
    title: "Compare models",
    description:
      "Train several approaches on the same split, then see the tradeoffs side by side.",
  },
  {
    number: "02",
    title: "Understand results",
    description:
      "Move beyond a single score with metrics, error analysis, and feature signals.",
  },
  {
    number: "03",
    title: "Learn why",
    description:
      "Get plain-English explanations grounded in the experiment you actually ran.",
  },
];

const steps = [
  ["01", "Choose a dataset", "Upload a CSV or begin with a safe demo dataset."],
  ["02", "Configure your experiment", "Select a target, task type, and candidate models."],
  ["03", "Make a better decision", "Compare results and inspect the predictions behind them."],
];

export default function Home() {
  return (
    <main className="min-h-screen overflow-hidden bg-[#fafaf9] text-[#161614]">
      <header className="mx-auto flex w-full max-w-6xl items-center justify-between px-6 py-5 lg:px-8">
        <a className="flex items-center gap-2.5 font-semibold tracking-tight" href="#top">
          <span className="grid h-8 w-8 place-items-center rounded-lg bg-[#161614] text-sm text-white">M</span>
          ML Lab
        </a>
        <nav className="hidden items-center gap-7 text-sm text-[#62615b] md:flex">
          <a className="transition hover:text-[#161614]" href="#workflow">How it works</a>
          <a className="transition hover:text-[#161614]" href="#features">Features</a>
          <a className="transition hover:text-[#161614]" href="/learn">Learn</a>
        </nav>
        <a className="rounded-lg border border-[#dfded8] px-3.5 py-2 text-sm font-medium transition hover:border-[#aaa8a0]" href="/experiments/new">
          Start experimenting
        </a>
      </header>

      <section id="top" className="relative mx-auto max-w-6xl px-6 pb-24 pt-16 lg:px-8 lg:pb-32 lg:pt-24">
        <div className="absolute -right-56 top-2 -z-0 h-[29rem] w-[29rem] rounded-full bg-[#e9eee8] blur-3xl" />
        <div className="relative z-10 max-w-3xl">
          <p className="mb-6 inline-flex items-center gap-2 rounded-full border border-[#dcded7] bg-white/80 px-3 py-1.5 text-xs font-medium text-[#5c665b] shadow-sm">
            <span className="h-1.5 w-1.5 rounded-full bg-[#5f8163]" />
            A calmer way to experiment with ML
          </p>
          <h1 className="max-w-3xl text-5xl font-semibold leading-[1.04] tracking-[-0.055em] sm:text-6xl lg:text-7xl">
            Understand your machine learning models.
          </h1>
          <p className="mt-7 max-w-2xl text-lg leading-8 text-[#686761] sm:text-xl">
            Upload a dataset, compare models, analyze errors, and understand why your models behave the way they do.
          </p>
          <div className="mt-9 flex flex-col gap-3 sm:flex-row">
            <a className="rounded-lg bg-[#161614] px-5 py-3 text-center text-sm font-medium text-white shadow-sm transition hover:bg-[#33332f]" href="/experiments/new">
              Start an experiment <span aria-hidden="true">→</span>
            </a>
            <a className="rounded-lg border border-[#d8d7d0] bg-white px-5 py-3 text-center text-sm font-medium transition hover:border-[#aaa8a0]" href="/datasets">
              Try a demo dataset
            </a>
          </div>
        </div>

        <div className="relative z-10 mt-16 grid max-w-5xl gap-3 rounded-2xl border border-[#e3e2dc] bg-white p-4 shadow-[0_20px_60px_-30px_rgba(31,31,25,0.28)] sm:grid-cols-[1.1fr_1fr] sm:p-5">
          <div className="rounded-xl bg-[#f5f6f2] p-5">
            <div className="flex items-center justify-between text-xs text-[#72716a]"><span>EXPERIMENT OVERVIEW</span><span>Completed just now</span></div>
            <h2 className="mt-6 text-xl font-semibold tracking-tight">Student Performance</h2>
            <p className="mt-1 text-sm text-[#74736c]">Regression · 4 models · 4,832 rows</p>
            <div className="mt-7 rounded-lg border border-[#dfe2dc] bg-white p-4">
              <p className="text-xs font-medium tracking-wide text-[#667965]">BEST MODEL</p>
              <div className="mt-3 flex items-end justify-between"><span className="text-lg font-semibold">Random Forest</span><span className="text-3xl font-semibold tracking-tight">0.87</span></div>
              <p className="mt-1 text-right text-xs text-[#75746d]">R² score</p>
            </div>
          </div>
          <div className="rounded-xl border border-[#e6e5df] p-5">
            <div className="flex items-center justify-between"><h2 className="font-semibold">Model performance</h2><span className="rounded-md bg-[#f2f4ee] px-2 py-1 text-xs text-[#637262]">R²</span></div>
            <div className="mt-7 space-y-5">
              {[['Random Forest', '87%', '0.87'], ['Gradient Boosting', '84%', '0.84'], ['Neural Network', '81%', '0.81'], ['Linear Regression', '74%', '0.74']].map(([name, width, value]) => (
                <div key={name}>
                  <div className="mb-2 flex justify-between text-sm"><span>{name}</span><span className="font-medium">{value}</span></div>
                  <div className="h-2 overflow-hidden rounded-full bg-[#efefeb]"><div className="h-full rounded-full bg-[#6f8b6f]" style={{ width }} /></div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section id="features" className="border-y border-[#e7e6e0] bg-white">
        <div className="mx-auto max-w-6xl px-6 py-20 lg:px-8">
          <p className="text-xs font-semibold tracking-[0.16em] text-[#697b68]">BUILT FOR CLEAR THINKING</p>
          <div className="mt-4 flex max-w-2xl flex-col gap-5 sm:flex-row sm:items-end sm:justify-between">
            <h2 className="text-3xl font-semibold tracking-[-0.035em] sm:text-4xl">Everything you need to go from data to understanding.</h2>
          </div>
          <div className="mt-12 grid divide-y divide-[#e7e6e0] border-y border-[#e7e6e0] md:grid-cols-3 md:divide-x md:divide-y-0">
            {features.map((feature) => (
              <article key={feature.number} className="px-0 py-8 md:px-8 md:first:pl-0 md:last:pr-0">
                <span className="text-xs font-medium text-[#7d8d7b]">{feature.number}</span>
                <h3 className="mt-6 text-lg font-semibold">{feature.title}</h3>
                <p className="mt-3 max-w-xs text-sm leading-6 text-[#706f68]">{feature.description}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section id="workflow" className="mx-auto max-w-6xl px-6 py-24 lg:px-8">
        <div className="grid gap-12 lg:grid-cols-[0.8fr_1.2fr]">
          <div><p className="text-xs font-semibold tracking-[0.16em] text-[#697b68]">SIMPLE BY DEFAULT</p><h2 className="mt-4 text-3xl font-semibold tracking-[-0.035em] sm:text-4xl">A focused workflow that keeps the science visible.</h2></div>
          <div className="space-y-7">
            {steps.map(([number, title, body]) => <div key={number} className="grid grid-cols-[2.5rem_1fr] gap-4"><span className="pt-1 text-sm font-medium text-[#7d8d7b]">{number}</span><div><h3 className="font-semibold">{title}</h3><p className="mt-2 text-sm leading-6 text-[#706f68]">{body}</p></div></div>)}
          </div>
        </div>
      </section>

      <section className="mx-4 mb-4 rounded-2xl bg-[#20201d] px-6 py-16 text-white sm:mx-6 lg:mx-8">
        <div className="mx-auto flex max-w-6xl flex-col items-start justify-between gap-8 md:flex-row md:items-end"><div><p className="text-xs font-semibold tracking-[0.16em] text-[#aebea9]">READY WHEN YOU ARE</p><h2 className="mt-4 max-w-xl text-3xl font-semibold tracking-[-0.035em] sm:text-4xl">Try your first experiment in minutes.</h2></div><a className="rounded-lg bg-[#edf1e9] px-5 py-3 text-sm font-medium text-[#24251f] transition hover:bg-white" href="/experiments/new">Start experimenting →</a></div>
      </section>

      <footer className="mx-auto flex max-w-6xl flex-col gap-3 px-6 py-8 text-sm text-[#73726b] sm:flex-row sm:items-center sm:justify-between lg:px-8"><span>© 2026 ML Lab</span><span>Built for responsible experimentation.</span></footer>
    </main>
  );
}
